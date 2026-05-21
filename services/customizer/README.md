# Customizer Service

**Model customization and fine-tuning service for the NeMo Platform.**

Customizer provides a user-friendly REST API that abstracts away low-level training frameworks like Automodel, Megatron-Bridge, and NeMo RL. Users specify high-level training parameters (model, dataset, hyperparameters), and Customizer handles the complexity of distributed training, checkpoint management, and framework-specific configuration.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [API Layer](#api-layer)
- [Compilation Pipeline](#compilation-pipeline)
- [Training Task](#training-task)
- [Training Backends](#training-backends)
- [Configuration Reference](#configuration-reference)
- [Related Documentation](#related-documentation)

---

## Overview

### Purpose

Customizer enables model customization through:

- **Supervised Fine-Tuning (SFT)** - Full weights or parameter-efficient (LoRA)
- **Knowledge Distillation (KD)** - Transfer knowledge from larger teacher models
- **Direct Preference Optimization (DPO)** - Preference-based alignment *(coming soon)*
- **Group Relative Policy Optimization (GRPO)** - RL-based post-training *(coming soon)*

### Where Customizer Fits

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        NeMo Platform                           │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│   │   Models    │  │  Datasets   │  │    Jobs     │  │    Files    │         │
│   │   Service   │  │   Service   │  │   Service   │  │   Service   │         │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│          │                │                │                │                │
│          └────────────────┼────────────────┼────────────────┘                │
│                           │                │                                 │
│                   ┌───────▼────────────────▼───────┐                         │
│                   │      CUSTOMIZER SERVICE        │                         │
│                   │                                │                         │
│                   │  • REST API                    │                         │
│                   │  • Job Compilation             │                         │
│                   │  • Training Orchestration      │                         │
│                   └────────────────────────────────┘                         │
│                                    │                                         │
│                   ┌────────────────┼────────────────┐                        │
│                   │                │                │                        │
│              ┌────▼────┐     ┌─────▼────┐    ┌─────▼────┐                    │
│              │Automodel│     │Megatron  │    │ NeMo RL  │                    │
│              │ Backend │     │ Bridge   │    │ Backend  │                    │
│              └─────────┘     └──────────┘    └──────────┘                    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

Customizer acts as the "functional service" that orchestrates model customization workflows by:

1. Accepting high-level job requests via REST API
2. Compiling requests into multi-step platform jobs
3. Delegating training to specialized backend containers
4. Managing checkpoints and outputting HuggingFace-compatible models

---

## Architecture

Customizer uses a **layered architecture** with clean separation between API concerns, business logic, and execution:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              REST API LAYER                                 │
│  api/v2/jobs/endpoints.py, schemas.py                                       │
│  CustomizationJobInput → user-facing schema                                 │
└────────────────────────────────────────┬────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           JOB COMPILATION LAYER                             │
│  app/jobs/compiler.py                                                       │
│  CustomizationJobInput → PlatformJobSpec (multi-step)                       │
│                                                                             │
│  Steps:                                                                     │
│    1. model-and-dataset-download (file_io task)                             │
│    2. customization-training-job (training task)                            │
│    3. model-upload (file_io task)                                           │
│    4. model-entity-creation (model_entity task)                             │
└────────────────────────────────────────┬────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TRAINING STEP COMPILATION                            │
│  app/jobs/training/compiler.py                                              │
│  CustomizationJobInput → TrainingStepConfig (standardized)                  │
│                                                                             │
│  - Validates parallelism constraints                                        │
│  - Determines backend (automodel/megatron_bridge/nemo_rl)                   │
│  - Builds standardized TrainingStepConfig                                   │
└────────────────────────────────────────┬────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TRAINING TASK LAYER                              │
│  tasks/training/__main__.py, runner.py                                      │
│                                                                             │
│  TrainingRunner orchestrates:                                               │
│    1. Config compilation (coordinator only)                                 │
│    2. Training execution (all ranks via torchrun)                           │
│    3. Checkpoint processing (coordinator only)                              │
│    4. Result writing                                                        │
└────────────────────────────────────────┬────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TRAINING BACKEND LAYER                            │
│  tasks/training/backends/{automodel,megatron_bridge,nemo_rl}/               │
│                                                                             │
│  TrainingBackend protocol implementations:                                  │
│    - compile_config()      → Library-specific YAML                          │
│    - execute_training()    → torchrun subprocess                            │
│    - find_best_checkpoint()                                                 │
│    - process_checkpoint()  → HuggingFace format output                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## API Layer

### CustomizationJobInput

The REST API accepts a `CustomizationJobInput` that captures user intent:

```python
class CustomizationJobInput(BaseModel):
    model: str                         # Model to customize
    training: TrainingMethod           # Training configuration (SFT, Distillation, DPO)
    dataset: str                       # Dataset URI (fileset://...)
    output: Optional[OutputRequest]    # Output name
    integrations: Optional[IntegrationParams]  # WandB, MLflow
```

### Training Configuration

Training is configured via a discriminated union (`TrainingMethod`) that includes `SFTTraining`, `DistillationTraining`, and `DPOTraining`. Each training type shares common fields:

```python
class _TrainingBase(BaseModel):
    peft: Optional[LoRAParams]         # PEFT configuration (LoRA)
    epochs: int = 1
    batch_size: int = 32
    learning_rate: float = 1e-4
    
    # Parallelism (nested)
    parallelism: Optional[Parallelism] = None  # num_nodes, num_gpus_per_node, TP, PP, etc.
```

---

## Compilation Pipeline

### Step 1: Job Compilation

`platform_job_config_compiler()` transforms `CustomizationJobInput` → `PlatformJobSpec`:

```python
async def platform_job_config_compiler(input_spec, entities_client) -> PlatformJobSpec:
    # Build file I/O config for model/dataset download
    file_io_config = _build_file_io_config(input_spec)
    
    # Compile training step with resolved paths
    training_compiler = TrainingStepCompiler()
    training_step = training_compiler.compile(job_input, resolved_paths, base_env)
    
    return PlatformJobSpec(steps=[
        # Step 1: Download model and dataset
        PlatformJobStep(name="model-and-dataset-download", ...),
        # Step 2: Training
        training_step,
        # Step 3: Upload output model
        PlatformJobStep(name="model-upload", ...),
    ])
```

### Step 2: Training Step Compilation

`TrainingStepCompiler.compile()` produces a `PlatformJobStep` with `TrainingStepConfig`:

```python
def compile(self, job_input, resolved_paths, base_env) -> PlatformJobStep:
    # Validate input (parallelism constraints, batch size, etc.)
    validate_customization_job_input(job_input)
    
    # Determine backend based on training type and parallelism
    backend = self._determine_backend(job_input)
    
    # Build standardized config
    training_config = TrainingStepConfig(
        backend=backend,
        model=ModelConfig(...),
        dataset=DatasetConfig(...),
        training=TrainingConfig(...),
        parallelism=ParallelismParams(...),
        ...
    )
    
    return PlatformJobStep(
        name="customization-training-job",
        executor=DistributedGPUExecutionProviderSpec(...),
        config=training_config.model_dump(),
    )
```

### Backend Selection Logic

```python
def _determine_backend(self, job_input) -> TrainingBackend:
    # RL training types → nemo_rl
    if training_type in (DPO, GRPO):
        return TrainingBackend.NEMO_RL
    
    # Advanced parallelism → megatron_bridge
    if pipeline_parallel > 1 or expert_parallel > 1:
        return TrainingBackend.MEGATRON_BRIDGE
    
    # Default → automodel
    return TrainingBackend.AUTOMODEL
```

---

## Training Task

### Entry Point

The training task (`tasks/training/__main__.py`) runs in GPU containers:

```python
def run() -> int:
    # Get paths and distributed context
    storage_path = get_storage_path()
    barrier_dir = get_barrier_dir()  # Namespaced by task ID
    dist_ctx = DistributedContext.from_env(barrier_dir)
    
    # Load config and backend
    customizer_config = load_config()
    backend = load_backend(customizer_config.backend)
    
    # Execute training
    runner = TrainingRunner(dist_ctx, customizer_config, progress, backend, storage_path)
    result = runner.run()
    
    return 0 if result.success else 1
```

### TrainingRunner Phases

The runner orchestrates training across single-node and multi-node environments:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COORDINATOR (Rank 0)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. validate_backend()                                                      │
│  2. compile_config() → write YAML                                           │
│  3. signal("config_ready")                                                  │
│  4. execute_training() ────────────────────────┐                            │
│  5. sync_point("training_complete") ◄──────────┼─── All ranks participate   │
│  6. find_best_checkpoint()                     │                            │
│  7. process_checkpoint() → HF format           │                            │
│  8. signal("postprocess_complete")             │                            │
│  9. write_result()                             │                            │
└────────────────────────────────────────────────┼────────────────────────────┘
                                                 │
┌────────────────────────────────────────────────┼────────────────────────────┐
│                         WORKER (Rank > 0)      │                            │
├────────────────────────────────────────────────┼────────────────────────────┤
│  1. wait_for_coordinator("config_ready")       │                            │
│  2. load config from YAML                      │                            │
│  3. execute_training() ────────────────────────┘                            │
│  4. sync_point("training_complete")                                         │
│  5. wait_for_coordinator("postprocess_complete")                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Distributed Coordination

File-based barriers enable cross-pod synchronization on shared storage:

```python
class DistributedContext:
    def signal(self, barrier_name: str):
        """Create marker file indicating this rank is ready."""
        marker = self._marker_path(barrier_name, self.rank)
        marker.touch()
    
    def wait_for_coordinator(self, barrier_name: str):
        """Poll for coordinator's marker file."""
        marker = self._marker_path(barrier_name, rank=0)
        while not marker.exists():
            time.sleep(self._poll_interval)
    
    def sync_point(self, barrier_name: str):
        """Signal and wait for all ranks."""
        self.signal(barrier_name)
        self.wait_all(barrier_name)
```

---

## Training Backends

### TrainingBackend Protocol

Each backend implements the `TrainingBackend` protocol:

```python
class TrainingBackend(Protocol):
    @property
    def backend_type(self) -> TrainingBackendEnum: ...
    
    def compile_config(
        self, customizer_config: TrainingStepConfig, workspace_dir: Path
    ) -> dict[str, Any]:
        """Transform standardized config to library-specific format."""
    
    def execute_training(
        self, customizer_config, library_config, progress
    ) -> TrainingMetrics:
        """Execute training using library-specific wrappers."""
    
    def find_best_checkpoint(self, workspace_dir, config) -> Path:
        """Find the best checkpoint after training."""
    
    def process_checkpoint(
        self, checkpoint_path, output_path, config, library_config
    ) -> CheckpointInfo:
        """Process checkpoint to HuggingFace format."""
```

### Automodel Backend

**Status:** ✅ Implemented

The automodel backend uses NeMo Automodel for PyTorch-native distributed training:

```
TrainingStepConfig
       │
       ▼
┌──────────────────────────┐
│ compile_automodel_config │
│                          │
│  - Dataset preparation   │
│  - Schema detection      │
│  - Optimal pack size     │
│  - FSDP2 config          │
│  - LoRA config           │
│  - KD config             │
└──────────┬───────────────┘
           │
           ▼
    automodel_config.yaml
           │
           ▼
┌──────────────────────────┐
│    torchrun --nproc...   │
│    finetune.py           │
│                          │
│  CustomizerRecipeWrapper │
│  wraps Automodel recipes │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  process_checkpoint()    │
│                          │
│  - LoRA merge (if needed)│
│  - FSDP2 arch fix        │
│  - Chat template apply   │
│  → HuggingFace format    │
└──────────────────────────┘
```

### Megatron-Bridge Backend

**Status:** 🔜 Planned

Required for:
- DoRA PEFT method
- Pipeline parallelism (PP > 1)
- Expert parallelism (MoE)
- Megatron-native models (GPT-OSS)

### NeMo RL Backend

**Status:** 🔜 Planned

Required for:
- DPO (Direct Preference Optimization)
- GRPO (Group Relative Policy Optimization)
- Reward model training
- Multi-turn RL

---

## Configuration Reference

### TrainingStepConfig

The standardized, backend-agnostic configuration:

```python
class TrainingStepConfig(BaseModel):
    # Backend selection
    backend: TrainingBackend  # automodel, megatron_bridge, nemo_rl
    
    # Model
    model: ModelConfig        # path, max_seq_length, precision
    
    # Dataset
    dataset: DatasetConfig    # path, prompt_template
    
    # Training type
    training: TrainingConfig  # type, finetuning_type, lora, kd
    
    # Schedule
    schedule: ScheduleConfig  # epochs, max_steps, val_check_interval
    
    # Batching
    batch: BatchConfig        # global_batch_size, micro_batch_size, sequence_packing
    
    # Optimizer
    optimizer: OptimizerConfig  # learning_rate, weight_decay, warmup_steps
    
    # Parallelism
    parallelism: ParallelismParams  # TP, PP, CP, EP, num_nodes
    
    # Integrations
    integrations: IntegrationParams  # wandb, mlflow
```

### TrainingResult

Output from training execution:

```python
class TrainingResult(BaseModel):
    success: bool
    error_message: Optional[str]
    checkpoint: Optional[CheckpointInfo]  # path, format, precision
    gpu_info: Optional[GPUInfo]           # architecture, memory
    metrics: TrainingMetrics              # final_loss, total_steps
    training_duration_seconds: Optional[float]
```

---

## Related Documentation

- [Training Backends Deep Dive](src/nmp/customizer/tasks/training/README.md) - Detailed analysis of Automodel, Megatron-Bridge, and NeMo RL
- [Container Architecture](../../architecture/docs/containers.md) - How training containers are built
- [Tasks and Jobs](../../architecture/docs/tasks-and-jobs.md) - Platform job execution model
- [Services Overview](../../architecture/docs/services.md) - NeMo Platform service architecture
