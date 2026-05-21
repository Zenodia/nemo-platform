# Customizer Training Backends

This document provides a comprehensive overview of the training backends used by Customizer, their capabilities, and the mapping between library features and Customizer support.

## Table of Contents

- [Overview](#overview)
- [Backend Selection](#backend-selection)
- [NeMo Automodel](#nemo-automodel)
- [NeMo Megatron-Bridge](#nemo-megatron-bridge)
- [NeMo RL](#nemo-rl)
- [Why Multiple Backends?](#why-multiple-backends)
- [Feature Comparison Matrix](#feature-comparison-matrix)
- [Implementation Priorities](#implementation-priorities)

## Overview

Customizer abstracts three training libraries into a unified API:

| Backend | Library | Primary Use Cases | Container |
|---------|---------|-------------------|-----------|
| `automodel` | NeMo Automodel | SFT, LoRA, KD for HuggingFace models | `nmp-gpu-tasks` |
| `megatron_bridge` | NeMo Megatron-Bridge | DoRA, PP>1, MoE, Megatron models | `nmp-gpu-tasks` |
| `nemo_rl` | NeMo RL | DPO, GRPO, reward modeling | `nmp-gpu-tasks` |

Each backend implements the `TrainingBackend` protocol:

```python
class TrainingBackend(Protocol):
    def compile_config(self, config: TrainingStepConfig, workspace_dir: Path) -> dict
    def execute_training(self, config, library_config, progress) -> TrainingMetrics
    def find_best_checkpoint(self, workspace_dir, config) -> Path
    def process_checkpoint(self, checkpoint_path, output_path, config, library_config) -> CheckpointInfo
```

## Backend Selection

The `TrainingStepCompiler` automatically selects the backend based on job configuration:

```python
def _determine_backend(job_input) -> TrainingBackend:
    # RL training types → nemo_rl
    if training_type in (TrainingType.DPO, TrainingType.GRPO):
        return TrainingBackend.NEMO_RL
    
    # Advanced parallelism → megatron_bridge
    if pipeline_parallel_size > 1 or expert_model_parallel_size > 1:
        return TrainingBackend.MEGATRON_BRIDGE
    
    # Default → automodel
    return TrainingBackend.AUTOMODEL
```

## NeMo Automodel

**Repository:** https://github.com/NVIDIA-NeMo/Automodel  
**Documentation:** https://docs.nvidia.com/nemo/automodel/latest/

### Library Overview

NeMo Automodel is a PyTorch DTensor-native SPMD library for large-scale LLM and VLM training. Key characteristics:

- **Day-0 HuggingFace Support** - Train any model from HuggingFace Hub without conversion
- **PyTorch Native** - Uses FSDP2, DTensor, and native parallelism
- **YAML-Driven** - Configuration via YAML with CLI overrides
- **SPMD Architecture** - Same code runs on 1 GPU or 1000+ by changing mesh

### Feature Mapping

| Automodel Feature | Description | Customizer Support | Notes |
|-------------------|-------------|-------------------|-------|
| **Training Types** |
| SFT (Full Weights) | Train all model parameters | ✅ Supported | Primary use case |
| LoRA PEFT | Low-rank adaptation | ✅ Supported | Via `finetuning_type=lora` |
| LoRA Merged | Merge adapter into base | ✅ Supported | Via `finetuning_type=lora_merged` |
| Knowledge Distillation | Teacher→Student transfer | ✅ Supported | Via `training_type=distillation` |
| Pretraining | Train from scratch | ❌ Not exposed | Out of scope for Customizer |
| VLM SFT | Vision-Language fine-tuning | ❌ Missing | See [VLM Plan](#vlm-sft-plan) |
| VLM LoRA | Vision-Language PEFT | ❌ Missing | See [VLM Plan](#vlm-sft-plan) |
| **Parallelism** |
| FSDP2 | Fully Sharded Data Parallel | ✅ Supported | Default strategy |
| Tensor Parallelism | Split weights across GPUs | ✅ Supported | Via `tensor_parallel_size` |
| Pipeline Parallelism | Split layers across GPUs | ⚠️ Basic support | PyTorch native; use MB for VPP/advanced opts |
| Context Parallelism | Split sequence for long context | ✅ Supported | Via `context_parallel_size` |
| Sequence Parallelism | Parallelize LayerNorm/Dropout | ✅ Supported | Via `use_sequence_parallel` |
| HSDP | Hybrid Sharded Data Parallel | ✅ Supported | Multi-node FSDP2 |
| Expert Parallelism | MoE expert distribution | ✅ Supported | Via `expert_model_parallel_size` |
| **Optimization** |
| Sequence Packing | Pack short sequences | ✅ Supported | Via `sequence_packing_enabled` |
| FP8 Training | 8-bit floating point | ❌ Missing | See [FP8 Plan](#fp8-training-plan) |
| torch.compile | JIT compilation | ❌ Missing | Requires `compile` config section |
| Gradient Checkpointing | Memory optimization | ❌ Missing | Not exposed in API |
| **Checkpointing** |
| DCP (SafeTensors) | Distributed checkpoints | ✅ Supported | Default format |
| HF Export | Convert to HuggingFace | ✅ Supported | `process_checkpoint()` |
| Consolidated Save | Single-file checkpoint | ✅ Supported | For single-node |
| **Integrations** |
| WandB | Weights & Biases | ✅ Supported | Via `integrations.wandb` |
| MLflow | MLflow tracking | ✅ Supported | Via `integrations.mlflow` |
| **Models** |
| Dense LLMs | Llama, Qwen, Gemma, Phi, etc. | ✅ Supported | Day-0 HF support |
| MoE LLMs | DeepSeek V3, Mixtral, etc. | ✅ Supported | Via custom model detection |
| VLMs | Gemma-3-VL, Qwen2-VL, etc. | ❌ Missing | See [VLM Plan](#vlm-sft-plan) |
| Embedding Models | Bi-encoder, BERT | ❌ Missing | Different training recipe |

### Implementation Details

**Current Implementation:**

```
backends/automodel/
├── backend.py      # TrainingBackend protocol implementation
├── config.py       # compile_automodel_config() - YAML generation
├── checkpoints.py  # Checkpoint discovery and processing
├── finetune.py     # torchrun entry point (recipe dispatch)
├── callbacks.py    # TrainingProgressCallback for progress reporting
└── requirements.txt
```

**Config Compilation Flow:**

1. **Dataset Preparation** - Merge files, detect schema (chat/SFT/custom)
2. **Sequence Packing** - Calculate optimal pack size from dataset statistics
3. **FSDP2 Manager** - Configure TP/PP/CP/DP mesh
4. **Model Loading** - HuggingFace model with precision settings
5. **LoRA Config** - If PEFT enabled, configure adapter
6. **KD Config** - If distillation, add teacher model and loss

**Recipe Dispatch (finetune.py):**

```python
def create_customizer_recipe(cfg):
    if _is_kd_config(cfg):
        base_recipe = KnowledgeDistillationRecipeForNextTokenPrediction(cfg)
    else:
        base_recipe = TrainFinetuneRecipeForNextTokenPrediction(cfg)
    return CustomizerRecipeWrapper(base_recipe)
```

### Missing Features - Implementation Plans

#### VLM SFT Plan

**Priority:** P2 (Feature enhancement)

Automodel supports VLM fine-tuning via:
- `nemo_automodel.recipes.vlm.train_ft.TrainFinetuneRecipeForVLM`
- Models: Gemma-3-VL, Qwen2-VL, Phi-4-MM, InternVL

**Implementation Steps:**

1. Add `model_type` field to `TrainingStepConfig` (enum: `llm`, `vlm`)
2. Detect VLM from model architecture in `compile_automodel_config()`
3. Configure VLM-specific dataset class (`VLMChatDataset`)
4. Add image processing configuration
5. Switch to VLM recipe in `finetune.py`:
   ```python
   if is_vlm:
       from nemo_automodel.recipes.vlm.train_ft import TrainFinetuneRecipeForVLM
       base_recipe = TrainFinetuneRecipeForVLM(cfg)
   ```
6. Handle multi-modal checkpointing

#### FP8 Training Plan

**Priority:** P3 (Performance optimization)

Automodel supports FP8 via TorchAO with `torch.compile`:

```yaml
compile:
  enabled: true
  mode: "default"

fp8:
  enabled: true
  recipe_name: tensorwise
  enable_fsdp_float8_all_gather: true
```

**Implementation Steps:**

1. Add `fp8_enabled: bool` to `Hyperparameters`
2. Validate hardware requirements (H100+)
3. Add `compile` and `fp8` sections to config compilation
4. Update container to include TorchAO


## NeMo Megatron-Bridge

**Repository:** https://github.com/NVIDIA-NeMo/Megatron-Bridge  
**Documentation:** https://docs.nvidia.com/nemo/megatron-bridge/latest/

### Library Overview

NeMo Megatron-Bridge provides a bridge between HuggingFace and Megatron Core, enabling high-performance training with Megatron's optimizations. Key characteristics:

- **Bidirectional Conversion** - HF ↔ Megatron Core checkpoints
- **Megatron Core Backend** - Leverage optimized kernels and parallelism
- **DoRA Support** - Weight-Decomposed Low-Rank Adaptation
- **6D Parallelism** - TP/PP/CP/SP/EP/ETP for massive scale

### Feature Mapping

| Megatron-Bridge Feature | Description | Customizer Support | Notes |
|-------------------------|-------------|-------------------|-------|
| **Training Types** |
| Pretraining | Train from scratch | ❌ Not exposed | Out of scope |
| SFT | Supervised fine-tuning | ❌ Missing | See [MB SFT Plan](#megatron-bridge-sft-plan) |
| LoRA PEFT | Low-rank adaptation | ❌ Missing | See [MB LoRA Plan](#megatron-bridge-lora-plan) |
| DoRA PEFT | Weight-decomposed LoRA | ❌ Missing | See [DoRA Plan](#dora-plan) |
| **Conversion** |
| HF → Megatron | Import HF checkpoints | ❌ Missing | Required for MB backend |
| Megatron → HF | Export to HF format | ❌ Missing | Required for MB backend |
| Online Conversion | Stream without intermediate files | ❌ Missing | Memory-efficient |
| **Parallelism** |
| Tensor Parallel | Split attention/FFN | ❌ Missing | Requires MB backend |
| Pipeline Parallel | Split layers | ❌ Missing | **Advanced PP (VPP, comm overlap)** |
| Virtual Pipeline | Interleaved schedule | ❌ Missing | Reduces bubble time |
| Context Parallel | Long sequence support | ❌ Missing | Ring attention |
| Expert Parallel | MoE distribution | ❌ Missing | **Key differentiator** |
| Expert Tensor Parallel | TP within experts | ❌ Missing | For large experts |
| **Optimization** |
| FP8 (Transformer Engine) | Hardware-accelerated FP8 | ❌ Missing | Better than TorchAO |
| FP4 Training | 4-bit precision | ❌ Missing | Memory efficiency |
| Sequence Packing | Pack short sequences | ❌ Missing | Megatron-style |
| Communication Overlap | Hide comm latency | ❌ Missing | Async gradient sync |
| **Models** |
| Standard LLMs | Llama, Qwen, Gemma, etc. | ❌ Missing | Via AutoBridge |
| GPT-OSS | OpenAI-style models | ❌ Missing | **Megatron-native** |
| GLM-4.5 | Chinese LLM | ❌ Missing | Custom bridge |
| DeepSeek V2/V3 | Large MoE | ❌ Missing | EP required |
| Nemotron-H | NVIDIA hybrid | ❌ Missing | Custom architecture |
| VLMs | Gemma3-VL, Qwen2.5-VL | ❌ Missing | Vision-language |

### Implementation Status

**Status:** ⬜ Not Started

Backend implementation requires:

1. **Bridge Integration** - `AutoBridge.from_hf_pretrained()` for checkpoint import
2. **Training Loop** - Megatron Core training with `pretrain()` or `finetune()`
3. **PEFT Support** - LoRA and DoRA via `megatron.bridge.peft`
4. **Export** - `bridge.save_hf_pretrained()` for checkpoint export

### Missing Features - Implementation Plans

#### Megatron-Bridge SFT Plan

**Priority:** P2 (Specialized scenarios)

Required when:
- **Advanced Pipeline Parallelism**: Virtual Pipeline Parallelism (VPP) for reduced bubble time, communication overlap
- **Large-scale PP**: 8+ pipeline stages with production-grade reliability
- **Expert Parallelism**: MoE models with expert-specific optimizations
- **DoRA PEFT**: Weight-decomposed LoRA (not available in Automodel)
- **FP8 with Transformer Engine**: Hardware-accelerated FP8 training

**Implementation Steps:**

1. Create `backends/megatron_bridge/backend.py`:
   ```python
   class MegatronBridgeBackend(TrainingBackend):
       def compile_config(self, config, workspace_dir):
           # 1. Create AutoBridge from HF model
           # 2. Configure Megatron provider
           # 3. Build training config
   ```

2. Create `backends/megatron_bridge/config.py` for config compilation:
   ```python
   def compile_megatron_config(config: TrainingStepConfig) -> ConfigContainer:
       bridge = AutoBridge.from_hf_pretrained(config.model.path)
       provider = bridge.to_megatron_provider()
       provider.tensor_model_parallel_size = config.parallelism.tensor_parallel_size
       provider.pipeline_model_parallel_size = config.parallelism.pipeline_parallel_size
       ...
   ```

3. Create training entry point using `finetune()` function

4. Implement checkpoint export via `save_hf_pretrained()`

#### DoRA Plan

**Priority:** P2 (PEFT enhancement)

DoRA (Weight-Decomposed LoRA) available in Megatron-Bridge:

```python
from megatron.bridge.peft.dora import DoRA

peft = DoRA(dim=32, alpha=32, dropout=0.0)
```

**Implementation Steps:**

1. Add `DoRAConfig` to `TrainingStepConfig`:
   ```python
   class DoRAConfig(BaseModel):
       dim: int = 32
       alpha: int = 32
       dropout: float = 0.0
   ```

2. Add `dora` option to `FinetuningType` enum

3. Implement in Megatron-Bridge backend config compilation

4. Update backend selection:
   ```python
   if finetuning_type == FinetuningType.DORA:
       return TrainingBackend.MEGATRON_BRIDGE
   ```



## NeMo RL

**Repository:** https://github.com/NVIDIA-NeMo/RL  
**Documentation:** https://docs.nvidia.com/nemo/rl/latest/

### Library Overview

NeMo RL is a post-training library for reinforcement learning methods. Key characteristics:

- **Ray-Based** - Distributed training with Ray actors
- **Dual Training Backends** - DTensor (via Automodel) or Megatron Core
- **Dual Generation Backends** - vLLM or Megatron Core inference
- **Algorithm Support** - GRPO, DPO, SFT, reward modeling

### Infrastructure Challenge: Ray on Volcano

NeMo RL's architecture is Ray-based, while Customizer uses Volcano to provision GPU pods and executes training using torchrun. This creates an architectural tension:

| Aspect | Volcano + torchrun (Automodel) | Ray (NeMo RL) |
|--------|--------------------------------|---------------|
| **Orchestrator** | Volcano CRD + PyTorch plugin | Ray Head + Workers |
| **Pod provisioning** | Gang scheduling via Volcano | Ray Placement Groups |
| **Networking** | Headless K8s service | Ray GCS (port 6379) + object store |
| **Env vars injected** | `MASTER_ADDR`, `MASTER_PORT`, `WORLD_SIZE`, `RANK` | Same, but set by Ray internally |
| **Process model** | 1 process per pod, all start together | Driver spawns Ray Actors dynamically |

**Solution:** Bootstrap Ray on Volcano-provisioned pods.

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      VOLCANO JOB (Gang Scheduled)                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Pod 0 (RANK=0)                      Pod 1 to N (RANK>0)                    | 
│   ┌─────────────────────────────┐     ┌────────────────────────────────┐     │
│   │ __main__.py                 │     │ __main__.py                    │     │
│   │   │                         │     │   │                            │     │
│   │   ├─ Load NemoRLBackend     │     │   ├─ Load NemoRLBackend        │     │
│   │   │                         │     │   │                            │     │
│   │   └─ execute_training()     │     │   └─ execute_training()        │     │
│   │        │                    │     │        │                       │     │
│   └────────┼────────────────────┘     └────────┼───────────────────────┘     │
│            │                                   │                             │
│   ┌────────▼────────────────────┐     ┌────────▼───────────────────────┐     │
│   │ ray_bootstrap.py            │     │ ray_bootstrap.py               │     │
│   │   │                         │     │   │                            │     │
│   │   ├─ ray start --head       │     │   ├─ ray start                 │     │
│   │   │    --node-ip=$MASTER_ADDR     │   │    --address=$MASTER_ADDR  │     │
│   │   │    --port=6379          │     │   │    :6379                   │     │
│   │   │                         │     │   │                            │     │
│   │   ├─ Poll until all workers │     │   └─ Block until ENDED signal  │     │
│   │   │    connected            │     │                                │     │
│   │   │                         │     └────────────────────────────────┘     │
│   │   ├─ run dpo_driver.py or   │                                            │
│   │   │      grpo_driver.py     │                                            │
│   │   │                         │                                            │
│   │   └─ cleanup: signal ENDED  │                                            │
│   └─────────────────────────────┘                                            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Feature Mapping

| NeMo RL Feature | Description | Customizer Support | Notes |
|-----------------|-------------|-------------------|-------|
| **Algorithms** |
| GRPO | Group Relative Policy Optimization | ❌ Missing | See [GRPO Plan](#grpo-plan) |
| GSPO | Group-wise Sampling PO | ❌ Missing | GRPO variant |
| DAPO | Decoupled Clip + Dynamic Sampling | ❌ Missing | Advanced GRPO |
| DPO | Direct Preference Optimization | ❌ Missing | See [DPO Plan](#dpo-plan) |
| SFT | Supervised Fine-Tuning (warmup) | ❌ Missing | Pre-RL step |
| Reward Modeling | Train reward models | ❌ Missing | See [RM Plan](#reward-model-plan) |
| On-Policy Distillation | KL-guided distillation | ❌ Missing | Student→Teacher |
| **Environments** |
| Math | Mathematical reasoning | ❌ Missing | OpenMathInstruct-2 |
| Code | Code generation | ❌ Missing | Code correctness |
| Reward Model | RM-based rewards | ❌ Missing | Trained RM |
| Multi-Turn | Tool use, games | ❌ Missing | Conversation RL |
| **Training Backends** |
| DTensor (Automodel) | PyTorch FSDP2, TP, CP, SP | ❌ Missing | Default backend |
| Megatron Core | 6D parallelism | ❌ Missing | Large-scale |
| **Generation Backends** |
| vLLM | High-throughput inference | ❌ Missing | Default engine |
| Megatron Inference | No weight conversion | ❌ Missing | Day-0 support |
| **Optimization** |
| Sequence Packing | Reduce padding | ❌ Missing | Training efficiency |
| Dynamic Batching | Variable batch sizes | ❌ Missing | Generation efficiency |
| FP8 Training | End-to-end FP8 | ❌ Missing | Megatron + vLLM |
| Async RL | Asynchronous rollouts | ❌ Missing | Off-policy training |
| **VLM Support** |
| VLM SFT | Vision-language SFT | ❌ Missing | Multi-modal |
| VLM GRPO | Vision-language RL | ❌ Missing | Multi-modal RL |
| **Data Formats** |
| Preference Pairs | Chosen/rejected | ❌ Missing | DPO datasets |
| Response | Input/output | ❌ Missing | SFT/GRPO datasets |
| HelpSteer3 | NVIDIA preference | ❌ Missing | Built-in support |

### Implementation Status

**Status:** ⬜ Not Started

### Components

Expected component layout for the NeMo RL backend:

| File | Purpose |
|------|---------|
| `ray_bootstrap.py` | Ray cluster bootstrap on Volcano-provisioned pods |
| `backends/nemo_rl/backend.py` | Entry point orchestrator |
| `backends/nemo_rl/config.py` | DPO/GRPO config generation |
| `backends/nemo_rl/dpo_driver.py` | DPO training driver |
| `backends/nemo_rl/grpo_driver.py` | GRPO training driver |
| `backends/nemo_rl/logger.py` | Progress reporting |

### Proposed Directory Structure

```
backends/nemo_rl/
├── backend.py           # TrainingBackend protocol implementation
├── config.py            # TrainingStepConfig → NeMo RL YAML
├── ray_bootstrap.py     # Python equivalent of run-ray.sh
├── dpo_driver.py        # DPO training driver (torchrun entry)
├── grpo_driver.py       # GRPO training driver (torchrun entry)
├── checkpoints.py       # DCP → HuggingFace conversion
├── logger.py            # NemoRLLogger for progress reporting
└── environments/        # GRPO environment configs
    ├── __init__.py
    ├── math.py          # Math environment (penguin)
    ├── code.py          # Code execution environment
    └── reward_model.py  # RM-based environment
```

### Key Migration Components

#### 1. Ray Bootstrap (`ray_bootstrap.py`)

Rewrite `run-ray.sh` in Python for better integration:

```python
class RayClusterBootstrap:
    """Bootstrap Ray cluster on Volcano-provisioned pods."""
    
    def __init__(self, rank: int, world_size: int, master_addr: str):
        self.rank = rank
        self.world_size = world_size
        self.master_addr = master_addr
        self.gcs_port = 6379
        self.gpus_per_node = int(os.getenv("GPUS_PER_NODE", 1))
        
    def start(self) -> None:
        """Start Ray head (rank 0) or worker (rank > 0)."""
        if self.rank == 0:
            self._start_head()
            self._wait_for_workers()
        else:
            self._start_worker()
            self._wait_for_termination()
    
    def _start_head(self) -> None:
        """Start Ray head node."""
        subprocess.run([
            "ray", "start", "--head",
            "--disable-usage-stats",
            f"--node-ip-address={self.master_addr}",
            f"--port={self.gcs_port}",
            f'--resources={{"worker_units": {self.gpus_per_node}}}',
            "--block"
        ], check=True)
    
    def _start_worker(self) -> None:
        """Start Ray worker node."""
        subprocess.run([
            "ray", "start",
            f"--address={self.master_addr}:{self.gcs_port}",
            "--disable-usage-stats",
            f'--resources={{"worker_units": {self.gpus_per_node}}}',
            "--block"
        ], check=True)
    
    def _wait_for_workers(self) -> None:
        """Poll until all workers connected."""
        expected = self.world_size * self.gpus_per_node
        while True:
            worker_units = self._get_worker_units()
            if worker_units >= expected:
                break
            time.sleep(2)
    
    def _get_worker_units(self) -> int:
        """Extract worker_units from ray status."""
        result = subprocess.run(["ray", "status"], capture_output=True, text=True)
        # Parse worker_units from output
        ...
```

#### 2. NeMo RL Backend (`backend.py`)

```python
class NemoRLBackend:
    """TrainingBackend implementation for NeMo RL (DPO/GRPO)."""
    
    @property
    def backend_type(self) -> TrainingBackendEnum:
        return TrainingBackendEnum.NEMO_RL
    
    def compile_config(
        self, config: TrainingStepConfig, workspace_dir: Path
    ) -> LibraryConfig:
        """Compile TrainingStepConfig to NeMo RL YAML format."""
        if config.training.type == "dpo":
            cfg = self._compile_dpo_config(config, workspace_dir)
        elif config.training.type == "grpo":
            cfg = self._compile_grpo_config(config, workspace_dir)
        else:
            raise ValueError(f"Unsupported RL training type: {config.training.type}")
        
        config_path = workspace_dir / "nemo_rl_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(cfg, f)
        
        return LibraryConfig(config=cfg, config_path=config_path)
    
    def execute_training(
        self,
        customizer_config: TrainingStepConfig,
        library_config: LibraryConfig,
        progress: ProgressReporter,
    ) -> TrainingMetrics:
        """Execute NeMo RL training via Ray bootstrap."""
        # 1. Start Ray cluster
        bootstrap = RayClusterBootstrap(
            rank=int(os.getenv("RANK", 0)),
            world_size=int(os.getenv("WORLD_SIZE", 1)),
            master_addr=os.getenv("MASTER_ADDR"),
        )
        
        # 2. On rank 0: start head, wait for workers, run driver
        if bootstrap.rank == 0:
            bootstrap.start_head()
            bootstrap.wait_for_workers()
            
            # Run DPO or GRPO driver
            driver = self._get_driver_path(customizer_config)
            result = subprocess.run([
                "python", driver,
                "--config", str(library_config.config_path),
            ])
            
            bootstrap.cleanup()
            return self._parse_metrics(result)
        else:
            # Workers just run Ray and block
            bootstrap.start_worker()
            return TrainingMetrics()
```

#### 3. Config Compilation

Port the config generation from `TrainingDPOConfig` and `TrainingGRPOConfig`:

```python
def _compile_dpo_config(
    self, config: TrainingStepConfig, workspace_dir: Path
) -> dict:
    """Generate NeMo RL DPO configuration."""
    hp = config.training.dpo
    p = config.parallelism
    
    return {
        "dpo": {
            "max_num_epochs": config.schedule.epochs,
            "max_num_steps": config.schedule.max_steps,
            "val_period": config.schedule.val_check_interval,
            "reference_policy_kl_penalty": hp.ref_policy_kl_penalty,
            "preference_loss_weight": hp.preference_loss_weight,
            "sft_loss_weight": hp.sft_loss_weight,
        },
        "policy": {
            "model_name": str(config.model.path),
            "train_global_batch_size": config.batch.global_batch_size,
            "train_micro_batch_size": config.batch.micro_batch_size,
            "max_total_sequence_length": config.model.max_seq_length,
            "precision": config.model.precision,
            "dtensor_cfg": {
                "enabled": True,
                "tensor_parallel_size": p.tensor_parallel_size,
                "context_parallel_size": p.context_parallel_size,
            },
        },
        "cluster": {
            "gpus_per_node": p.num_gpus_per_node,
            "num_nodes": p.num_nodes,
        },
        "checkpointing": {
            "enabled": True,
            "checkpoint_dir": str(workspace_dir / "checkpoints"),
        },
        "data": {
            "train_data_path": str(config.dataset.path),
            "val_data_path": str(config.dataset.val_path),
        },
    }
```

#### 4. Checkpoint Processing

NeMo RL uses DCP (Distributed Checkpoint Protocol), requiring conversion to HuggingFace:

```python
def process_checkpoint(
    self,
    checkpoint_path: Path,
    output_path: Path,
    config: TrainingStepConfig,
    library_config: LibraryConfig,
) -> CheckpointInfo:
    """Convert NeMo RL DCP checkpoint to HuggingFace format."""
    from nemo_rl.utils.native_checkpoint import convert_dcp_to_hf
    from transformers import AutoModelForCausalLM
    
    # Find best checkpoint
    best_ckpt = self.find_best_checkpoint(checkpoint_path.parent, config)
    
    # Convert DCP to HF
    hf_path = convert_dcp_to_hf(
        dcp_ckpt_path=best_ckpt / "policy" / "weights",
        hf_ckpt_path=output_path,
        model_name_or_path=library_config.config["policy"]["model_name"],
        tokenizer_name_or_path=best_ckpt / "policy" / "tokenizer",
    )
    
    # Re-save with safetensors
    model = AutoModelForCausalLM.from_pretrained(hf_path)
    model.save_pretrained(hf_path, safe_serialization=True)
    
    return CheckpointInfo(path=hf_path, format="hf")
```

### Missing Features - Implementation Plans

#### GRPO Plan

**Priority:** P1 (Core RL feature)

GRPO uses group-relative advantages for stable policy optimization.

**Implementation Steps:**

1. Extend `TrainingStepConfig` with GRPO configuration:

```python
class GRPOConfig(BaseModel):
    environment: str = "math"  # math, code, reward_model
    num_generations_per_prompt: int = 8
    num_prompts_per_step: int = 32
    ref_policy_kl_penalty: float = 0.01
    ratio_clip_min: float = 0.8
    ratio_clip_max: float = 1.2
    normalize_rewards: bool = True
    use_rloo: bool = True  # Leave-one-out baseline
    # Generation config
    generation_backend: str = "vllm"
    generation_temperature: float = 1.0
    generation_top_p: float = 1.0
    max_new_tokens: int = 512
```

2. Port `TrainingGRPOConfig` from legacy:
   - Environment configuration (math, code, instruction_following, etc.)
   - vLLM generation settings
   - Penguin environment integration
   - Tool call parser configuration (per model family)

3. Port GRPO driver from `run_grpo_penguin.py`:
   - Dataset preparation with `prepare_datasets_add_agent_ref()`
   - Environment setup (`Penguin` actor)
   - `grpo_train()` execution
   - DCP → HF checkpoint conversion

#### DPO Plan

**Priority:** P1 (Core alignment feature)

DPO optimizes preferences without explicit reward modeling.

**Implementation Steps:**

1. Extend `TrainingStepConfig` with DPO configuration:

```python
class DPOConfig(BaseModel):
    ref_policy_kl_penalty: float = 0.05
    preference_average_log_probs: bool = False
    sft_average_log_probs: bool = False
    preference_loss_weight: float = 1.0
    sft_loss_weight: float = 0.0  # Optional regularization
    max_grad_norm: float = 1.0
```

2. Port `TrainingDPOConfig` from legacy:
   - Preference dataset validation
   - Policy configuration (DTensor backend)
   - Checkpointing settings
   - WandB/MLflow integration

3. Port DPO driver from `run_dpo.py`:
   - Dataset loading with `DPODataset`
   - Preprocessing with `dpo_preprocessor()`
   - `dpo_train()` execution
   - DCP → HF checkpoint conversion

#### Reward Model Plan

**Priority:** P2 (RL infrastructure)

Train reward models for GRPO with reward model environment.

**Implementation Steps:**

1. Add `training_type = REWARD_MODEL` to enum

2. Create RM configuration:

```python
class RewardModelConfig(BaseModel):
    val_global_batch_size: int = 64
    preference_margin: float = 0.0
```

3. Port from NeMo RL's `rm_train()` algorithm

4. Support RM deployment for GRPO environment

### Migration Phases

#### Phase 2a: Infrastructure (P1)

- [ ] Add Ray to `nmp-gpu-tasks` container
- [ ] Create `ray_bootstrap.py` (port from `run-ray.sh`)
- [ ] Verify Ray cluster works on Volcano pods
- [ ] Test multi-node Ray cluster formation

#### Phase 2b: DPO Implementation (P1)

- [ ] Create `backends/nemo_rl/backend.py` skeleton
- [ ] Port `TrainingDPOConfig` to `config.py`
- [ ] Port `run_dpo.py` to `dpo_driver.py`
- [ ] Implement DCP → HF checkpoint conversion
- [ ] Add preference dataset validation
- [ ] E2E test with DPO training

#### Phase 2c: GRPO Implementation (P1)

- [ ] Port `TrainingGRPOConfig` to `config.py`
- [ ] Port `run_grpo_penguin.py` to `grpo_driver.py`
- [ ] Port environment configs (math, code, etc.)
- [ ] Configure vLLM generation backend
- [ ] E2E test with GRPO training

#### Phase 2d: Integration (P1)

- [ ] Port `NemoRLLogger` for progress reporting
- [ ] WandB/MLflow integration
- [ ] Update `TrainingStepCompiler` for RL selection
- [ ] Documentation

## Why Multiple Backends?

### The 80/20 Rule: Simplicity vs Scale

While Megatron-Bridge offers advanced features like Virtual Pipeline Parallelism (VPP) and production-grade optimizations, **most users don't need this complexity**. Customizer uses a layered approach where each backend serves distinct use cases:

| Use Case | % of Users | Backend | Rationale |
|----------|------------|---------|-----------|
| **Standard fine-tuning** (7B-70B, 1-8 GPUs) | ~80% | Automodel | Zero conversion, instant HF support |
| **Large-scale training** (VPP, 8+ PP stages) | ~15% | Megatron-Bridge | Production-grade, advanced optimizations |
| **Alignment training** (DPO, GRPO) | ~5% | NeMo RL | Specialized RL algorithms |

### Day-0 HuggingFace Support

**Automodel:**
```python
# Instant - works with ANY HF model
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-1B")
# Ready to train immediately - no conversion needed
```

**Megatron-Bridge:**
```python
# Requires architecture-specific bridge implementation
bridge = AutoBridge.from_hf_pretrained("meta-llama/Llama-3.2-1B")
# Must define per-parameter mappings (QKV fusion, TP/PP distribution)
provider = bridge.to_megatron_provider()
model = provider.provide_distributed_model()
```

**Impact for new HF models** (e.g., Qwen3-next, GLM-4.6):
- **Automodel**: Works immediately (just upgrade `transformers`)
- **Megatron-Bridge**: Requires weeks to implement bridge + mappings + testing

### Complexity Comparison

| Aspect | Automodel | Megatron-Bridge |
|--------|-----------|-----------------|
| **Setup Time** | Seconds | Minutes-Hours (conversion) |
| **New Model Support** | Automatic | Manual bridge implementation |
| **Config Complexity** | Simple YAML | TP/PP topology + Megatron internals |
| **Debugging** | Standard PyTorch | Megatron Core expertise required |
| **Checkpoint Format** | HF-native (DCP) | Megatron (requires export) |
| **Operational Overhead** | Minimal | Conversion at start + end of training |

### When You Need Megatron-Bridge

Use Megatron-Bridge **only** when you need:

1. **Virtual Pipeline Parallelism (VPP)** - For PP > 4 stages to minimize pipeline bubbles
2. **Production-Scale Training** - 1000+ nodes with communication overlap optimizations
3. **Megatron-Native Models** - GPT-OSS or custom Megatron architectures
4. **DoRA PEFT** - Weight-decomposed LoRA (not available in Automodel)
5. **FP8 with Transformer Engine** - Hardware-accelerated FP8 (better than TorchAO)

### Example: Fine-tune Llama-3.2-3B with LoRA (4 GPUs)

**Automodel Path (Recommended):**
```bash
# Total time: ~30 seconds to start training
uv run torchrun --nproc_per_node=4 finetune.py --config llama_3_2_3b_sft.yaml
# Uses FSDP2 automatically, starts training immediately
```

**Megatron-Bridge Path (Unnecessary Complexity):**
```bash
# 1. Convert HF → Megatron (5-10 minutes)
python convert_hf_to_megatron.py --hf-path meta-llama/Llama-3.2-3B

# 2. Configure Megatron parallelism (complex ConfigContainer)
# 3. Train with Megatron Core
python train_megatron.py --megatron-config ...

# 4. Convert back Megatron → HF (5-10 minutes)
python convert_megatron_to_hf.py
```

**Result:** Megatron-Bridge adds 10-20 minutes overhead with **zero performance benefit** for this use case.

### Strategic Decision

Customizer's multi-backend architecture provides:
- ✅ **Simplicity by default** (Automodel) - Fast iteration, instant HF support
- ✅ **Power when needed** (Megatron-Bridge) - VPP, scale, production features
- ✅ **Specialized algorithms** (NeMo RL) - DPO, GRPO, reward modeling

This gives users the **best of both worlds** without forcing unnecessary complexity.

## Feature Comparison Matrix

### Training Types

| Feature | Automodel | Megatron-Bridge | NeMo RL | Customizer |
|---------|-----------|-----------------|---------|------------|
| SFT (Full Weights) | ✅ | ✅ | ✅ (warmup) | ✅ (automodel) |
| LoRA | ✅ | ✅ | ✅ | ✅ (automodel) |
| DoRA | ❌ | ✅ | ❌ | ❌ |
| KD (Same Tokenizer) | ✅ | ⚠️ experimental | ❌ | ✅ (automodel) |
| On-Policy Distillation | ❌ | ❌ | ✅ | ❌ |
| DPO | ❌ | ❌ | ✅ | ❌ |
| GRPO | ❌ | ❌ | ✅ | ❌ |
| Reward Modeling | ❌ | ❌ | ✅ | ❌ |

### Parallelism

| Feature | Automodel | Megatron-Bridge | NeMo RL | Customizer |
|---------|-----------|-----------------|---------|------------|
| FSDP2 | ✅ | ❌ | ✅ (DTensor) | ✅ |
| Tensor Parallel | ✅ | ✅ | ✅ | ✅ |
| Pipeline Parallel | ⚠️ basic | ✅ VPP+advanced | ✅ (Megatron) | ⚠️ Basic via Automodel; MB for VPP |
| Context Parallel | ✅ | ✅ | ✅ | ✅ |
| Expert Parallel | ✅ | ✅ | ✅ | ⚠️ EP>1 → MB |
| Sequence Parallel | ✅ | ✅ | ✅ | ✅ |

### Precision

| Feature | Automodel | Megatron-Bridge | NeMo RL | Customizer |
|---------|-----------|-----------------|---------|------------|
| BF16 | ✅ | ✅ | ✅ | ✅ |
| FP16 | ✅ | ✅ | ✅ | ✅ |
| FP8 (TorchAO) | ✅ | ❌ | ⚠️ | ❌ |
| FP8 (Transformer Engine) | ❌ | ✅ | ✅ (Megatron) | ❌ |
| FP4 | ❌ | ✅ | ❌ | ❌ |

### Model Types

| Feature | Automodel | Megatron-Bridge | NeMo RL | Customizer |
|---------|-----------|-----------------|---------|------------|
| HuggingFace LLMs | ✅ Day-0 | ✅ via bridge | ✅ | ✅ |
| Megatron-Native | ⚠️ custom impl | ✅ | ✅ (Megatron) | ❌ |
| VLMs | ✅ | ✅ | ✅ | ❌ |
| MoE | ✅ | ✅ | ✅ | ⚠️ via automodel |
| Embedding Models | ✅ | ❌ | ❌ | ❌ |

## Implementation Priorities

### Phase 1: Automodel Enhancements ✅ COMPLETED

- [x] SFT full weights
- [x] LoRA PEFT
- [x] LoRA merged
- [x] Knowledge Distillation
- [x] Sequence Packing
- [x] WandB/MLflow integration

### Phase 2: RL Backend (P1)

- [ ] NeMo RL backend skeleton
- [ ] DPO implementation
- [ ] GRPO implementation
- [ ] Preference dataset validation

### Phase 3: Megatron-Bridge Backend (P2)

- [ ] Backend skeleton with AutoBridge
- [ ] SFT/LoRA support
- [ ] DoRA PEFT method
- [ ] Pipeline parallelism > 1

### Phase 4: VLM Support (P2)

- [ ] VLM model detection
- [ ] Automodel VLM recipe integration
- [ ] Multi-modal dataset handling
- [ ] VLM checkpointing

### Phase 5: Performance Optimizations (P3)

- [ ] FP8 training (Automodel + TorchAO)
- [ ] torch.compile integration
- [ ] Gradient checkpointing exposure
- [ ] Megatron FP8 via Transformer Engine

### Phase 6: Advanced Features (P3)

- [ ] Multi-turn RL environments
- [ ] Async GRPO
- [ ] Reward model training
- [ ] Multi-step pipelines (SFT → RL)


## GPU RAM Utilization Experiments
### Table 40GBS GPUs
Dataset: email-composition

| name                                    | finetuning_type | max GPU RAM | seq len | max GPU RAM   | seq len | max GPU RAM | seq len |
|-----------------------------------------|-----------------|-------------|---------|---------------|---------|-------------|---------|
| llama-3.2-1b@v1.0.0+40GB                 | lora            | 20%         | 432     |               |         |             |         |
| llama-3.2-1b@v1.0.0+40GB                 | all_weights     | 66%         | 1728    |               |         |             |         |
| llama-3.2-1b-instruct@v1.0.0+40GB        | lora            | 20%         | 1728    | 31%           | 4096    | 47%         | 8192    |
| llama-3.2-1b-instruct@v1.0.0+40GB        | all_weights     | 66%         | 1728    | 74%           | 4096    | 71%, 4x GPU | 8192    |
| llama-3.2-nv-embedqa-1b@v2+40GB          | all_weights     | 60%         | N/A     |               |         |             |         |
| llama-3.2-3b-instruct@v1.0.0+40GB        | lora            | 47%         | 3456    |               |         |             |         |
| llama-3.1-8b-instruct@v1.0.0+40GB        | lora            | 53%         | 3456    | 55%           | 4096    | 97%         | 8192    |
| llama-3.1-8b-instruct@v1.0.0+40GB        | all_weights     | 50%         | 1296    | 80%           | 4096    | 85%, TP=8   | 8192    |
| llama3-70b-instruct@v1.0.0+40GB          | lora            | 76%         | 1296    |               |         |             |         |
| llama-3.1-70b-instruct@v1.0.0+40GB       | lora            | 76%         | 1296    | N/A           | 4096    | N/A         | 8192    |
| llama-3.3-70b-instruct@v1.0.0+40GB       | lora            | 73%         | 1296    |               |         |             |         |
| nemotron-nano-llama-3.1-8b@v1.0.0+40GB   | lora            | 36%         | 1728    |               |         |             |         |
| nemotron-nano-llama-3.1-8b@v1.0.0+40GB   | all_weights     | 50%         | 1296    |               |         |             |         |
| nemotron-super-llama-3.3-49b@v1.0.0+40GB | lora            | 65%         | 1296    | 88%, 4x4 TP=8 | 4096    | N/A         |         |
| phi-4@v1.0.0+40GB                        | lora            | 51%         | 342     |               |         |             |         |