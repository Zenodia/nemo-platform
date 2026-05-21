# NeMo Framework Error Table for Customizer Implementation

This table maps NeMo Framework errors to Custom Exception Classes for implementation.

## Validation Status Legend

These markers indicate whether an error needs a rule in `error_rules.yaml`. Reviewed the code and categorized each potential error:

> **`[VALIDATED]`** = Pre-validated in Customizer before NeMo execution (e.g., by `prepare_dataset()`, `validate_datasets()`, or API validation). These errors cannot reach the training backend.
>
> **`[ADD]`** = May occur at runtime and needs an error handling rule in `error_rules.yaml`. These are the errors we care about.
>
> **`[NEVER OCCUR]`** = Will never occur with current Customizer configuration (e.g., T5 models not supported, or features we don't expose).

---

## Custom Exception Classes

### Classes That NEED Implementation (have [ADD] errors)

| Exception Class | HTTP Status | Description | [ADD] Count |
|----------------|-------------|-------------|-------------|
| `DatasetFormatError` | 400 | Dataset has invalid format/schema | 4 |
| `ModelNotFoundError` | 404 | Model/checkpoint path doesn't exist | 3 |
| `ModelLoadError` | 500 | Failed to load/initialize model | 2 |
| `TrainingConfigError` | 400 | Invalid training config (parallelism, batch, PEFT) | 7 |
| `CheckpointError` | 500 | Checkpoint save/load failure | 10 |
| `CudaError` | 500 | GPU/CUDA runtime error | 1 |
| `DistributedError` | 500 | Distributed training failure | 3 |
| `TrainingTimeoutError` | 500 | Training exceeded time limit | 1 |
| `InternalError` | 500 | Unexpected internal error | 3 |

---

### Classes That DON'T Need Implementation (all [VALIDATED] or [NEVER OCCUR])

| Exception Class | HTTP Status | Reason Not Needed |
|----------------|-------------|-------------------|
| `DatasetNotFoundError` | 404 | T5 not supported; files created by `prepare_dataset()` and validated in `validate_datasets()` before training |
| `DatasetPermissionError` | 403 | Never occurs - Customizer creates files with correct permissions |

---

## Error Mapping Table

### 1. DatasetNotFoundError (404)

| NeMo Error Raised | Validation Status | What It Means | Code Pointer |
|-------------------|-------------------|---------------|--------------|
| `FileNotFoundError(f"Data file {self.file_path} not found")` | `[NEVER OCCUR]` T5 not supported; files validated by `prepare_dataset()` + `validate_datasets()` | Dataset file doesn't exist at specified path | `/opt/NeMo/nemo/collections/llm/t5/data/core.py:108` |

**User Message**: `Dataset not found: {details}. Please verify the dataset path exists and is accessible.`

---

### 2. DatasetFormatError (400)

| NeMo Error Raised | Validation Status | What It Means | Code Pointer |
|-------------------|-------------------|---------------|--------------|
| `RuntimeError(f"no sample to consume: {total_samples}")` | `[ADD]` May occur at runtime | Dataset is empty or has zero valid samples | `/opt/NeMo/nemo/lightning/data.py:260` |
| `RuntimeError(f"no samples left to consume: {consumed_samples}, {total_samples}")` | `[ADD]` May occur at runtime | All samples have been consumed during training | `/opt/NeMo/nemo/lightning/data.py:341` |
| `logger.error(f"Error while loading example {idx} from dataset {self.file_path}")` | `[ADD]` May occur at runtime | Failed to parse/load a specific sample | `/opt/NeMo/nemo/collections/llm/gpt/data/core.py:357` |
| `KeyError: {field}` | `[ADD]` May occur at runtime | Required field missing from dataset sample | `/opt/NeMo/nemo/collections/llm/gpt/data/core.py:518-524` |
| `ValueError("Dataset does not have a tokenizer and cannot be used as a chat dataset")` | `[VALIDATED]` in `CustomizerTrainingConfig.set_chat_template()` | Chat dataset requires tokenizer with chat template | `/opt/NeMo/nemo/collections/llm/gpt/data/core.py:1009` |
| `DatasetFormatError` with context: "error validating dataset" | `[VALIDATED]` in `datasets.validate_datasets()` | Dataset doesn't match expected format/schema | `/app/services/customizer/src/customizer_training/train.py:460-462` |
| `ValueError(f"{self.truncation_method} is not supported")` | `[NEVER OCCUR]` Customizer uses valid truncation methods | Invalid truncation method (not 'left' or 'right') | `/opt/NeMo/nemo/collections/llm/gpt/data/core.py:481,506` |

**User Message**: `Dataset format error: {details}. Please check your dataset matches the expected schema.`

---

### 3. ModelNotFoundError (404)

| NeMo Error Raised | Validation Status | What It Means | Code Pointer |
|-------------------|-------------------|---------------|--------------|
| `FileNotFoundError(f"Checkpoint file not found: {path}")` | `[ADD]` May occur at runtime | The specified checkpoint path does not exist | `/opt/NeMo/nemo/lightning/io/pl.py:390` |
| `NotFoundError(f"There were no checkpoints found in checkpoint_dir...:{checkpoint_dir}. Cannot resume.")` | `[ADD]` May occur at runtime | The checkpoint directory is empty when resuming | `/opt/NeMo/nemo/lightning/resume.py:248-250` |
| `ValueError("Nemotron Super models expect HF source code to exist at $ckpt/nemotron_src")` | `[ADD]` May occur at runtime | Nemotron model missing required HF source code | `/app/services/customizer/src/customizer_training/train.py:425-427` |
| `ValueError("model_path is a required variable for finetuning")` | `[VALIDATED]` in `CustomizerTrainingConfig.base_required_keys` | model_path not provided in configuration | `/app/services/customizer/src/customizer_training/train.py:403-405` |
| `ValueError("teacher is required for Knowledge Distillation")` | `[VALIDATED]` in `validation.validate_hyperparams()` | KD enabled but no teacher model specified | `/app/services/customizer/src/customizer_training/train.py:493-494` |

**User Message**: `Model not found: {path}. Please verify the model path is correct.`

---

### 4. ModelLoadError (500)

| NeMo Error Raised | Validation Status | What It Means | Code Pointer |
|-------------------|-------------------|---------------|--------------|
| `ValueError(f"Shape mismatch for parameter {name}: target shape {param.shape} vs source shape {source_state[name].shape}")` | `[ADD]` May occur at runtime (model corruption) | Model parameter shape doesn't match checkpoint | `/opt/NeMo/nemo/lightning/io/state.py:167-168` |
| `ValueError(f"Shape mismatch for buffer {name}: {buffer.shape} vs {target_state[name].shape}")` | `[ADD]` May occur at runtime (model corruption) | Model buffer shape doesn't match checkpoint | `/opt/NeMo/nemo/lightning/io/state.py:190` |
| `ValueError(f"Artifact '{artifact.attr}' is required but not provided")` | `[VALIDATED]` `is_nemo_model_directory()` checks required structure | Required model artifact missing from checkpoint | `/opt/NeMo/nemo/lightning/io/mixin.py:663,668` |
| `ValueError(f"checkpoint type must be HF or NeMo 2 only - found {orig_model_type}")` | `[VALIDATED]` in `determine_llm_model_type()` + train.py:420-423 | Model checkpoint is not HF or NeMo 2.0 format | `/app/services/customizer/src/customizer_training/train.py:420-423` |
| `ValueError(f"No connector found for extension '{ext}' for {cls}")` | `[NEVER OCCUR]` `determine_llm_model_type()` validates HF/NeMo format; export uses known formats | No import/export connector for file extension | `/opt/NeMo/nemo/lightning/io/mixin.py:468` |
| `ValueError("Model must be an instance of ConnectorMixin")` | `[NEVER OCCUR]` Customizer uses compatible models | Model doesn't implement required NeMo interface | `/opt/NeMo/nemo/lightning/io/api.py:164,198` |

**User Message**: `Model loading failed: {details}. The model may be corrupted or incompatible.`

---

### 5. TrainingConfigError (400)

#### 5a. Parallelism Config Errors

| NeMo Error Raised | Validation Status | What It Means | Code Pointer |
|-------------------|-------------------|---------------|--------------|
| `RuntimeError("data_parallel_rank should be smaller than data size, but {data_parallel_rank} >= {data_parallel_size}")` | `[ADD]` May occur at runtime | Process rank exceeds the number of data parallel processes | `/opt/NeMo/nemo/lightning/data.py:266-268` |
| `RuntimeError(f"decoder world_size ({decoder_world_size}) is not divisible by pipeline_model_parallel_size ({pipeline_model_parallel_size})")` | `[ADD]` May occur at runtime | Decoder world size not divisible by PP size | `/opt/NeMo/nemo/lightning/megatron_init.py:386-387` |
| `RuntimeError(f"data parallel size must be greater than 0, but {data_parallel_size}")` | `[VALIDATED]` in `TrainingSFTConfig` lines 146-147 | data_parallel_size computed to zero or negative | `/opt/NeMo/nemo/lightning/data.py:264` |
| `ValueError(f"Expected world_size ({world_size}) to be greater than/equal to pipeline size ({pp})")` | `[VALIDATED]` in `TrainingSFTConfig` lines 149-154 | Not enough GPUs for the pipeline parallel config | `/opt/NeMo/nemo/lightning/_strategy_lib.py:79` |
| `ValueError(f"Invalid DDP type: {ddp}")` | `[NEVER OCCUR]` Customizer uses valid DDP types | Invalid DDP type (not 'megatron' or 'pytorch') | `/opt/NeMo/nemo/lightning/pytorch/strategies/megatron_strategy.py:395,440` |
| `ValueError("Please set ddp to megatron to use FSDP.")` | `[NEVER OCCUR]` Customizer configures FSDP correctly | FSDP enabled but DDP type not set to 'megatron' | `/opt/NeMo/nemo/lightning/pytorch/strategies/megatron_strategy.py:391,436` |
| `ValueError("Default data step is being used in a context parallel environment...")` | `[NEVER OCCUR]` Customizer doesn't use context parallelism | Context parallelism requires custom data step | `/opt/NeMo/nemo/lightning/megatron_parallel.py:131-132` |

#### 5b. Batch Config Errors

| NeMo Error Raised | Validation Status | What It Means | Code Pointer |
|-------------------|-------------------|---------------|--------------|
| `RuntimeError(f"global_batch_size ({global_batch_size}) is not divisible by micro_batch_size ({micro_batch_size}) x data_parallel_size ({data_parallel_size})")` | `[ADD]` May occur at runtime | global_batch_size not evenly divisible | `/opt/NeMo/nemo/lightning/data.py:272-275` |
| `RuntimeError("MegatronPretrainingRandomSampler does not support drop_last=False when micro_batch_size * data_parallel_size > 1...")` | `[ADD]` May occur at runtime | Cannot use drop_last=False with multiple GPUs | `/opt/NeMo/nemo/lightning/data.py:403-407` |
| `ValueError("num_microbatches is not set")` | `[ADD]` May occur at runtime | num_microbatches not configured for PP training | `/opt/NeMo/nemo/lightning/megatron_parallel.py:1272` |
| `ValueError(f"Sequence length {L} is not divisible by num_chunks {num_chunks}")` | `[ADD]` May occur at runtime (Hyena models only) | Sequence length doesn't divide evenly | `/opt/NeMo/nemo/collections/llm/gpt/model/megatron/hyena/hyena_utils.py:192,1452` |
| `ValueError(f"Found {end_checkpoints[0]} indicating that the last training run has already completed.")` | `[ADD]` May occur at runtime | End checkpoint exists, training finished | `/opt/NeMo/nemo/lightning/resume.py:254-256` |
| `ValueError(f"Multiple checkpoints {end_checkpoints} that matches *end.ckpt.")` | `[ADD]` May occur at runtime | Multiple end checkpoints in directory | `/opt/NeMo/nemo/lightning/resume.py:262` |
| `ValueError("seq_length is not set")` | `[VALIDATED]` in `TrainingSFTConfig.required_keys` (model.max_seq_length) | seq_length not configured in model/data config | `/opt/NeMo/nemo/lightning/megatron_parallel.py:1275` |
| `RuntimeError(f"micro_batch_size size must be greater than 0, but {micro_batch_size}")` | `[NEVER OCCUR]` Customizer sets valid micro_batch_size | micro_batch_size was set to zero or negative | `/opt/NeMo/nemo/lightning/data.py:262` |
| `RuntimeError("pad_samples_to_global_batch_size can be True only when global_batch_size is set to an integer value")` | `[NEVER OCCUR]` Customizer always sets global_batch_size | Sample padding enabled without global_batch_size | `/opt/NeMo/nemo/lightning/data.py:278-280` |
| `Exception(f'{dataloader_type} dataloader type is not supported.')` | `[NEVER OCCUR]` Customizer uses valid dataloader types | Invalid dataloader_type value provided | `/opt/NeMo/nemo/lightning/data.py:219` |
| `ValueError("micro_batch_size is not set")` | `[NEVER OCCUR]` Customizer always sets micro_batch_size | micro_batch_size not configured | `/opt/NeMo/nemo/lightning/megatron_parallel.py:1278` |
| `ValueError('Seed ({}) should be a positive integer.'.format(seed_))` | `[NEVER OCCUR]` Customizer uses valid seed | Random seed is zero, negative, or not integer | `/opt/NeMo/nemo/lightning/megatron_init.py:241` |

#### 5c. PEFT Config Errors (ALL NEVER OCCUR)

| NeMo Error Raised | Validation Status | What It Means | Code Pointer |
|-------------------|-------------------|---------------|--------------|
| `ValueError(f"Your checkpoint contains PEFT weights, but your specified export target 'hf' should be changed to 'hf-peft'...")` | `[NEVER OCCUR]` Customizer handles PEFT export correctly | Trying to export PEFT checkpoint as standard HF | `/opt/NeMo/nemo/lightning/io/api.py:205-206` |

**User Message**: `Training configuration error: {details}. Please check your parallelism or batch settings.`

---

### 6. CheckpointError (500)

| NeMo Error Raised | Validation Status | What It Means | Code Pointer |
|-------------------|-------------------|---------------|--------------|
| `ValueError(f"Distributed checkpoints should be a directory. Found: {path}.")` | `[ADD]` May occur at runtime | File provided instead of directory for distributed ckpt | `/opt/NeMo/nemo/lightning/io/pl.py:392` |
| `ValueError("End checkpoint is unfinished and cannot be used to resume the training...")` | `[ADD]` May occur at runtime | Training interrupted during checkpoint save | `/opt/NeMo/nemo/lightning/resume.py:215-218` |
| `ValueError("Last checkpoint is unfinished and cannot be used to resume the training...")` | `[ADD]` May occur at runtime | Most recent checkpoint save was interrupted | `/opt/NeMo/nemo/lightning/resume.py:225-229` |
| `RuntimeError(f"{e}\n{RESHARDING_LOAD_ERROR}")` | `[ADD]` May occur at runtime | Parallelism settings don't match checkpoint | `/opt/NeMo/nemo/lightning/pytorch/strategies/megatron_strategy.py:1198-1206` |
| `RuntimeError(f"Additional keys: {keys} in checkpoint but not in model.")` | `[ADD]` May occur at runtime | Checkpoint contains keys not in model | `/opt/NeMo/nemo/lightning/io/state.py:207` |
| `ValueError(f"No matches found for source key: {source_key}")` | `[ADD]` May occur at runtime | Cannot map checkpoint key to model key | `/opt/NeMo/nemo/lightning/io/state.py:321` |
| `RuntimeError("The source state dict is empty, possibly because it was saved with a different configuration or format.")` | `[ADD]` May occur at runtime | Checkpoint state dict empty or corrupted | `/opt/NeMo/nemo/lightning/_strategy_lib.py:404-405` |
| Exception with context: "Failed to find checkpoint after training" | `[ADD]` May occur at runtime | Training completed but checkpoint files not saved | `/app/services/customizer/src/customizer_training/train.py:554-557` |
| Exception with context: "Error exporting model" | `[ADD]` May occur at runtime | Model export to target format failed | `/app/services/customizer/src/customizer_training/train.py:608-610` |
| Exception with context: "Error uploading model" | `[ADD]` May occur at runtime | Model upload to storage failed | `/app/services/customizer/src/customizer_training/train.py:617-620` |

**User Message**: `Checkpoint error: {details}. The checkpoint may be corrupted or incompatible.`

---

### 7. CudaError (500)

| NeMo Error Raised | Validation Status | What It Means | Code Pointer |
|-------------------|-------------------|---------------|--------------|
| `torch.cuda.OutOfMemoryError` or "CUDA out of memory" in message | `[ADD]` May occur at runtime | GPU memory exceeded during training | Runtime |

**User Message**: `GPU error: {details}. Try reducing batch_size or max_seq_length.`

---

### 8. DistributedError (500)

| NeMo Error Raised | Validation Status | What It Means | Code Pointer |
|-------------------|-------------------|---------------|--------------|
| `RuntimeError("torch.distributed is not available. Cannot initialize distributed process group")` | `[ADD]` Environment-dependent | PyTorch distributed not installed | `/opt/NeMo/nemo/lightning/pytorch/strategies/megatron_strategy.py:634` |
| Various NCCL communication errors | `[ADD]` May occur at runtime | Distributed training communication failure | Runtime |
| `TimeoutError` in distributed context | `[ADD]` May occur at runtime | GPUs/nodes became unresponsive | Runtime |

**User Message**: `Distributed training error: {details}.`

---

### 9. TrainingTimeoutError (500)

| NeMo Error Raised | Validation Status | What It Means | Code Pointer |
|-------------------|-------------------|---------------|--------------|
| `subprocess.TimeoutExpired` | `[ADD]` May occur at runtime | Training process exceeded time limit | `/app/services/customizer/src/customizer_training/train.py:530-532` |

**User Message**: `Training exceeded time limit. Consider reducing training steps or increasing timeout.`

---

### 10. InternalError (500)

| NeMo Error Raised | Validation Status | What It Means | Code Pointer |
|-------------------|-------------------|---------------|--------------|
| `LoggerMisconfigurationError("The pytorch lightning trainer...contained a logger...")` | `[ADD]` May occur at runtime | Trainer has logger conflict | `/opt/NeMo/nemo/utils/exp_manager.py:862-869` |
| Exception with context: "error preparing training configuration" | `[ADD]` May occur at runtime | Failed to build training config | `/app/services/customizer/src/customizer_training/train.py:463-465` |
| `Exception(f"Training subprocess returned with error code: {returncode}")` | `[ADD]` May occur at runtime | Training process exited with non-zero code | `/app/services/customizer/src/customizer_training/train.py:526-529` |
| `Exception("Microbatch calculator already initialized.")` | `[NEVER OCCUR]` Customizer doesn't reinitialize | Microbatch calculator set up twice | `/opt/NeMo/nemo/lightning/data.py:115,134` |
| `ValueError("Hydra changed the working directory. This interferes with ExpManger's functionality...")` | `[NEVER OCCUR]` Customizer doesn't use Hydra | Hydra changed working directory | `/opt/NeMo/nemo/utils/exp_manager.py:855-858` |
| `ValueError(f"Resuming requires the log_dir {log_dir} to be passed to exp_manager")` | `[NEVER OCCUR]` Customizer sets log_dir | log_dir not specified for resume | `/opt/NeMo/nemo/utils/exp_manager.py:920` |

**User Message**: `An internal error occurred: {details}.`
