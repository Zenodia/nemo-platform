// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// TEMP: SafeSynthesizer-specific schema types inlined while the safe-synthesizer SDK is being rebuilt.
// Source: @nemo/sdk/generated/platform/schema/SafeSynthesizer*.ts plus SS-only config types
// (ClassifyConfig, Column, GenerateParameters, etc. — these were referenced only by SafeSynthesizer).
// Restore SDK imports (`@nemo/sdk/generated/platform/schema`) once the SDK regenerates with safe-synthesizer support.

// Truly shared types still live in the SDK — re-export from there.
export type {
  DatetimeFilter,
  PaginationData,
  PlatformJobStatus,
} from '../../generated/platform/schema';

import type {
  DatetimeFilter,
  PaginationData,
  PlatformJobStatus,
} from '../../generated/platform/schema';

// ----- SafeSynthesizerJob -----
export interface SafeSynthesizerJob {
  id?: string;
  name: string;
  description?: string;
  project?: string;
  workspace?: string;
  created_at?: string;
  updated_at?: string;
  spec: SafeSynthesizerJobConfig;
  status?: PlatformJobStatus;
  status_details?: SafeSynthesizerJobStatusDetails;
  error_details?: SafeSynthesizerJobErrorDetails;
  ownership?: SafeSynthesizerJobOwnership;
  custom_fields?: SafeSynthesizerJobCustomFields;
}

// ----- SafeSynthesizerJobConfig -----
/**
 * Configuration model for Safe Synthesizer jobs.

Used primarily internally to configure a run submitted to the NeMo Jobs
Microservice.
 */
export interface SafeSynthesizerJobConfig {
  /** The data source for the job. */
  data_source: string;
  /** The Safe Synthesizer parameters configuration. */
  config: SafeSynthesizerParameters;
  /** Name of platform secret containing the HuggingFace token. Must exist in the same workspace as the job. */
  hf_token_secret?: string;
  /** Whether to run LLM training and generation phases. When False the task only performs PII replacement and returns the processed data. */
  enable_synthesis?: boolean;
}

// ----- SafeSynthesizerJobCustomFields -----
export type SafeSynthesizerJobCustomFields = { [key: string]: unknown };

// ----- SafeSynthesizerJobErrorDetails -----
export type SafeSynthesizerJobErrorDetails = { [key: string]: unknown };

// ----- SafeSynthesizerJobOwnership -----
export type SafeSynthesizerJobOwnership = { [key: string]: unknown };

// ----- SafeSynthesizerJobRequest -----
export interface SafeSynthesizerJobRequest {
  name?: string;
  description?: string;
  project?: string;
  spec: SafeSynthesizerJobConfig;
  ownership?: SafeSynthesizerJobRequestOwnership;
  custom_fields?: SafeSynthesizerJobRequestCustomFields;
}

// ----- SafeSynthesizerJobRequestCustomFields -----
export type SafeSynthesizerJobRequestCustomFields = { [key: string]: unknown };

// ----- SafeSynthesizerJobRequestOwnership -----
export type SafeSynthesizerJobRequestOwnership = { [key: string]: unknown };

// ----- SafeSynthesizerJobStatusDetails -----
export type SafeSynthesizerJobStatusDetails = { [key: string]: unknown };

// ----- SafeSynthesizerJobsListFilter -----
export interface SafeSynthesizerJobsListFilter {
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

// ----- SafeSynthesizerJobsSortField -----
export type SafeSynthesizerJobsSortField =
  (typeof SafeSynthesizerJobsSortField)[keyof typeof SafeSynthesizerJobsSortField];

export const SafeSynthesizerJobsSortField = {
  created_at: 'created_at',
  '-created_at': '-created_at',
  updated_at: 'updated_at',
  '-updated_at': '-updated_at',
} as const;

// ----- SafeSynthesizerJobsPage -----
export interface SafeSynthesizerJobsPage {
  data: SafeSynthesizerJob[];
  /** Pagination information. */
  pagination?: PaginationData;
  /** The field on which the results are sorted. */
  sort?: string;
  /** Filtering information. */
  filter?: SafeSynthesizerJobsPageFilter;
}

// ----- SafeSynthesizerJobsPageFilter -----
/**
 * Filtering information.
 */
export type SafeSynthesizerJobsPageFilter = { [key: string]: unknown };

// ----- SafeSynthesizerParameters -----
/**
 * Main configuration class for the Safe Synthesizer pipeline.

This is the top-level configuration class that orchestrates all aspects of
synthetic data generation including training, generation, privacy, evaluation,
and data handling. It provides validation to ensure parameter compatibility.
 */
export interface SafeSynthesizerParameters {
  /** Configuration controlling how input data is grouped and split for training and evaluation. */
  data?: DataParameters;
  /** Parameters for evaluating the quality of generated synthetic data. */
  evaluation?: EvaluationParameters;
  /** Hyperparameters for model training such as learning rate, batch size, and LoRA adapter settings. */
  training?: TrainingHyperparams;
  /** Parameters governing synthetic data generation including temperature, top-p, and number of records to produce. */
  generation?: GenerateParameters;
  /** Differential-privacy hyperparameters. When ``None``, differential privacy is disabled entirely. */
  privacy?: DifferentialPrivacyHyperparams;
  /** Configuration for time-series mode. Time-series pipeline is currently experimental. */
  time_series?: TimeSeriesParameters;
  /** PII replacement configuration. When ``None``, PII replacement is skipped. */
  replace_pii?: PiiReplacerConfig;
}

// ----- SafeSynthesizerSummary -----
/**
 * Aggregated quality, privacy, and record-count metrics for a pipeline run.
 */
export interface SafeSynthesizerSummary {
  /** Weighted composite of the five sub-scores below (SQS). Higher is better (0--10 scale). */
  synthetic_data_quality_score?: number;
  /** How closely pairwise column correlations in synthetic data match the original for numeric and categorical columns. */
  column_correlation_stability_score?: number;
  /** PCA-based comparison of multivariate structure between real and synthetic data for numeric and categorical columns. */
  deep_structure_stability_score?: number;
  /** Per-column Jensen-Shannon distance between training and synthetic distributions averaged across all numeric and categorical columns. */
  column_distribution_stability_score?: number;
  /** Embedding-based semantic closeness between real and synthetic free-text columns. */
  text_semantic_similarity_score?: number;
  /** Jensen-Shannon divergence over sentence count, words-per-sentence, and characters-per-word distributions between real and synthetic free-text columns. */
  text_structure_similarity_score?: number;
  /** Composite of MIA and AIA protection scores. */
  data_privacy_score?: number;
  /** Resistance to attacks that try to determine whether a record was in the training set. */
  membership_inference_protection_score?: number;
  /** Resistance to attacks that try to infer sensitive attributes from quasi-identifiers. */
  attribute_inference_protection_score?: number;
  /** Count of synthetic records that passed schema and format validation. */
  num_valid_records?: number;
  /** Count of synthetic records filtered out during validation. */
  num_invalid_records?: number;
  /** Total LLM generation prompts issued. */
  num_prompts?: number;
  /** Ratio of valid records: ``num_valid_records / (num_valid_records + num_invalid_records)``. */
  valid_record_fraction?: number;
  /** Per-stage wall-clock durations. */
  timing: SafeSynthesizerTiming;
}

// ----- SafeSynthesizerTiming -----
/**
 * Wall-clock durations for each pipeline stage.
 */
export interface SafeSynthesizerTiming {
  /** Total end-to-end pipeline duration in seconds. */
  total_time_sec?: number;
  /** Time spent on PII replacement. */
  pii_replacer_time_sec?: number;
  /** Time spent on model training. */
  training_time_sec?: number;
  /** Time spent generating synthetic records. */
  generation_time_sec?: number;
  /** Time spent evaluating synthetic data quality. */
  evaluation_time_sec?: number;
}

// ----- SafeSynthesizerListJobsParams -----
export type SafeSynthesizerListJobsParams = {
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
  sort?: SafeSynthesizerJobsSortField;
  /**
   * Filter jobs on various criteria.
   */
  filter?: SafeSynthesizerJobsListFilter;
};

// ----- SafeSynthesizerGetJobLogsParams -----
export type SafeSynthesizerGetJobLogsParams = {
  limit?: number;
  page_cursor?: string;
};

// ----- ClassifyConfig -----
/**
 * Configuration for column classification using an LLM.
 */
export interface ClassifyConfig {
  /** Enable column classification. */
  enable_classify?: boolean;
  /** List of entity types to classify. */
  entities?: string[];
  /** Number of column values to sample for classification. */
  num_samples?: number;
  /** Name of the model provider in the Inference Gateway for column classification. The job compiler will resolve this to the appropriate endpoint URL. */
  classify_model_provider?: string;
}

// ----- Column -----
/**
 * Rule matcher for selecting columns by name, position, condition, entity, or type.
 */
export interface Column {
  /** Column name. */
  name?: string;
  /** Column position. */
  position?: number | number[];
  /** Column condition. */
  condition?: string;
  /** Rename to value. */
  value?: string;
  /** Column entity match. */
  entity?: string | string[];
  /** Column type match. */
  type?: string | string[];
}

// ----- ColumnActions -----
/**
 * Container for column add, drop, and rename operations.
 */
export interface ColumnActions {
  /** Columns to add. */
  add?: Column[];
  /** Columns to drop. */
  drop?: Column[];
  /** Columns to rename. */
  rename?: Column[];
}

// ----- DataParameters -----
/**
 * Configuration for grouping, ordering, and splitting input data for training and evaluation.
 */
export interface DataParameters {
  /** Column to group training examples by. This is useful when you want the model to learn inter-record correlations for a given grouping of records. */
  group_training_examples_by?: string;
  /** Column to order training examples by. This is useful when you want the model to learn sequential relationships for a given ordering of records. If you provide this parameter, you must also provide ``group_training_examples_by``. */
  order_training_examples_by?: string;
  /** If specified, adds at most this number of sequences per example. Supports 'auto' where a value of 1 is chosen if differential privacy is enabled, and 10 otherwise. If not specified or set to 'auto', fills up context. Required for DP to limit contribution of each example. */
  max_sequences_per_example?: 'auto' | number;
  /** Amount of records to hold out for evaluation. If this is a float between 0 and 1, that ratio of records is held out. If an integer greater than 1, that number of records is held out. If the value is equal to zero, no holdout will be performed. Must be >= 0. */
  holdout?: number;
  /** Maximum number of records to hold out. Overrides any behavior set by ``holdout``. Must be >= 0. */
  max_holdout?: number;
  /** Random state for holdout split to ensure reproducibility. */
  random_state?: number;
}

// ----- DifferentialPrivacyHyperparams -----
/**
 * Hyperparameters for differential privacy during training.

These parameters configure differential privacy (DP) training using DP-SGD algorithm.
When enabled, they provide formal privacy guarantees by adding calibrated noise
during training.
 */
export interface DifferentialPrivacyHyperparams {
  /** Enable differentially-private training with DP-SGD. */
  dp_enabled?: boolean;
  /** Target privacy budget -- lower values provide stronger privacy. Must be > 0. */
  epsilon?: number;
  /** Probability of accidentally leaking information. Should be much smaller than 1/n where n is the number of training records. Setting to 'auto' uses delta of 1/n^1.2. Must be in [0, 1) or 'auto'. */
  delta?: 'auto' | number;
  /** Maximum L2 norm for per-sample gradient clipping. Must be > 0. */
  per_sample_max_grad_norm?: number;
}

// ----- EvaluationParameters -----
/**
 * Configuration for evaluating synthetic data quality and privacy.

This class controls which evaluation metrics are computed and how they are configured.
It includes privacy attack evaluations, statistical quality metrics, and downstream
machine learning performance assessments.
 */
export interface EvaluationParameters {
  /** Enable membership inference attack evaluation for privacy assessment. */
  mia_enabled?: boolean;
  /** Enable attribute inference attack evaluation for privacy assessment. */
  aia_enabled?: boolean;
  /** Number of columns to include in statistical quality reports. */
  sqs_report_columns?: number;
  /** Number of rows to include in statistical quality reports. */
  sqs_report_rows?: number;
  /** Number of mandatory columns that must be used in evaluation. */
  mandatory_columns?: number;
  /** Enable or disable evaluation. */
  enabled?: boolean;
  /** Number of quasi-identifiers to sample for privacy attacks. */
  quasi_identifier_count?: number;
  /** Enable PII Replay detection. */
  pii_replay_enabled?: boolean;
  /** List of entities for PII Replay. If not provided, default entities will be used. */
  pii_replay_entities?: string[];
  /** List of columns for PII Replay. If not provided, only entities will be used. */
  pii_replay_columns?: string[];
}

// ----- GenerateParameters -----
/**
 * Configuration parameters for synthetic data generation.

These parameters control how synthetic data is generated after the model is trained.
They affect the quality, diversity, and validity of the generated synthetic records.
 */
export interface GenerateParameters {
  /** Number of records to generate. */
  num_records?: number;
  /** Sampling temperature for controlling randomness (higher = more random). */
  temperature?: number;
  /** The value used to control the likelihood of the model repeating the same token. Must be > 0. */
  repetition_penalty?: number;
  /** Nucleus sampling probability for token selection. Must be in (0, 1]. */
  top_p?: number;
  /** Number of consecutive generations where the ``invalid_fraction_threshold`` is reached before stopping generation. Must be >= 1. */
  patience?: number;
  /** The fraction of invalid records that will stop generation after the ``patience`` limit is reached. Must be in [0, 1]. */
  invalid_fraction_threshold?: number;
  /** Whether to use structured generation for better format control. */
  use_structured_generation?: boolean;
  /** The backend used by vLLM when ``use_structured_generation`` is ``True``. Supported backends: 'outlines', 'guidance', 'xgrammar', 'lm-format-enforcer'. 'auto' will allow vLLM to choose the backend. */
  structured_generation_backend?: GenerateParametersStructuredGenerationBackend;
  /** The method used to generate the schema from your dataset and pass it to the generation backend. 'regex' uses a custom regex construction method that tends to be more comprehensive than 'json_schema' at the cost of speed. */
  structured_generation_schema_method?: GenerateParametersStructuredGenerationSchemaMethod;
  /** Whether to use a regex that matches exactly one sequence or record if ``max_sequences_per_example`` is 1. */
  structured_generation_use_single_sequence?: boolean;
  /** Enforce time-series fidelity by enforcing order, intervals, start and end times of the records. */
  enforce_timeseries_fidelity?: boolean;
  /** Validation parameters controlling validation logic and automatic fixes when parsing LLM output and converting to tabular data. */
  validation?: ValidationParameters;
  /** The attention backend for the vLLM engine. Common values: 'FLASHINFER', 'FLASH_ATTN', 'TRITON_ATTN', 'FLEX_ATTENTION'. If ``None`` or 'auto', vLLM will auto-select the best available backend. */
  attention_backend?: string;
}

// ----- GenerateParametersStructuredGenerationBackend -----
/**
 * The backend used by vLLM when ``use_structured_generation`` is ``True``. Supported backends: 'outlines', 'guidance', 'xgrammar', 'lm-format-enforcer'. 'auto' will allow vLLM to choose the backend.
 */
export type GenerateParametersStructuredGenerationBackend =
  (typeof GenerateParametersStructuredGenerationBackend)[keyof typeof GenerateParametersStructuredGenerationBackend];

export const GenerateParametersStructuredGenerationBackend = {
  auto: 'auto',
  xgrammar: 'xgrammar',
  guidance: 'guidance',
  outlines: 'outlines',
  'lm-format-enforcer': 'lm-format-enforcer',
} as const;

// ----- GenerateParametersStructuredGenerationSchemaMethod -----
/**
 * The method used to generate the schema from your dataset and pass it to the generation backend. 'regex' uses a custom regex construction method that tends to be more comprehensive than 'json_schema' at the cost of speed.
 */
export type GenerateParametersStructuredGenerationSchemaMethod =
  (typeof GenerateParametersStructuredGenerationSchemaMethod)[keyof typeof GenerateParametersStructuredGenerationSchemaMethod];

export const GenerateParametersStructuredGenerationSchemaMethod = {
  regex: 'regex',
  json_schema: 'json_schema',
} as const;

// ----- GlinerConfig -----
/**
 * Configuration for the GLiNER named-entity recognition model.
 */
export interface GlinerConfig {
  /** Enable GLiNER NER module. */
  enable_gliner?: boolean;
  /** Enable GLiNER batch mode. */
  enable_batch_mode?: boolean;
  /** GLiNER batch size. */
  batch_size?: number;
  /** GLiNER batch chunk length in characters. */
  chunk_length?: number;
  /** GLiNER model name. */
  gliner_model?: string;
}

// ----- Globals -----
/**
 * Global settings for the PII replacer including locales, seed, NER, and classification.
 */
export interface Globals {
  /** List of locales. */
  locales?: string[];
  /** Optional random seed. */
  seed?: number;
  /** Column classification configuration. */
  classify?: ClassifyConfig;
  /** Named Entity Recognition configuration. */
  ner?: NERConfig;
  /** List of columns to preserve as immutable across all transformations. */
  lock_columns?: string[];
}

// ----- NERConfig -----
/**
 * Configuration for Named Entity Recognition.
 */
export interface NERConfig {
  /** NER model threshold. */
  ner_threshold?: number;
  /** Enable NER regular expressions (experimental). */
  enable_regexps?: boolean;
  /** GLiNER NER configuration. */
  gliner?: GlinerConfig;
  /** List of entity types to recognize. If unset, classification entity types are used. */
  ner_entities?: string[];
}

// ----- PiiReplacerConfig -----
/**
 * Configuration for PII replacer.

Defines how PII data should be detected and replaced in a dataset.
 */
export interface PiiReplacerConfig {
  /** Global configuration options. */
  globals?: Globals;
  /**
   * List of transformation steps to perform on input data.
   * @minItems 1
   * @maxItems 10
   */
  steps: StepDefinition[];
}

// ----- Row -----
/**
 * Rule matcher for selecting rows by name, condition, entity, or type.
 */
export interface Row {
  /** Row name. */
  name?: string | string[];
  /** Row condition match. */
  condition?: string;
  /** Foreach expression. */
  foreach?: string;
  /** Row value definition. */
  value?: string;
  /** Row entity match. */
  entity?: string | string[];
  /** Row type match. */
  type?: string | string[];
  /** Row fallback value. */
  fallback_value?: string;
  /** Rule description for human consumption. */
  description?: string;
}

// ----- RowActions -----
/**
 * Container for row drop and update operations.
 */
export interface RowActions {
  /** Rows to drop. */
  drop?: Row[];
  /** Rows to update. */
  update?: Row[];
}

// ----- StepDefinition -----
/**
 * Single transformation step with optional variables, column actions, and row actions.
 */
export interface StepDefinition {
  /** Variable names and templates. */
  vars?: StepDefinitionVars;
  /** Columns transform configuration. */
  columns?: ColumnActions;
  /** Rows transform configurations. */
  rows?: RowActions;
}

// ----- StepDefinitionVars -----
/**
 * Variable names and templates.
 */
export type StepDefinitionVars = { [key: string]: string | { [key: string]: unknown } | unknown[] };

// ----- TimeSeriesParameters -----
/**
 * Configuration for time-series mode in the Safe Synthesizer pipeline.

Controls whether a dataset is treated as time-series data, including
timestamp column selection, interval inference, and format validation.
The time-series pipeline is currently experimental.
 */
export interface TimeSeriesParameters {
  /** Whether to treat the dataset as time series. When enabled, either ``timestamp_column`` or ``timestamp_interval_seconds`` is required. For grouped time series, ``group_training_examples_by`` needs to be set. */
  is_timeseries?: boolean;
  /** Name of the column containing timestamps used to order records when ``is_timeseries`` is ``True``. Required only when ``is_timeseries`` is ``True`` and ``timestamp_interval_seconds`` is not provided. */
  timestamp_column?: string;
  /** Interval in seconds between timestamps. If not provided, the timestamp column will be used to infer the interval. */
  timestamp_interval_seconds?: number;
  /** Format of the timestamp column. Accepts either: (1) Python strftime format codes for string timestamps (e.g., '%Y-%m-%d %H:%M:%S', '%m/%d/%Y'), or (2) 'elapsed_seconds' for numeric (int/float) timestamps representing seconds as an increasing counter (e.g., 0, 60, 120 for 1-minute intervals). If not provided, the format will be inferred from the data. */
  timestamp_format?: string;
  /** Start timestamp. If not provided, the first timestamp in the timestamp column will be used. */
  start_timestamp?: string | number;
  /** Stop timestamp. If not provided, the last timestamp in the timestamp column will be used. */
  stop_timestamp?: string | number;
}

// ----- TrainingHyperparams -----
/**
 * Hyperparameters that control the training process behavior.

This class contains all the fine-tuning hyperparameters that control how the model
learns, including learning rates, batch sizes, LoRA configuration, and optimization
settings. These parameters directly affect training performance and quality.
 */
export interface TrainingHyperparams {
  /** Number of records the model will see during training. This parameter is a proxy for training time. For example, if its value is the same size as the input dataset, this is like training for a single epoch. If its value is larger, this is like training for multiple (possibly fractional) epochs. If its value is smaller, this is like training for a fraction of an epoch. Supports 'auto' where a reasonable value is chosen based on other config params and data. */
  num_input_records_to_sample?: 'auto' | number;
  /** The batch size per device for training. Must be >= 1. */
  batch_size?: number;
  /** Number of update steps to accumulate the gradients for, before performing a backward/update pass. This technique increases the effective batch size that will fit into GPU memory. Must be >= 1. */
  gradient_accumulation_steps?: number;
  /** The weight decay to apply to all layers except all bias and LayerNorm weights in the AdamW optimizer. Must be in (0, 1). */
  weight_decay?: number;
  /** Ratio of total training steps used for a linear warmup from 0 to the learning rate. Must be > 0. */
  warmup_ratio?: number;
  /** The scheduler type to use. See the HuggingFace documentation of ``SchedulerType`` for all possible values. */
  lr_scheduler?: string;
  /** The initial learning rate for `AdamW` optimizer. Must be in (0, 1). Setting to 'auto' uses a model-specific default if one exists. */
  learning_rate?: 'auto' | number;
  /** The rank of the LoRA update matrices. Lower rank results in smaller update matrices with fewer trainable parameters. Must be > 0. */
  lora_r?: number;
  /** The ratio of the LoRA scaling factor (alpha) to the LoRA rank. Empirically, this parameter works well when set to 0.5, 1, or 2. Must be in [0.5, 3]. */
  lora_alpha_over_r?: number;
  /** The list of transformer modules to apply LoRA to. Possible modules: 'q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'. */
  lora_target_modules?: string[];
  /** Whether to use Unsloth for optimized training. */
  use_unsloth?: 'auto' | boolean;
  /** Scale the base LLM's context length by this factor using RoPE scaling. Must be >= 1 or 'auto'. */
  rope_scaling_factor?: 'auto' | number;
  /** The fraction of the training data used for validation. Must be in [0, 1]. If set to 0, no validation will be performed. If set larger than 0, validation loss will be computed and reported throughout training. */
  validation_ratio?: number;
  /** The number of steps between validation checks for the HF Trainer arguments. Must be > 0. */
  validation_steps?: number;
  /** Pretrained model to use for fine-tuning. Defaults to SmolLM3. May be a Hugging Face model ID (loaded from the Hugging Face Hub or cache) or a local path. See security note in docs before using untrusted sources. */
  pretrained_model?: string;
  /** Whether to quantize the model during training. This can reduce memory usage and potentially speed up training, but may also impact model accuracy. */
  quantize_model?: boolean;
  /** The number of bits to use for quantization if ``quantize_model`` is ``True``. Accepts 8 or 4. */
  quantization_bits?: TrainingHyperparamsQuantizationBits;
  /** The PEFT (Parameter-Efficient Fine-Tuning) implementation to use. Options: 'lora' for Low-Rank Adaptation, 'QLORA' for Quantized LoRA. */
  peft_implementation?: string;
  /** The fraction of the total VRAM to use for training. Modify this to allow longer sequences. Must be in [0, 1]. */
  max_vram_fraction?: number;
  /** The attention implementation to use for model loading. Default uses Flash Attention 3 via the HuggingFace Kernels Hub (requires the 'kernels' pip package; falls back to 'sdpa' if the 'kernels' package is not installed). Other common values: 'flash_attention_2' (requires flash-attn pip package), 'sdpa' (PyTorch scaled dot product attention), 'eager' (standard PyTorch). Custom HuggingFace Kernels Hub paths (e.g. 'kernels-community/flash-attn2') are also supported. */
  attn_implementation?: string;
}

// ----- TrainingHyperparamsQuantizationBits -----
/**
 * The number of bits to use for quantization if ``quantize_model`` is ``True``. Accepts 8 or 4.
 */
export type TrainingHyperparamsQuantizationBits =
  (typeof TrainingHyperparamsQuantizationBits)[keyof typeof TrainingHyperparamsQuantizationBits];

export const TrainingHyperparamsQuantizationBits = {
  NUMBER_4: 4,
  NUMBER_8: 8,
} as const;

// ----- ValidationParameters -----
/**
 * Configuration for record and sequence validation.

These parameters control the validation and automatic fixes when going
from LLM output to tabular data.
 */
export interface ValidationParameters {
  /** Whether to accept completions without both beginning and end of sequence delineators as a single sequence. */
  group_by_accept_no_delineator?: boolean;
  /** Whether to ignore invalid records in a sequence and proceed with the valid records. */
  group_by_ignore_invalid_records?: boolean;
  /** Whether to automatically fix non-unique group-by values in a sequence by using the first unique value for all records. */
  group_by_fix_non_unique_value?: boolean;
  /** Whether to automatically fix unordered records in a sequence by sorting the records. */
  group_by_fix_unordered_records?: boolean;
}
