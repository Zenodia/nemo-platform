// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// TEMP: customizer-specific schema types inlined while the customizer SDK is being rebuilt.
// Source: @nemo/sdk/generated/platform/schema/Customization*.ts and customizer training types.
// Restore SDK imports (`@nemo/sdk/generated/platform/schema`) once the SDK regenerates with customizer support.

// Verbatim copy of generated code; eslint suppressed (typecheck still runs).

// Shared types still live in the SDK — re-export from there.
export type { PlatformJobStatus, PaginationData, SecretRef } from '../../generated/platform/schema';

import type {
  PlatformJobStatus,
  PaginationData,
  SecretRef,
  DatetimeFilter,
} from '../../generated/platform/schema';

// ----- Precision -----
// Inlined: was in SDK as a customizer-only training enum, removed when customizer SDK was dropped.
export type Precision = (typeof Precision)[keyof typeof Precision];

export const Precision = {
  fp8: 'fp8',
  bf16: 'bf16',
  fp16: 'fp16',
  fp32: 'fp32',
} as const;

// ----- DeploymentParamsAdditionalEnvs -----
// Inlined: was in SDK as a customizer-only deployment-config type, removed when customizer SDK was dropped.
export type DeploymentParamsAdditionalEnvs = { [key: string]: string };

// ----- DeploymentParams -----
// Inlined: was in SDK as a customizer-only deployment-config type, removed when customizer SDK was dropped.
export interface DeploymentParams {
  /** Number of GPUs required for the deployment */
  gpu?: number;
  /** Additional environment variables for the deployment */
  additional_envs?: DeploymentParamsAdditionalEnvs;
  /** Disk size for the deployment */
  disk_size?: string;
  /** Container image name from NGC. If not specified, defaults to multi-llm */
  image_name?: string;
  /** Container image tag from NGC */
  image_tag?: string;
  /** When automatically deploying a full SFT training, this parameter being set to true will allow subsequent LoRA adapters to be trained and deployed against it. */
  lora_enabled?: boolean;
  /** Tool calling configuration override for the NIM deployment. */
  tool_call_config?: ToolCallParams;
}

// ----- CustomizationJobsSortField -----
export type CustomizationJobsSortField =
  (typeof CustomizationJobsSortField)[keyof typeof CustomizationJobsSortField];

export const CustomizationJobsSortField = {
  created_at: 'created_at',
  '-created_at': '-created_at',
  updated_at: 'updated_at',
  '-updated_at': '-updated_at',
} as const;

// ----- CustomizationJobsListFilter -----
export interface CustomizationJobsListFilter {
  /** Jobs created at 'gte' datetime or 'lte' datetime. */
  created_at?: DatetimeFilter;
  /** Name of the job. */
  name?: string;
  /** Workspace of the job. */
  workspace?: string;
  /** Project containing the job. */
  project?: string;
  /** The current status. */
  status?: PlatformJobStatus;
  /** Jobs updated at 'gte' datetime or 'lte' datetime. */
  updated_at?: DatetimeFilter;
}

// ----- CustomizationJob -----
export interface CustomizationJob {
  id?: string;
  name: string;
  description?: string;
  project?: string;
  workspace?: string;
  created_at?: string;
  updated_at?: string;
  spec: CustomizationJobOutput;
  status?: PlatformJobStatus;
  status_details?: CustomizationJobStatusDetails;
  error_details?: CustomizationJobErrorDetails;
  ownership?: CustomizationJobOwnership;
  custom_fields?: CustomizationJobCustomFields;
}

// ----- CustomizationJobCustomFields -----
export type CustomizationJobCustomFields = { [key: string]: unknown };

// ----- CustomizationJobErrorDetails -----
export type CustomizationJobErrorDetails = { [key: string]: unknown };

// ----- CustomizationJobInput -----
/**
 * Input schema for creating customization jobs.
 */
export interface CustomizationJobInput {
  /** Model reference (e.g., 'workspace/model-name'). */
  model: string;
  /** Dataset URI. Supported protocol: fileset:// (e.g., fileset://workspace/name). */
  dataset: string;
  /** Training method and hyperparameters. */
  training: SFTTrainingInput | DistillationTrainingInput | DPOTrainingInput;
  /** Third-party integrations (e.g., Weights & Biases, MLflow). */
  integrations?: IntegrationParamsInput;
  /** Deployment configuration for auto-deploying the model after training. Pass a string to reference an existing ModelDeploymentConfig by name (e.g., 'my-config' or 'workspace/my-config'). An object provides inline NIM deployment parameters. Omit to skip deployment. */
  deployment_config?: string | DeploymentParams;
  /** Custom user-defined fields. */
  custom_fields?: CustomizationJobInputCustomFields;
  /** Output artifact configuration. If omitted, name is auto-generated as `{model}-{dataset}-<random-hex>`. The output type (model vs adapter) is always inferred from the training configuration. */
  output?: OutputRequest;
}

// ----- CustomizationJobInputCustomFields -----
/**
 * Custom user-defined fields.
 */
export type CustomizationJobInputCustomFields = { [key: string]: unknown };

// ----- CustomizationJobOutput -----
/**
 * Customization job details returned by the server.
 */
export interface CustomizationJobOutput {
  /** Model reference (e.g., 'workspace/model-name'). */
  model: string;
  /** Dataset URI. Supported protocol: fileset:// (e.g., fileset://workspace/name). */
  dataset: string;
  /** Training method and hyperparameters. */
  training: SFTTrainingOutput | DistillationTrainingOutput | DPOTrainingOutput;
  /** Third-party integrations (e.g., Weights & Biases, MLflow). */
  integrations?: IntegrationParamsOutput;
  /** Deployment configuration for auto-deploying the model after training. Pass a string to reference an existing ModelDeploymentConfig by name (e.g., 'my-config' or 'workspace/my-config'). An object provides inline NIM deployment parameters. Omit to skip deployment. */
  deployment_config?: string | DeploymentParams;
  /** Custom user-defined fields. */
  custom_fields?: CustomizationJobOutputCustomFields;
  /** Output artifact created by this job. */
  output: OutputResponse;
}

// ----- CustomizationJobOutputCustomFields -----
/**
 * Custom user-defined fields.
 */
export type CustomizationJobOutputCustomFields = { [key: string]: unknown };

// ----- CustomizationJobOwnership -----
export type CustomizationJobOwnership = { [key: string]: unknown };

// ----- CustomizationJobRequest -----
export interface CustomizationJobRequest {
  name?: string;
  description?: string;
  project?: string;
  spec: CustomizationJobInput;
  ownership?: CustomizationJobRequestOwnership;
  custom_fields?: CustomizationJobRequestCustomFields;
}

// ----- CustomizationJobRequestCustomFields -----
export type CustomizationJobRequestCustomFields = { [key: string]: unknown };

// ----- CustomizationJobRequestOwnership -----
export type CustomizationJobRequestOwnership = { [key: string]: unknown };

// ----- CustomizationJobStatusDetails -----
export type CustomizationJobStatusDetails = { [key: string]: unknown };

// ----- CustomizationJobsPage -----
export interface CustomizationJobsPage {
  data: CustomizationJob[];
  /** Pagination information. */
  pagination?: PaginationData;
  /** The field on which the results are sorted. */
  sort?: string;
  /** Filtering information. */
  filter?: CustomizationJobsPageFilter;
}

// ----- CustomizationJobsPageFilter -----
/**
 * Filtering information.
 */
export type CustomizationJobsPageFilter = { [key: string]: unknown };

// ----- CustomizationGetJobLogsParams -----
export type CustomizationGetJobLogsParams = {
  limit?: number;
  page_cursor?: string;
};

// ----- CustomizationListJobsParams -----
export type CustomizationListJobsParams = {
  /**
   * Page number.
   * @exclusiveMinimum 0
   */
  page?: number;
  /**
   * Page size.
   * @exclusiveMinimum 0
   */
  page_size?: number;
  /**
   * The field to sort by. To sort in decreasing order, use `-` in front of the field name.
   */
  sort?: CustomizationJobsSortField;
  /**
   * Filter jobs on various criteria.
   */
  filter?: CustomizationJobsListFilter;
};

// ----- DPOTrainingInput -----
/**
 * Direct Preference Optimization.
 */
export interface DPOTrainingInput {
  /** PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning. */
  peft?: LoRAParams;
  /** Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning. */
  learning_rate?: number;
  /** Minimum learning rate for cosine decay. Optional; used with learning rate schedules. */
  min_learning_rate?: number;
  /** Weight decay coefficient. Helps prevent overfitting. */
  weight_decay?: number;
  /** Adam beta1 parameter. Adjust for optimizer tuning. */
  adam_beta1?: number;
  /** Adam beta2 parameter. Adjust for optimizer tuning. */
  adam_beta2?: number;
  /**
   * Linear warmup steps. Recommended: 10% of total training steps for stable training.
   * @minimum 0
   */
  warmup_steps?: number;
  /** Optimizer name (e.g., 'adamw'). */
  optimizer?: string;
  /**
   * Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.
   * @exclusiveMinimum 0
   */
  epochs?: number;
  /** Max training steps. Overrides epochs if set. */
  max_steps?: number;
  /** Logging frequency in steps. Controls how often training metrics are logged. */
  log_every_n_steps?: number;
  /** Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count. */
  val_check_interval?: number;
  /**
   * Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.
   * @exclusiveMinimum 0
   */
  batch_size?: number;
  /**
   * Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.
   * @exclusiveMinimum 0
   */
  micro_batch_size?: number;
  /** Enable sequence packing for efficiency. Can improve training speed. */
  sequence_packing?: boolean;
  /**
   * Maximum token sequence length for training. Higher = more memory, longer training.
   * @exclusiveMinimum 0
   */
  max_seq_length?: number;
  /** Model precision for training. Auto-detected if unset. */
  precision?: Precision;
  /** Random seed for reproducibility. Optional. */
  seed?: number;
  parallelism?: ParallelismParams;
  /** Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default. */
  execution_profile?: string;
  type?: 'dpo';
  /**
   * KL penalty coefficient (beta in DPO paper).
   * @minimum 0
   */
  ref_policy_kl_penalty?: number;
  /** Average log probabilities for preference loss calculation. */
  preference_average_log_probs?: boolean;
  /** Average log probabilities for SFT regularization loss. */
  sft_average_log_probs?: boolean;
  /**
   * Weight for the preference (DPO) loss term.
   * @minimum 0
   */
  preference_loss_weight?: number;
  /**
   * Weight for SFT regularization loss (0 = disabled).
   * @minimum 0
   */
  sft_loss_weight?: number;
  /**
   * Maximum gradient norm for clipping.
   * @minimum 0
   */
  max_grad_norm?: number;
}

// ----- DPOTrainingOutput -----
/**
 * Direct Preference Optimization.
 */
export interface DPOTrainingOutput {
  /** PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning. */
  peft?: LoRAParams;
  /** Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning. */
  learning_rate?: number;
  /** Minimum learning rate for cosine decay. Optional; used with learning rate schedules. */
  min_learning_rate?: number;
  /** Weight decay coefficient. Helps prevent overfitting. */
  weight_decay?: number;
  /** Adam beta1 parameter. Adjust for optimizer tuning. */
  adam_beta1?: number;
  /** Adam beta2 parameter. Adjust for optimizer tuning. */
  adam_beta2?: number;
  /**
   * Linear warmup steps. Recommended: 10% of total training steps for stable training.
   * @minimum 0
   */
  warmup_steps?: number;
  /** Optimizer name (e.g., 'adamw'). */
  optimizer?: string;
  /**
   * Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.
   * @exclusiveMinimum 0
   */
  epochs?: number;
  /** Max training steps. Overrides epochs if set. */
  max_steps?: number;
  /** Logging frequency in steps. Controls how often training metrics are logged. */
  log_every_n_steps?: number;
  /** Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count. */
  val_check_interval?: number;
  /**
   * Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.
   * @exclusiveMinimum 0
   */
  batch_size?: number;
  /**
   * Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.
   * @exclusiveMinimum 0
   */
  micro_batch_size?: number;
  /** Enable sequence packing for efficiency. Can improve training speed. */
  sequence_packing?: boolean;
  /**
   * Maximum token sequence length for training. Higher = more memory, longer training.
   * @exclusiveMinimum 0
   */
  max_seq_length?: number;
  /** Model precision for training. Auto-detected if unset. */
  precision?: Precision;
  /** Random seed for reproducibility. Optional. */
  seed?: number;
  parallelism?: ParallelismParams;
  /** Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default. */
  execution_profile?: string;
  type?: 'dpo';
  /**
   * KL penalty coefficient (beta in DPO paper).
   * @minimum 0
   */
  ref_policy_kl_penalty?: number;
  /** Average log probabilities for preference loss calculation. */
  preference_average_log_probs?: boolean;
  /** Average log probabilities for SFT regularization loss. */
  sft_average_log_probs?: boolean;
  /**
   * Weight for the preference (DPO) loss term.
   * @minimum 0
   */
  preference_loss_weight?: number;
  /**
   * Weight for SFT regularization loss (0 = disabled).
   * @minimum 0
   */
  sft_loss_weight?: number;
  /**
   * Maximum gradient norm for clipping.
   * @minimum 0
   */
  max_grad_norm?: number;
}

// ----- DistillationTrainingInput -----
/**
 * Knowledge Distillation with a teacher model.

Customizer's differentiator — not available in Unsloth.
Trains the student model to match the teacher's output distribution.
 */
export interface DistillationTrainingInput {
  /** PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning. */
  peft?: LoRAParams;
  /** Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning. */
  learning_rate?: number;
  /** Minimum learning rate for cosine decay. Optional; used with learning rate schedules. */
  min_learning_rate?: number;
  /** Weight decay coefficient. Helps prevent overfitting. */
  weight_decay?: number;
  /** Adam beta1 parameter. Adjust for optimizer tuning. */
  adam_beta1?: number;
  /** Adam beta2 parameter. Adjust for optimizer tuning. */
  adam_beta2?: number;
  /**
   * Linear warmup steps. Recommended: 10% of total training steps for stable training.
   * @minimum 0
   */
  warmup_steps?: number;
  /** Optimizer name (e.g., 'adamw'). */
  optimizer?: string;
  /**
   * Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.
   * @exclusiveMinimum 0
   */
  epochs?: number;
  /** Max training steps. Overrides epochs if set. */
  max_steps?: number;
  /** Logging frequency in steps. Controls how often training metrics are logged. */
  log_every_n_steps?: number;
  /** Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count. */
  val_check_interval?: number;
  /**
   * Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.
   * @exclusiveMinimum 0
   */
  batch_size?: number;
  /**
   * Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.
   * @exclusiveMinimum 0
   */
  micro_batch_size?: number;
  /** Enable sequence packing for efficiency. Can improve training speed. */
  sequence_packing?: boolean;
  /**
   * Maximum token sequence length for training. Higher = more memory, longer training.
   * @exclusiveMinimum 0
   */
  max_seq_length?: number;
  /** Model precision for training. Auto-detected if unset. */
  precision?: Precision;
  /** Random seed for reproducibility. Optional. */
  seed?: number;
  parallelism?: ParallelismParams;
  /** Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default. */
  execution_profile?: string;
  type?: 'distillation';
  /** Teacher model URN (e.g., 'workspace/model-name'). Must have the same vocabulary as the student model. */
  teacher_model: string;
  /** Precision for loading the frozen teacher model. Lower precision reduces memory but may affect logit quality. */
  teacher_precision?: DistillationTrainingInputTeacherPrecision;
  /**
   * Balance between CE loss and KD loss. 0.0 = CE only, 1.0 = KD only.
   * @minimum 0
   * @maximum 1
   */
  distillation_ratio?: number;
  /**
   * Softmax temperature for KD. Higher = softer probability distributions.
   * @exclusiveMinimum 0
   */
  distillation_temperature?: number;
}

// ----- DistillationTrainingInputTeacherPrecision -----
/**
 * Precision for loading the frozen teacher model. Lower precision reduces memory but may affect logit quality.
 */
export type DistillationTrainingInputTeacherPrecision =
  (typeof DistillationTrainingInputTeacherPrecision)[keyof typeof DistillationTrainingInputTeacherPrecision];

export const DistillationTrainingInputTeacherPrecision = {
  bf16: 'bf16',
  fp16: 'fp16',
  fp32: 'fp32',
} as const;

// ----- DistillationTrainingOutput -----
/**
 * Knowledge Distillation with a teacher model.

Customizer's differentiator — not available in Unsloth.
Trains the student model to match the teacher's output distribution.
 */
export interface DistillationTrainingOutput {
  /** PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning. */
  peft?: LoRAParams;
  /** Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning. */
  learning_rate?: number;
  /** Minimum learning rate for cosine decay. Optional; used with learning rate schedules. */
  min_learning_rate?: number;
  /** Weight decay coefficient. Helps prevent overfitting. */
  weight_decay?: number;
  /** Adam beta1 parameter. Adjust for optimizer tuning. */
  adam_beta1?: number;
  /** Adam beta2 parameter. Adjust for optimizer tuning. */
  adam_beta2?: number;
  /**
   * Linear warmup steps. Recommended: 10% of total training steps for stable training.
   * @minimum 0
   */
  warmup_steps?: number;
  /** Optimizer name (e.g., 'adamw'). */
  optimizer?: string;
  /**
   * Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.
   * @exclusiveMinimum 0
   */
  epochs?: number;
  /** Max training steps. Overrides epochs if set. */
  max_steps?: number;
  /** Logging frequency in steps. Controls how often training metrics are logged. */
  log_every_n_steps?: number;
  /** Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count. */
  val_check_interval?: number;
  /**
   * Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.
   * @exclusiveMinimum 0
   */
  batch_size?: number;
  /**
   * Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.
   * @exclusiveMinimum 0
   */
  micro_batch_size?: number;
  /** Enable sequence packing for efficiency. Can improve training speed. */
  sequence_packing?: boolean;
  /**
   * Maximum token sequence length for training. Higher = more memory, longer training.
   * @exclusiveMinimum 0
   */
  max_seq_length?: number;
  /** Model precision for training. Auto-detected if unset. */
  precision?: Precision;
  /** Random seed for reproducibility. Optional. */
  seed?: number;
  parallelism?: ParallelismParams;
  /** Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default. */
  execution_profile?: string;
  type?: 'distillation';
  /** Teacher model URN (e.g., 'workspace/model-name'). Must have the same vocabulary as the student model. */
  teacher_model: string;
  /** Precision for loading the frozen teacher model. Lower precision reduces memory but may affect logit quality. */
  teacher_precision?: DistillationTrainingOutputTeacherPrecision;
  /**
   * Balance between CE loss and KD loss. 0.0 = CE only, 1.0 = KD only.
   * @minimum 0
   * @maximum 1
   */
  distillation_ratio?: number;
  /**
   * Softmax temperature for KD. Higher = softer probability distributions.
   * @exclusiveMinimum 0
   */
  distillation_temperature?: number;
}

// ----- DistillationTrainingOutputTeacherPrecision -----
/**
 * Precision for loading the frozen teacher model. Lower precision reduces memory but may affect logit quality.
 */
export type DistillationTrainingOutputTeacherPrecision =
  (typeof DistillationTrainingOutputTeacherPrecision)[keyof typeof DistillationTrainingOutputTeacherPrecision];

export const DistillationTrainingOutputTeacherPrecision = {
  bf16: 'bf16',
  fp16: 'fp16',
  fp32: 'fp32',
} as const;

// ----- FinetuningType -----
/**
 * Finetuning types.
 */
export type FinetuningType = (typeof FinetuningType)[keyof typeof FinetuningType];

export const FinetuningType = {
  lora_merged: 'lora_merged',
  all_weights: 'all_weights',
  last_layer: 'last_layer',
  top_layers: 'top_layers',
  gradual_unfreezing: 'gradual_unfreezing',
  bias_only: 'bias_only',
  attention_only: 'attention_only',
  lora: 'lora',
  qlora: 'qlora',
  adalora: 'adalora',
  dora: 'dora',
  lora_plus: 'lora_plus',
  prompt_tuning: 'prompt_tuning',
  prefix_tuning: 'prefix_tuning',
  p_tuning: 'p_tuning',
  p_tuning_v2: 'p_tuning_v2',
  soft_prompt: 'soft_prompt',
  ppo: 'ppo',
  dpo: 'dpo',
  cdpo: 'cdpo',
  ipo: 'ipo',
  orpo: 'orpo',
  kto: 'kto',
  rrhf: 'rrhf',
  grpo: 'grpo',
} as const;

// ----- IntegrationParamsInput -----
/**
 * Third-party integration configurations.

Each integration type has its own optional field. To enable an integration,
provide its configuration object. Omit or set to None to disable.
 */
export interface IntegrationParamsInput {
  /** Weights & Biases integration configuration. */
  wandb?: WandBParams;
  /** MLflow integration configuration. */
  mlflow?: MLflowParams;
}

// ----- IntegrationParamsOutput -----
/**
 * Third-party integration configurations.

Each integration type has its own optional field. To enable an integration,
provide its configuration object. Omit or set to None to disable.
 */
export interface IntegrationParamsOutput {
  /** Weights & Biases integration configuration. */
  wandb?: WandBParams;
  /** MLflow integration configuration. */
  mlflow?: MLflowParams;
}

// ----- LoRAParams -----
/**
 * LoRA adapter configuration.
 */
export interface LoRAParams {
  /** Enable quantized training to reduce GPU memory. If the base model is full-precision, it will be quantized at load time. If the base model is already pre-quantized, this configures the expected precision. The trained adapter remains full-precision. */
  quantization?: QuantizationParams;
  type?: 'lora';
  /**
   * LoRA rank (low-rank dimension). Higher values increase capacity but use more memory.
   * @minimum 1
   * @maximum 256
   */
  rank?: number;
  /**
   * LoRA alpha scaling factor. Common practice: alpha = 2-4x rank.
   * @minimum 1
   */
  alpha?: number;
  /**
   * LoRA dropout probability for regularization.
   * @minimum 0
   * @maximum 1
   */
  dropout?: number;
  /** Module name patterns to apply LoRA to (e.g., ['*.q_proj', '*.v_proj']). If not set, applies to all '*proj' linear layers. */
  target_modules?: string[];
  /** Merge LoRA weights into base model after training. Produces a full-weight checkpoint instead of an adapter. */
  merge?: boolean;
  /** Enable DoRA (Weight-Decomposed Low-Rank Adaptation). Decomposes weight updates into magnitude and direction components. Can improve quality especially at low ranks, but adds training overhead. */
  use_dora?: boolean;
}

// ----- MLflowParams -----
/**
 * MLflow integration configuration.
 */
export interface MLflowParams {
  /** MLflow experiment name (groups related runs). Defaults to output.name if not set. */
  experiment_name?: string;
  /** MLflow run name. Defaults to job_id if not provided. */
  run_name?: string;
  /** MLflow tags as key-value pairs for filtering runs. */
  tags?: MLflowParamsTags;
  /** MLflow run description. */
  description?: string;
  /** MLflow tracking server URI (e.g., 'http://mlflow.mycompany.com:5000'). Can also be set via MLFLOW_TRACKING_URI environment variable. */
  tracking_uri?: string;
}

// ----- MLflowParamsTags -----
/**
 * MLflow tags as key-value pairs for filtering runs.
 */
export type MLflowParamsTags = { [key: string]: string };

// ----- OutputNameType -----
/**
 * Output artifact type.
 */
export type OutputNameType = (typeof OutputNameType)[keyof typeof OutputNameType];

export const OutputNameType = {
  adapter: 'adapter',
  model: 'model',
} as const;

// ----- OutputRequest -----
/**
 * Output artifact configuration provided by the user.
 */
export interface OutputRequest {
  /**
   * Name of the output artifact. Used to identify it during deployment and inference.
   * @maxLength 255
   * @pattern ^[\w\-.]+$
   */
  name: string;
}

// ----- OutputResponse -----
/**
 * Resolved output artifact details returned by the server.
 */
export interface OutputResponse {
  /**
   * Name of the output artifact. Used to identify it during deployment and inference.
   * @maxLength 255
   * @pattern ^[\w\-.]+$
   */
  name: string;
  /** Output artifact type. Either `model` (full fine-tuned weights) or `adapter` (LoRA adapter weights). */
  type: OutputNameType;
  /**
   * FileSet name where output artifacts are stored.
   * @maxLength 255
   * @pattern ^[\w\-.]+$
   */
  fileset: string;
}

// ----- ParallelismParams -----
/**
 * Distributed training parallelism configuration.

Most users only need num_gpus_per_node. Advanced users can configure
tensor/pipeline/context/expert parallelism for large models.
 */
export interface ParallelismParams {
  /**
   * Number of gpus per node.
   * @exclusiveMinimum 0
   */
  num_gpus_per_node?: number;
  /**
   * Number of nodes.
   * @exclusiveMinimum 0
   */
  num_nodes?: number;
  /**
   * Tensor parallel size.
   * @exclusiveMinimum 0
   */
  tensor_parallel_size?: number;
  /**
   * Pipeline parallel size.
   * @exclusiveMinimum 0
   */
  pipeline_parallel_size?: number;
  /**
   * Context parallel size.
   * @exclusiveMinimum 0
   */
  context_parallel_size?: number;
  /** Expert parallel size (MoE models). */
  expert_parallel_size?: number;
  /** Enable sequence parallelism. */
  sequence_parallel?: boolean;
}

// ----- QuantizationParams -----
/**
 * Base model quantization for memory-efficient PEFT training.

Supports two scenarios:
- Full-precision base model: quantized on-the-fly at load time
- Pre-quantized base model: loaded directly at the specified precision

In both cases, base model weights are frozen and only the PEFT adapter
parameters are trained in full precision.
 */
export interface QuantizationParams {
  /** Quantization precision. '4bit' (NF4) for maximum memory savings, '8bit' (LLM.int8) for a balance of quality and memory. */
  precision?: QuantizationParamsPrecision;
}

// ----- QuantizationParamsPrecision -----
/**
 * Quantization precision. '4bit' (NF4) for maximum memory savings, '8bit' (LLM.int8) for a balance of quality and memory.
 */
export type QuantizationParamsPrecision =
  (typeof QuantizationParamsPrecision)[keyof typeof QuantizationParamsPrecision];

export const QuantizationParamsPrecision = {
  '4bit': '4bit',
  '8bit': '8bit',
} as const;

// ----- SFTTrainingInput -----
/**
 * Supervised Fine-Tuning.
 */
export interface SFTTrainingInput {
  /** PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning. */
  peft?: LoRAParams;
  /** Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning. */
  learning_rate?: number;
  /** Minimum learning rate for cosine decay. Optional; used with learning rate schedules. */
  min_learning_rate?: number;
  /** Weight decay coefficient. Helps prevent overfitting. */
  weight_decay?: number;
  /** Adam beta1 parameter. Adjust for optimizer tuning. */
  adam_beta1?: number;
  /** Adam beta2 parameter. Adjust for optimizer tuning. */
  adam_beta2?: number;
  /**
   * Linear warmup steps. Recommended: 10% of total training steps for stable training.
   * @minimum 0
   */
  warmup_steps?: number;
  /** Optimizer name (e.g., 'adamw'). */
  optimizer?: string;
  /**
   * Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.
   * @exclusiveMinimum 0
   */
  epochs?: number;
  /** Max training steps. Overrides epochs if set. */
  max_steps?: number;
  /** Logging frequency in steps. Controls how often training metrics are logged. */
  log_every_n_steps?: number;
  /** Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count. */
  val_check_interval?: number;
  /**
   * Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.
   * @exclusiveMinimum 0
   */
  batch_size?: number;
  /**
   * Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.
   * @exclusiveMinimum 0
   */
  micro_batch_size?: number;
  /** Enable sequence packing for efficiency. Can improve training speed. */
  sequence_packing?: boolean;
  /**
   * Maximum token sequence length for training. Higher = more memory, longer training.
   * @exclusiveMinimum 0
   */
  max_seq_length?: number;
  /** Model precision for training. Auto-detected if unset. */
  precision?: Precision;
  /** Random seed for reproducibility. Optional. */
  seed?: number;
  parallelism?: ParallelismParams;
  /** Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default. */
  execution_profile?: string;
  type?: 'sft';
}

// ----- SFTTrainingOutput -----
/**
 * Supervised Fine-Tuning.
 */
export interface SFTTrainingOutput {
  /** PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning. */
  peft?: LoRAParams;
  /** Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning. */
  learning_rate?: number;
  /** Minimum learning rate for cosine decay. Optional; used with learning rate schedules. */
  min_learning_rate?: number;
  /** Weight decay coefficient. Helps prevent overfitting. */
  weight_decay?: number;
  /** Adam beta1 parameter. Adjust for optimizer tuning. */
  adam_beta1?: number;
  /** Adam beta2 parameter. Adjust for optimizer tuning. */
  adam_beta2?: number;
  /**
   * Linear warmup steps. Recommended: 10% of total training steps for stable training.
   * @minimum 0
   */
  warmup_steps?: number;
  /** Optimizer name (e.g., 'adamw'). */
  optimizer?: string;
  /**
   * Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.
   * @exclusiveMinimum 0
   */
  epochs?: number;
  /** Max training steps. Overrides epochs if set. */
  max_steps?: number;
  /** Logging frequency in steps. Controls how often training metrics are logged. */
  log_every_n_steps?: number;
  /** Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count. */
  val_check_interval?: number;
  /**
   * Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.
   * @exclusiveMinimum 0
   */
  batch_size?: number;
  /**
   * Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.
   * @exclusiveMinimum 0
   */
  micro_batch_size?: number;
  /** Enable sequence packing for efficiency. Can improve training speed. */
  sequence_packing?: boolean;
  /**
   * Maximum token sequence length for training. Higher = more memory, longer training.
   * @exclusiveMinimum 0
   */
  max_seq_length?: number;
  /** Model precision for training. Auto-detected if unset. */
  precision?: Precision;
  /** Random seed for reproducibility. Optional. */
  seed?: number;
  parallelism?: ParallelismParams;
  /** Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default. */
  execution_profile?: string;
  type?: 'sft';
}

// ----- ToolCallParams -----
/**
 * Tool calling configuration for NIM deployments.
 */
export interface ToolCallParams {
  /** Name of the tool call parser to use (e.g., 'openai', 'hermes', 'pythonic', 'llama3_json', 'mistral'). */
  tool_call_parser?: string;
  /**
   * Reference to a fileset containing the custom tool call plugin Python file. Expected format: '{workspace}/{fileset_name}'.
   * @pattern ^[\w\-.]+/[\w\-.]+$
   */
  tool_call_plugin?: string;
  /** Whether to enable automatic tool choice. */
  auto_tool_choice?: boolean;
}

// ----- WandBParams -----
/**
 * Weights & Biases integration configuration.

To use W&B, provide an api_key_secret referencing a secret that contains
the WANDB_API_KEY value. Optionally provide base_url for self-hosted W&B servers.
 */
export interface WandBParams {
  /** W&B project name (groups related runs). Defaults to output.name if not set. */
  project?: string;
  /** W&B run name. Defaults to job_id if not provided. */
  name?: string;
  /** W&B entity (team or username). */
  entity?: string;
  /** W&B tags for filtering runs. */
  tags?: string[];
  /** W&B notes/description for the run. */
  notes?: string;
  /** Base URL for self-hosted W&B server (e.g., 'https://wandb.mycompany.com'). If not provided, uses the default W&B cloud service. */
  base_url?: string;
  /** Reference to a secret containing the WANDB_API_KEY. Format: 'secret_name' (uses request workspace) or 'workspace/secret_name' (explicit workspace). */
  api_key_secret?: SecretRef;
}
