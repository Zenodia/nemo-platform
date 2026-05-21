# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for DPO configuration compilation.

Tests the compile_dpo_config function which transforms TrainingStepConfig
into NeMo RL DPO configuration dict format.
"""

from pathlib import Path
from typing import Any

import pytest
import yaml
from nmp.customizer.app.jobs.context import NMPJobContext
from nmp.customizer.tasks.training.backends.nemo_rl.dpo_config import (
    _adapt_precision,
    _build_optimizer_config,
    _build_scheduler_config,
    _build_sequence_packing_config,
    compile_dpo_config,
)
from nmp.customizer.tasks.training.datasets.preparation import PreparedDataset
from nmp.customizer.tasks.training.schemas import (
    DPOConfig,
    ModelConfig,
    OptimizerType,
    Precision,
    TrainingBackend,
    TrainingStepConfig,
    TrainingType,
    WandBConfig,
)
from pytest_mock import MockerFixture

# Path to test data
# tests/tasks/training/backends/nemo_rl -> tests/testdata/dpo
TEST_DATA_DIR = Path(__file__).parent.parent.parent.parent / "testdata" / "dpo"
EXPECTED_CONFIG_PATH = TEST_DATA_DIR / "expected_dpo_config.yaml"


def build_training_step_config(**kwargs: Any) -> TrainingStepConfig:
    """Build TrainingStepConfig with default output_model for tests."""
    kwargs.setdefault("output_model", "output-model-name")
    return TrainingStepConfig(**kwargs)


@pytest.fixture
def expected_config() -> dict[str, Any]:
    """Load expected config from YAML file."""
    with open(EXPECTED_CONFIG_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture
def sample_chat_template() -> str:
    """Sample Llama-3 chat template."""
    return (
        "{% for message in messages %}{% set content = '<|start_header_id|>' "
        "+ message['role'] + '<|end_header_id|>\n\n' "
        "+ message['content'] | trim + '<|eot_id|>' %}{% if loop.index0 == 0 %}{% "
        "set content = bos_token + content %}{% endif %}{{ content }}{% endfor %}{% if "
        "add_generation_prompt %}{{ '<|start_header_id|>assistant<|end_header_id|>\n\n' }}{% endif %}"
    )


@pytest.fixture
def training_step_config() -> TrainingStepConfig:
    """Create a TrainingStepConfig matching the expected output."""
    return build_training_step_config(
        backend=TrainingBackend.NEMO_RL,
        model=ModelConfig(
            path="/mount/models/llama-3_2-1b-instruct-hf",
            name="meta/llama-3.2-1b-instruct",
            precision=Precision.BF16,
            max_seq_length=2048,
        ),
        dataset=TrainingStepConfig.DatasetConfig(
            path=f"{TEST_DATA_DIR}/dpo-convo",
        ),
        training=TrainingStepConfig.TrainingConfig(
            training_type=TrainingType.DPO,
            dpo=DPOConfig(
                ref_policy_kl_penalty=0.05,
                preference_average_log_probs=False,
                sft_average_log_probs=False,
                preference_loss_weight=1.0,
                sft_loss_weight=0.0,
                max_grad_norm=1.0,
            ),
        ),
        schedule=TrainingStepConfig.ScheduleConfig(
            epochs=1,
            max_steps=None,  # Computed from dataset
            val_check_interval=0.5,  # 50% of epoch
        ),
        batch=TrainingStepConfig.BatchConfig(
            global_batch_size=16,
            micro_batch_size=1,
            sequence_packing=False,
        ),
        optimizer=TrainingStepConfig.OptimizerConfig(
            learning_rate=5e-6,
            min_learning_rate=0.0,
            weight_decay=0.01,
            beta1=0.9,
            beta2=0.99,
            warmup_steps=200,
        ),
        parallelism=TrainingStepConfig.ParallelismConfig(
            num_nodes=1,
            num_gpus_per_node=1,
            tensor_parallel_size=1,
            pipeline_parallel_size=1,
            context_parallel_size=1,
            sequence_parallel=False,
        ),
        seed=42,  # Moved to top-level
    )


@pytest.fixture
def mock_prepared_dataset(tmp_path: Path) -> PreparedDataset:
    """Create a mock prepared dataset with known sample counts."""
    # Create mock dataset files
    train_file = tmp_path / "dataset" / "train.jsonl"
    val_file = tmp_path / "dataset" / "validation.jsonl"
    train_file.parent.mkdir(parents=True, exist_ok=True)

    # Create minimal JSONL content (88 steps * 16 batch_size = 1408 samples)
    train_samples = 1408
    val_samples = 100

    # Write dummy training data
    with open(train_file, "w") as f:
        for i in range(train_samples):
            f.write(f'{{"prompt": "q{i}", "chosen_response": "a", "rejected_response": "b"}}\n')

    # Write dummy validation data
    with open(val_file, "w") as f:
        for i in range(val_samples):
            f.write(f'{{"prompt": "q{i}", "chosen_response": "a", "rejected_response": "b"}}\n')

    return PreparedDataset(
        merged_dir=tmp_path / "dataset",
        train_file=train_file,
        validation_file=val_file,
        train_samples=train_samples,
        validation_samples=val_samples,
    )


@pytest.fixture
def job_ctx(tmp_path: Path) -> NMPJobContext:
    """Create a mock NMPJobContext for testing."""
    return NMPJobContext(
        workspace="test-workspace",
        job_id="test-job-id",
        attempt_id="attempt-0",
        step="training",
        task="dpo",
        jobs_url=None,
        files_url=None,
        storage_path=tmp_path / "storage",
        config_path=tmp_path / "config.yaml",
    )


class TestCompileDpoConfig:
    """Tests for compile_dpo_config function."""

    def test_compile_produces_valid_yaml_structure(
        self,
        training_step_config: TrainingStepConfig,
        mock_prepared_dataset: PreparedDataset,
        sample_chat_template: str,
        job_ctx: NMPJobContext,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Test that compile_dpo_config produces all required top-level sections."""
        # Mock prepare_dataset to return controlled values
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.prepare_dataset",
            return_value=mock_prepared_dataset,
        )
        # Mock chat template resolution
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.resolve_chat_template",
            return_value=sample_chat_template,
        )
        # Mock dataset validation to avoid slow file parsing
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.DatasetValidator.validate_dataset",
            return_value=None,
        )

        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)

        result = compile_dpo_config(training_step_config, job_ctx)

        # Verify all top-level sections exist
        assert "dpo" in result
        assert "checkpointing" in result
        assert "policy" in result
        assert "data" in result
        assert "logger" in result
        assert "cluster" in result

    def test_dpo_section_matches_expected(
        self,
        training_step_config: TrainingStepConfig,
        mock_prepared_dataset: PreparedDataset,
        expected_config: dict[str, Any],
        sample_chat_template: str,
        job_ctx: NMPJobContext,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Test that dpo section matches expected configuration."""
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.prepare_dataset",
            return_value=mock_prepared_dataset,
        )
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.resolve_chat_template",
            return_value=sample_chat_template,
        )
        # Mock dataset validation to avoid slow file parsing
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.DatasetValidator.validate_dataset",
            return_value=None,
        )

        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)

        result = compile_dpo_config(training_step_config, job_ctx)

        # Compare DPO section
        assert result["dpo"]["max_num_epochs"] == expected_config["dpo"]["max_num_epochs"]
        assert result["dpo"]["max_num_steps"] == expected_config["dpo"]["max_num_steps"]
        assert result["dpo"]["val_period"] == expected_config["dpo"]["val_period"]
        assert result["dpo"]["val_batches"] == expected_config["dpo"]["val_batches"]
        assert result["dpo"]["val_global_batch_size"] == expected_config["dpo"]["val_global_batch_size"]
        assert result["dpo"]["val_micro_batch_size"] == expected_config["dpo"]["val_micro_batch_size"]
        assert result["dpo"]["val_at_start"] == expected_config["dpo"]["val_at_start"]
        assert result["dpo"]["seed"] == expected_config["dpo"]["seed"]
        assert result["dpo"]["reference_policy_kl_penalty"] == expected_config["dpo"]["reference_policy_kl_penalty"]
        assert result["dpo"]["preference_average_log_probs"] == expected_config["dpo"]["preference_average_log_probs"]
        assert result["dpo"]["sft_average_log_probs"] == expected_config["dpo"]["sft_average_log_probs"]
        assert result["dpo"]["preference_loss_weight"] == expected_config["dpo"]["preference_loss_weight"]
        assert result["dpo"]["sft_loss_weight"] == expected_config["dpo"]["sft_loss_weight"]

    def test_policy_section_structure(
        self,
        training_step_config: TrainingStepConfig,
        mock_prepared_dataset: PreparedDataset,
        expected_config: dict[str, Any],
        sample_chat_template: str,
        job_ctx: NMPJobContext,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Test that policy section has correct structure."""
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.prepare_dataset",
            return_value=mock_prepared_dataset,
        )
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.resolve_chat_template",
            return_value=sample_chat_template,
        )
        # Mock dataset validation to avoid slow file parsing
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.DatasetValidator.validate_dataset",
            return_value=None,
        )

        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)

        result = compile_dpo_config(training_step_config, job_ctx)

        policy = result["policy"]

        # Verify model configuration
        assert policy["model_name"] == expected_config["policy"]["model_name"]
        assert policy["train_global_batch_size"] == expected_config["policy"]["train_global_batch_size"]
        assert policy["train_micro_batch_size"] == expected_config["policy"]["train_micro_batch_size"]
        assert policy["max_total_sequence_length"] == expected_config["policy"]["max_total_sequence_length"]
        assert policy["precision"] == expected_config["policy"]["precision"]
        assert policy["max_grad_norm"] == expected_config["policy"]["max_grad_norm"]

        # Verify tokenizer structure
        assert "tokenizer" in policy
        assert policy["tokenizer"]["name"] == expected_config["policy"]["model_name"]
        assert "chat_template" in policy["tokenizer"]

        # Verify dtensor_cfg structure
        assert "dtensor_cfg" in policy
        dtensor = policy["dtensor_cfg"]
        assert dtensor["enabled"] == expected_config["policy"]["dtensor_cfg"]["enabled"]
        assert dtensor["tensor_parallel_size"] == expected_config["policy"]["dtensor_cfg"]["tensor_parallel_size"]
        assert dtensor["context_parallel_size"] == expected_config["policy"]["dtensor_cfg"]["context_parallel_size"]

        # Verify optimizer structure
        assert "optimizer" in policy
        assert policy["optimizer"]["name"] == expected_config["policy"]["optimizer"]["name"]
        assert policy["optimizer"]["kwargs"]["lr"] == expected_config["policy"]["optimizer"]["kwargs"]["lr"]

        # Verify scheduler structure
        assert "scheduler" in policy
        assert len(policy["scheduler"]) == 3  # LinearLR, CosineAnnealingLR, milestones

    def test_checkpointing_section(
        self,
        training_step_config: TrainingStepConfig,
        mock_prepared_dataset: PreparedDataset,
        expected_config: dict[str, Any],
        sample_chat_template: str,
        job_ctx: NMPJobContext,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Test that checkpointing section matches expected values."""
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.prepare_dataset",
            return_value=mock_prepared_dataset,
        )
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.resolve_chat_template",
            return_value=sample_chat_template,
        )
        # Mock dataset validation to avoid slow file parsing
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.DatasetValidator.validate_dataset",
            return_value=None,
        )

        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)

        result = compile_dpo_config(training_step_config, job_ctx)

        ckpt = result["checkpointing"]
        expected_ckpt = expected_config["checkpointing"]

        assert ckpt["enabled"] == expected_ckpt["enabled"]
        assert ckpt["metric_name"] == expected_ckpt["metric_name"]
        assert ckpt["higher_is_better"] == expected_ckpt["higher_is_better"]
        assert ckpt["keep_top_k"] == expected_ckpt["keep_top_k"]
        assert ckpt["save_period"] == expected_ckpt["save_period"]

    def test_val_period_and_save_period_are_synchronized(
        self,
        training_step_config: TrainingStepConfig,
        mock_prepared_dataset: PreparedDataset,
        sample_chat_template: str,
        job_ctx: NMPJobContext,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Test that val_period and save_period use the same value.

        This is a workaround for NeMo RL's checkpointing behavior where:
        - Checkpoints are saved on last step regardless of save_period (due to is_last_step)
        - Validation only runs when (total_steps + 1) % val_period == 0

        To ensure validation metrics are available when checkpoints are saved,
        both periods must be synchronized (use the same value).
        """
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.prepare_dataset",
            return_value=mock_prepared_dataset,
        )
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.resolve_chat_template",
            return_value=sample_chat_template,
        )
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.DatasetValidator.validate_dataset",
            return_value=None,
        )

        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)

        result = compile_dpo_config(training_step_config, job_ctx)

        # val_period and save_period must be the same to ensure validation
        # metrics are available when checkpoints are saved
        assert result["dpo"]["val_period"] == result["checkpointing"]["save_period"]

    def test_val_period_is_exactly_equal_to_val_check_interval(
        self,
        mock_prepared_dataset: PreparedDataset,
        sample_chat_template: str,
        job_ctx: NMPJobContext,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Test that val_period is exactly equal to val_check_interval.

        NeMo RL saves checkpoints on the last step regardless of save_period.
        To ensure validation metrics are available when checkpoints are saved,
        val_period must be exactly equal to val_check_interval.
        """
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.prepare_dataset",
            return_value=mock_prepared_dataset,
        )
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.resolve_chat_template",
            return_value=sample_chat_template,
        )
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.DatasetValidator.validate_dataset",
            return_value=None,
        )

        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # Create config with explicit val_check_interval of 10 steps
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(
                path="/mount/models/llama-3_2-1b-instruct-hf",
                name="meta/llama-3.2-1b-instruct",
                precision=Precision.BF16,
                max_seq_length=2048,
            ),
            dataset=TrainingStepConfig.DatasetConfig(
                path=f"{TEST_DATA_DIR}/dpo-convo",
            ),
            training=TrainingStepConfig.TrainingConfig(
                training_type=TrainingType.DPO,
            ),
            schedule=TrainingStepConfig.ScheduleConfig(
                epochs=1,
                val_check_interval=10,  # Explicit step count
            ),
            batch=TrainingStepConfig.BatchConfig(
                global_batch_size=16,
                micro_batch_size=1,
            ),
            optimizer=TrainingStepConfig.OptimizerConfig(),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = compile_dpo_config(config, job_ctx)

        # val_period should be exactly equal to val_check_interval
        assert result["dpo"]["val_period"] == 10
        assert result["checkpointing"]["save_period"] == 10

    def test_cluster_section(
        self,
        training_step_config: TrainingStepConfig,
        mock_prepared_dataset: PreparedDataset,
        expected_config: dict[str, Any],
        sample_chat_template: str,
        job_ctx: NMPJobContext,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Test that cluster section matches expected values."""
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.prepare_dataset",
            return_value=mock_prepared_dataset,
        )
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.resolve_chat_template",
            return_value=sample_chat_template,
        )
        # Mock dataset validation to avoid slow file parsing
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.DatasetValidator.validate_dataset",
            return_value=None,
        )

        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)

        result = compile_dpo_config(training_step_config, job_ctx)

        assert result["cluster"] == expected_config["cluster"]

    def test_yaml_serialization_roundtrip(
        self,
        training_step_config: TrainingStepConfig,
        mock_prepared_dataset: PreparedDataset,
        sample_chat_template: str,
        job_ctx: NMPJobContext,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Test that the config can be serialized to YAML and loaded back."""
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.prepare_dataset",
            return_value=mock_prepared_dataset,
        )
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.resolve_chat_template",
            return_value=sample_chat_template,
        )
        # Mock dataset validation to avoid slow file parsing
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.DatasetValidator.validate_dataset",
            return_value=None,
        )

        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)

        result = compile_dpo_config(training_step_config, job_ctx)

        # Serialize to YAML
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(result, f, default_flow_style=False)

        # Load back and verify
        with open(config_path) as f:
            loaded = yaml.safe_load(f)

        assert loaded["dpo"]["max_num_epochs"] == result["dpo"]["max_num_epochs"]
        assert loaded["policy"]["model_name"] == result["policy"]["model_name"]
        assert loaded["cluster"] == result["cluster"]

    def test_nemo_rl_wandb_config_omits_dir(
        self,
        training_step_config: TrainingStepConfig,
        mock_prepared_dataset: PreparedDataset,
        sample_chat_template: str,
        job_ctx: NMPJobContext,
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """NeMo-RL logger passes dir separately, so wandb config must not include it."""
        monkeypatch.setenv("WANDB_API_KEY", "test-api-key")
        training_step_config.integrations = TrainingStepConfig.IntegrationsConfig(
            wandb=WandBConfig(project="test-project"),
        )
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.prepare_dataset",
            return_value=mock_prepared_dataset,
        )
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.resolve_chat_template",
            return_value=sample_chat_template,
        )
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.dpo_config.DatasetValidator.validate_dataset",
            return_value=None,
        )

        result = compile_dpo_config(training_step_config, job_ctx)

        assert result["logger"]["wandb_enabled"] is True
        assert "wandb" in result["logger"]
        assert "dir" not in result["logger"]["wandb"]


class TestAdaptPrecision:
    """Tests for _adapt_precision helper function."""

    @pytest.mark.parametrize(
        ("input_precision", "expected"),
        [
            ("bf16", "bfloat16"),
            ("bf16-mixed", "bfloat16"),
            ("fp16", "float16"),
            ("fp32", "float32"),
            (None, "bfloat16"),
        ],
    )
    def test_precision_mapping(self, input_precision: str | None, expected: str) -> None:
        """Test precision string adaptation."""
        result = _adapt_precision(input_precision)
        assert result == expected

    def test_unknown_precision_defaults_to_bfloat16(self) -> None:
        """Test that unknown precision values default to bfloat16."""
        result = _adapt_precision("unknown")
        assert result == "bfloat16"


class TestBuildSequencePackingConfig:
    """Tests for _build_sequence_packing_config helper function."""

    def test_sequence_packing_disabled(self) -> None:
        """Test config when sequence packing is disabled."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(sequence_packing=False),
            optimizer=TrainingStepConfig.OptimizerConfig(),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = _build_sequence_packing_config(config)
        assert result == {"enabled": False}

    def test_sequence_packing_enabled(self) -> None:
        """Test config when sequence packing is enabled."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(sequence_packing=True),
            optimizer=TrainingStepConfig.OptimizerConfig(),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = _build_sequence_packing_config(config)

        assert result["enabled"] is False


class TestBuildOptimizerConfig:
    """Tests for _build_optimizer_config helper function."""

    def test_optimizer_config_values(self) -> None:
        """Test optimizer configuration values."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(),
            optimizer=TrainingStepConfig.OptimizerConfig(
                learning_rate=1e-5,
                weight_decay=0.02,
                beta1=0.85,
                beta2=0.95,
            ),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = _build_optimizer_config(config)

        assert result["name"] == "torch.optim.AdamW"
        assert result["kwargs"]["lr"] == 1e-5
        assert result["kwargs"]["weight_decay"] == 0.02
        assert result["kwargs"]["betas"] == [0.85, 0.95]
        assert result["kwargs"]["eps"] == 1e-5
        assert result["kwargs"]["foreach"] is False
        assert result["kwargs"]["fused"] is False


class TestBuildSchedulerConfig:
    """Tests for _build_scheduler_config helper function."""

    def test_scheduler_config_structure(self) -> None:
        """Test scheduler configuration structure."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(),
            optimizer=TrainingStepConfig.OptimizerConfig(
                learning_rate=1e-4,
                min_learning_rate=1e-6,
                warmup_steps=100,
            ),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = _build_scheduler_config(config, total_steps=1000)

        assert isinstance(result, list)
        assert len(result) == 3

        # LinearLR warmup
        assert result[0]["name"] == "torch.optim.lr_scheduler.LinearLR"
        assert result[0]["kwargs"]["total_iters"] == 100
        assert result[0]["kwargs"]["end_factor"] == 1.0

        # CosineAnnealingLR decay
        assert result[1]["name"] == "torch.optim.lr_scheduler.CosineAnnealingLR"
        assert result[1]["kwargs"]["eta_min"] == 1e-6
        # T_max is now computed as max(total_steps - warmup_steps, 1) = max(1000 - 100, 1) = 900
        assert result[1]["kwargs"]["T_max"] == 900

        # Milestones
        assert result[2]["milestones"] == [100]

    @pytest.mark.parametrize(
        "optimizer_type",
        [
            OptimizerType.ADAM_WITH_FLAT_LR,
            OptimizerType.ADAMW_WITH_FLAT_LR,
        ],
    )
    def test_flat_lr_scheduler_returns_constant_lr(self, optimizer_type: OptimizerType) -> None:
        """Test that flat LR optimizer types return ConstantLR scheduler."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(),
            optimizer=TrainingStepConfig.OptimizerConfig(
                optimizer_type=optimizer_type,
                learning_rate=1e-4,
                warmup_steps=100,
            ),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = _build_scheduler_config(config, total_steps=500)

        assert isinstance(result, dict)
        assert result == {
            "name": "torch.optim.lr_scheduler.ConstantLR",
            "kwargs": {
                "factor": 1.0,
                "total_iters": 500,
            },
        }

    @pytest.mark.parametrize(
        "optimizer_type",
        [
            OptimizerType.ADAM_WITH_COSINE_ANNEALING,
            OptimizerType.ADAMW_WITH_COSINE_ANNEALING,
        ],
    )
    def test_cosine_annealing_scheduler_returns_composite_scheduler(self, optimizer_type: OptimizerType) -> None:
        """Test that cosine annealing optimizer types return composite scheduler."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(),
            optimizer=TrainingStepConfig.OptimizerConfig(
                optimizer_type=optimizer_type,
                learning_rate=1e-4,
                min_learning_rate=1e-6,
                warmup_steps=50,
            ),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = _build_scheduler_config(config, total_steps=1000)

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["name"] == "torch.optim.lr_scheduler.LinearLR"
        assert result[1]["name"] == "torch.optim.lr_scheduler.CosineAnnealingLR"
        assert result[2]["milestones"] == [50]

    def test_cosine_annealing_start_factor_calculation(self) -> None:
        """Test start_factor is computed as min_lr / lr."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(),
            optimizer=TrainingStepConfig.OptimizerConfig(
                optimizer_type=OptimizerType.ADAMW_WITH_COSINE_ANNEALING,
                learning_rate=1e-3,
                min_learning_rate=1e-5,
                warmup_steps=200,
            ),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = _build_scheduler_config(config, total_steps=1000)

        assert isinstance(result, list)
        expected_start_factor = 1e-5 / 1e-3  # 0.01
        assert result[0]["kwargs"]["start_factor"] == expected_start_factor
        assert result[0]["kwargs"]["end_factor"] == 1.0
        assert result[0]["kwargs"]["total_iters"] == 200

    def test_cosine_annealing_with_zero_learning_rate(self) -> None:
        """Test that zero learning rate uses minimum start_factor of 1e-5."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(),
            optimizer=TrainingStepConfig.OptimizerConfig(
                optimizer_type=OptimizerType.ADAMW_WITH_COSINE_ANNEALING,
                learning_rate=0.0,
                min_learning_rate=0.0,
                warmup_steps=100,
            ),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = _build_scheduler_config(config, total_steps=1000)

        assert isinstance(result, list)
        # When lr=0, start_factor should default to 1e-5
        assert result[0]["kwargs"]["start_factor"] == 1e-5

    def test_cosine_annealing_with_none_min_learning_rate(self) -> None:
        """Test that None min_learning_rate defaults to 0.0."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(),
            optimizer=TrainingStepConfig.OptimizerConfig(
                optimizer_type=OptimizerType.ADAMW_WITH_COSINE_ANNEALING,
                learning_rate=1e-4,
                min_learning_rate=None,
                warmup_steps=100,
            ),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = _build_scheduler_config(config, total_steps=1000)

        assert isinstance(result, list)
        # min_lr defaults to 0.0, so start_factor = max(0/1e-4, 1e-5) = 1e-5
        assert result[0]["kwargs"]["start_factor"] == 1e-5
        assert result[1]["kwargs"]["eta_min"] == 0.0

    def test_cosine_annealing_start_factor_minimum_bound(self) -> None:
        """Test that start_factor never goes below 1e-5."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(),
            optimizer=TrainingStepConfig.OptimizerConfig(
                optimizer_type=OptimizerType.ADAMW_WITH_COSINE_ANNEALING,
                learning_rate=1.0,
                min_learning_rate=1e-10,  # Would give 1e-10 start_factor
                warmup_steps=100,
            ),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = _build_scheduler_config(config, total_steps=1000)

        assert isinstance(result, list)
        # min_lr/lr = 1e-10 < 1e-5, so start_factor should be clamped to 1e-5
        assert result[0]["kwargs"]["start_factor"] == 1e-5

    def test_flat_lr_ignores_warmup_steps(self) -> None:
        """Test that flat LR scheduler ignores warmup_steps configuration."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(),
            optimizer=TrainingStepConfig.OptimizerConfig(
                optimizer_type=OptimizerType.ADAMW_WITH_FLAT_LR,
                learning_rate=1e-4,
                warmup_steps=500,  # Should be ignored
            ),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = _build_scheduler_config(config, total_steps=1000)

        assert isinstance(result, dict)
        # ConstantLR uses total_steps, not warmup_steps
        assert result["kwargs"]["total_iters"] == 1000

    def test_flat_lr_uses_total_steps_parameter(self) -> None:
        """Test that flat LR scheduler uses the total_steps parameter."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(),
            optimizer=TrainingStepConfig.OptimizerConfig(
                optimizer_type=OptimizerType.ADAM_WITH_FLAT_LR,
            ),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result_500 = _build_scheduler_config(config, total_steps=500)
        result_2000 = _build_scheduler_config(config, total_steps=2000)

        assert isinstance(result_500, dict)
        assert isinstance(result_2000, dict)
        assert result_500["kwargs"]["total_iters"] == 500
        assert result_2000["kwargs"]["total_iters"] == 2000

    def test_cosine_annealing_warmup_steps_in_milestones(self) -> None:
        """Test that warmup_steps is correctly set in milestones."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(),
            optimizer=TrainingStepConfig.OptimizerConfig(
                optimizer_type=OptimizerType.ADAMW_WITH_COSINE_ANNEALING,
                learning_rate=1e-4,
                warmup_steps=250,
            ),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = _build_scheduler_config(config, total_steps=1000)

        assert isinstance(result, list)
        assert result[0]["kwargs"]["total_iters"] == 250
        assert result[2]["milestones"] == [250]

    def test_cosine_annealing_eta_min_matches_min_learning_rate(self) -> None:
        """Test that CosineAnnealingLR eta_min matches min_learning_rate."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(),
            optimizer=TrainingStepConfig.OptimizerConfig(
                optimizer_type=OptimizerType.ADAMW_WITH_COSINE_ANNEALING,
                learning_rate=1e-3,
                min_learning_rate=5e-5,
                warmup_steps=100,
            ),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = _build_scheduler_config(config, total_steps=1000)

        assert isinstance(result, list)
        assert result[1]["kwargs"]["eta_min"] == 5e-5

    def test_cosine_annealing_t_max_calculation(self) -> None:
        """Test that CosineAnnealingLR T_max is calculated as total_steps - warmup_steps."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(),
            optimizer=TrainingStepConfig.OptimizerConfig(
                optimizer_type=OptimizerType.ADAMW_WITH_COSINE_ANNEALING,
                warmup_steps=100,
            ),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = _build_scheduler_config(config, total_steps=1000)

        assert isinstance(result, list)
        # T_max should be computed as max(total_steps - warmup_steps, 1) = max(1000 - 100, 1) = 900
        assert result[1]["kwargs"]["T_max"] == 900

    def test_cosine_annealing_t_max_minimum_value(self) -> None:
        """Test that CosineAnnealingLR T_max has a minimum value of 1."""
        config = build_training_step_config(
            backend=TrainingBackend.NEMO_RL,
            model=ModelConfig(path="/model"),
            dataset=TrainingStepConfig.DatasetConfig(path="/data"),
            training=TrainingStepConfig.TrainingConfig(training_type=TrainingType.DPO),
            schedule=TrainingStepConfig.ScheduleConfig(),
            batch=TrainingStepConfig.BatchConfig(),
            optimizer=TrainingStepConfig.OptimizerConfig(
                optimizer_type=OptimizerType.ADAMW_WITH_COSINE_ANNEALING,
                warmup_steps=500,
            ),
            parallelism=TrainingStepConfig.ParallelismConfig(),
        )

        result = _build_scheduler_config(config, total_steps=100)

        assert isinstance(result, list)
        # T_max should be at least 1 even when warmup_steps > total_steps
        # max(100 - 500, 1) = max(-400, 1) = 1
        assert result[1]["kwargs"]["T_max"] == 1
