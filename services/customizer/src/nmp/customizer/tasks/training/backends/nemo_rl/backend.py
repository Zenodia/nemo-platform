# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

"""TrainingBackend protocol implementation for NeMo RL (DPO)."""

import logging
import os
import signal
from pathlib import Path
from typing import Any, Optional, cast

from nemo_rl.utils.checkpoint import CheckpointingConfig, CheckpointManager
from nmp.customizer.app.jobs.context import NMPJobContext
from nmp.customizer.tasks.training.backends.nemo_rl.checkpoints import convert_dcp_to_huggingface
from nmp.customizer.tasks.training.chat_templates import apply_chat_template_to_checkpoint
from nmp.customizer.tasks.training.errors.parser import parse_error_from_output
from nmp.customizer.tasks.training.progress import JobsServiceProgressReporter
from nmp.customizer.tasks.training.protocol import LibraryConfig, TrainingBackend
from nmp.customizer.tasks.training.schemas import (
    CheckpointFormat,
    CheckpointInfo,
    TrainingMetrics,
    TrainingStepConfig,
    TrainingType,
)
from nmp.customizer.tasks.training.schemas import (
    TrainingBackend as TrainingBackendEnum,
)

from .dpo_config import compile_dpo_config
from .grpo_config import compile_grpo_config
from .ray_bootstrap import create_bootstrap_from_env

logger = logging.getLogger(__name__)

# Path to driver scripts (relative to this module)
_DRIVER_DIR = Path(__file__).parent


class NemoRLBackend(TrainingBackend):
    """TrainingBackend implementation for NeMo RL (DPO).

    This backend handles DPO (Direct Preference Optimization) training using NeMo RL.

    Key responsibilities:
    - Run pre-training conversions (model to HF format) via injected converter
    - Compile TrainingStepConfig to NeMo RL YAML format
    - Bootstrap Ray cluster on Volcano-provisioned pods
    - Execute appropriate training driver (DPO)
    - Process checkpoints to standard output format

    Args:
        job_ctx: Job context with job metadata
        nemo_to_hf_converter: Optional converter for model format conversion
    """

    def __init__(
        self,
        job_ctx: NMPJobContext,
    ) -> None:
        """Initialize the backend.

        Args:
            job_ctx: Job context with job metadata
        """
        self._job_ctx = job_ctx

    @property
    def backend_type(self) -> TrainingBackendEnum:
        return TrainingBackendEnum.NEMO_RL

    def compile_config(
        self,
        customizer_config: TrainingStepConfig,
        workspace_dir: Path,
    ) -> dict[str, Any]:
        """Compile TrainingStepConfig to NeMo RL YAML format.

        Args:
            config: The training step configuration
            workspace_dir: Directory for storing generated config files

        Returns:
            Configuration dict for NeMo RL (will be serialized to YAML)
        """
        training_type = customizer_config.training.training_type

        if training_type == TrainingType.DPO:
            return compile_dpo_config(customizer_config, self._job_ctx)
        elif training_type == TrainingType.GRPO:
            return compile_grpo_config(customizer_config, self._job_ctx)
        else:
            raise ValueError(
                f"NemoRLBackend does not support training type: {training_type}. "
                f"Supported types: {TrainingType.DPO}, {TrainingType.GRPO}"
            )

    def execute_training(
        self,
        customizer_config: TrainingStepConfig,
        library_config: LibraryConfig,
        progress: JobsServiceProgressReporter,
    ) -> TrainingMetrics:
        """Execute NeMo RL training via Ray bootstrap.

        Args:
            customizer_config: The training step configuration
            library_config: The compiled library configuration
            progress: Progress reporter for status updates

        Returns:
            TrainingMetrics with results from the training run
        """
        progress.report_running("training", backend=self.backend_type.value)

        # Get the workspace directory from config path
        workspace_dir = library_config.config_path.parent

        # Set up environment variables for the driver
        os.environ["BASE_LOG_DIR"] = str(workspace_dir)

        num_gpus_per_node = customizer_config.parallelism.num_gpus_per_node
        os.environ["GPUS_PER_NODE"] = str(num_gpus_per_node)

        # MLflow integration (if configured)
        if customizer_config.integrations and customizer_config.integrations.mlflow:
            mlflow_config = customizer_config.integrations.mlflow
            if mlflow_config.tracking_uri:
                os.environ["MLFLOW_URI"] = mlflow_config.tracking_uri

        # Build driver arguments
        driver_path = self._get_driver_path(customizer_config)
        driver_args = [
            "--config",
            str(library_config.config_path),
            "--id",
            self._job_ctx.job_id,
            "--output-model",
            customizer_config.model.name or "output_model",
        ]

        # Bootstrap Ray cluster and run driver
        logger.info(f"Starting Ray cluster and running driver: {driver_path}")
        logger.info(f"Driver args: {driver_args}")

        bootstrap = create_bootstrap_from_env()

        # Set up signal handler for cleanup — terminate the driver subprocess
        # explicitly so it doesn't become orphaned, then let SystemExit propagate
        # to trigger Ray cluster cleanup in the bootstrap's finally block.
        def cleanup(signum, frame):
            logger.warning(f"Signal {signum} received, terminating driver and cleaning up")
            bootstrap.terminate_driver(signum)
            raise SystemExit(signum)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        exit_code = bootstrap.run_with_driver(str(driver_path), driver_args)

        if exit_code != 0:
            parsed = parse_error_from_output(bootstrap.driver_output, exit_code)
            raise parsed.to_exception()

        logger.info("Training completed successfully")

        # Return empty metrics (actual metrics are logged during training)
        return TrainingMetrics(total_steps=0, total_epochs=0)

    def _get_driver_path(self, config: TrainingStepConfig) -> Path:
        """Get the appropriate driver script path based on training type.

        Args:
            config: Training configuration with type information

        Returns:
            Path to the driver script (dpo_driver.py or grpo_driver.py)
        """
        training_type = config.training.training_type

        if training_type == TrainingType.DPO:
            return _DRIVER_DIR / "dpo_driver.py"
        elif training_type == TrainingType.GRPO:
            return _DRIVER_DIR / "grpo_driver.py"
        else:
            raise ValueError(f"No driver available for training type: {training_type}")

    def find_best_checkpoint(
        self,
        workspace_dir: Path,
        customizer_config: TrainingStepConfig,
        library_config: Optional[LibraryConfig] = None,
    ) -> Path:
        """Find the best checkpoint after training.

        NeMo RL driver converts the best checkpoint to HuggingFace format
        and saves it to {workspace_dir}/output. This method returns that path.

        Args:
            workspace_dir: Directory containing training artifacts
            customizer_config: Training configuration

        Returns:
            Path to the converted HF checkpoint
        """
        if library_config is None:
            raise ValueError("Library config is required to find the best checkpoint")

        checkpointing_config = library_config.config_dict["checkpointing"]
        if checkpointing_config is None or not isinstance(checkpointing_config, dict):
            raise ValueError("Checkpointing config is required to find the best checkpoint")

        checkpointing_config = cast(CheckpointingConfig, checkpointing_config)
        checkpointer = CheckpointManager(checkpointing_config)

        try:
            best_checkpoint = checkpointer.get_best_checkpoint_path()
        except KeyError:
            # NeMo RL saves a checkpoint on the last step even without validation.
            # If that checkpoint lacks the metric, get_best_checkpoint_path() raises
            # KeyError. Fall back to the latest checkpoint.
            logger.warning("Metric not found in all checkpoints, falling back to latest checkpoint")
            best_checkpoint = checkpointer.get_latest_checkpoint_path()

        if best_checkpoint is None:
            raise ValueError("No best checkpoint found")

        best_checkpoint_path = Path(best_checkpoint)
        if not best_checkpoint_path.exists():
            raise ValueError(f"Best checkpoint not found at {best_checkpoint_path}")

        return best_checkpoint_path

    def process_checkpoint(
        self,
        checkpoint_path: Path,
        output_path: Path,
        customizer_config: TrainingStepConfig,
        library_config: LibraryConfig | None = None,
    ) -> CheckpointInfo:
        """Process NeMo RL checkpoint to standard output format.

        The NeMo RL driver already converts checkpoints to HuggingFace format.
        This method copies the output and applies the chat template.

        Args:
            checkpoint_path: Path to the checkpoint directory in the DCP format
            output_path: Where to write the processed checkpoint in the HF format
            customizer_config: Training configuration
            library_config: Library-specific config (contains chat template)

        Returns:
            CheckpointInfo with output path, format, and precision
        """
        logger.info("Processing created checkpoint")
        hf_checkpoint_path = convert_dcp_to_huggingface(checkpoint_path, output_path)

        # Apply chat template if available
        chat_template = None
        if library_config and library_config.config_dict:
            chat_template = library_config.config_dict.get("policy", {}).get("tokenizer", {}).get("chat_template")

        if chat_template:
            apply_chat_template_to_checkpoint(hf_checkpoint_path, chat_template)
            logger.debug("Applied chat template to checkpoint")

        return CheckpointInfo(
            path=str(hf_checkpoint_path),
            format=CheckpointFormat.HF,
            precision=customizer_config.model.precision,
        )
