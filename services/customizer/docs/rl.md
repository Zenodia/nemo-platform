# NeMo-RL Error Table for Customizer Implementation

This table maps NeMo-RL v0.4.0 errors to Custom Exception Classes for implementation.

## Validation Status Legend

These markers indicate whether an error needs a rule in `error_rules.yaml`. Reviewed the code and categorized each potential error:

> **`[VALIDATED]`** = Pre-validated in Customizer before NeMo-RL execution (e.g., by `prepare_dataset()`, `validate_datasets()`, or API validation). These errors cannot reach the training backend.
>
> **`[ADD]`** = May occur at runtime and needs an error handling rule in `error_rules.yaml`. These are the errors we care about.
>
> **`[NEVER OCCUR]`** = Will never occur with current Customizer configuration (e.g., uses eval datasets we don't expose, or packing algorithms we don't use).

---

## Custom Exception Classes

### Classes That NEED Implementation (have [ADD] errors)

| Exception Class | HTTP Status | Description | [ADD] Count |
|----------------|-------------|-------------|-------------|
| `DatasetFormatError` | 400 | Dataset has invalid format/schema | 2 |
| `TrainingConfigError` | 400 | Invalid training config (parallelism, GRPO/DPO params, etc.) | 26 |
| `TrainingEnvironmentError` | 400 | Invalid environment configuration (GRPO) | 3 |
| `ModelLoadError` | 500 | Failed to load/initialize model | 4 |
| `CheckpointError` | 500 | Checkpoint save/load failure | 4 |
| `CudaError` | 500 | GPU/CUDA runtime error | 2 |
| `DistributedError` | 500 | Distributed training/Ray failure | 8 |
| `GenerationError` | 500 | vLLM generation/inference failure | 10 |
| `TrainingTimeoutError` | 500 | Training exceeded time limit | 1 |
| `InternalError` | 500 | Unexpected internal error | 5 |

---

### Classes That DON'T Need Implementation (all [VALIDATED] or [NEVER OCCUR])

| Exception Class | HTTP Status | Reason Not Needed |
|----------------|-------------|-------------------|
| `DatasetNotFoundError` | 404 | All errors pre-validated by `prepare_dataset()` in Customizer |
| `ModelNotFoundError` | 404 | All errors pre-validated by API before training starts |

---

## Error Mapping Table

### 1. DatasetFormatError (400)

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `ValueError(f"text must be a string or a list of strings, got {type(text)}")` | `[ADD]` May occur at runtime | Text input is not a string or list of strings | `/opt/nemo-rl/nemo_rl/data/datasets/processed_dataset.py:89` |
| `FileNotFoundError(f"Prompt file {prompt_file} not found")` | `[ADD]` May occur at runtime | A prompt file does not exist at the specified path | `/opt/nemo-rl/nemo_rl/data/interfaces.py:71` |
| `ValueError(f"Invalid variant for aime dataset: aime{variant}")` | `[NEVER OCCUR]` Custom datasets used | AIME dataset variant is invalid | `/opt/nemo-rl/nemo_rl/data/datasets/eval_datasets/aime.py:41` |
| `ValueError("No data processor for task {datum_dict['task_name']}")` | `[NEVER OCCUR]` Customizer uses registered task names | Task name not registered in the processor registry | `/opt/nemo-rl/examples/run_vlm_grpo.py:118` |
| `ValueError("Unsupported content type: {content['type']}")` | `[NEVER OCCUR]` Customizer uses valid content types | Invalid content type in multimodal messages | `/opt/nemo-rl/examples/run_vlm_grpo.py:138` |

**User Message**: `Dataset format error: {details}. Please check your dataset matches the expected schema.`

---

### 2. TrainingConfigError (400)

#### 2a. Parallelism Config Errors

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `ValueError("Configure either Megatron (policy.megatron_cfg.enabled=true) or DTensor (policy.dtensor_cfg.enabled=true), not both.")` | `[ADD]` May occur at runtime | Both Megatron and DTensor are enabled | `/opt/nemo-rl/nemo_rl/models/policy/lm_policy.py:88` |
| `ValueError("Please either set policy.megatron_cfg.enabled=true... or set policy.dtensor_cfg.enabled=true...")` | `[ADD]` May occur at runtime | Neither Megatron nor DTensor is enabled | `/opt/nemo-rl/nemo_rl/models/policy/lm_policy.py:102` |
| `ValueError(f"World size ({actual_world_size}) is insufficient for the parallelism configuration...")` | `[ADD]` May occur at runtime | Total GPUs are less than required for PP * CP * TP | `/opt/nemo-rl/nemo_rl/models/policy/lm_policy.py:126` |
| `ValueError(f"World size ({actual_world_size}) must be divisible by PP * CP * TP ({model_parallel_size})...")` | `[ADD]` May occur at runtime | World size not evenly divisible by parallelism dimensions | `/opt/nemo-rl/nemo_rl/models/policy/lm_policy.py:135` |
| `AssertionError(f"World size({world_size}) must equal to dp_size({dp_size}) * tp_size({tp_size}) * cp_size({cp_size}) to use DTensor")` | `[ADD]` May occur at runtime | DTensor world size must equal product of DP * TP * CP | `/opt/nemo-rl/nemo_rl/models/policy/dtensor_policy_worker.py:296` |
| `AssertionError("Dynamic batching is only supported for single pipeline parallel stage")` | `[ADD]` May occur at runtime | Dynamic batching enabled with PP > 1 | `/opt/nemo-rl/nemo_rl/models/policy/lm_policy.py:200` |
| `AssertionError("Dynamic Batching is exclusive of Sequence Packing...")` | `[ADD]` May occur at runtime | Dynamic batching and sequence packing both enabled | `/opt/nemo-rl/nemo_rl/models/policy/lm_policy.py:212` |
| `AssertionError("Sequence packing is not supported for VLM models...")` | `[ADD]` May occur at runtime | Sequence packing enabled for a Vision-Language Model | `/opt/nemo-rl/nemo_rl/models/policy/dtensor_policy_worker.py:205` |
| `ValueError("Context parallel is not supported for sequence packing...")` | `[ADD]` May occur at runtime | Context parallelism enabled with sequence packing in DTensor | `/opt/nemo-rl/nemo_rl/models/policy/dtensor_policy_worker.py:291` |
| `AssertionError("Context parallel is not supported for Gemma3ForCausalLM...")` | `[ADD]` May occur at runtime | Context parallelism enabled with Gemma3 model | `/opt/nemo-rl/nemo_rl/models/policy/dtensor_policy_worker.py:306` |
| `AssertionError("Context parallel is yet not supported for VLM models...")` | `[ADD]` May occur at runtime | Context parallelism enabled for Vision-Language Model | `/opt/nemo-rl/nemo_rl/models/policy/dtensor_policy_worker.py:317` |
| `RuntimeError("Context Parallelism (CP>1) requires sequence packing to be enabled.")` | `[ADD]` May occur at runtime | Megatron backend CP > 1 without sequence packing | `/opt/nemo-rl/nemo_rl/models/policy/megatron_policy_worker.py:1631` |
| `AssertionError("It's a known issue that context parallel can't be used together with sequence parallel in DTensor worker...")` | `[NEVER OCCUR]` Customizer doesn't combine CP+SP | Context parallel with sequence parallel in DTensor | `/opt/nemo-rl/nemo_rl/models/policy/dtensor_policy_worker.py:311` |
| `AssertionError("Sequence Packing must be enabled to use Context Parallelism with MCore")` | `[NEVER OCCUR]` Duplicate of megatron_policy_worker.py check | Megatron setup CP without packing | `/opt/nemo-rl/nemo_rl/models/policy/megatron_policy_worker.py:558` |

#### 2b. DPO/GRPO Algorithm Config Errors

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `AssertionError("Dynamic batching is currently not supported with DPO...")` | `[ADD]` May occur at runtime | Dynamic batching enabled with DPO | `/opt/nemo-rl/nemo_rl/algorithms/dpo.py:130` |
| `AssertionError("Sequence packing is currently not supported with DPO...")` | `[ADD]` May occur at runtime | Sequence packing enabled with DPO | `/opt/nemo-rl/nemo_rl/algorithms/dpo.py:134` |
| `AssertionError("A generation config in the PolicyConfig is required for GRPO")` | `[ADD]` May occur at runtime | GRPO requires generation config | `/opt/nemo-rl/nemo_rl/algorithms/grpo.py:216` |
| `AssertionError("Validation dataset is required if validation is enabled")` | `[ADD]` May occur at runtime | Validation enabled but no val dataset | `/opt/nemo-rl/nemo_rl/algorithms/grpo.py:273` |
| `AssertionError("Non-colocated inference is not supported for Megatron generation backends...")` | `[ADD]` May occur at runtime | Non-colocated inference with Megatron | `/opt/nemo-rl/nemo_rl/algorithms/grpo.py:348` |
| `AssertionError(f"Configuration error: (num_prompts_per_step * num_generations_per_prompt) = {expected_batch_size} must be divisible by data_parallel size {dp_size}.")` | `[ADD]` May occur at runtime | Batch size not divisible by DP size | `/opt/nemo-rl/nemo_rl/algorithms/grpo.py:1875` |
| `ValueError("Dynamic sampling has reached the maximum allowed number of batches ({dynamic_sampling_max_gen_batches})...")` | `[ADD]` May occur at runtime | Dynamic sampling exceeded max generation batches per step | `/opt/nemo-rl/nemo_rl/algorithms/grpo.py:680` |

#### 2c. Async GRPO Config Errors

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `AssertionError("Async GRPO requires vLLM backend with vllm_cfg.async_engine=True...")` | `[ADD]` May occur at runtime | Async GRPO without async vLLM engine | `/opt/nemo-rl/nemo_rl/algorithms/grpo.py:1564` |
| `AssertionError("Importance sampling correction must be enabled for async GRPO...")` | `[ADD]` May occur at runtime | Async GRPO without importance sampling | `/opt/nemo-rl/nemo_rl/algorithms/grpo.py:1568` |
| `AssertionError("Colocated inference is not supported for async GRPO...")` | `[ADD]` May occur at runtime | Async GRPO with colocated inference | `/opt/nemo-rl/nemo_rl/algorithms/grpo.py:1610` |

#### 2d. Sampling/Generation Config Errors

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `ValueError("top_k sampling with values < {TOP_K_THRESHOLD} is not supported...")` | `[ADD]` May occur at runtime | top_k too low for vLLM V1 logprob accuracy | `/opt/nemo-rl/nemo_rl/models/generation/vllm/vllm_generation.py:96` |
| `ValueError("top_p sampling with values < {TOP_P_THRESHOLD} is not supported...")` | `[ADD]` May occur at runtime | top_p too low for vLLM V1 logprob accuracy | `/opt/nemo-rl/nemo_rl/models/generation/vllm/vllm_generation.py:108` |

#### 2e. Megatron-Specific Config Errors

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `NotImplementedError("Reward models are not yet supported with the Megatron backend...")` | `[ADD]` May occur at runtime | Reward model training not supported with Megatron | `/opt/nemo-rl/nemo_rl/models/policy/megatron_policy_worker.py:478` |
| `AssertionError("MoE aux loss is currently not supported...")` | `[ADD]` May occur at runtime | MoE auxiliary loss enabled (known Megatron-LM bug) | `/opt/nemo-rl/nemo_rl/models/policy/megatron_policy_worker.py:684` |
| `AssertionError("Currently for optimizer offloading, only optimizer_offload_fraction=1.0 is supported")` | `[NEVER OCCUR]` Customizer uses default config | Partial optimizer offload not supported | `/opt/nemo-rl/nemo_rl/models/policy/megatron_policy_worker.py:637` |
| `AssertionError("defer_fp32_logits must be True if logprob_chunk_size is set")` | `[NEVER OCCUR]` Customizer uses default config | Megatron logprob chunking misconfigured | `/opt/nemo-rl/nemo_rl/models/policy/megatron_policy_worker.py:645` |
| `AssertionError("train_iters must be set in megatron_cfg...")` | `[NEVER OCCUR]` Customizer sets train_iters | Missing train_iters in Megatron config | `/opt/nemo-rl/nemo_rl/models/policy/megatron_policy_worker.py:668` |
| `AssertionError("activation_func must be set if not using gated_linear_unit...")` | `[NEVER OCCUR]` Customizer uses supported models | Missing activation function in model config conversion | `/opt/nemo-rl/nemo_rl/models/policy/megatron_policy_worker.py:607` |

#### 2f. Distillation Config Errors

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `AssertionError(f"Distillation does not support DTensor sequence parallel + sequence packing...")` | `[NEVER OCCUR]` Distillation not used | Distillation with sequence parallel + packing | `/opt/nemo-rl/nemo_rl/algorithms/distillation.py:211` |

**User Message**: `Training configuration error: {details}. Please check your parallelism, batch size, or algorithm settings.`

---

### 3. TrainingEnvironmentError (400)

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `ValueError(f"Unable to find compatible environment - {self.env_name}")` | `[ADD]` May occur at runtime | GRPO environment name is not recognized | Customizer `grpo_config.py` |
| `ValueError("hyperparameters.environment is required for GRPO, but it is not set")` | `[ADD]` May occur at runtime | GRPO environment not configured | Customizer `grpo_config.py` |
| `ValueError(f"No environment found for task type: {task_name}")` | `[ADD]` May occur at runtime | No environment registered for task | `/opt/nemo-rl/nemo_rl/experience/rollouts.py:255` |
| `ValueError("hyperparameters.environment.name is required for GRPO, but it is not set")` | `[VALIDATED]` in config validation | GRPO environment name missing | Customizer `grpo_config.py` |
| `ValueError(f"Invalid reward function: {reward_func_name}")` | `[NEVER OCCUR]` Customizer sets valid functions | VLM reward function is invalid | `/opt/nemo-rl/nemo_rl/environments/vlm_environment.py:80` |
| `ValueError("No reward functions provided")` | `[NEVER OCCUR]` Customizer provides functions | VLM environment has no reward functions | `/opt/nemo-rl/nemo_rl/environments/vlm_environment.py:89` |

**User Message**: `Environment configuration error: {details}. Please check your GRPO environment settings.`

---

### 4. ModelLoadError (500)

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `ImportError("vLLM is not installed...")` | `[ADD]` Environment-dependent | vLLM library not installed | `/opt/nemo-rl/nemo_rl/models/generation/vllm/vllm_worker.py:302` |
| `ValueError(f"Missing required keys for GenerationOutputSpec: {missing_keys}")` | `[ADD]` May occur at runtime | Generation output missing required fields | `/opt/nemo-rl/nemo_rl/models/policy/lm_policy.py:598` |
| `ValueError(f"Missing required keys for ScoreOutputSpec: {missing_keys}")` | `[ADD]` May occur at runtime | Score output missing required fields | `/opt/nemo-rl/nemo_rl/models/policy/lm_policy.py:643` |
| `FileNotFoundError("Pretrained run config not found at {pretrained_run_config} on rank={rank}...")` | `[ADD]` May occur at runtime | HF-to-Megatron conversion output not accessible on worker node | `/opt/nemo-rl/nemo_rl/models/policy/megatron_policy_worker.py:531` |
| `ValueError(f"Unknown precision: {self.cfg['precision']}")` | `[NEVER OCCUR]` Customizer provides valid precision | Invalid precision setting | `/opt/nemo-rl/nemo_rl/models/policy/dtensor_policy_worker.py:199` |
| `ValueError(f"Unknown reward model type: {rm_type}")` | `[NEVER OCCUR]` Customizer provides valid model types | Invalid reward model type | `/opt/nemo-rl/nemo_rl/models/policy/dtensor_policy_worker.py:258` |

**User Message**: `Model loading failed: {details}. The model or dependencies may be missing or incompatible.`

---

### 5. CheckpointError (500)

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `json.JSONDecodeError` when loading training_info | `[ADD]` May occur at runtime | Checkpoint metadata is corrupted | `/opt/nemo-rl/nemo_rl/utils/checkpoint.py:288` |
| `RuntimeError("Distributed process group is not initialized. Cannot save checkpoint.")` | `[ADD]` May occur at runtime | Process group died before checkpoint save | `/opt/nemo-rl/nemo_rl/models/policy/megatron_policy_worker.py:2158` |
| `RuntimeError("Megatron core state or model is not initialized. Cannot save checkpoint.")` | `[ADD]` May occur at runtime | Model failed to initialize before checkpoint | `/opt/nemo-rl/nemo_rl/models/policy/megatron_policy_worker.py:2163` |
| `FileExistsError("HF checkpoint already exists at {hf_ckpt_path}...")` | `[ADD]` May occur at runtime | Previous HF checkpoint not cleaned up | `/opt/nemo-rl/nemo_rl/utils/native_checkpoint.py:237` |
| `ValueError("optimizer_path must be provided when saving optimizer state")` | `[NEVER OCCUR]` Customizer provides paths | Missing optimizer path for checkpoint | `/opt/nemo-rl/nemo_rl/utils/native_checkpoint.py:164` |
| `ValueError("tokenizer_path must be provided when saving tokenizer state")` | `[NEVER OCCUR]` Customizer provides paths | Missing tokenizer path for checkpoint | `/opt/nemo-rl/nemo_rl/utils/native_checkpoint.py:172` |

**User Message**: `Checkpoint error: {details}. The checkpoint may be corrupted or inaccessible.`

---

### 6. CudaError (500)

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `torch.cuda.OutOfMemoryError` or "CUDA out of memory" | `[ADD]` May occur at runtime | GPU does not have enough memory for batch/model | Runtime |
| `RuntimeError` with "CUDA" in message | `[ADD]` May occur at runtime | General GPU error occurred | Runtime |

**User Message**: `GPU error: {details}. Try reducing batch_size, max_seq_length, or num_generations_per_prompt.`

---

### 7. DistributedError (500)

#### 7a. Ray Cluster Errors

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `ResourceInsufficientError(f"Not enough GPUs available...")` | `[ADD]` May occur at runtime | Cluster doesn't have enough GPUs | `/opt/nemo-rl/nemo_rl/distributed/virtual_cluster.py:298` |
| `ResourceInsufficientError(f"Not enough CPUs available...")` | `[ADD]` May occur at runtime | Cluster doesn't have enough CPUs | `/opt/nemo-rl/nemo_rl/distributed/virtual_cluster.py:303` |
| `ResourceInsufficientError(f"Maximum number of retries reached ({max_retries})...")` | `[ADD]` May occur at runtime | Cluster resources unstable | `/opt/nemo-rl/nemo_rl/distributed/virtual_cluster.py:275` |
| `TimeoutError("Timed out waiting for placement groups to be ready...")` | `[ADD]` May occur at runtime | Placement groups couldn't be allocated | `/opt/nemo-rl/nemo_rl/distributed/virtual_cluster.py:353` |
| `RuntimeError("No valid placement groups found...")` | `[ADD]` May occur at runtime | No valid placement groups for address/port | `/opt/nemo-rl/nemo_rl/distributed/virtual_cluster.py:408` |

#### 7b. Worker Group Errors

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `ValueError(f"workers_per_node list length ({len(workers_per_node)}) must match...")` | `[ADD]` May occur at runtime | Workers per node mismatch with placement groups | `/opt/nemo-rl/nemo_rl/distributed/worker_groups.py:371` |
| `ValueError("Sharding annotations must be provided to use sharded data distribution")` | `[ADD]` May occur at runtime | Missing sharding annotations | `/opt/nemo-rl/nemo_rl/distributed/worker_groups.py:816` |
| `ValueError("workers_per_node must be None (for default distribution), an int, or a list")` | `[NEVER OCCUR]` Customizer sets correctly | Invalid workers_per_node type | `/opt/nemo-rl/nemo_rl/distributed/worker_groups.py:378` |

#### 7c. Infrastructure Errors

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `OSError` containing "No space left on device" | `[ADD]` May occur at runtime | Ephemeral disk storage (/tmp) exhausted by Ray session logs | Runtime (Ray worker nodes) |

**User Message**: `Distributed training error: {details}. Please check cluster resources and configuration.`

---

### 8. GenerationError (500)

#### 8a. Weight Update / Refit Errors

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `RuntimeError("Updating weights for the generation policy failed during refit...")` | `[ADD]` May occur at runtime | Failed to update vLLM weights from training policy | `/opt/nemo-rl/nemo_rl/algorithms/grpo.py:822` |

#### 8b. Async/Sync API Mismatch Errors

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `RuntimeError("generate_text cannot be used with async_engine=True...")` | `[ADD]` May occur at runtime | Sync method called on async engine | `/opt/nemo-rl/nemo_rl/models/generation/vllm/vllm_worker.py:648` |
| `RuntimeError("update_weights_via_ipc_zmq cannot be used with async_engine=True...")` | `[ADD]` May occur at runtime | Sync IPC update on async engine | `/opt/nemo-rl/nemo_rl/models/generation/vllm/vllm_worker.py:723` |
| `AssertionError("Async generation is not enabled...")` | `[ADD]` May occur at runtime | Async generation called without async engine | `/opt/nemo-rl/nemo_rl/experience/rollouts.py:139` |

#### 8c. vLLM Resource Allocation Errors

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `ValueError("No placement groups available in the cluster")` | `[ADD]` May occur at runtime | No placement groups for vLLM workers | `/opt/nemo-rl/nemo_rl/models/generation/vllm/vllm_generation.py:238` |
| `RuntimeError("Failed to retrieve bundle/node mapping from placement group")` | `[ADD]` May occur at runtime | Cannot get placement group mapping | `/opt/nemo-rl/nemo_rl/models/generation/vllm/vllm_generation.py:258` |
| `ValueError("Placement group contains no bundles")` | `[ADD]` May occur at runtime | Empty placement group | `/opt/nemo-rl/nemo_rl/models/generation/vllm/vllm_generation.py:279` |
| `ValueError("Unable to allocate any worker groups with the available resources.")` | `[ADD]` May occur at runtime | Insufficient resources for vLLM workers | `/opt/nemo-rl/nemo_rl/models/generation/vllm/vllm_generation.py:292` |

#### 8d. Rollout / Generation Runtime Errors

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `RuntimeError(f"Error in sample {i} rollout: {e}")` | `[ADD]` May occur at runtime | Error during rollout for a sample | `/opt/nemo-rl/nemo_rl/experience/rollouts.py:834` |
| `RuntimeError(f"No output received for request {request_id}")` | `[ADD]` May occur at runtime | Async generation request returned no output | `/opt/nemo-rl/nemo_rl/models/generation/vllm/vllm_worker_async.py:626` |

**User Message**: `Generation error: {details}. There was a problem during model inference.`

---

### 9. TrainingTimeoutError (500)

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `subprocess.TimeoutExpired` | `[ADD]` May occur at runtime | Training subprocess exceeded `training_timeout` from API config | Customizer `runner.py` |

**User Message**: `Training exceeded time limit. Consider reducing training steps or increasing timeout.`

---

### 10. InternalError (500)

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `ValueError(f"Found {len(old_trajectories)} trajectories older than min_valid_version {min_valid_version}")` | `[ADD]` May occur at runtime | Async GRPO replay buffer has stale trajectories | `/opt/nemo-rl/nemo_rl/algorithms/async_utils.py:144` |
| `RuntimeError(f"tensors for {key=} must have same number of dimensions...")` | `[ADD]` May occur at runtime | Tensor dimension mismatch in message processing | `/opt/nemo-rl/nemo_rl/data/llm_message_utils.py:111` |
| `RuntimeError(f"expected consistent types but got: {[t.dtype for t in tensors]}")` | `[ADD]` May occur at runtime | Tensor dtype mismatch | `/opt/nemo-rl/nemo_rl/data/llm_message_utils.py:225` |
| `RuntimeError(f"expected tensors on the same device but got: {[t.device for t in tensors]}")` | `[ADD]` May occur at runtime | Tensors on different devices | `/opt/nemo-rl/nemo_rl/data/llm_message_utils.py:229` |
| `ValueError("Object must exist on at least one PP rank")` | `[ADD]` May occur at runtime | PP data not present on any pipeline stage | `/opt/nemo-rl/nemo_rl/models/policy/megatron_policy_worker.py:177` |
| `ValueError(f"max_size must be positive, got {max_size}")` | `[NEVER OCCUR]` Customizer sets correctly | Replay buffer max_size invalid | `/opt/nemo-rl/nemo_rl/algorithms/async_utils.py:45` |

**User Message**: `An internal error occurred: {details}.`

---

## Packing Algorithm Errors

These errors occur during sequence packing and are generally configuration issues:

| NeMo-RL Error Raised | Validation Status | What It Means | Code Pointer |
|----------------------|-------------------|---------------|--------------|
| `ValueError(f"Cannot create {target_bin_count} bins with only {total_sequences} sequences...")` | `[ADD]` May occur at runtime | Not enough sequences for packing | `/opt/nemo-rl/nemo_rl/data/packing/algorithms.py:123` |
| `ValueError(f"Sequence length {length} exceeds bin capacity {self.bin_capacity}")` | `[ADD]` May occur at runtime | Single sequence too long for packing | `/opt/nemo-rl/nemo_rl/data/packing/algorithms.py:254` |
| `ValueError("min_bin_count must be nonnegative")` | `[NEVER OCCUR]` | Packing config invalid | `/opt/nemo-rl/nemo_rl/data/packing/algorithms.py:68` |
| `ValueError("bin_count_multiple must be positive")` | `[NEVER OCCUR]` | Packing config invalid | `/opt/nemo-rl/nemo_rl/data/packing/algorithms.py:70` |
| `ValueError("bin_capacity must be positive")` | `[NEVER OCCUR]` | Packing config invalid | `/opt/nemo-rl/nemo_rl/data/packing/algorithms.py:541` |
| `ValueError(f"Unknown packing algorithm: {algorithm}...")` | `[NEVER OCCUR]` | Unknown packing algorithm | `/opt/nemo-rl/nemo_rl/data/packing/algorithms.py:669` |
