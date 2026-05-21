// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// TEMP: SafeSynthesizer zod schemas inlined while the safe-synthesizer SDK is being rebuilt.
// Source: @nemo/sdk/generated/platform/zod/safe-synthesizer.ts (verbatim copy).
// Restore SDK imports once the SDK regenerates with safe-synthesizer support.

/* eslint-disable */
// Verbatim copy of generated code; eslint suppressed (typecheck still runs).

import * as zod from 'zod';

/**
 * @summary Create Job
 */
export const SafeSynthesizerCreateJobParams = zod.object({
  workspace: zod.string(),
});

export const safeSynthesizerCreateJobBodySpecConfigOneDataOneMaxSequencesPerExampleDefault = `auto`;
export const safeSynthesizerCreateJobBodySpecConfigOneDataOneHoldoutDefault = 0.05;
export const safeSynthesizerCreateJobBodySpecConfigOneDataOneMaxHoldoutDefault = 2000;
export const safeSynthesizerCreateJobBodySpecConfigOneEvaluationOneMiaEnabledDefault = true;
export const safeSynthesizerCreateJobBodySpecConfigOneEvaluationOneAiaEnabledDefault = true;
export const safeSynthesizerCreateJobBodySpecConfigOneEvaluationOneSqsReportColumnsDefault = 250;
export const safeSynthesizerCreateJobBodySpecConfigOneEvaluationOneSqsReportRowsDefault = 5000;
export const safeSynthesizerCreateJobBodySpecConfigOneEvaluationOneEnabledDefault = true;
export const safeSynthesizerCreateJobBodySpecConfigOneEvaluationOneQuasiIdentifierCountDefault = 3;
export const safeSynthesizerCreateJobBodySpecConfigOneEvaluationOnePiiReplayEnabledDefault = true;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneNumInputRecordsToSampleDefault = `auto`;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneBatchSizeDefault = 1;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneGradientAccumulationStepsDefault = 8;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneWeightDecayDefault = 0.01;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneWarmupRatioDefault = 0.05;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneLrSchedulerDefault = `cosine`;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneLearningRateDefault = `auto`;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneLoraRDefault = 32;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneLoraAlphaOverRDefault = 1;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneLoraTargetModulesDefault = [
  `q_proj`,
  `k_proj`,
  `v_proj`,
  `o_proj`,
];
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneUseUnslothDefault = `auto`;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneRopeScalingFactorDefault = `auto`;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneValidationRatioDefault = 0;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneValidationStepsDefault = 15;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOnePretrainedModelDefault = `HuggingFaceTB/SmolLM3-3B`;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneQuantizeModelDefault = false;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneQuantizationBitsDefault = 8;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOnePeftImplementationDefault = `QLORA`;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneMaxVramFractionDefault = 0.8;
export const safeSynthesizerCreateJobBodySpecConfigOneTrainingOneAttnImplementationDefault = `kernels-community/vllm-flash-attn3`;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOneNumRecordsDefault = 1000;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOneTemperatureDefault = 0.9;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOneRepetitionPenaltyDefault = 1;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOneTopPDefault = 1;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOnePatienceDefault = 3;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOneInvalidFractionThresholdDefault = 0.8;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOneUseStructuredGenerationDefault = false;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOneStructuredGenerationBackendDefault = `auto`;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOneStructuredGenerationSchemaMethodDefault = `regex`;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOneStructuredGenerationUseSingleSequenceDefault = false;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOneEnforceTimeseriesFidelityDefault = false;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOneValidationOneGroupByAcceptNoDelineatorDefault = false;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOneValidationOneGroupByIgnoreInvalidRecordsDefault = false;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOneValidationOneGroupByFixNonUniqueValueDefault = false;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOneValidationOneGroupByFixUnorderedRecordsDefault = false;
export const safeSynthesizerCreateJobBodySpecConfigOneGenerationOneAttentionBackendDefault = `auto`;
export const safeSynthesizerCreateJobBodySpecConfigOnePrivacyOneDpEnabledDefault = false;
export const safeSynthesizerCreateJobBodySpecConfigOnePrivacyOneEpsilonDefault = 8;
export const safeSynthesizerCreateJobBodySpecConfigOnePrivacyOneDeltaDefault = `auto`;
export const safeSynthesizerCreateJobBodySpecConfigOnePrivacyOnePerSampleMaxGradNormDefault = 1;
export const safeSynthesizerCreateJobBodySpecConfigOneTimeSeriesOneIsTimeseriesDefault = false;
export const safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneClassifyOneNumSamplesDefault = 3;
export const safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneClassifyDefault = {
  num_samples: 3,
};
export const safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneNerThresholdDefault = 0.3;
export const safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneEnableRegexpsDefault = false;
export const safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableGlinerDefault = true;
export const safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableBatchModeDefault = true;
export const safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneBatchSizeDefault = 8;
export const safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneChunkLengthDefault = 512;
export const safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneGlinerModelDefault = `nvidia/gliner-PII`;
export const safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerDefault = {
  enable_gliner: true,
  enable_batch_mode: true,
  batch_size: 8,
  chunk_length: 512,
  gliner_model: 'nvidia/gliner-PII',
};
export const safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerDefault = {
  ner_threshold: 0.3,
  enable_regexps: false,
};
export const safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneStepsMax = 10;

export const safeSynthesizerCreateJobBodySpecEnableSynthesisDefault = true;

export const SafeSynthesizerCreateJobBody = zod.object({
  name: zod.string().optional(),
  description: zod.string().optional(),
  project: zod.string().optional(),
  spec: zod
    .object({
      data_source: zod.string().describe('The data source for the job.'),
      config: zod
        .object({
          data: zod
            .object({
              group_training_examples_by: zod
                .string()
                .optional()
                .describe(
                  'Column to group training examples by. This is useful when you want the model to learn inter-record correlations for a given grouping of records.'
                ),
              order_training_examples_by: zod
                .string()
                .optional()
                .describe(
                  'Column to order training examples by. This is useful when you want the model to learn sequential relationships for a given ordering of records. If you provide this parameter, you must also provide ``group_training_examples_by``.'
                ),
              max_sequences_per_example: zod
                .union([zod.literal('auto'), zod.number()])
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneDataOneMaxSequencesPerExampleDefault
                )
                .describe(
                  "If specified, adds at most this number of sequences per example. Supports 'auto' where a value of 1 is chosen if differential privacy is enabled, and 10 otherwise. If not specified or set to 'auto', fills up context. Required for DP to limit contribution of each example."
                ),
              holdout: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOneDataOneHoldoutDefault)
                .describe(
                  'Amount of records to hold out for evaluation. If this is a float between 0 and 1, that ratio of records is held out. If an integer greater than 1, that number of records is held out. If the value is equal to zero, no holdout will be performed. Must be >= 0.'
                ),
              max_holdout: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOneDataOneMaxHoldoutDefault)
                .describe(
                  'Maximum number of records to hold out. Overrides any behavior set by ``holdout``. Must be >= 0.'
                ),
              random_state: zod
                .number()
                .optional()
                .describe('Random state for holdout split to ensure reproducibility.'),
            })
            .describe(
              'Configuration for grouping, ordering, and splitting input data for training and evaluation.'
            )
            .optional()
            .describe(
              'Configuration controlling how input data is grouped and split for training and evaluation.'
            ),
          evaluation: zod
            .object({
              mia_enabled: zod
                .boolean()
                .default(safeSynthesizerCreateJobBodySpecConfigOneEvaluationOneMiaEnabledDefault)
                .describe('Enable membership inference attack evaluation for privacy assessment.'),
              aia_enabled: zod
                .boolean()
                .default(safeSynthesizerCreateJobBodySpecConfigOneEvaluationOneAiaEnabledDefault)
                .describe('Enable attribute inference attack evaluation for privacy assessment.'),
              sqs_report_columns: zod
                .number()
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneEvaluationOneSqsReportColumnsDefault
                )
                .describe('Number of columns to include in statistical quality reports.'),
              sqs_report_rows: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOneEvaluationOneSqsReportRowsDefault)
                .describe('Number of rows to include in statistical quality reports.'),
              mandatory_columns: zod
                .number()
                .optional()
                .describe('Number of mandatory columns that must be used in evaluation.'),
              enabled: zod
                .boolean()
                .default(safeSynthesizerCreateJobBodySpecConfigOneEvaluationOneEnabledDefault)
                .describe('Enable or disable evaluation.'),
              quasi_identifier_count: zod
                .number()
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneEvaluationOneQuasiIdentifierCountDefault
                )
                .describe('Number of quasi-identifiers to sample for privacy attacks.'),
              pii_replay_enabled: zod
                .boolean()
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneEvaluationOnePiiReplayEnabledDefault
                )
                .describe('Enable PII Replay detection.'),
              pii_replay_entities: zod
                .array(zod.string())
                .optional()
                .describe(
                  'List of entities for PII Replay. If not provided, default entities will be used.'
                ),
              pii_replay_columns: zod
                .array(zod.string())
                .optional()
                .describe(
                  'List of columns for PII Replay. If not provided, only entities will be used.'
                ),
            })
            .describe(
              'Configuration for evaluating synthetic data quality and privacy.\n\nThis class controls which evaluation metrics are computed and how they are configured.\nIt includes privacy attack evaluations, statistical quality metrics, and downstream\nmachine learning performance assessments.'
            )
            .optional()
            .describe('Parameters for evaluating the quality of generated synthetic data.'),
          training: zod
            .object({
              num_input_records_to_sample: zod
                .union([zod.literal('auto'), zod.number()])
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneTrainingOneNumInputRecordsToSampleDefault
                )
                .describe(
                  "Number of records the model will see during training. This parameter is a proxy for training time. For example, if its value is the same size as the input dataset, this is like training for a single epoch. If its value is larger, this is like training for multiple (possibly fractional) epochs. If its value is smaller, this is like training for a fraction of an epoch. Supports 'auto' where a reasonable value is chosen based on other config params and data."
                ),
              batch_size: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOneTrainingOneBatchSizeDefault)
                .describe('The batch size per device for training. Must be >= 1.'),
              gradient_accumulation_steps: zod
                .number()
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneTrainingOneGradientAccumulationStepsDefault
                )
                .describe(
                  'Number of update steps to accumulate the gradients for, before performing a backward\/update pass. This technique increases the effective batch size that will fit into GPU memory. Must be >= 1.'
                ),
              weight_decay: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOneTrainingOneWeightDecayDefault)
                .describe(
                  'The weight decay to apply to all layers except all bias and LayerNorm weights in the AdamW optimizer. Must be in (0, 1).'
                ),
              warmup_ratio: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOneTrainingOneWarmupRatioDefault)
                .describe(
                  'Ratio of total training steps used for a linear warmup from 0 to the learning rate. Must be > 0.'
                ),
              lr_scheduler: zod
                .string()
                .default(safeSynthesizerCreateJobBodySpecConfigOneTrainingOneLrSchedulerDefault)
                .describe(
                  'The scheduler type to use. See the HuggingFace documentation of ``SchedulerType`` for all possible values.'
                ),
              learning_rate: zod
                .union([zod.literal('auto'), zod.number()])
                .default(safeSynthesizerCreateJobBodySpecConfigOneTrainingOneLearningRateDefault)
                .describe(
                  "The initial learning rate for `AdamW` optimizer. Must be in (0, 1). Setting to 'auto' uses a model-specific default if one exists."
                ),
              lora_r: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOneTrainingOneLoraRDefault)
                .describe(
                  'The rank of the LoRA update matrices. Lower rank results in smaller update matrices with fewer trainable parameters. Must be > 0.'
                ),
              lora_alpha_over_r: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOneTrainingOneLoraAlphaOverRDefault)
                .describe(
                  'The ratio of the LoRA scaling factor (alpha) to the LoRA rank. Empirically, this parameter works well when set to 0.5, 1, or 2. Must be in [0.5, 3].'
                ),
              lora_target_modules: zod
                .array(zod.string())
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneTrainingOneLoraTargetModulesDefault
                )
                .describe(
                  "The list of transformer modules to apply LoRA to. Possible modules: 'q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'."
                ),
              use_unsloth: zod
                .union([zod.literal('auto'), zod.boolean()])
                .default(safeSynthesizerCreateJobBodySpecConfigOneTrainingOneUseUnslothDefault)
                .describe('Whether to use Unsloth for optimized training.'),
              rope_scaling_factor: zod
                .union([zod.literal('auto'), zod.number()])
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneTrainingOneRopeScalingFactorDefault
                )
                .describe(
                  "Scale the base LLM's context length by this factor using RoPE scaling. Must be >= 1 or 'auto'."
                ),
              validation_ratio: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOneTrainingOneValidationRatioDefault)
                .describe(
                  'The fraction of the training data used for validation. Must be in [0, 1]. If set to 0, no validation will be performed. If set larger than 0, validation loss will be computed and reported throughout training.'
                ),
              validation_steps: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOneTrainingOneValidationStepsDefault)
                .describe(
                  'The number of steps between validation checks for the HF Trainer arguments. Must be > 0.'
                ),
              pretrained_model: zod
                .string()
                .default(safeSynthesizerCreateJobBodySpecConfigOneTrainingOnePretrainedModelDefault)
                .describe(
                  'Pretrained model to use for fine-tuning. Defaults to SmolLM3. May be a Hugging Face model ID (loaded from the Hugging Face Hub or cache) or a local path. See security note in docs before using untrusted sources.'
                ),
              quantize_model: zod
                .boolean()
                .default(safeSynthesizerCreateJobBodySpecConfigOneTrainingOneQuantizeModelDefault)
                .describe(
                  'Whether to quantize the model during training. This can reduce memory usage and potentially speed up training, but may also impact model accuracy.'
                ),
              quantization_bits: zod
                .union([zod.literal(4), zod.literal(8)])
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneTrainingOneQuantizationBitsDefault
                )
                .describe(
                  'The number of bits to use for quantization if ``quantize_model`` is ``True``. Accepts 8 or 4.'
                ),
              peft_implementation: zod
                .string()
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneTrainingOnePeftImplementationDefault
                )
                .describe(
                  "The PEFT (Parameter-Efficient Fine-Tuning) implementation to use. Options: 'lora' for Low-Rank Adaptation, 'QLORA' for Quantized LoRA."
                ),
              max_vram_fraction: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOneTrainingOneMaxVramFractionDefault)
                .describe(
                  'The fraction of the total VRAM to use for training. Modify this to allow longer sequences. Must be in [0, 1].'
                ),
              attn_implementation: zod
                .string()
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneTrainingOneAttnImplementationDefault
                )
                .describe(
                  "The attention implementation to use for model loading. Default uses Flash Attention 3 via the HuggingFace Kernels Hub (requires the 'kernels' pip package; falls back to 'sdpa' if the 'kernels' package is not installed). Other common values: 'flash_attention_2' (requires flash-attn pip package), 'sdpa' (PyTorch scaled dot product attention), 'eager' (standard PyTorch). Custom HuggingFace Kernels Hub paths (e.g. 'kernels-community\/flash-attn2') are also supported."
                ),
            })
            .describe(
              'Hyperparameters that control the training process behavior.\n\nThis class contains all the fine-tuning hyperparameters that control how the model\nlearns, including learning rates, batch sizes, LoRA configuration, and optimization\nsettings. These parameters directly affect training performance and quality.'
            )
            .optional()
            .describe(
              'Hyperparameters for model training such as learning rate, batch size, and LoRA adapter settings.'
            ),
          generation: zod
            .object({
              num_records: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOneGenerationOneNumRecordsDefault)
                .describe('Number of records to generate.'),
              temperature: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOneGenerationOneTemperatureDefault)
                .describe(
                  'Sampling temperature for controlling randomness (higher = more random).'
                ),
              repetition_penalty: zod
                .number()
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneGenerationOneRepetitionPenaltyDefault
                )
                .describe(
                  'The value used to control the likelihood of the model repeating the same token. Must be > 0.'
                ),
              top_p: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOneGenerationOneTopPDefault)
                .describe('Nucleus sampling probability for token selection. Must be in (0, 1].'),
              patience: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOneGenerationOnePatienceDefault)
                .describe(
                  'Number of consecutive generations where the ``invalid_fraction_threshold`` is reached before stopping generation. Must be >= 1.'
                ),
              invalid_fraction_threshold: zod
                .number()
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneGenerationOneInvalidFractionThresholdDefault
                )
                .describe(
                  'The fraction of invalid records that will stop generation after the ``patience`` limit is reached. Must be in [0, 1].'
                ),
              use_structured_generation: zod
                .boolean()
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneGenerationOneUseStructuredGenerationDefault
                )
                .describe('Whether to use structured generation for better format control.'),
              structured_generation_backend: zod
                .enum(['auto', 'xgrammar', 'guidance', 'outlines', 'lm-format-enforcer'])
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneGenerationOneStructuredGenerationBackendDefault
                )
                .describe(
                  "The backend used by vLLM when ``use_structured_generation`` is ``True``. Supported backends: 'outlines', 'guidance', 'xgrammar', 'lm-format-enforcer'. 'auto' will allow vLLM to choose the backend."
                ),
              structured_generation_schema_method: zod
                .enum(['regex', 'json_schema'])
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneGenerationOneStructuredGenerationSchemaMethodDefault
                )
                .describe(
                  "The method used to generate the schema from your dataset and pass it to the generation backend. 'regex' uses a custom regex construction method that tends to be more comprehensive than 'json_schema' at the cost of speed."
                ),
              structured_generation_use_single_sequence: zod
                .boolean()
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneGenerationOneStructuredGenerationUseSingleSequenceDefault
                )
                .describe(
                  'Whether to use a regex that matches exactly one sequence or record if ``max_sequences_per_example`` is 1.'
                ),
              enforce_timeseries_fidelity: zod
                .boolean()
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneGenerationOneEnforceTimeseriesFidelityDefault
                )
                .describe(
                  'Enforce time-series fidelity by enforcing order, intervals, start and end times of the records.'
                ),
              validation: zod
                .object({
                  group_by_accept_no_delineator: zod
                    .boolean()
                    .default(
                      safeSynthesizerCreateJobBodySpecConfigOneGenerationOneValidationOneGroupByAcceptNoDelineatorDefault
                    )
                    .describe(
                      'Whether to accept completions without both beginning and end of sequence delineators as a single sequence.'
                    ),
                  group_by_ignore_invalid_records: zod
                    .boolean()
                    .default(
                      safeSynthesizerCreateJobBodySpecConfigOneGenerationOneValidationOneGroupByIgnoreInvalidRecordsDefault
                    )
                    .describe(
                      'Whether to ignore invalid records in a sequence and proceed with the valid records.'
                    ),
                  group_by_fix_non_unique_value: zod
                    .boolean()
                    .default(
                      safeSynthesizerCreateJobBodySpecConfigOneGenerationOneValidationOneGroupByFixNonUniqueValueDefault
                    )
                    .describe(
                      'Whether to automatically fix non-unique group-by values in a sequence by using the first unique value for all records.'
                    ),
                  group_by_fix_unordered_records: zod
                    .boolean()
                    .default(
                      safeSynthesizerCreateJobBodySpecConfigOneGenerationOneValidationOneGroupByFixUnorderedRecordsDefault
                    )
                    .describe(
                      'Whether to automatically fix unordered records in a sequence by sorting the records.'
                    ),
                })
                .describe(
                  'Configuration for record and sequence validation.\n\nThese parameters control the validation and automatic fixes when going\nfrom LLM output to tabular data.'
                )
                .optional()
                .describe(
                  'Validation parameters controlling validation logic and automatic fixes when parsing LLM output and converting to tabular data.'
                ),
              attention_backend: zod
                .string()
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOneGenerationOneAttentionBackendDefault
                )
                .describe(
                  "The attention backend for the vLLM engine. Common values: 'FLASHINFER', 'FLASH_ATTN', 'TRITON_ATTN', 'FLEX_ATTENTION'. If ``None`` or 'auto', vLLM will auto-select the best available backend."
                ),
            })
            .describe(
              'Configuration parameters for synthetic data generation.\n\nThese parameters control how synthetic data is generated after the model is trained.\nThey affect the quality, diversity, and validity of the generated synthetic records.'
            )
            .optional()
            .describe(
              'Parameters governing synthetic data generation including temperature, top-p, and number of records to produce.'
            ),
          privacy: zod
            .object({
              dp_enabled: zod
                .boolean()
                .default(safeSynthesizerCreateJobBodySpecConfigOnePrivacyOneDpEnabledDefault)
                .describe('Enable differentially-private training with DP-SGD.'),
              epsilon: zod
                .number()
                .default(safeSynthesizerCreateJobBodySpecConfigOnePrivacyOneEpsilonDefault)
                .describe(
                  'Target privacy budget -- lower values provide stronger privacy. Must be > 0.'
                ),
              delta: zod
                .union([zod.literal('auto'), zod.number()])
                .default(safeSynthesizerCreateJobBodySpecConfigOnePrivacyOneDeltaDefault)
                .describe(
                  "Probability of accidentally leaking information. Should be much smaller than 1\/n where n is the number of training records. Setting to 'auto' uses delta of 1\/n^1.2. Must be in [0, 1) or 'auto'."
                ),
              per_sample_max_grad_norm: zod
                .number()
                .default(
                  safeSynthesizerCreateJobBodySpecConfigOnePrivacyOnePerSampleMaxGradNormDefault
                )
                .describe('Maximum L2 norm for per-sample gradient clipping. Must be > 0.'),
            })
            .describe(
              'Hyperparameters for differential privacy during training.\n\nThese parameters configure differential privacy (DP) training using DP-SGD algorithm.\nWhen enabled, they provide formal privacy guarantees by adding calibrated noise\nduring training.'
            )
            .optional()
            .describe(
              'Differential-privacy hyperparameters. When ``None``, differential privacy is disabled entirely.'
            ),
          time_series: zod
            .object({
              is_timeseries: zod
                .boolean()
                .default(safeSynthesizerCreateJobBodySpecConfigOneTimeSeriesOneIsTimeseriesDefault)
                .describe(
                  'Whether to treat the dataset as time series. When enabled, either ``timestamp_column`` or ``timestamp_interval_seconds`` is required. For grouped time series, ``group_training_examples_by`` needs to be set.'
                ),
              timestamp_column: zod
                .string()
                .optional()
                .describe(
                  'Name of the column containing timestamps used to order records when ``is_timeseries`` is ``True``. Required only when ``is_timeseries`` is ``True`` and ``timestamp_interval_seconds`` is not provided.'
                ),
              timestamp_interval_seconds: zod
                .number()
                .optional()
                .describe(
                  'Interval in seconds between timestamps. If not provided, the timestamp column will be used to infer the interval.'
                ),
              timestamp_format: zod
                .string()
                .optional()
                .describe(
                  "Format of the timestamp column. Accepts either: (1) Python strftime format codes for string timestamps (e.g., '%Y-%m-%d %H:%M:%S', '%m\/%d\/%Y'), or (2) 'elapsed_seconds' for numeric (int\/float) timestamps representing seconds as an increasing counter (e.g., 0, 60, 120 for 1-minute intervals). If not provided, the format will be inferred from the data."
                ),
              start_timestamp: zod
                .union([zod.string(), zod.number()])
                .optional()
                .describe(
                  'Start timestamp. If not provided, the first timestamp in the timestamp column will be used.'
                ),
              stop_timestamp: zod
                .union([zod.string(), zod.number()])
                .optional()
                .describe(
                  'Stop timestamp. If not provided, the last timestamp in the timestamp column will be used.'
                ),
            })
            .describe(
              'Configuration for time-series mode in the Safe Synthesizer pipeline.\n\nControls whether a dataset is treated as time-series data, including\ntimestamp column selection, interval inference, and format validation.\nThe time-series pipeline is currently experimental.'
            )
            .optional()
            .describe(
              'Configuration for time-series mode. Time-series pipeline is currently experimental.'
            ),
          replace_pii: zod
            .object({
              globals: zod
                .object({
                  locales: zod.array(zod.string()).optional().describe('List of locales.'),
                  seed: zod.number().optional().describe('Optional random seed.'),
                  classify: zod
                    .object({
                      enable_classify: zod
                        .boolean()
                        .optional()
                        .describe('Enable column classification.'),
                      entities: zod
                        .array(zod.string())
                        .optional()
                        .describe('List of entity types to classify.'),
                      num_samples: zod
                        .number()
                        .default(
                          safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneClassifyOneNumSamplesDefault
                        )
                        .describe('Number of column values to sample for classification.'),
                      classify_model_provider: zod
                        .string()
                        .optional()
                        .describe(
                          'Name of the model provider in the Inference Gateway for column classification. The job compiler will resolve this to the appropriate endpoint URL.'
                        ),
                    })
                    .describe('Configuration for column classification using an LLM.')
                    .default(
                      safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneClassifyDefault
                    )
                    .describe('Column classification configuration.'),
                  ner: zod
                    .object({
                      ner_threshold: zod
                        .number()
                        .default(
                          safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneNerThresholdDefault
                        )
                        .describe('NER model threshold.'),
                      enable_regexps: zod
                        .boolean()
                        .default(
                          safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneEnableRegexpsDefault
                        )
                        .describe('Enable NER regular expressions (experimental).'),
                      gliner: zod
                        .object({
                          enable_gliner: zod
                            .boolean()
                            .default(
                              safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableGlinerDefault
                            )
                            .describe('Enable GLiNER NER module.'),
                          enable_batch_mode: zod
                            .boolean()
                            .default(
                              safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableBatchModeDefault
                            )
                            .describe('Enable GLiNER batch mode.'),
                          batch_size: zod
                            .number()
                            .default(
                              safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneBatchSizeDefault
                            )
                            .describe('GLiNER batch size.'),
                          chunk_length: zod
                            .number()
                            .default(
                              safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneChunkLengthDefault
                            )
                            .describe('GLiNER batch chunk length in characters.'),
                          gliner_model: zod
                            .string()
                            .default(
                              safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneGlinerModelDefault
                            )
                            .describe('GLiNER model name.'),
                        })
                        .describe('Configuration for the GLiNER named-entity recognition model.')
                        .default(
                          safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerDefault
                        )
                        .describe('GLiNER NER configuration.'),
                      ner_entities: zod
                        .array(zod.string())
                        .optional()
                        .describe(
                          'List of entity types to recognize. If unset, classification entity types are used.'
                        ),
                    })
                    .describe('Configuration for Named Entity Recognition.')
                    .default(
                      safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneGlobalsOneNerDefault
                    )
                    .describe('Named Entity Recognition configuration.'),
                  lock_columns: zod
                    .array(zod.string())
                    .optional()
                    .describe(
                      'List of columns to preserve as immutable across all transformations.'
                    ),
                })
                .describe(
                  'Global settings for the PII replacer including locales, seed, NER, and classification.'
                )
                .optional()
                .describe('Global configuration options.'),
              steps: zod
                .array(
                  zod
                    .object({
                      vars: zod
                        .record(
                          zod.string(),
                          zod.union([
                            zod.string(),
                            zod.record(zod.string(), zod.unknown()),
                            zod.array(zod.unknown()),
                          ])
                        )
                        .optional()
                        .describe('Variable names and templates.'),
                      columns: zod
                        .object({
                          add: zod
                            .array(
                              zod
                                .object({
                                  name: zod.string().optional().describe('Column name.'),
                                  position: zod
                                    .union([zod.number(), zod.array(zod.number())])
                                    .optional()
                                    .describe('Column position.'),
                                  condition: zod.string().optional().describe('Column condition.'),
                                  value: zod.string().optional().describe('Rename to value.'),
                                  entity: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column entity match.'),
                                  type: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column type match.'),
                                })
                                .describe(
                                  'Rule matcher for selecting columns by name, position, condition, entity, or type.'
                                )
                            )
                            .optional()
                            .describe('Columns to add.'),
                          drop: zod
                            .array(
                              zod
                                .object({
                                  name: zod.string().optional().describe('Column name.'),
                                  position: zod
                                    .union([zod.number(), zod.array(zod.number())])
                                    .optional()
                                    .describe('Column position.'),
                                  condition: zod.string().optional().describe('Column condition.'),
                                  value: zod.string().optional().describe('Rename to value.'),
                                  entity: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column entity match.'),
                                  type: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column type match.'),
                                })
                                .describe(
                                  'Rule matcher for selecting columns by name, position, condition, entity, or type.'
                                )
                            )
                            .optional()
                            .describe('Columns to drop.'),
                          rename: zod
                            .array(
                              zod
                                .object({
                                  name: zod.string().optional().describe('Column name.'),
                                  position: zod
                                    .union([zod.number(), zod.array(zod.number())])
                                    .optional()
                                    .describe('Column position.'),
                                  condition: zod.string().optional().describe('Column condition.'),
                                  value: zod.string().optional().describe('Rename to value.'),
                                  entity: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column entity match.'),
                                  type: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column type match.'),
                                })
                                .describe(
                                  'Rule matcher for selecting columns by name, position, condition, entity, or type.'
                                )
                            )
                            .optional()
                            .describe('Columns to rename.'),
                        })
                        .describe('Container for column add, drop, and rename operations.')
                        .optional()
                        .describe('Columns transform configuration.'),
                      rows: zod
                        .object({
                          drop: zod
                            .array(
                              zod
                                .object({
                                  name: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row name.'),
                                  condition: zod
                                    .string()
                                    .optional()
                                    .describe('Row condition match.'),
                                  foreach: zod.string().optional().describe('Foreach expression.'),
                                  value: zod.string().optional().describe('Row value definition.'),
                                  entity: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row entity match.'),
                                  type: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row type match.'),
                                  fallback_value: zod
                                    .string()
                                    .optional()
                                    .describe('Row fallback value.'),
                                  description: zod
                                    .string()
                                    .optional()
                                    .describe('Rule description for human consumption.'),
                                })
                                .describe(
                                  'Rule matcher for selecting rows by name, condition, entity, or type.'
                                )
                            )
                            .optional()
                            .describe('Rows to drop.'),
                          update: zod
                            .array(
                              zod
                                .object({
                                  name: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row name.'),
                                  condition: zod
                                    .string()
                                    .optional()
                                    .describe('Row condition match.'),
                                  foreach: zod.string().optional().describe('Foreach expression.'),
                                  value: zod.string().optional().describe('Row value definition.'),
                                  entity: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row entity match.'),
                                  type: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row type match.'),
                                  fallback_value: zod
                                    .string()
                                    .optional()
                                    .describe('Row fallback value.'),
                                  description: zod
                                    .string()
                                    .optional()
                                    .describe('Rule description for human consumption.'),
                                })
                                .describe(
                                  'Rule matcher for selecting rows by name, condition, entity, or type.'
                                )
                            )
                            .optional()
                            .describe('Rows to update.'),
                        })
                        .describe('Container for row drop and update operations.')
                        .optional()
                        .describe('Rows transform configurations.'),
                    })
                    .describe(
                      'Single transformation step with optional variables, column actions, and row actions.'
                    )
                )
                .min(1)
                .max(safeSynthesizerCreateJobBodySpecConfigOneReplacePiiOneStepsMax)
                .describe('List of transformation steps to perform on input data.'),
            })
            .describe(
              'Configuration for PII replacer.\n\nDefines how PII data should be detected and replaced in a dataset.'
            )
            .optional()
            .describe('PII replacement configuration. When ``None``, PII replacement is skipped.'),
        })
        .describe(
          'Main configuration class for the Safe Synthesizer pipeline.\n\nThis is the top-level configuration class that orchestrates all aspects of\nsynthetic data generation including training, generation, privacy, evaluation,\nand data handling. It provides validation to ensure parameter compatibility.'
        )
        .describe('The Safe Synthesizer parameters configuration.'),
      hf_token_secret: zod
        .string()
        .optional()
        .describe(
          'Name of platform secret containing the HuggingFace token. Must exist in the same workspace as the job.'
        ),
      enable_synthesis: zod
        .boolean()
        .default(safeSynthesizerCreateJobBodySpecEnableSynthesisDefault)
        .describe(
          'Whether to run LLM training and generation phases. When False the task only performs PII replacement and returns the processed data.'
        ),
    })
    .describe(
      'Configuration model for Safe Synthesizer jobs.\n\nUsed primarily internally to configure a run submitted to the NeMo Jobs\nMicroservice.'
    ),
  ownership: zod.record(zod.string(), zod.unknown()).optional(),
  custom_fields: zod.record(zod.string(), zod.unknown()).optional(),
});

/**
 * @summary List Jobs
 */
export const SafeSynthesizerListJobsParams = zod.object({
  workspace: zod.string(),
});

export const safeSynthesizerListJobsQueryPageDefault = 1;
export const safeSynthesizerListJobsQueryPageExclusiveMin = 0;

export const safeSynthesizerListJobsQueryPageSizeDefault = 10;
export const safeSynthesizerListJobsQueryPageSizeExclusiveMin = 0;

export const safeSynthesizerListJobsQuerySortDefault = `-created_at`;

export const SafeSynthesizerListJobsQueryParams = zod.object({
  page: zod
    .number()
    .gt(safeSynthesizerListJobsQueryPageExclusiveMin)
    .default(safeSynthesizerListJobsQueryPageDefault)
    .describe('Page number.'),
  page_size: zod
    .number()
    .gt(safeSynthesizerListJobsQueryPageSizeExclusiveMin)
    .default(safeSynthesizerListJobsQueryPageSizeDefault)
    .describe('Page size.'),
  sort: zod
    .enum(['created_at', '-created_at', 'updated_at', '-updated_at'])
    .default(safeSynthesizerListJobsQuerySortDefault)
    .describe(
      'The field to sort by. To sort in decreasing order, use `-` in front of the field name.'
    ),
  filter: zod
    .object({
      created_at: zod
        .object({
          $gte: zod
            .string()
            .optional()
            .describe('Filter for results greater than or equal to this datetime.'),
          $lte: zod
            .string()
            .optional()
            .describe('Filter for results less than or equal to this datetime.'),
        })
        .optional()
        .describe("Jobs created at 'gte' datetime or 'lte' datetime."),
      name: zod.string().optional().describe('Name of the job.'),
      workspace: zod.string().optional().describe('Workspace of the job.'),
      project: zod.string().optional().describe('Project containing the job.'),
      status: zod
        .enum([
          'created',
          'pending',
          'active',
          'cancelled',
          'cancelling',
          'error',
          'completed',
          'paused',
          'pausing',
          'resuming',
        ])
        .describe(
          'Enumeration of possible job statuses.\n\nThis enum represents the various states a job can be in during its lifecycle,\nfrom creation to a terminal state.'
        )
        .optional()
        .describe('The current status.'),
      updated_at: zod
        .object({
          $gte: zod
            .string()
            .optional()
            .describe('Filter for results greater than or equal to this datetime.'),
          $lte: zod
            .string()
            .optional()
            .describe('Filter for results less than or equal to this datetime.'),
        })
        .optional()
        .describe("Jobs updated at 'gte' datetime or 'lte' datetime."),
    })
    .optional()
    .describe('Filter jobs on various criteria.'),
});

export const safeSynthesizerListJobsResponseDataItemSpecConfigOneDataOneMaxSequencesPerExampleDefault = `auto`;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneDataOneHoldoutDefault = 0.05;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneDataOneMaxHoldoutDefault = 2000;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneEvaluationOneMiaEnabledDefault = true;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneEvaluationOneAiaEnabledDefault = true;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneEvaluationOneSqsReportColumnsDefault = 250;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneEvaluationOneSqsReportRowsDefault = 5000;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneEvaluationOneEnabledDefault = true;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneEvaluationOneQuasiIdentifierCountDefault = 3;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneEvaluationOnePiiReplayEnabledDefault = true;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneNumInputRecordsToSampleDefault = `auto`;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneBatchSizeDefault = 1;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneGradientAccumulationStepsDefault = 8;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneWeightDecayDefault = 0.01;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneWarmupRatioDefault = 0.05;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneLrSchedulerDefault = `cosine`;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneLearningRateDefault = `auto`;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneLoraRDefault = 32;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneLoraAlphaOverRDefault = 1;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneLoraTargetModulesDefault =
  [`q_proj`, `k_proj`, `v_proj`, `o_proj`];
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneUseUnslothDefault = `auto`;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneRopeScalingFactorDefault = `auto`;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneValidationRatioDefault = 0;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneValidationStepsDefault = 15;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOnePretrainedModelDefault = `HuggingFaceTB/SmolLM3-3B`;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneQuantizeModelDefault = false;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneQuantizationBitsDefault = 8;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOnePeftImplementationDefault = `QLORA`;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneMaxVramFractionDefault = 0.8;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneAttnImplementationDefault = `kernels-community/vllm-flash-attn3`;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneNumRecordsDefault = 1000;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneTemperatureDefault = 0.9;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneRepetitionPenaltyDefault = 1;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneTopPDefault = 1;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOnePatienceDefault = 3;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneInvalidFractionThresholdDefault = 0.8;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneUseStructuredGenerationDefault = false;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneStructuredGenerationBackendDefault = `auto`;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneStructuredGenerationSchemaMethodDefault = `regex`;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneStructuredGenerationUseSingleSequenceDefault = false;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneEnforceTimeseriesFidelityDefault = false;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneValidationOneGroupByAcceptNoDelineatorDefault = false;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneValidationOneGroupByIgnoreInvalidRecordsDefault = false;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneValidationOneGroupByFixNonUniqueValueDefault = false;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneValidationOneGroupByFixUnorderedRecordsDefault = false;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneAttentionBackendDefault = `auto`;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOnePrivacyOneDpEnabledDefault = false;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOnePrivacyOneEpsilonDefault = 8;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOnePrivacyOneDeltaDefault = `auto`;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOnePrivacyOnePerSampleMaxGradNormDefault = 1;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneTimeSeriesOneIsTimeseriesDefault = false;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneClassifyOneNumSamplesDefault = 3;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneClassifyDefault =
  { num_samples: 3 };
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneNerThresholdDefault = 0.3;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneEnableRegexpsDefault = false;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableGlinerDefault = true;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableBatchModeDefault = true;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneBatchSizeDefault = 8;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneChunkLengthDefault = 512;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneGlinerModelDefault = `nvidia/gliner-PII`;
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerDefault =
  {
    enable_gliner: true,
    enable_batch_mode: true,
    batch_size: 8,
    chunk_length: 512,
    gliner_model: 'nvidia/gliner-PII',
  };
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerDefault =
  { ner_threshold: 0.3, enable_regexps: false };
export const safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneStepsMax = 10;

export const safeSynthesizerListJobsResponseDataItemSpecEnableSynthesisDefault = true;

export const SafeSynthesizerListJobsResponse = zod.object({
  data: zod.array(
    zod.object({
      id: zod.string().optional(),
      name: zod.string(),
      description: zod.string().optional(),
      project: zod.string().optional(),
      workspace: zod.string().optional(),
      created_at: zod.string().optional(),
      updated_at: zod.string().optional(),
      spec: zod
        .object({
          data_source: zod.string().describe('The data source for the job.'),
          config: zod
            .object({
              data: zod
                .object({
                  group_training_examples_by: zod
                    .string()
                    .optional()
                    .describe(
                      'Column to group training examples by. This is useful when you want the model to learn inter-record correlations for a given grouping of records.'
                    ),
                  order_training_examples_by: zod
                    .string()
                    .optional()
                    .describe(
                      'Column to order training examples by. This is useful when you want the model to learn sequential relationships for a given ordering of records. If you provide this parameter, you must also provide ``group_training_examples_by``.'
                    ),
                  max_sequences_per_example: zod
                    .union([zod.literal('auto'), zod.number()])
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneDataOneMaxSequencesPerExampleDefault
                    )
                    .describe(
                      "If specified, adds at most this number of sequences per example. Supports 'auto' where a value of 1 is chosen if differential privacy is enabled, and 10 otherwise. If not specified or set to 'auto', fills up context. Required for DP to limit contribution of each example."
                    ),
                  holdout: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneDataOneHoldoutDefault
                    )
                    .describe(
                      'Amount of records to hold out for evaluation. If this is a float between 0 and 1, that ratio of records is held out. If an integer greater than 1, that number of records is held out. If the value is equal to zero, no holdout will be performed. Must be >= 0.'
                    ),
                  max_holdout: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneDataOneMaxHoldoutDefault
                    )
                    .describe(
                      'Maximum number of records to hold out. Overrides any behavior set by ``holdout``. Must be >= 0.'
                    ),
                  random_state: zod
                    .number()
                    .optional()
                    .describe('Random state for holdout split to ensure reproducibility.'),
                })
                .describe(
                  'Configuration for grouping, ordering, and splitting input data for training and evaluation.'
                )
                .optional()
                .describe(
                  'Configuration controlling how input data is grouped and split for training and evaluation.'
                ),
              evaluation: zod
                .object({
                  mia_enabled: zod
                    .boolean()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneEvaluationOneMiaEnabledDefault
                    )
                    .describe(
                      'Enable membership inference attack evaluation for privacy assessment.'
                    ),
                  aia_enabled: zod
                    .boolean()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneEvaluationOneAiaEnabledDefault
                    )
                    .describe(
                      'Enable attribute inference attack evaluation for privacy assessment.'
                    ),
                  sqs_report_columns: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneEvaluationOneSqsReportColumnsDefault
                    )
                    .describe('Number of columns to include in statistical quality reports.'),
                  sqs_report_rows: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneEvaluationOneSqsReportRowsDefault
                    )
                    .describe('Number of rows to include in statistical quality reports.'),
                  mandatory_columns: zod
                    .number()
                    .optional()
                    .describe('Number of mandatory columns that must be used in evaluation.'),
                  enabled: zod
                    .boolean()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneEvaluationOneEnabledDefault
                    )
                    .describe('Enable or disable evaluation.'),
                  quasi_identifier_count: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneEvaluationOneQuasiIdentifierCountDefault
                    )
                    .describe('Number of quasi-identifiers to sample for privacy attacks.'),
                  pii_replay_enabled: zod
                    .boolean()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneEvaluationOnePiiReplayEnabledDefault
                    )
                    .describe('Enable PII Replay detection.'),
                  pii_replay_entities: zod
                    .array(zod.string())
                    .optional()
                    .describe(
                      'List of entities for PII Replay. If not provided, default entities will be used.'
                    ),
                  pii_replay_columns: zod
                    .array(zod.string())
                    .optional()
                    .describe(
                      'List of columns for PII Replay. If not provided, only entities will be used.'
                    ),
                })
                .describe(
                  'Configuration for evaluating synthetic data quality and privacy.\n\nThis class controls which evaluation metrics are computed and how they are configured.\nIt includes privacy attack evaluations, statistical quality metrics, and downstream\nmachine learning performance assessments.'
                )
                .optional()
                .describe('Parameters for evaluating the quality of generated synthetic data.'),
              training: zod
                .object({
                  num_input_records_to_sample: zod
                    .union([zod.literal('auto'), zod.number()])
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneNumInputRecordsToSampleDefault
                    )
                    .describe(
                      "Number of records the model will see during training. This parameter is a proxy for training time. For example, if its value is the same size as the input dataset, this is like training for a single epoch. If its value is larger, this is like training for multiple (possibly fractional) epochs. If its value is smaller, this is like training for a fraction of an epoch. Supports 'auto' where a reasonable value is chosen based on other config params and data."
                    ),
                  batch_size: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneBatchSizeDefault
                    )
                    .describe('The batch size per device for training. Must be >= 1.'),
                  gradient_accumulation_steps: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneGradientAccumulationStepsDefault
                    )
                    .describe(
                      'Number of update steps to accumulate the gradients for, before performing a backward\/update pass. This technique increases the effective batch size that will fit into GPU memory. Must be >= 1.'
                    ),
                  weight_decay: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneWeightDecayDefault
                    )
                    .describe(
                      'The weight decay to apply to all layers except all bias and LayerNorm weights in the AdamW optimizer. Must be in (0, 1).'
                    ),
                  warmup_ratio: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneWarmupRatioDefault
                    )
                    .describe(
                      'Ratio of total training steps used for a linear warmup from 0 to the learning rate. Must be > 0.'
                    ),
                  lr_scheduler: zod
                    .string()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneLrSchedulerDefault
                    )
                    .describe(
                      'The scheduler type to use. See the HuggingFace documentation of ``SchedulerType`` for all possible values.'
                    ),
                  learning_rate: zod
                    .union([zod.literal('auto'), zod.number()])
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneLearningRateDefault
                    )
                    .describe(
                      "The initial learning rate for `AdamW` optimizer. Must be in (0, 1). Setting to 'auto' uses a model-specific default if one exists."
                    ),
                  lora_r: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneLoraRDefault
                    )
                    .describe(
                      'The rank of the LoRA update matrices. Lower rank results in smaller update matrices with fewer trainable parameters. Must be > 0.'
                    ),
                  lora_alpha_over_r: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneLoraAlphaOverRDefault
                    )
                    .describe(
                      'The ratio of the LoRA scaling factor (alpha) to the LoRA rank. Empirically, this parameter works well when set to 0.5, 1, or 2. Must be in [0.5, 3].'
                    ),
                  lora_target_modules: zod
                    .array(zod.string())
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneLoraTargetModulesDefault
                    )
                    .describe(
                      "The list of transformer modules to apply LoRA to. Possible modules: 'q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'."
                    ),
                  use_unsloth: zod
                    .union([zod.literal('auto'), zod.boolean()])
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneUseUnslothDefault
                    )
                    .describe('Whether to use Unsloth for optimized training.'),
                  rope_scaling_factor: zod
                    .union([zod.literal('auto'), zod.number()])
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneRopeScalingFactorDefault
                    )
                    .describe(
                      "Scale the base LLM's context length by this factor using RoPE scaling. Must be >= 1 or 'auto'."
                    ),
                  validation_ratio: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneValidationRatioDefault
                    )
                    .describe(
                      'The fraction of the training data used for validation. Must be in [0, 1]. If set to 0, no validation will be performed. If set larger than 0, validation loss will be computed and reported throughout training.'
                    ),
                  validation_steps: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneValidationStepsDefault
                    )
                    .describe(
                      'The number of steps between validation checks for the HF Trainer arguments. Must be > 0.'
                    ),
                  pretrained_model: zod
                    .string()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOnePretrainedModelDefault
                    )
                    .describe(
                      'Pretrained model to use for fine-tuning. Defaults to SmolLM3. May be a Hugging Face model ID (loaded from the Hugging Face Hub or cache) or a local path. See security note in docs before using untrusted sources.'
                    ),
                  quantize_model: zod
                    .boolean()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneQuantizeModelDefault
                    )
                    .describe(
                      'Whether to quantize the model during training. This can reduce memory usage and potentially speed up training, but may also impact model accuracy.'
                    ),
                  quantization_bits: zod
                    .union([zod.literal(4), zod.literal(8)])
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneQuantizationBitsDefault
                    )
                    .describe(
                      'The number of bits to use for quantization if ``quantize_model`` is ``True``. Accepts 8 or 4.'
                    ),
                  peft_implementation: zod
                    .string()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOnePeftImplementationDefault
                    )
                    .describe(
                      "The PEFT (Parameter-Efficient Fine-Tuning) implementation to use. Options: 'lora' for Low-Rank Adaptation, 'QLORA' for Quantized LoRA."
                    ),
                  max_vram_fraction: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneMaxVramFractionDefault
                    )
                    .describe(
                      'The fraction of the total VRAM to use for training. Modify this to allow longer sequences. Must be in [0, 1].'
                    ),
                  attn_implementation: zod
                    .string()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTrainingOneAttnImplementationDefault
                    )
                    .describe(
                      "The attention implementation to use for model loading. Default uses Flash Attention 3 via the HuggingFace Kernels Hub (requires the 'kernels' pip package; falls back to 'sdpa' if the 'kernels' package is not installed). Other common values: 'flash_attention_2' (requires flash-attn pip package), 'sdpa' (PyTorch scaled dot product attention), 'eager' (standard PyTorch). Custom HuggingFace Kernels Hub paths (e.g. 'kernels-community\/flash-attn2') are also supported."
                    ),
                })
                .describe(
                  'Hyperparameters that control the training process behavior.\n\nThis class contains all the fine-tuning hyperparameters that control how the model\nlearns, including learning rates, batch sizes, LoRA configuration, and optimization\nsettings. These parameters directly affect training performance and quality.'
                )
                .optional()
                .describe(
                  'Hyperparameters for model training such as learning rate, batch size, and LoRA adapter settings.'
                ),
              generation: zod
                .object({
                  num_records: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneNumRecordsDefault
                    )
                    .describe('Number of records to generate.'),
                  temperature: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneTemperatureDefault
                    )
                    .describe(
                      'Sampling temperature for controlling randomness (higher = more random).'
                    ),
                  repetition_penalty: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneRepetitionPenaltyDefault
                    )
                    .describe(
                      'The value used to control the likelihood of the model repeating the same token. Must be > 0.'
                    ),
                  top_p: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneTopPDefault
                    )
                    .describe(
                      'Nucleus sampling probability for token selection. Must be in (0, 1].'
                    ),
                  patience: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOnePatienceDefault
                    )
                    .describe(
                      'Number of consecutive generations where the ``invalid_fraction_threshold`` is reached before stopping generation. Must be >= 1.'
                    ),
                  invalid_fraction_threshold: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneInvalidFractionThresholdDefault
                    )
                    .describe(
                      'The fraction of invalid records that will stop generation after the ``patience`` limit is reached. Must be in [0, 1].'
                    ),
                  use_structured_generation: zod
                    .boolean()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneUseStructuredGenerationDefault
                    )
                    .describe('Whether to use structured generation for better format control.'),
                  structured_generation_backend: zod
                    .enum(['auto', 'xgrammar', 'guidance', 'outlines', 'lm-format-enforcer'])
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneStructuredGenerationBackendDefault
                    )
                    .describe(
                      "The backend used by vLLM when ``use_structured_generation`` is ``True``. Supported backends: 'outlines', 'guidance', 'xgrammar', 'lm-format-enforcer'. 'auto' will allow vLLM to choose the backend."
                    ),
                  structured_generation_schema_method: zod
                    .enum(['regex', 'json_schema'])
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneStructuredGenerationSchemaMethodDefault
                    )
                    .describe(
                      "The method used to generate the schema from your dataset and pass it to the generation backend. 'regex' uses a custom regex construction method that tends to be more comprehensive than 'json_schema' at the cost of speed."
                    ),
                  structured_generation_use_single_sequence: zod
                    .boolean()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneStructuredGenerationUseSingleSequenceDefault
                    )
                    .describe(
                      'Whether to use a regex that matches exactly one sequence or record if ``max_sequences_per_example`` is 1.'
                    ),
                  enforce_timeseries_fidelity: zod
                    .boolean()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneEnforceTimeseriesFidelityDefault
                    )
                    .describe(
                      'Enforce time-series fidelity by enforcing order, intervals, start and end times of the records.'
                    ),
                  validation: zod
                    .object({
                      group_by_accept_no_delineator: zod
                        .boolean()
                        .default(
                          safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneValidationOneGroupByAcceptNoDelineatorDefault
                        )
                        .describe(
                          'Whether to accept completions without both beginning and end of sequence delineators as a single sequence.'
                        ),
                      group_by_ignore_invalid_records: zod
                        .boolean()
                        .default(
                          safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneValidationOneGroupByIgnoreInvalidRecordsDefault
                        )
                        .describe(
                          'Whether to ignore invalid records in a sequence and proceed with the valid records.'
                        ),
                      group_by_fix_non_unique_value: zod
                        .boolean()
                        .default(
                          safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneValidationOneGroupByFixNonUniqueValueDefault
                        )
                        .describe(
                          'Whether to automatically fix non-unique group-by values in a sequence by using the first unique value for all records.'
                        ),
                      group_by_fix_unordered_records: zod
                        .boolean()
                        .default(
                          safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneValidationOneGroupByFixUnorderedRecordsDefault
                        )
                        .describe(
                          'Whether to automatically fix unordered records in a sequence by sorting the records.'
                        ),
                    })
                    .describe(
                      'Configuration for record and sequence validation.\n\nThese parameters control the validation and automatic fixes when going\nfrom LLM output to tabular data.'
                    )
                    .optional()
                    .describe(
                      'Validation parameters controlling validation logic and automatic fixes when parsing LLM output and converting to tabular data.'
                    ),
                  attention_backend: zod
                    .string()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneGenerationOneAttentionBackendDefault
                    )
                    .describe(
                      "The attention backend for the vLLM engine. Common values: 'FLASHINFER', 'FLASH_ATTN', 'TRITON_ATTN', 'FLEX_ATTENTION'. If ``None`` or 'auto', vLLM will auto-select the best available backend."
                    ),
                })
                .describe(
                  'Configuration parameters for synthetic data generation.\n\nThese parameters control how synthetic data is generated after the model is trained.\nThey affect the quality, diversity, and validity of the generated synthetic records.'
                )
                .optional()
                .describe(
                  'Parameters governing synthetic data generation including temperature, top-p, and number of records to produce.'
                ),
              privacy: zod
                .object({
                  dp_enabled: zod
                    .boolean()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOnePrivacyOneDpEnabledDefault
                    )
                    .describe('Enable differentially-private training with DP-SGD.'),
                  epsilon: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOnePrivacyOneEpsilonDefault
                    )
                    .describe(
                      'Target privacy budget -- lower values provide stronger privacy. Must be > 0.'
                    ),
                  delta: zod
                    .union([zod.literal('auto'), zod.number()])
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOnePrivacyOneDeltaDefault
                    )
                    .describe(
                      "Probability of accidentally leaking information. Should be much smaller than 1\/n where n is the number of training records. Setting to 'auto' uses delta of 1\/n^1.2. Must be in [0, 1) or 'auto'."
                    ),
                  per_sample_max_grad_norm: zod
                    .number()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOnePrivacyOnePerSampleMaxGradNormDefault
                    )
                    .describe('Maximum L2 norm for per-sample gradient clipping. Must be > 0.'),
                })
                .describe(
                  'Hyperparameters for differential privacy during training.\n\nThese parameters configure differential privacy (DP) training using DP-SGD algorithm.\nWhen enabled, they provide formal privacy guarantees by adding calibrated noise\nduring training.'
                )
                .optional()
                .describe(
                  'Differential-privacy hyperparameters. When ``None``, differential privacy is disabled entirely.'
                ),
              time_series: zod
                .object({
                  is_timeseries: zod
                    .boolean()
                    .default(
                      safeSynthesizerListJobsResponseDataItemSpecConfigOneTimeSeriesOneIsTimeseriesDefault
                    )
                    .describe(
                      'Whether to treat the dataset as time series. When enabled, either ``timestamp_column`` or ``timestamp_interval_seconds`` is required. For grouped time series, ``group_training_examples_by`` needs to be set.'
                    ),
                  timestamp_column: zod
                    .string()
                    .optional()
                    .describe(
                      'Name of the column containing timestamps used to order records when ``is_timeseries`` is ``True``. Required only when ``is_timeseries`` is ``True`` and ``timestamp_interval_seconds`` is not provided.'
                    ),
                  timestamp_interval_seconds: zod
                    .number()
                    .optional()
                    .describe(
                      'Interval in seconds between timestamps. If not provided, the timestamp column will be used to infer the interval.'
                    ),
                  timestamp_format: zod
                    .string()
                    .optional()
                    .describe(
                      "Format of the timestamp column. Accepts either: (1) Python strftime format codes for string timestamps (e.g., '%Y-%m-%d %H:%M:%S', '%m\/%d\/%Y'), or (2) 'elapsed_seconds' for numeric (int\/float) timestamps representing seconds as an increasing counter (e.g., 0, 60, 120 for 1-minute intervals). If not provided, the format will be inferred from the data."
                    ),
                  start_timestamp: zod
                    .union([zod.string(), zod.number()])
                    .optional()
                    .describe(
                      'Start timestamp. If not provided, the first timestamp in the timestamp column will be used.'
                    ),
                  stop_timestamp: zod
                    .union([zod.string(), zod.number()])
                    .optional()
                    .describe(
                      'Stop timestamp. If not provided, the last timestamp in the timestamp column will be used.'
                    ),
                })
                .describe(
                  'Configuration for time-series mode in the Safe Synthesizer pipeline.\n\nControls whether a dataset is treated as time-series data, including\ntimestamp column selection, interval inference, and format validation.\nThe time-series pipeline is currently experimental.'
                )
                .optional()
                .describe(
                  'Configuration for time-series mode. Time-series pipeline is currently experimental.'
                ),
              replace_pii: zod
                .object({
                  globals: zod
                    .object({
                      locales: zod.array(zod.string()).optional().describe('List of locales.'),
                      seed: zod.number().optional().describe('Optional random seed.'),
                      classify: zod
                        .object({
                          enable_classify: zod
                            .boolean()
                            .optional()
                            .describe('Enable column classification.'),
                          entities: zod
                            .array(zod.string())
                            .optional()
                            .describe('List of entity types to classify.'),
                          num_samples: zod
                            .number()
                            .default(
                              safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneClassifyOneNumSamplesDefault
                            )
                            .describe('Number of column values to sample for classification.'),
                          classify_model_provider: zod
                            .string()
                            .optional()
                            .describe(
                              'Name of the model provider in the Inference Gateway for column classification. The job compiler will resolve this to the appropriate endpoint URL.'
                            ),
                        })
                        .describe('Configuration for column classification using an LLM.')
                        .default(
                          safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneClassifyDefault
                        )
                        .describe('Column classification configuration.'),
                      ner: zod
                        .object({
                          ner_threshold: zod
                            .number()
                            .default(
                              safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneNerThresholdDefault
                            )
                            .describe('NER model threshold.'),
                          enable_regexps: zod
                            .boolean()
                            .default(
                              safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneEnableRegexpsDefault
                            )
                            .describe('Enable NER regular expressions (experimental).'),
                          gliner: zod
                            .object({
                              enable_gliner: zod
                                .boolean()
                                .default(
                                  safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableGlinerDefault
                                )
                                .describe('Enable GLiNER NER module.'),
                              enable_batch_mode: zod
                                .boolean()
                                .default(
                                  safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableBatchModeDefault
                                )
                                .describe('Enable GLiNER batch mode.'),
                              batch_size: zod
                                .number()
                                .default(
                                  safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneBatchSizeDefault
                                )
                                .describe('GLiNER batch size.'),
                              chunk_length: zod
                                .number()
                                .default(
                                  safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneChunkLengthDefault
                                )
                                .describe('GLiNER batch chunk length in characters.'),
                              gliner_model: zod
                                .string()
                                .default(
                                  safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneGlinerModelDefault
                                )
                                .describe('GLiNER model name.'),
                            })
                            .describe(
                              'Configuration for the GLiNER named-entity recognition model.'
                            )
                            .default(
                              safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerDefault
                            )
                            .describe('GLiNER NER configuration.'),
                          ner_entities: zod
                            .array(zod.string())
                            .optional()
                            .describe(
                              'List of entity types to recognize. If unset, classification entity types are used.'
                            ),
                        })
                        .describe('Configuration for Named Entity Recognition.')
                        .default(
                          safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneGlobalsOneNerDefault
                        )
                        .describe('Named Entity Recognition configuration.'),
                      lock_columns: zod
                        .array(zod.string())
                        .optional()
                        .describe(
                          'List of columns to preserve as immutable across all transformations.'
                        ),
                    })
                    .describe(
                      'Global settings for the PII replacer including locales, seed, NER, and classification.'
                    )
                    .optional()
                    .describe('Global configuration options.'),
                  steps: zod
                    .array(
                      zod
                        .object({
                          vars: zod
                            .record(
                              zod.string(),
                              zod.union([
                                zod.string(),
                                zod.record(zod.string(), zod.unknown()),
                                zod.array(zod.unknown()),
                              ])
                            )
                            .optional()
                            .describe('Variable names and templates.'),
                          columns: zod
                            .object({
                              add: zod
                                .array(
                                  zod
                                    .object({
                                      name: zod.string().optional().describe('Column name.'),
                                      position: zod
                                        .union([zod.number(), zod.array(zod.number())])
                                        .optional()
                                        .describe('Column position.'),
                                      condition: zod
                                        .string()
                                        .optional()
                                        .describe('Column condition.'),
                                      value: zod.string().optional().describe('Rename to value.'),
                                      entity: zod
                                        .union([zod.string(), zod.array(zod.string())])
                                        .optional()
                                        .describe('Column entity match.'),
                                      type: zod
                                        .union([zod.string(), zod.array(zod.string())])
                                        .optional()
                                        .describe('Column type match.'),
                                    })
                                    .describe(
                                      'Rule matcher for selecting columns by name, position, condition, entity, or type.'
                                    )
                                )
                                .optional()
                                .describe('Columns to add.'),
                              drop: zod
                                .array(
                                  zod
                                    .object({
                                      name: zod.string().optional().describe('Column name.'),
                                      position: zod
                                        .union([zod.number(), zod.array(zod.number())])
                                        .optional()
                                        .describe('Column position.'),
                                      condition: zod
                                        .string()
                                        .optional()
                                        .describe('Column condition.'),
                                      value: zod.string().optional().describe('Rename to value.'),
                                      entity: zod
                                        .union([zod.string(), zod.array(zod.string())])
                                        .optional()
                                        .describe('Column entity match.'),
                                      type: zod
                                        .union([zod.string(), zod.array(zod.string())])
                                        .optional()
                                        .describe('Column type match.'),
                                    })
                                    .describe(
                                      'Rule matcher for selecting columns by name, position, condition, entity, or type.'
                                    )
                                )
                                .optional()
                                .describe('Columns to drop.'),
                              rename: zod
                                .array(
                                  zod
                                    .object({
                                      name: zod.string().optional().describe('Column name.'),
                                      position: zod
                                        .union([zod.number(), zod.array(zod.number())])
                                        .optional()
                                        .describe('Column position.'),
                                      condition: zod
                                        .string()
                                        .optional()
                                        .describe('Column condition.'),
                                      value: zod.string().optional().describe('Rename to value.'),
                                      entity: zod
                                        .union([zod.string(), zod.array(zod.string())])
                                        .optional()
                                        .describe('Column entity match.'),
                                      type: zod
                                        .union([zod.string(), zod.array(zod.string())])
                                        .optional()
                                        .describe('Column type match.'),
                                    })
                                    .describe(
                                      'Rule matcher for selecting columns by name, position, condition, entity, or type.'
                                    )
                                )
                                .optional()
                                .describe('Columns to rename.'),
                            })
                            .describe('Container for column add, drop, and rename operations.')
                            .optional()
                            .describe('Columns transform configuration.'),
                          rows: zod
                            .object({
                              drop: zod
                                .array(
                                  zod
                                    .object({
                                      name: zod
                                        .union([zod.string(), zod.array(zod.string())])
                                        .optional()
                                        .describe('Row name.'),
                                      condition: zod
                                        .string()
                                        .optional()
                                        .describe('Row condition match.'),
                                      foreach: zod
                                        .string()
                                        .optional()
                                        .describe('Foreach expression.'),
                                      value: zod
                                        .string()
                                        .optional()
                                        .describe('Row value definition.'),
                                      entity: zod
                                        .union([zod.string(), zod.array(zod.string())])
                                        .optional()
                                        .describe('Row entity match.'),
                                      type: zod
                                        .union([zod.string(), zod.array(zod.string())])
                                        .optional()
                                        .describe('Row type match.'),
                                      fallback_value: zod
                                        .string()
                                        .optional()
                                        .describe('Row fallback value.'),
                                      description: zod
                                        .string()
                                        .optional()
                                        .describe('Rule description for human consumption.'),
                                    })
                                    .describe(
                                      'Rule matcher for selecting rows by name, condition, entity, or type.'
                                    )
                                )
                                .optional()
                                .describe('Rows to drop.'),
                              update: zod
                                .array(
                                  zod
                                    .object({
                                      name: zod
                                        .union([zod.string(), zod.array(zod.string())])
                                        .optional()
                                        .describe('Row name.'),
                                      condition: zod
                                        .string()
                                        .optional()
                                        .describe('Row condition match.'),
                                      foreach: zod
                                        .string()
                                        .optional()
                                        .describe('Foreach expression.'),
                                      value: zod
                                        .string()
                                        .optional()
                                        .describe('Row value definition.'),
                                      entity: zod
                                        .union([zod.string(), zod.array(zod.string())])
                                        .optional()
                                        .describe('Row entity match.'),
                                      type: zod
                                        .union([zod.string(), zod.array(zod.string())])
                                        .optional()
                                        .describe('Row type match.'),
                                      fallback_value: zod
                                        .string()
                                        .optional()
                                        .describe('Row fallback value.'),
                                      description: zod
                                        .string()
                                        .optional()
                                        .describe('Rule description for human consumption.'),
                                    })
                                    .describe(
                                      'Rule matcher for selecting rows by name, condition, entity, or type.'
                                    )
                                )
                                .optional()
                                .describe('Rows to update.'),
                            })
                            .describe('Container for row drop and update operations.')
                            .optional()
                            .describe('Rows transform configurations.'),
                        })
                        .describe(
                          'Single transformation step with optional variables, column actions, and row actions.'
                        )
                    )
                    .min(1)
                    .max(safeSynthesizerListJobsResponseDataItemSpecConfigOneReplacePiiOneStepsMax)
                    .describe('List of transformation steps to perform on input data.'),
                })
                .describe(
                  'Configuration for PII replacer.\n\nDefines how PII data should be detected and replaced in a dataset.'
                )
                .optional()
                .describe(
                  'PII replacement configuration. When ``None``, PII replacement is skipped.'
                ),
            })
            .describe(
              'Main configuration class for the Safe Synthesizer pipeline.\n\nThis is the top-level configuration class that orchestrates all aspects of\nsynthetic data generation including training, generation, privacy, evaluation,\nand data handling. It provides validation to ensure parameter compatibility.'
            )
            .describe('The Safe Synthesizer parameters configuration.'),
          hf_token_secret: zod
            .string()
            .optional()
            .describe(
              'Name of platform secret containing the HuggingFace token. Must exist in the same workspace as the job.'
            ),
          enable_synthesis: zod
            .boolean()
            .default(safeSynthesizerListJobsResponseDataItemSpecEnableSynthesisDefault)
            .describe(
              'Whether to run LLM training and generation phases. When False the task only performs PII replacement and returns the processed data.'
            ),
        })
        .describe(
          'Configuration model for Safe Synthesizer jobs.\n\nUsed primarily internally to configure a run submitted to the NeMo Jobs\nMicroservice.'
        ),
      status: zod
        .enum([
          'created',
          'pending',
          'active',
          'cancelled',
          'cancelling',
          'error',
          'completed',
          'paused',
          'pausing',
          'resuming',
        ])
        .optional()
        .describe(
          'Enumeration of possible job statuses.\n\nThis enum represents the various states a job can be in during its lifecycle,\nfrom creation to a terminal state.'
        ),
      status_details: zod.record(zod.string(), zod.unknown()).optional(),
      error_details: zod.record(zod.string(), zod.unknown()).optional(),
      ownership: zod.record(zod.string(), zod.unknown()).optional(),
      custom_fields: zod.record(zod.string(), zod.unknown()).optional(),
    })
  ),
  pagination: zod
    .object({
      page: zod.number().describe('The current page number.'),
      page_size: zod.number().describe('The page size used for the query.'),
      current_page_size: zod.number().describe('The size for the current page.'),
      total_pages: zod.number().describe('The total number of pages.'),
      total_results: zod.number().describe('The total number of results.'),
    })
    .optional()
    .describe('Pagination information.'),
  sort: zod.string().optional().describe('The field on which the results are sorted.'),
  filter: zod.record(zod.string(), zod.unknown()).optional().describe('Filtering information.'),
});

/**
 * @summary Download Job Result Adapter
 */
export const SafeSynthesizerDownloadJobResultAdapterParams = zod.object({
  workspace: zod.string(),
  job: zod.string(),
});

/**
 * @summary Download Job Result Evaluation-Report
 */
export const SafeSynthesizerDownloadJobResultEvaluationReportParams = zod.object({
  workspace: zod.string(),
  job: zod.string(),
});

/**
 * @summary Download Job Result Summary
 */
export const SafeSynthesizerDownloadJobResultSummaryParams = zod.object({
  workspace: zod.string(),
  job: zod.string(),
});

export const SafeSynthesizerDownloadJobResultSummaryResponse = zod
  .object({
    synthetic_data_quality_score: zod
      .number()
      .optional()
      .describe(
        'Weighted composite of the five sub-scores below (SQS). Higher is better (0--10 scale).'
      ),
    column_correlation_stability_score: zod
      .number()
      .optional()
      .describe(
        'How closely pairwise column correlations in synthetic data match the original for numeric and categorical columns.'
      ),
    deep_structure_stability_score: zod
      .number()
      .optional()
      .describe(
        'PCA-based comparison of multivariate structure between real and synthetic data for numeric and categorical columns.'
      ),
    column_distribution_stability_score: zod
      .number()
      .optional()
      .describe(
        'Per-column Jensen-Shannon distance between training and synthetic distributions averaged across all numeric and categorical columns.'
      ),
    text_semantic_similarity_score: zod
      .number()
      .optional()
      .describe('Embedding-based semantic closeness between real and synthetic free-text columns.'),
    text_structure_similarity_score: zod
      .number()
      .optional()
      .describe(
        'Jensen-Shannon divergence over sentence count, words-per-sentence, and characters-per-word distributions between real and synthetic free-text columns.'
      ),
    data_privacy_score: zod
      .number()
      .optional()
      .describe('Composite of MIA and AIA protection scores.'),
    membership_inference_protection_score: zod
      .number()
      .optional()
      .describe(
        'Resistance to attacks that try to determine whether a record was in the training set.'
      ),
    attribute_inference_protection_score: zod
      .number()
      .optional()
      .describe(
        'Resistance to attacks that try to infer sensitive attributes from quasi-identifiers.'
      ),
    num_valid_records: zod
      .number()
      .optional()
      .describe('Count of synthetic records that passed schema and format validation.'),
    num_invalid_records: zod
      .number()
      .optional()
      .describe('Count of synthetic records filtered out during validation.'),
    num_prompts: zod.number().optional().describe('Total LLM generation prompts issued.'),
    valid_record_fraction: zod
      .number()
      .optional()
      .describe(
        'Ratio of valid records: ``num_valid_records \/ (num_valid_records + num_invalid_records)``.'
      ),
    timing: zod
      .object({
        total_time_sec: zod
          .number()
          .optional()
          .describe('Total end-to-end pipeline duration in seconds.'),
        pii_replacer_time_sec: zod.number().optional().describe('Time spent on PII replacement.'),
        training_time_sec: zod.number().optional().describe('Time spent on model training.'),
        generation_time_sec: zod
          .number()
          .optional()
          .describe('Time spent generating synthetic records.'),
        evaluation_time_sec: zod
          .number()
          .optional()
          .describe('Time spent evaluating synthetic data quality.'),
      })
      .describe('Wall-clock durations for each pipeline stage.')
      .describe('Per-stage wall-clock durations.'),
  })
  .describe('Aggregated quality, privacy, and record-count metrics for a pipeline run.');

/**
 * @summary Download Job Result Synthetic-Data
 */
export const SafeSynthesizerDownloadJobResultSyntheticDataParams = zod.object({
  workspace: zod.string(),
  job: zod.string(),
});

/**
 * @summary Get Job Result
 */
export const SafeSynthesizerGetJobResultParams = zod.object({
  workspace: zod.string(),
  job: zod.string(),
  name: zod.string(),
});

export const SafeSynthesizerGetJobResultResponse = zod.object({
  name: zod.string(),
  job: zod.string(),
  workspace: zod.string(),
  project: zod.string().optional(),
  created_at: zod.string().datetime({}).optional(),
  updated_at: zod.string().datetime({}).optional(),
  artifact_url: zod.string(),
  artifact_storage_type: zod.enum(['fileset']),
  download_url: zod.string().optional(),
});

/**
 * @summary Download Job Result
 */
export const SafeSynthesizerDownloadJobResultParams = zod.object({
  workspace: zod.string(),
  job: zod.string(),
  name: zod.string(),
});

/**
 * @summary Get Job
 */
export const SafeSynthesizerGetJobParams = zod.object({
  workspace: zod.string(),
  name: zod.string(),
});

export const safeSynthesizerGetJobResponseSpecConfigOneDataOneMaxSequencesPerExampleDefault = `auto`;
export const safeSynthesizerGetJobResponseSpecConfigOneDataOneHoldoutDefault = 0.05;
export const safeSynthesizerGetJobResponseSpecConfigOneDataOneMaxHoldoutDefault = 2000;
export const safeSynthesizerGetJobResponseSpecConfigOneEvaluationOneMiaEnabledDefault = true;
export const safeSynthesizerGetJobResponseSpecConfigOneEvaluationOneAiaEnabledDefault = true;
export const safeSynthesizerGetJobResponseSpecConfigOneEvaluationOneSqsReportColumnsDefault = 250;
export const safeSynthesizerGetJobResponseSpecConfigOneEvaluationOneSqsReportRowsDefault = 5000;
export const safeSynthesizerGetJobResponseSpecConfigOneEvaluationOneEnabledDefault = true;
export const safeSynthesizerGetJobResponseSpecConfigOneEvaluationOneQuasiIdentifierCountDefault = 3;
export const safeSynthesizerGetJobResponseSpecConfigOneEvaluationOnePiiReplayEnabledDefault = true;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneNumInputRecordsToSampleDefault = `auto`;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneBatchSizeDefault = 1;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneGradientAccumulationStepsDefault = 8;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneWeightDecayDefault = 0.01;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneWarmupRatioDefault = 0.05;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneLrSchedulerDefault = `cosine`;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneLearningRateDefault = `auto`;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneLoraRDefault = 32;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneLoraAlphaOverRDefault = 1;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneLoraTargetModulesDefault = [
  `q_proj`,
  `k_proj`,
  `v_proj`,
  `o_proj`,
];
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneUseUnslothDefault = `auto`;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneRopeScalingFactorDefault = `auto`;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneValidationRatioDefault = 0;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneValidationStepsDefault = 15;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOnePretrainedModelDefault = `HuggingFaceTB/SmolLM3-3B`;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneQuantizeModelDefault = false;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneQuantizationBitsDefault = 8;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOnePeftImplementationDefault = `QLORA`;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneMaxVramFractionDefault = 0.8;
export const safeSynthesizerGetJobResponseSpecConfigOneTrainingOneAttnImplementationDefault = `kernels-community/vllm-flash-attn3`;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOneNumRecordsDefault = 1000;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOneTemperatureDefault = 0.9;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOneRepetitionPenaltyDefault = 1;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOneTopPDefault = 1;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOnePatienceDefault = 3;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOneInvalidFractionThresholdDefault = 0.8;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOneUseStructuredGenerationDefault = false;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOneStructuredGenerationBackendDefault = `auto`;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOneStructuredGenerationSchemaMethodDefault = `regex`;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOneStructuredGenerationUseSingleSequenceDefault = false;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOneEnforceTimeseriesFidelityDefault = false;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOneValidationOneGroupByAcceptNoDelineatorDefault = false;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOneValidationOneGroupByIgnoreInvalidRecordsDefault = false;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOneValidationOneGroupByFixNonUniqueValueDefault = false;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOneValidationOneGroupByFixUnorderedRecordsDefault = false;
export const safeSynthesizerGetJobResponseSpecConfigOneGenerationOneAttentionBackendDefault = `auto`;
export const safeSynthesizerGetJobResponseSpecConfigOnePrivacyOneDpEnabledDefault = false;
export const safeSynthesizerGetJobResponseSpecConfigOnePrivacyOneEpsilonDefault = 8;
export const safeSynthesizerGetJobResponseSpecConfigOnePrivacyOneDeltaDefault = `auto`;
export const safeSynthesizerGetJobResponseSpecConfigOnePrivacyOnePerSampleMaxGradNormDefault = 1;
export const safeSynthesizerGetJobResponseSpecConfigOneTimeSeriesOneIsTimeseriesDefault = false;
export const safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneClassifyOneNumSamplesDefault = 3;
export const safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneClassifyDefault = {
  num_samples: 3,
};
export const safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneNerThresholdDefault = 0.3;
export const safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneEnableRegexpsDefault = false;
export const safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableGlinerDefault = true;
export const safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableBatchModeDefault = true;
export const safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneBatchSizeDefault = 8;
export const safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneChunkLengthDefault = 512;
export const safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneGlinerModelDefault = `nvidia/gliner-PII`;
export const safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerDefault =
  {
    enable_gliner: true,
    enable_batch_mode: true,
    batch_size: 8,
    chunk_length: 512,
    gliner_model: 'nvidia/gliner-PII',
  };
export const safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerDefault = {
  ner_threshold: 0.3,
  enable_regexps: false,
};
export const safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneStepsMax = 10;

export const safeSynthesizerGetJobResponseSpecEnableSynthesisDefault = true;

export const SafeSynthesizerGetJobResponse = zod.object({
  id: zod.string().optional(),
  name: zod.string(),
  description: zod.string().optional(),
  project: zod.string().optional(),
  workspace: zod.string().optional(),
  created_at: zod.string().optional(),
  updated_at: zod.string().optional(),
  spec: zod
    .object({
      data_source: zod.string().describe('The data source for the job.'),
      config: zod
        .object({
          data: zod
            .object({
              group_training_examples_by: zod
                .string()
                .optional()
                .describe(
                  'Column to group training examples by. This is useful when you want the model to learn inter-record correlations for a given grouping of records.'
                ),
              order_training_examples_by: zod
                .string()
                .optional()
                .describe(
                  'Column to order training examples by. This is useful when you want the model to learn sequential relationships for a given ordering of records. If you provide this parameter, you must also provide ``group_training_examples_by``.'
                ),
              max_sequences_per_example: zod
                .union([zod.literal('auto'), zod.number()])
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneDataOneMaxSequencesPerExampleDefault
                )
                .describe(
                  "If specified, adds at most this number of sequences per example. Supports 'auto' where a value of 1 is chosen if differential privacy is enabled, and 10 otherwise. If not specified or set to 'auto', fills up context. Required for DP to limit contribution of each example."
                ),
              holdout: zod
                .number()
                .default(safeSynthesizerGetJobResponseSpecConfigOneDataOneHoldoutDefault)
                .describe(
                  'Amount of records to hold out for evaluation. If this is a float between 0 and 1, that ratio of records is held out. If an integer greater than 1, that number of records is held out. If the value is equal to zero, no holdout will be performed. Must be >= 0.'
                ),
              max_holdout: zod
                .number()
                .default(safeSynthesizerGetJobResponseSpecConfigOneDataOneMaxHoldoutDefault)
                .describe(
                  'Maximum number of records to hold out. Overrides any behavior set by ``holdout``. Must be >= 0.'
                ),
              random_state: zod
                .number()
                .optional()
                .describe('Random state for holdout split to ensure reproducibility.'),
            })
            .describe(
              'Configuration for grouping, ordering, and splitting input data for training and evaluation.'
            )
            .optional()
            .describe(
              'Configuration controlling how input data is grouped and split for training and evaluation.'
            ),
          evaluation: zod
            .object({
              mia_enabled: zod
                .boolean()
                .default(safeSynthesizerGetJobResponseSpecConfigOneEvaluationOneMiaEnabledDefault)
                .describe('Enable membership inference attack evaluation for privacy assessment.'),
              aia_enabled: zod
                .boolean()
                .default(safeSynthesizerGetJobResponseSpecConfigOneEvaluationOneAiaEnabledDefault)
                .describe('Enable attribute inference attack evaluation for privacy assessment.'),
              sqs_report_columns: zod
                .number()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneEvaluationOneSqsReportColumnsDefault
                )
                .describe('Number of columns to include in statistical quality reports.'),
              sqs_report_rows: zod
                .number()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneEvaluationOneSqsReportRowsDefault
                )
                .describe('Number of rows to include in statistical quality reports.'),
              mandatory_columns: zod
                .number()
                .optional()
                .describe('Number of mandatory columns that must be used in evaluation.'),
              enabled: zod
                .boolean()
                .default(safeSynthesizerGetJobResponseSpecConfigOneEvaluationOneEnabledDefault)
                .describe('Enable or disable evaluation.'),
              quasi_identifier_count: zod
                .number()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneEvaluationOneQuasiIdentifierCountDefault
                )
                .describe('Number of quasi-identifiers to sample for privacy attacks.'),
              pii_replay_enabled: zod
                .boolean()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneEvaluationOnePiiReplayEnabledDefault
                )
                .describe('Enable PII Replay detection.'),
              pii_replay_entities: zod
                .array(zod.string())
                .optional()
                .describe(
                  'List of entities for PII Replay. If not provided, default entities will be used.'
                ),
              pii_replay_columns: zod
                .array(zod.string())
                .optional()
                .describe(
                  'List of columns for PII Replay. If not provided, only entities will be used.'
                ),
            })
            .describe(
              'Configuration for evaluating synthetic data quality and privacy.\n\nThis class controls which evaluation metrics are computed and how they are configured.\nIt includes privacy attack evaluations, statistical quality metrics, and downstream\nmachine learning performance assessments.'
            )
            .optional()
            .describe('Parameters for evaluating the quality of generated synthetic data.'),
          training: zod
            .object({
              num_input_records_to_sample: zod
                .union([zod.literal('auto'), zod.number()])
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneTrainingOneNumInputRecordsToSampleDefault
                )
                .describe(
                  "Number of records the model will see during training. This parameter is a proxy for training time. For example, if its value is the same size as the input dataset, this is like training for a single epoch. If its value is larger, this is like training for multiple (possibly fractional) epochs. If its value is smaller, this is like training for a fraction of an epoch. Supports 'auto' where a reasonable value is chosen based on other config params and data."
                ),
              batch_size: zod
                .number()
                .default(safeSynthesizerGetJobResponseSpecConfigOneTrainingOneBatchSizeDefault)
                .describe('The batch size per device for training. Must be >= 1.'),
              gradient_accumulation_steps: zod
                .number()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneTrainingOneGradientAccumulationStepsDefault
                )
                .describe(
                  'Number of update steps to accumulate the gradients for, before performing a backward\/update pass. This technique increases the effective batch size that will fit into GPU memory. Must be >= 1.'
                ),
              weight_decay: zod
                .number()
                .default(safeSynthesizerGetJobResponseSpecConfigOneTrainingOneWeightDecayDefault)
                .describe(
                  'The weight decay to apply to all layers except all bias and LayerNorm weights in the AdamW optimizer. Must be in (0, 1).'
                ),
              warmup_ratio: zod
                .number()
                .default(safeSynthesizerGetJobResponseSpecConfigOneTrainingOneWarmupRatioDefault)
                .describe(
                  'Ratio of total training steps used for a linear warmup from 0 to the learning rate. Must be > 0.'
                ),
              lr_scheduler: zod
                .string()
                .default(safeSynthesizerGetJobResponseSpecConfigOneTrainingOneLrSchedulerDefault)
                .describe(
                  'The scheduler type to use. See the HuggingFace documentation of ``SchedulerType`` for all possible values.'
                ),
              learning_rate: zod
                .union([zod.literal('auto'), zod.number()])
                .default(safeSynthesizerGetJobResponseSpecConfigOneTrainingOneLearningRateDefault)
                .describe(
                  "The initial learning rate for `AdamW` optimizer. Must be in (0, 1). Setting to 'auto' uses a model-specific default if one exists."
                ),
              lora_r: zod
                .number()
                .default(safeSynthesizerGetJobResponseSpecConfigOneTrainingOneLoraRDefault)
                .describe(
                  'The rank of the LoRA update matrices. Lower rank results in smaller update matrices with fewer trainable parameters. Must be > 0.'
                ),
              lora_alpha_over_r: zod
                .number()
                .default(safeSynthesizerGetJobResponseSpecConfigOneTrainingOneLoraAlphaOverRDefault)
                .describe(
                  'The ratio of the LoRA scaling factor (alpha) to the LoRA rank. Empirically, this parameter works well when set to 0.5, 1, or 2. Must be in [0.5, 3].'
                ),
              lora_target_modules: zod
                .array(zod.string())
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneTrainingOneLoraTargetModulesDefault
                )
                .describe(
                  "The list of transformer modules to apply LoRA to. Possible modules: 'q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'."
                ),
              use_unsloth: zod
                .union([zod.literal('auto'), zod.boolean()])
                .default(safeSynthesizerGetJobResponseSpecConfigOneTrainingOneUseUnslothDefault)
                .describe('Whether to use Unsloth for optimized training.'),
              rope_scaling_factor: zod
                .union([zod.literal('auto'), zod.number()])
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneTrainingOneRopeScalingFactorDefault
                )
                .describe(
                  "Scale the base LLM's context length by this factor using RoPE scaling. Must be >= 1 or 'auto'."
                ),
              validation_ratio: zod
                .number()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneTrainingOneValidationRatioDefault
                )
                .describe(
                  'The fraction of the training data used for validation. Must be in [0, 1]. If set to 0, no validation will be performed. If set larger than 0, validation loss will be computed and reported throughout training.'
                ),
              validation_steps: zod
                .number()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneTrainingOneValidationStepsDefault
                )
                .describe(
                  'The number of steps between validation checks for the HF Trainer arguments. Must be > 0.'
                ),
              pretrained_model: zod
                .string()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneTrainingOnePretrainedModelDefault
                )
                .describe(
                  'Pretrained model to use for fine-tuning. Defaults to SmolLM3. May be a Hugging Face model ID (loaded from the Hugging Face Hub or cache) or a local path. See security note in docs before using untrusted sources.'
                ),
              quantize_model: zod
                .boolean()
                .default(safeSynthesizerGetJobResponseSpecConfigOneTrainingOneQuantizeModelDefault)
                .describe(
                  'Whether to quantize the model during training. This can reduce memory usage and potentially speed up training, but may also impact model accuracy.'
                ),
              quantization_bits: zod
                .union([zod.literal(4), zod.literal(8)])
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneTrainingOneQuantizationBitsDefault
                )
                .describe(
                  'The number of bits to use for quantization if ``quantize_model`` is ``True``. Accepts 8 or 4.'
                ),
              peft_implementation: zod
                .string()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneTrainingOnePeftImplementationDefault
                )
                .describe(
                  "The PEFT (Parameter-Efficient Fine-Tuning) implementation to use. Options: 'lora' for Low-Rank Adaptation, 'QLORA' for Quantized LoRA."
                ),
              max_vram_fraction: zod
                .number()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneTrainingOneMaxVramFractionDefault
                )
                .describe(
                  'The fraction of the total VRAM to use for training. Modify this to allow longer sequences. Must be in [0, 1].'
                ),
              attn_implementation: zod
                .string()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneTrainingOneAttnImplementationDefault
                )
                .describe(
                  "The attention implementation to use for model loading. Default uses Flash Attention 3 via the HuggingFace Kernels Hub (requires the 'kernels' pip package; falls back to 'sdpa' if the 'kernels' package is not installed). Other common values: 'flash_attention_2' (requires flash-attn pip package), 'sdpa' (PyTorch scaled dot product attention), 'eager' (standard PyTorch). Custom HuggingFace Kernels Hub paths (e.g. 'kernels-community\/flash-attn2') are also supported."
                ),
            })
            .describe(
              'Hyperparameters that control the training process behavior.\n\nThis class contains all the fine-tuning hyperparameters that control how the model\nlearns, including learning rates, batch sizes, LoRA configuration, and optimization\nsettings. These parameters directly affect training performance and quality.'
            )
            .optional()
            .describe(
              'Hyperparameters for model training such as learning rate, batch size, and LoRA adapter settings.'
            ),
          generation: zod
            .object({
              num_records: zod
                .number()
                .default(safeSynthesizerGetJobResponseSpecConfigOneGenerationOneNumRecordsDefault)
                .describe('Number of records to generate.'),
              temperature: zod
                .number()
                .default(safeSynthesizerGetJobResponseSpecConfigOneGenerationOneTemperatureDefault)
                .describe(
                  'Sampling temperature for controlling randomness (higher = more random).'
                ),
              repetition_penalty: zod
                .number()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneGenerationOneRepetitionPenaltyDefault
                )
                .describe(
                  'The value used to control the likelihood of the model repeating the same token. Must be > 0.'
                ),
              top_p: zod
                .number()
                .default(safeSynthesizerGetJobResponseSpecConfigOneGenerationOneTopPDefault)
                .describe('Nucleus sampling probability for token selection. Must be in (0, 1].'),
              patience: zod
                .number()
                .default(safeSynthesizerGetJobResponseSpecConfigOneGenerationOnePatienceDefault)
                .describe(
                  'Number of consecutive generations where the ``invalid_fraction_threshold`` is reached before stopping generation. Must be >= 1.'
                ),
              invalid_fraction_threshold: zod
                .number()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneGenerationOneInvalidFractionThresholdDefault
                )
                .describe(
                  'The fraction of invalid records that will stop generation after the ``patience`` limit is reached. Must be in [0, 1].'
                ),
              use_structured_generation: zod
                .boolean()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneGenerationOneUseStructuredGenerationDefault
                )
                .describe('Whether to use structured generation for better format control.'),
              structured_generation_backend: zod
                .enum(['auto', 'xgrammar', 'guidance', 'outlines', 'lm-format-enforcer'])
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneGenerationOneStructuredGenerationBackendDefault
                )
                .describe(
                  "The backend used by vLLM when ``use_structured_generation`` is ``True``. Supported backends: 'outlines', 'guidance', 'xgrammar', 'lm-format-enforcer'. 'auto' will allow vLLM to choose the backend."
                ),
              structured_generation_schema_method: zod
                .enum(['regex', 'json_schema'])
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneGenerationOneStructuredGenerationSchemaMethodDefault
                )
                .describe(
                  "The method used to generate the schema from your dataset and pass it to the generation backend. 'regex' uses a custom regex construction method that tends to be more comprehensive than 'json_schema' at the cost of speed."
                ),
              structured_generation_use_single_sequence: zod
                .boolean()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneGenerationOneStructuredGenerationUseSingleSequenceDefault
                )
                .describe(
                  'Whether to use a regex that matches exactly one sequence or record if ``max_sequences_per_example`` is 1.'
                ),
              enforce_timeseries_fidelity: zod
                .boolean()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneGenerationOneEnforceTimeseriesFidelityDefault
                )
                .describe(
                  'Enforce time-series fidelity by enforcing order, intervals, start and end times of the records.'
                ),
              validation: zod
                .object({
                  group_by_accept_no_delineator: zod
                    .boolean()
                    .default(
                      safeSynthesizerGetJobResponseSpecConfigOneGenerationOneValidationOneGroupByAcceptNoDelineatorDefault
                    )
                    .describe(
                      'Whether to accept completions without both beginning and end of sequence delineators as a single sequence.'
                    ),
                  group_by_ignore_invalid_records: zod
                    .boolean()
                    .default(
                      safeSynthesizerGetJobResponseSpecConfigOneGenerationOneValidationOneGroupByIgnoreInvalidRecordsDefault
                    )
                    .describe(
                      'Whether to ignore invalid records in a sequence and proceed with the valid records.'
                    ),
                  group_by_fix_non_unique_value: zod
                    .boolean()
                    .default(
                      safeSynthesizerGetJobResponseSpecConfigOneGenerationOneValidationOneGroupByFixNonUniqueValueDefault
                    )
                    .describe(
                      'Whether to automatically fix non-unique group-by values in a sequence by using the first unique value for all records.'
                    ),
                  group_by_fix_unordered_records: zod
                    .boolean()
                    .default(
                      safeSynthesizerGetJobResponseSpecConfigOneGenerationOneValidationOneGroupByFixUnorderedRecordsDefault
                    )
                    .describe(
                      'Whether to automatically fix unordered records in a sequence by sorting the records.'
                    ),
                })
                .describe(
                  'Configuration for record and sequence validation.\n\nThese parameters control the validation and automatic fixes when going\nfrom LLM output to tabular data.'
                )
                .optional()
                .describe(
                  'Validation parameters controlling validation logic and automatic fixes when parsing LLM output and converting to tabular data.'
                ),
              attention_backend: zod
                .string()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOneGenerationOneAttentionBackendDefault
                )
                .describe(
                  "The attention backend for the vLLM engine. Common values: 'FLASHINFER', 'FLASH_ATTN', 'TRITON_ATTN', 'FLEX_ATTENTION'. If ``None`` or 'auto', vLLM will auto-select the best available backend."
                ),
            })
            .describe(
              'Configuration parameters for synthetic data generation.\n\nThese parameters control how synthetic data is generated after the model is trained.\nThey affect the quality, diversity, and validity of the generated synthetic records.'
            )
            .optional()
            .describe(
              'Parameters governing synthetic data generation including temperature, top-p, and number of records to produce.'
            ),
          privacy: zod
            .object({
              dp_enabled: zod
                .boolean()
                .default(safeSynthesizerGetJobResponseSpecConfigOnePrivacyOneDpEnabledDefault)
                .describe('Enable differentially-private training with DP-SGD.'),
              epsilon: zod
                .number()
                .default(safeSynthesizerGetJobResponseSpecConfigOnePrivacyOneEpsilonDefault)
                .describe(
                  'Target privacy budget -- lower values provide stronger privacy. Must be > 0.'
                ),
              delta: zod
                .union([zod.literal('auto'), zod.number()])
                .default(safeSynthesizerGetJobResponseSpecConfigOnePrivacyOneDeltaDefault)
                .describe(
                  "Probability of accidentally leaking information. Should be much smaller than 1\/n where n is the number of training records. Setting to 'auto' uses delta of 1\/n^1.2. Must be in [0, 1) or 'auto'."
                ),
              per_sample_max_grad_norm: zod
                .number()
                .default(
                  safeSynthesizerGetJobResponseSpecConfigOnePrivacyOnePerSampleMaxGradNormDefault
                )
                .describe('Maximum L2 norm for per-sample gradient clipping. Must be > 0.'),
            })
            .describe(
              'Hyperparameters for differential privacy during training.\n\nThese parameters configure differential privacy (DP) training using DP-SGD algorithm.\nWhen enabled, they provide formal privacy guarantees by adding calibrated noise\nduring training.'
            )
            .optional()
            .describe(
              'Differential-privacy hyperparameters. When ``None``, differential privacy is disabled entirely.'
            ),
          time_series: zod
            .object({
              is_timeseries: zod
                .boolean()
                .default(safeSynthesizerGetJobResponseSpecConfigOneTimeSeriesOneIsTimeseriesDefault)
                .describe(
                  'Whether to treat the dataset as time series. When enabled, either ``timestamp_column`` or ``timestamp_interval_seconds`` is required. For grouped time series, ``group_training_examples_by`` needs to be set.'
                ),
              timestamp_column: zod
                .string()
                .optional()
                .describe(
                  'Name of the column containing timestamps used to order records when ``is_timeseries`` is ``True``. Required only when ``is_timeseries`` is ``True`` and ``timestamp_interval_seconds`` is not provided.'
                ),
              timestamp_interval_seconds: zod
                .number()
                .optional()
                .describe(
                  'Interval in seconds between timestamps. If not provided, the timestamp column will be used to infer the interval.'
                ),
              timestamp_format: zod
                .string()
                .optional()
                .describe(
                  "Format of the timestamp column. Accepts either: (1) Python strftime format codes for string timestamps (e.g., '%Y-%m-%d %H:%M:%S', '%m\/%d\/%Y'), or (2) 'elapsed_seconds' for numeric (int\/float) timestamps representing seconds as an increasing counter (e.g., 0, 60, 120 for 1-minute intervals). If not provided, the format will be inferred from the data."
                ),
              start_timestamp: zod
                .union([zod.string(), zod.number()])
                .optional()
                .describe(
                  'Start timestamp. If not provided, the first timestamp in the timestamp column will be used.'
                ),
              stop_timestamp: zod
                .union([zod.string(), zod.number()])
                .optional()
                .describe(
                  'Stop timestamp. If not provided, the last timestamp in the timestamp column will be used.'
                ),
            })
            .describe(
              'Configuration for time-series mode in the Safe Synthesizer pipeline.\n\nControls whether a dataset is treated as time-series data, including\ntimestamp column selection, interval inference, and format validation.\nThe time-series pipeline is currently experimental.'
            )
            .optional()
            .describe(
              'Configuration for time-series mode. Time-series pipeline is currently experimental.'
            ),
          replace_pii: zod
            .object({
              globals: zod
                .object({
                  locales: zod.array(zod.string()).optional().describe('List of locales.'),
                  seed: zod.number().optional().describe('Optional random seed.'),
                  classify: zod
                    .object({
                      enable_classify: zod
                        .boolean()
                        .optional()
                        .describe('Enable column classification.'),
                      entities: zod
                        .array(zod.string())
                        .optional()
                        .describe('List of entity types to classify.'),
                      num_samples: zod
                        .number()
                        .default(
                          safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneClassifyOneNumSamplesDefault
                        )
                        .describe('Number of column values to sample for classification.'),
                      classify_model_provider: zod
                        .string()
                        .optional()
                        .describe(
                          'Name of the model provider in the Inference Gateway for column classification. The job compiler will resolve this to the appropriate endpoint URL.'
                        ),
                    })
                    .describe('Configuration for column classification using an LLM.')
                    .default(
                      safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneClassifyDefault
                    )
                    .describe('Column classification configuration.'),
                  ner: zod
                    .object({
                      ner_threshold: zod
                        .number()
                        .default(
                          safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneNerThresholdDefault
                        )
                        .describe('NER model threshold.'),
                      enable_regexps: zod
                        .boolean()
                        .default(
                          safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneEnableRegexpsDefault
                        )
                        .describe('Enable NER regular expressions (experimental).'),
                      gliner: zod
                        .object({
                          enable_gliner: zod
                            .boolean()
                            .default(
                              safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableGlinerDefault
                            )
                            .describe('Enable GLiNER NER module.'),
                          enable_batch_mode: zod
                            .boolean()
                            .default(
                              safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableBatchModeDefault
                            )
                            .describe('Enable GLiNER batch mode.'),
                          batch_size: zod
                            .number()
                            .default(
                              safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneBatchSizeDefault
                            )
                            .describe('GLiNER batch size.'),
                          chunk_length: zod
                            .number()
                            .default(
                              safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneChunkLengthDefault
                            )
                            .describe('GLiNER batch chunk length in characters.'),
                          gliner_model: zod
                            .string()
                            .default(
                              safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneGlinerModelDefault
                            )
                            .describe('GLiNER model name.'),
                        })
                        .describe('Configuration for the GLiNER named-entity recognition model.')
                        .default(
                          safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerDefault
                        )
                        .describe('GLiNER NER configuration.'),
                      ner_entities: zod
                        .array(zod.string())
                        .optional()
                        .describe(
                          'List of entity types to recognize. If unset, classification entity types are used.'
                        ),
                    })
                    .describe('Configuration for Named Entity Recognition.')
                    .default(
                      safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerDefault
                    )
                    .describe('Named Entity Recognition configuration.'),
                  lock_columns: zod
                    .array(zod.string())
                    .optional()
                    .describe(
                      'List of columns to preserve as immutable across all transformations.'
                    ),
                })
                .describe(
                  'Global settings for the PII replacer including locales, seed, NER, and classification.'
                )
                .optional()
                .describe('Global configuration options.'),
              steps: zod
                .array(
                  zod
                    .object({
                      vars: zod
                        .record(
                          zod.string(),
                          zod.union([
                            zod.string(),
                            zod.record(zod.string(), zod.unknown()),
                            zod.array(zod.unknown()),
                          ])
                        )
                        .optional()
                        .describe('Variable names and templates.'),
                      columns: zod
                        .object({
                          add: zod
                            .array(
                              zod
                                .object({
                                  name: zod.string().optional().describe('Column name.'),
                                  position: zod
                                    .union([zod.number(), zod.array(zod.number())])
                                    .optional()
                                    .describe('Column position.'),
                                  condition: zod.string().optional().describe('Column condition.'),
                                  value: zod.string().optional().describe('Rename to value.'),
                                  entity: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column entity match.'),
                                  type: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column type match.'),
                                })
                                .describe(
                                  'Rule matcher for selecting columns by name, position, condition, entity, or type.'
                                )
                            )
                            .optional()
                            .describe('Columns to add.'),
                          drop: zod
                            .array(
                              zod
                                .object({
                                  name: zod.string().optional().describe('Column name.'),
                                  position: zod
                                    .union([zod.number(), zod.array(zod.number())])
                                    .optional()
                                    .describe('Column position.'),
                                  condition: zod.string().optional().describe('Column condition.'),
                                  value: zod.string().optional().describe('Rename to value.'),
                                  entity: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column entity match.'),
                                  type: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column type match.'),
                                })
                                .describe(
                                  'Rule matcher for selecting columns by name, position, condition, entity, or type.'
                                )
                            )
                            .optional()
                            .describe('Columns to drop.'),
                          rename: zod
                            .array(
                              zod
                                .object({
                                  name: zod.string().optional().describe('Column name.'),
                                  position: zod
                                    .union([zod.number(), zod.array(zod.number())])
                                    .optional()
                                    .describe('Column position.'),
                                  condition: zod.string().optional().describe('Column condition.'),
                                  value: zod.string().optional().describe('Rename to value.'),
                                  entity: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column entity match.'),
                                  type: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column type match.'),
                                })
                                .describe(
                                  'Rule matcher for selecting columns by name, position, condition, entity, or type.'
                                )
                            )
                            .optional()
                            .describe('Columns to rename.'),
                        })
                        .describe('Container for column add, drop, and rename operations.')
                        .optional()
                        .describe('Columns transform configuration.'),
                      rows: zod
                        .object({
                          drop: zod
                            .array(
                              zod
                                .object({
                                  name: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row name.'),
                                  condition: zod
                                    .string()
                                    .optional()
                                    .describe('Row condition match.'),
                                  foreach: zod.string().optional().describe('Foreach expression.'),
                                  value: zod.string().optional().describe('Row value definition.'),
                                  entity: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row entity match.'),
                                  type: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row type match.'),
                                  fallback_value: zod
                                    .string()
                                    .optional()
                                    .describe('Row fallback value.'),
                                  description: zod
                                    .string()
                                    .optional()
                                    .describe('Rule description for human consumption.'),
                                })
                                .describe(
                                  'Rule matcher for selecting rows by name, condition, entity, or type.'
                                )
                            )
                            .optional()
                            .describe('Rows to drop.'),
                          update: zod
                            .array(
                              zod
                                .object({
                                  name: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row name.'),
                                  condition: zod
                                    .string()
                                    .optional()
                                    .describe('Row condition match.'),
                                  foreach: zod.string().optional().describe('Foreach expression.'),
                                  value: zod.string().optional().describe('Row value definition.'),
                                  entity: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row entity match.'),
                                  type: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row type match.'),
                                  fallback_value: zod
                                    .string()
                                    .optional()
                                    .describe('Row fallback value.'),
                                  description: zod
                                    .string()
                                    .optional()
                                    .describe('Rule description for human consumption.'),
                                })
                                .describe(
                                  'Rule matcher for selecting rows by name, condition, entity, or type.'
                                )
                            )
                            .optional()
                            .describe('Rows to update.'),
                        })
                        .describe('Container for row drop and update operations.')
                        .optional()
                        .describe('Rows transform configurations.'),
                    })
                    .describe(
                      'Single transformation step with optional variables, column actions, and row actions.'
                    )
                )
                .min(1)
                .max(safeSynthesizerGetJobResponseSpecConfigOneReplacePiiOneStepsMax)
                .describe('List of transformation steps to perform on input data.'),
            })
            .describe(
              'Configuration for PII replacer.\n\nDefines how PII data should be detected and replaced in a dataset.'
            )
            .optional()
            .describe('PII replacement configuration. When ``None``, PII replacement is skipped.'),
        })
        .describe(
          'Main configuration class for the Safe Synthesizer pipeline.\n\nThis is the top-level configuration class that orchestrates all aspects of\nsynthetic data generation including training, generation, privacy, evaluation,\nand data handling. It provides validation to ensure parameter compatibility.'
        )
        .describe('The Safe Synthesizer parameters configuration.'),
      hf_token_secret: zod
        .string()
        .optional()
        .describe(
          'Name of platform secret containing the HuggingFace token. Must exist in the same workspace as the job.'
        ),
      enable_synthesis: zod
        .boolean()
        .default(safeSynthesizerGetJobResponseSpecEnableSynthesisDefault)
        .describe(
          'Whether to run LLM training and generation phases. When False the task only performs PII replacement and returns the processed data.'
        ),
    })
    .describe(
      'Configuration model for Safe Synthesizer jobs.\n\nUsed primarily internally to configure a run submitted to the NeMo Jobs\nMicroservice.'
    ),
  status: zod
    .enum([
      'created',
      'pending',
      'active',
      'cancelled',
      'cancelling',
      'error',
      'completed',
      'paused',
      'pausing',
      'resuming',
    ])
    .optional()
    .describe(
      'Enumeration of possible job statuses.\n\nThis enum represents the various states a job can be in during its lifecycle,\nfrom creation to a terminal state.'
    ),
  status_details: zod.record(zod.string(), zod.unknown()).optional(),
  error_details: zod.record(zod.string(), zod.unknown()).optional(),
  ownership: zod.record(zod.string(), zod.unknown()).optional(),
  custom_fields: zod.record(zod.string(), zod.unknown()).optional(),
});

/**
 * @summary Delete Job
 */
export const SafeSynthesizerDeleteJobParams = zod.object({
  workspace: zod.string(),
  name: zod.string(),
});

/**
 * @summary Cancel Job
 */
export const SafeSynthesizerCancelJobParams = zod.object({
  workspace: zod.string(),
  name: zod.string(),
});

export const safeSynthesizerCancelJobResponseSpecConfigOneDataOneMaxSequencesPerExampleDefault = `auto`;
export const safeSynthesizerCancelJobResponseSpecConfigOneDataOneHoldoutDefault = 0.05;
export const safeSynthesizerCancelJobResponseSpecConfigOneDataOneMaxHoldoutDefault = 2000;
export const safeSynthesizerCancelJobResponseSpecConfigOneEvaluationOneMiaEnabledDefault = true;
export const safeSynthesizerCancelJobResponseSpecConfigOneEvaluationOneAiaEnabledDefault = true;
export const safeSynthesizerCancelJobResponseSpecConfigOneEvaluationOneSqsReportColumnsDefault = 250;
export const safeSynthesizerCancelJobResponseSpecConfigOneEvaluationOneSqsReportRowsDefault = 5000;
export const safeSynthesizerCancelJobResponseSpecConfigOneEvaluationOneEnabledDefault = true;
export const safeSynthesizerCancelJobResponseSpecConfigOneEvaluationOneQuasiIdentifierCountDefault = 3;
export const safeSynthesizerCancelJobResponseSpecConfigOneEvaluationOnePiiReplayEnabledDefault = true;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneNumInputRecordsToSampleDefault = `auto`;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneBatchSizeDefault = 1;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneGradientAccumulationStepsDefault = 8;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneWeightDecayDefault = 0.01;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneWarmupRatioDefault = 0.05;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneLrSchedulerDefault = `cosine`;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneLearningRateDefault = `auto`;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneLoraRDefault = 32;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneLoraAlphaOverRDefault = 1;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneLoraTargetModulesDefault = [
  `q_proj`,
  `k_proj`,
  `v_proj`,
  `o_proj`,
];
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneUseUnslothDefault = `auto`;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneRopeScalingFactorDefault = `auto`;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneValidationRatioDefault = 0;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneValidationStepsDefault = 15;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOnePretrainedModelDefault = `HuggingFaceTB/SmolLM3-3B`;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneQuantizeModelDefault = false;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneQuantizationBitsDefault = 8;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOnePeftImplementationDefault = `QLORA`;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneMaxVramFractionDefault = 0.8;
export const safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneAttnImplementationDefault = `kernels-community/vllm-flash-attn3`;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneNumRecordsDefault = 1000;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneTemperatureDefault = 0.9;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneRepetitionPenaltyDefault = 1;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneTopPDefault = 1;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOnePatienceDefault = 3;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneInvalidFractionThresholdDefault = 0.8;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneUseStructuredGenerationDefault = false;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneStructuredGenerationBackendDefault = `auto`;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneStructuredGenerationSchemaMethodDefault = `regex`;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneStructuredGenerationUseSingleSequenceDefault = false;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneEnforceTimeseriesFidelityDefault = false;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneValidationOneGroupByAcceptNoDelineatorDefault = false;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneValidationOneGroupByIgnoreInvalidRecordsDefault = false;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneValidationOneGroupByFixNonUniqueValueDefault = false;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneValidationOneGroupByFixUnorderedRecordsDefault = false;
export const safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneAttentionBackendDefault = `auto`;
export const safeSynthesizerCancelJobResponseSpecConfigOnePrivacyOneDpEnabledDefault = false;
export const safeSynthesizerCancelJobResponseSpecConfigOnePrivacyOneEpsilonDefault = 8;
export const safeSynthesizerCancelJobResponseSpecConfigOnePrivacyOneDeltaDefault = `auto`;
export const safeSynthesizerCancelJobResponseSpecConfigOnePrivacyOnePerSampleMaxGradNormDefault = 1;
export const safeSynthesizerCancelJobResponseSpecConfigOneTimeSeriesOneIsTimeseriesDefault = false;
export const safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneClassifyOneNumSamplesDefault = 3;
export const safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneClassifyDefault = {
  num_samples: 3,
};
export const safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneNerThresholdDefault = 0.3;
export const safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneEnableRegexpsDefault = false;
export const safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableGlinerDefault = true;
export const safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableBatchModeDefault = true;
export const safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneBatchSizeDefault = 8;
export const safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneChunkLengthDefault = 512;
export const safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneGlinerModelDefault = `nvidia/gliner-PII`;
export const safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerDefault =
  {
    enable_gliner: true,
    enable_batch_mode: true,
    batch_size: 8,
    chunk_length: 512,
    gliner_model: 'nvidia/gliner-PII',
  };
export const safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerDefault = {
  ner_threshold: 0.3,
  enable_regexps: false,
};
export const safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneStepsMax = 10;

export const safeSynthesizerCancelJobResponseSpecEnableSynthesisDefault = true;

export const SafeSynthesizerCancelJobResponse = zod.object({
  id: zod.string().optional(),
  name: zod.string(),
  description: zod.string().optional(),
  project: zod.string().optional(),
  workspace: zod.string().optional(),
  created_at: zod.string().optional(),
  updated_at: zod.string().optional(),
  spec: zod
    .object({
      data_source: zod.string().describe('The data source for the job.'),
      config: zod
        .object({
          data: zod
            .object({
              group_training_examples_by: zod
                .string()
                .optional()
                .describe(
                  'Column to group training examples by. This is useful when you want the model to learn inter-record correlations for a given grouping of records.'
                ),
              order_training_examples_by: zod
                .string()
                .optional()
                .describe(
                  'Column to order training examples by. This is useful when you want the model to learn sequential relationships for a given ordering of records. If you provide this parameter, you must also provide ``group_training_examples_by``.'
                ),
              max_sequences_per_example: zod
                .union([zod.literal('auto'), zod.number()])
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneDataOneMaxSequencesPerExampleDefault
                )
                .describe(
                  "If specified, adds at most this number of sequences per example. Supports 'auto' where a value of 1 is chosen if differential privacy is enabled, and 10 otherwise. If not specified or set to 'auto', fills up context. Required for DP to limit contribution of each example."
                ),
              holdout: zod
                .number()
                .default(safeSynthesizerCancelJobResponseSpecConfigOneDataOneHoldoutDefault)
                .describe(
                  'Amount of records to hold out for evaluation. If this is a float between 0 and 1, that ratio of records is held out. If an integer greater than 1, that number of records is held out. If the value is equal to zero, no holdout will be performed. Must be >= 0.'
                ),
              max_holdout: zod
                .number()
                .default(safeSynthesizerCancelJobResponseSpecConfigOneDataOneMaxHoldoutDefault)
                .describe(
                  'Maximum number of records to hold out. Overrides any behavior set by ``holdout``. Must be >= 0.'
                ),
              random_state: zod
                .number()
                .optional()
                .describe('Random state for holdout split to ensure reproducibility.'),
            })
            .describe(
              'Configuration for grouping, ordering, and splitting input data for training and evaluation.'
            )
            .optional()
            .describe(
              'Configuration controlling how input data is grouped and split for training and evaluation.'
            ),
          evaluation: zod
            .object({
              mia_enabled: zod
                .boolean()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneEvaluationOneMiaEnabledDefault
                )
                .describe('Enable membership inference attack evaluation for privacy assessment.'),
              aia_enabled: zod
                .boolean()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneEvaluationOneAiaEnabledDefault
                )
                .describe('Enable attribute inference attack evaluation for privacy assessment.'),
              sqs_report_columns: zod
                .number()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneEvaluationOneSqsReportColumnsDefault
                )
                .describe('Number of columns to include in statistical quality reports.'),
              sqs_report_rows: zod
                .number()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneEvaluationOneSqsReportRowsDefault
                )
                .describe('Number of rows to include in statistical quality reports.'),
              mandatory_columns: zod
                .number()
                .optional()
                .describe('Number of mandatory columns that must be used in evaluation.'),
              enabled: zod
                .boolean()
                .default(safeSynthesizerCancelJobResponseSpecConfigOneEvaluationOneEnabledDefault)
                .describe('Enable or disable evaluation.'),
              quasi_identifier_count: zod
                .number()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneEvaluationOneQuasiIdentifierCountDefault
                )
                .describe('Number of quasi-identifiers to sample for privacy attacks.'),
              pii_replay_enabled: zod
                .boolean()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneEvaluationOnePiiReplayEnabledDefault
                )
                .describe('Enable PII Replay detection.'),
              pii_replay_entities: zod
                .array(zod.string())
                .optional()
                .describe(
                  'List of entities for PII Replay. If not provided, default entities will be used.'
                ),
              pii_replay_columns: zod
                .array(zod.string())
                .optional()
                .describe(
                  'List of columns for PII Replay. If not provided, only entities will be used.'
                ),
            })
            .describe(
              'Configuration for evaluating synthetic data quality and privacy.\n\nThis class controls which evaluation metrics are computed and how they are configured.\nIt includes privacy attack evaluations, statistical quality metrics, and downstream\nmachine learning performance assessments.'
            )
            .optional()
            .describe('Parameters for evaluating the quality of generated synthetic data.'),
          training: zod
            .object({
              num_input_records_to_sample: zod
                .union([zod.literal('auto'), zod.number()])
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneNumInputRecordsToSampleDefault
                )
                .describe(
                  "Number of records the model will see during training. This parameter is a proxy for training time. For example, if its value is the same size as the input dataset, this is like training for a single epoch. If its value is larger, this is like training for multiple (possibly fractional) epochs. If its value is smaller, this is like training for a fraction of an epoch. Supports 'auto' where a reasonable value is chosen based on other config params and data."
                ),
              batch_size: zod
                .number()
                .default(safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneBatchSizeDefault)
                .describe('The batch size per device for training. Must be >= 1.'),
              gradient_accumulation_steps: zod
                .number()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneGradientAccumulationStepsDefault
                )
                .describe(
                  'Number of update steps to accumulate the gradients for, before performing a backward\/update pass. This technique increases the effective batch size that will fit into GPU memory. Must be >= 1.'
                ),
              weight_decay: zod
                .number()
                .default(safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneWeightDecayDefault)
                .describe(
                  'The weight decay to apply to all layers except all bias and LayerNorm weights in the AdamW optimizer. Must be in (0, 1).'
                ),
              warmup_ratio: zod
                .number()
                .default(safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneWarmupRatioDefault)
                .describe(
                  'Ratio of total training steps used for a linear warmup from 0 to the learning rate. Must be > 0.'
                ),
              lr_scheduler: zod
                .string()
                .default(safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneLrSchedulerDefault)
                .describe(
                  'The scheduler type to use. See the HuggingFace documentation of ``SchedulerType`` for all possible values.'
                ),
              learning_rate: zod
                .union([zod.literal('auto'), zod.number()])
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneLearningRateDefault
                )
                .describe(
                  "The initial learning rate for `AdamW` optimizer. Must be in (0, 1). Setting to 'auto' uses a model-specific default if one exists."
                ),
              lora_r: zod
                .number()
                .default(safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneLoraRDefault)
                .describe(
                  'The rank of the LoRA update matrices. Lower rank results in smaller update matrices with fewer trainable parameters. Must be > 0.'
                ),
              lora_alpha_over_r: zod
                .number()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneLoraAlphaOverRDefault
                )
                .describe(
                  'The ratio of the LoRA scaling factor (alpha) to the LoRA rank. Empirically, this parameter works well when set to 0.5, 1, or 2. Must be in [0.5, 3].'
                ),
              lora_target_modules: zod
                .array(zod.string())
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneLoraTargetModulesDefault
                )
                .describe(
                  "The list of transformer modules to apply LoRA to. Possible modules: 'q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'."
                ),
              use_unsloth: zod
                .union([zod.literal('auto'), zod.boolean()])
                .default(safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneUseUnslothDefault)
                .describe('Whether to use Unsloth for optimized training.'),
              rope_scaling_factor: zod
                .union([zod.literal('auto'), zod.number()])
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneRopeScalingFactorDefault
                )
                .describe(
                  "Scale the base LLM's context length by this factor using RoPE scaling. Must be >= 1 or 'auto'."
                ),
              validation_ratio: zod
                .number()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneValidationRatioDefault
                )
                .describe(
                  'The fraction of the training data used for validation. Must be in [0, 1]. If set to 0, no validation will be performed. If set larger than 0, validation loss will be computed and reported throughout training.'
                ),
              validation_steps: zod
                .number()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneValidationStepsDefault
                )
                .describe(
                  'The number of steps between validation checks for the HF Trainer arguments. Must be > 0.'
                ),
              pretrained_model: zod
                .string()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneTrainingOnePretrainedModelDefault
                )
                .describe(
                  'Pretrained model to use for fine-tuning. Defaults to SmolLM3. May be a Hugging Face model ID (loaded from the Hugging Face Hub or cache) or a local path. See security note in docs before using untrusted sources.'
                ),
              quantize_model: zod
                .boolean()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneQuantizeModelDefault
                )
                .describe(
                  'Whether to quantize the model during training. This can reduce memory usage and potentially speed up training, but may also impact model accuracy.'
                ),
              quantization_bits: zod
                .union([zod.literal(4), zod.literal(8)])
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneQuantizationBitsDefault
                )
                .describe(
                  'The number of bits to use for quantization if ``quantize_model`` is ``True``. Accepts 8 or 4.'
                ),
              peft_implementation: zod
                .string()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneTrainingOnePeftImplementationDefault
                )
                .describe(
                  "The PEFT (Parameter-Efficient Fine-Tuning) implementation to use. Options: 'lora' for Low-Rank Adaptation, 'QLORA' for Quantized LoRA."
                ),
              max_vram_fraction: zod
                .number()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneMaxVramFractionDefault
                )
                .describe(
                  'The fraction of the total VRAM to use for training. Modify this to allow longer sequences. Must be in [0, 1].'
                ),
              attn_implementation: zod
                .string()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneTrainingOneAttnImplementationDefault
                )
                .describe(
                  "The attention implementation to use for model loading. Default uses Flash Attention 3 via the HuggingFace Kernels Hub (requires the 'kernels' pip package; falls back to 'sdpa' if the 'kernels' package is not installed). Other common values: 'flash_attention_2' (requires flash-attn pip package), 'sdpa' (PyTorch scaled dot product attention), 'eager' (standard PyTorch). Custom HuggingFace Kernels Hub paths (e.g. 'kernels-community\/flash-attn2') are also supported."
                ),
            })
            .describe(
              'Hyperparameters that control the training process behavior.\n\nThis class contains all the fine-tuning hyperparameters that control how the model\nlearns, including learning rates, batch sizes, LoRA configuration, and optimization\nsettings. These parameters directly affect training performance and quality.'
            )
            .optional()
            .describe(
              'Hyperparameters for model training such as learning rate, batch size, and LoRA adapter settings.'
            ),
          generation: zod
            .object({
              num_records: zod
                .number()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneNumRecordsDefault
                )
                .describe('Number of records to generate.'),
              temperature: zod
                .number()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneTemperatureDefault
                )
                .describe(
                  'Sampling temperature for controlling randomness (higher = more random).'
                ),
              repetition_penalty: zod
                .number()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneRepetitionPenaltyDefault
                )
                .describe(
                  'The value used to control the likelihood of the model repeating the same token. Must be > 0.'
                ),
              top_p: zod
                .number()
                .default(safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneTopPDefault)
                .describe('Nucleus sampling probability for token selection. Must be in (0, 1].'),
              patience: zod
                .number()
                .default(safeSynthesizerCancelJobResponseSpecConfigOneGenerationOnePatienceDefault)
                .describe(
                  'Number of consecutive generations where the ``invalid_fraction_threshold`` is reached before stopping generation. Must be >= 1.'
                ),
              invalid_fraction_threshold: zod
                .number()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneInvalidFractionThresholdDefault
                )
                .describe(
                  'The fraction of invalid records that will stop generation after the ``patience`` limit is reached. Must be in [0, 1].'
                ),
              use_structured_generation: zod
                .boolean()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneUseStructuredGenerationDefault
                )
                .describe('Whether to use structured generation for better format control.'),
              structured_generation_backend: zod
                .enum(['auto', 'xgrammar', 'guidance', 'outlines', 'lm-format-enforcer'])
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneStructuredGenerationBackendDefault
                )
                .describe(
                  "The backend used by vLLM when ``use_structured_generation`` is ``True``. Supported backends: 'outlines', 'guidance', 'xgrammar', 'lm-format-enforcer'. 'auto' will allow vLLM to choose the backend."
                ),
              structured_generation_schema_method: zod
                .enum(['regex', 'json_schema'])
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneStructuredGenerationSchemaMethodDefault
                )
                .describe(
                  "The method used to generate the schema from your dataset and pass it to the generation backend. 'regex' uses a custom regex construction method that tends to be more comprehensive than 'json_schema' at the cost of speed."
                ),
              structured_generation_use_single_sequence: zod
                .boolean()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneStructuredGenerationUseSingleSequenceDefault
                )
                .describe(
                  'Whether to use a regex that matches exactly one sequence or record if ``max_sequences_per_example`` is 1.'
                ),
              enforce_timeseries_fidelity: zod
                .boolean()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneEnforceTimeseriesFidelityDefault
                )
                .describe(
                  'Enforce time-series fidelity by enforcing order, intervals, start and end times of the records.'
                ),
              validation: zod
                .object({
                  group_by_accept_no_delineator: zod
                    .boolean()
                    .default(
                      safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneValidationOneGroupByAcceptNoDelineatorDefault
                    )
                    .describe(
                      'Whether to accept completions without both beginning and end of sequence delineators as a single sequence.'
                    ),
                  group_by_ignore_invalid_records: zod
                    .boolean()
                    .default(
                      safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneValidationOneGroupByIgnoreInvalidRecordsDefault
                    )
                    .describe(
                      'Whether to ignore invalid records in a sequence and proceed with the valid records.'
                    ),
                  group_by_fix_non_unique_value: zod
                    .boolean()
                    .default(
                      safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneValidationOneGroupByFixNonUniqueValueDefault
                    )
                    .describe(
                      'Whether to automatically fix non-unique group-by values in a sequence by using the first unique value for all records.'
                    ),
                  group_by_fix_unordered_records: zod
                    .boolean()
                    .default(
                      safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneValidationOneGroupByFixUnorderedRecordsDefault
                    )
                    .describe(
                      'Whether to automatically fix unordered records in a sequence by sorting the records.'
                    ),
                })
                .describe(
                  'Configuration for record and sequence validation.\n\nThese parameters control the validation and automatic fixes when going\nfrom LLM output to tabular data.'
                )
                .optional()
                .describe(
                  'Validation parameters controlling validation logic and automatic fixes when parsing LLM output and converting to tabular data.'
                ),
              attention_backend: zod
                .string()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneGenerationOneAttentionBackendDefault
                )
                .describe(
                  "The attention backend for the vLLM engine. Common values: 'FLASHINFER', 'FLASH_ATTN', 'TRITON_ATTN', 'FLEX_ATTENTION'. If ``None`` or 'auto', vLLM will auto-select the best available backend."
                ),
            })
            .describe(
              'Configuration parameters for synthetic data generation.\n\nThese parameters control how synthetic data is generated after the model is trained.\nThey affect the quality, diversity, and validity of the generated synthetic records.'
            )
            .optional()
            .describe(
              'Parameters governing synthetic data generation including temperature, top-p, and number of records to produce.'
            ),
          privacy: zod
            .object({
              dp_enabled: zod
                .boolean()
                .default(safeSynthesizerCancelJobResponseSpecConfigOnePrivacyOneDpEnabledDefault)
                .describe('Enable differentially-private training with DP-SGD.'),
              epsilon: zod
                .number()
                .default(safeSynthesizerCancelJobResponseSpecConfigOnePrivacyOneEpsilonDefault)
                .describe(
                  'Target privacy budget -- lower values provide stronger privacy. Must be > 0.'
                ),
              delta: zod
                .union([zod.literal('auto'), zod.number()])
                .default(safeSynthesizerCancelJobResponseSpecConfigOnePrivacyOneDeltaDefault)
                .describe(
                  "Probability of accidentally leaking information. Should be much smaller than 1\/n where n is the number of training records. Setting to 'auto' uses delta of 1\/n^1.2. Must be in [0, 1) or 'auto'."
                ),
              per_sample_max_grad_norm: zod
                .number()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOnePrivacyOnePerSampleMaxGradNormDefault
                )
                .describe('Maximum L2 norm for per-sample gradient clipping. Must be > 0.'),
            })
            .describe(
              'Hyperparameters for differential privacy during training.\n\nThese parameters configure differential privacy (DP) training using DP-SGD algorithm.\nWhen enabled, they provide formal privacy guarantees by adding calibrated noise\nduring training.'
            )
            .optional()
            .describe(
              'Differential-privacy hyperparameters. When ``None``, differential privacy is disabled entirely.'
            ),
          time_series: zod
            .object({
              is_timeseries: zod
                .boolean()
                .default(
                  safeSynthesizerCancelJobResponseSpecConfigOneTimeSeriesOneIsTimeseriesDefault
                )
                .describe(
                  'Whether to treat the dataset as time series. When enabled, either ``timestamp_column`` or ``timestamp_interval_seconds`` is required. For grouped time series, ``group_training_examples_by`` needs to be set.'
                ),
              timestamp_column: zod
                .string()
                .optional()
                .describe(
                  'Name of the column containing timestamps used to order records when ``is_timeseries`` is ``True``. Required only when ``is_timeseries`` is ``True`` and ``timestamp_interval_seconds`` is not provided.'
                ),
              timestamp_interval_seconds: zod
                .number()
                .optional()
                .describe(
                  'Interval in seconds between timestamps. If not provided, the timestamp column will be used to infer the interval.'
                ),
              timestamp_format: zod
                .string()
                .optional()
                .describe(
                  "Format of the timestamp column. Accepts either: (1) Python strftime format codes for string timestamps (e.g., '%Y-%m-%d %H:%M:%S', '%m\/%d\/%Y'), or (2) 'elapsed_seconds' for numeric (int\/float) timestamps representing seconds as an increasing counter (e.g., 0, 60, 120 for 1-minute intervals). If not provided, the format will be inferred from the data."
                ),
              start_timestamp: zod
                .union([zod.string(), zod.number()])
                .optional()
                .describe(
                  'Start timestamp. If not provided, the first timestamp in the timestamp column will be used.'
                ),
              stop_timestamp: zod
                .union([zod.string(), zod.number()])
                .optional()
                .describe(
                  'Stop timestamp. If not provided, the last timestamp in the timestamp column will be used.'
                ),
            })
            .describe(
              'Configuration for time-series mode in the Safe Synthesizer pipeline.\n\nControls whether a dataset is treated as time-series data, including\ntimestamp column selection, interval inference, and format validation.\nThe time-series pipeline is currently experimental.'
            )
            .optional()
            .describe(
              'Configuration for time-series mode. Time-series pipeline is currently experimental.'
            ),
          replace_pii: zod
            .object({
              globals: zod
                .object({
                  locales: zod.array(zod.string()).optional().describe('List of locales.'),
                  seed: zod.number().optional().describe('Optional random seed.'),
                  classify: zod
                    .object({
                      enable_classify: zod
                        .boolean()
                        .optional()
                        .describe('Enable column classification.'),
                      entities: zod
                        .array(zod.string())
                        .optional()
                        .describe('List of entity types to classify.'),
                      num_samples: zod
                        .number()
                        .default(
                          safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneClassifyOneNumSamplesDefault
                        )
                        .describe('Number of column values to sample for classification.'),
                      classify_model_provider: zod
                        .string()
                        .optional()
                        .describe(
                          'Name of the model provider in the Inference Gateway for column classification. The job compiler will resolve this to the appropriate endpoint URL.'
                        ),
                    })
                    .describe('Configuration for column classification using an LLM.')
                    .default(
                      safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneClassifyDefault
                    )
                    .describe('Column classification configuration.'),
                  ner: zod
                    .object({
                      ner_threshold: zod
                        .number()
                        .default(
                          safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneNerThresholdDefault
                        )
                        .describe('NER model threshold.'),
                      enable_regexps: zod
                        .boolean()
                        .default(
                          safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneEnableRegexpsDefault
                        )
                        .describe('Enable NER regular expressions (experimental).'),
                      gliner: zod
                        .object({
                          enable_gliner: zod
                            .boolean()
                            .default(
                              safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableGlinerDefault
                            )
                            .describe('Enable GLiNER NER module.'),
                          enable_batch_mode: zod
                            .boolean()
                            .default(
                              safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneEnableBatchModeDefault
                            )
                            .describe('Enable GLiNER batch mode.'),
                          batch_size: zod
                            .number()
                            .default(
                              safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneBatchSizeDefault
                            )
                            .describe('GLiNER batch size.'),
                          chunk_length: zod
                            .number()
                            .default(
                              safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneChunkLengthDefault
                            )
                            .describe('GLiNER batch chunk length in characters.'),
                          gliner_model: zod
                            .string()
                            .default(
                              safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerOneGlinerModelDefault
                            )
                            .describe('GLiNER model name.'),
                        })
                        .describe('Configuration for the GLiNER named-entity recognition model.')
                        .default(
                          safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerOneGlinerDefault
                        )
                        .describe('GLiNER NER configuration.'),
                      ner_entities: zod
                        .array(zod.string())
                        .optional()
                        .describe(
                          'List of entity types to recognize. If unset, classification entity types are used.'
                        ),
                    })
                    .describe('Configuration for Named Entity Recognition.')
                    .default(
                      safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneGlobalsOneNerDefault
                    )
                    .describe('Named Entity Recognition configuration.'),
                  lock_columns: zod
                    .array(zod.string())
                    .optional()
                    .describe(
                      'List of columns to preserve as immutable across all transformations.'
                    ),
                })
                .describe(
                  'Global settings for the PII replacer including locales, seed, NER, and classification.'
                )
                .optional()
                .describe('Global configuration options.'),
              steps: zod
                .array(
                  zod
                    .object({
                      vars: zod
                        .record(
                          zod.string(),
                          zod.union([
                            zod.string(),
                            zod.record(zod.string(), zod.unknown()),
                            zod.array(zod.unknown()),
                          ])
                        )
                        .optional()
                        .describe('Variable names and templates.'),
                      columns: zod
                        .object({
                          add: zod
                            .array(
                              zod
                                .object({
                                  name: zod.string().optional().describe('Column name.'),
                                  position: zod
                                    .union([zod.number(), zod.array(zod.number())])
                                    .optional()
                                    .describe('Column position.'),
                                  condition: zod.string().optional().describe('Column condition.'),
                                  value: zod.string().optional().describe('Rename to value.'),
                                  entity: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column entity match.'),
                                  type: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column type match.'),
                                })
                                .describe(
                                  'Rule matcher for selecting columns by name, position, condition, entity, or type.'
                                )
                            )
                            .optional()
                            .describe('Columns to add.'),
                          drop: zod
                            .array(
                              zod
                                .object({
                                  name: zod.string().optional().describe('Column name.'),
                                  position: zod
                                    .union([zod.number(), zod.array(zod.number())])
                                    .optional()
                                    .describe('Column position.'),
                                  condition: zod.string().optional().describe('Column condition.'),
                                  value: zod.string().optional().describe('Rename to value.'),
                                  entity: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column entity match.'),
                                  type: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column type match.'),
                                })
                                .describe(
                                  'Rule matcher for selecting columns by name, position, condition, entity, or type.'
                                )
                            )
                            .optional()
                            .describe('Columns to drop.'),
                          rename: zod
                            .array(
                              zod
                                .object({
                                  name: zod.string().optional().describe('Column name.'),
                                  position: zod
                                    .union([zod.number(), zod.array(zod.number())])
                                    .optional()
                                    .describe('Column position.'),
                                  condition: zod.string().optional().describe('Column condition.'),
                                  value: zod.string().optional().describe('Rename to value.'),
                                  entity: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column entity match.'),
                                  type: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Column type match.'),
                                })
                                .describe(
                                  'Rule matcher for selecting columns by name, position, condition, entity, or type.'
                                )
                            )
                            .optional()
                            .describe('Columns to rename.'),
                        })
                        .describe('Container for column add, drop, and rename operations.')
                        .optional()
                        .describe('Columns transform configuration.'),
                      rows: zod
                        .object({
                          drop: zod
                            .array(
                              zod
                                .object({
                                  name: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row name.'),
                                  condition: zod
                                    .string()
                                    .optional()
                                    .describe('Row condition match.'),
                                  foreach: zod.string().optional().describe('Foreach expression.'),
                                  value: zod.string().optional().describe('Row value definition.'),
                                  entity: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row entity match.'),
                                  type: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row type match.'),
                                  fallback_value: zod
                                    .string()
                                    .optional()
                                    .describe('Row fallback value.'),
                                  description: zod
                                    .string()
                                    .optional()
                                    .describe('Rule description for human consumption.'),
                                })
                                .describe(
                                  'Rule matcher for selecting rows by name, condition, entity, or type.'
                                )
                            )
                            .optional()
                            .describe('Rows to drop.'),
                          update: zod
                            .array(
                              zod
                                .object({
                                  name: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row name.'),
                                  condition: zod
                                    .string()
                                    .optional()
                                    .describe('Row condition match.'),
                                  foreach: zod.string().optional().describe('Foreach expression.'),
                                  value: zod.string().optional().describe('Row value definition.'),
                                  entity: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row entity match.'),
                                  type: zod
                                    .union([zod.string(), zod.array(zod.string())])
                                    .optional()
                                    .describe('Row type match.'),
                                  fallback_value: zod
                                    .string()
                                    .optional()
                                    .describe('Row fallback value.'),
                                  description: zod
                                    .string()
                                    .optional()
                                    .describe('Rule description for human consumption.'),
                                })
                                .describe(
                                  'Rule matcher for selecting rows by name, condition, entity, or type.'
                                )
                            )
                            .optional()
                            .describe('Rows to update.'),
                        })
                        .describe('Container for row drop and update operations.')
                        .optional()
                        .describe('Rows transform configurations.'),
                    })
                    .describe(
                      'Single transformation step with optional variables, column actions, and row actions.'
                    )
                )
                .min(1)
                .max(safeSynthesizerCancelJobResponseSpecConfigOneReplacePiiOneStepsMax)
                .describe('List of transformation steps to perform on input data.'),
            })
            .describe(
              'Configuration for PII replacer.\n\nDefines how PII data should be detected and replaced in a dataset.'
            )
            .optional()
            .describe('PII replacement configuration. When ``None``, PII replacement is skipped.'),
        })
        .describe(
          'Main configuration class for the Safe Synthesizer pipeline.\n\nThis is the top-level configuration class that orchestrates all aspects of\nsynthetic data generation including training, generation, privacy, evaluation,\nand data handling. It provides validation to ensure parameter compatibility.'
        )
        .describe('The Safe Synthesizer parameters configuration.'),
      hf_token_secret: zod
        .string()
        .optional()
        .describe(
          'Name of platform secret containing the HuggingFace token. Must exist in the same workspace as the job.'
        ),
      enable_synthesis: zod
        .boolean()
        .default(safeSynthesizerCancelJobResponseSpecEnableSynthesisDefault)
        .describe(
          'Whether to run LLM training and generation phases. When False the task only performs PII replacement and returns the processed data.'
        ),
    })
    .describe(
      'Configuration model for Safe Synthesizer jobs.\n\nUsed primarily internally to configure a run submitted to the NeMo Jobs\nMicroservice.'
    ),
  status: zod
    .enum([
      'created',
      'pending',
      'active',
      'cancelled',
      'cancelling',
      'error',
      'completed',
      'paused',
      'pausing',
      'resuming',
    ])
    .optional()
    .describe(
      'Enumeration of possible job statuses.\n\nThis enum represents the various states a job can be in during its lifecycle,\nfrom creation to a terminal state.'
    ),
  status_details: zod.record(zod.string(), zod.unknown()).optional(),
  error_details: zod.record(zod.string(), zod.unknown()).optional(),
  ownership: zod.record(zod.string(), zod.unknown()).optional(),
  custom_fields: zod.record(zod.string(), zod.unknown()).optional(),
});

/**
 * @summary Get Job Logs
 */
export const SafeSynthesizerGetJobLogsParams = zod.object({
  workspace: zod.string(),
  name: zod.string(),
});

export const SafeSynthesizerGetJobLogsQueryParams = zod.object({
  limit: zod.number().optional(),
  page_cursor: zod.string().optional(),
});

export const SafeSynthesizerGetJobLogsResponse = zod.object({
  data: zod.array(
    zod.object({
      timestamp: zod.string().datetime({}),
      job: zod.string(),
      job_step: zod.string(),
      job_task: zod.string(),
      message: zod.string(),
    })
  ),
  total: zod.number(),
  next_page: zod.string(),
  prev_page: zod.string(),
});

/**
 * @summary List Job Results
 */
export const SafeSynthesizerListJobResultsParams = zod.object({
  workspace: zod.string(),
  name: zod.string(),
});

export const SafeSynthesizerListJobResultsResponse = zod.object({
  data: zod.array(
    zod.object({
      name: zod.string(),
      job: zod.string(),
      workspace: zod.string(),
      project: zod.string().optional(),
      created_at: zod.string().datetime({}).optional(),
      updated_at: zod.string().datetime({}).optional(),
      artifact_url: zod.string(),
      artifact_storage_type: zod.enum(['fileset']),
      download_url: zod.string().optional(),
    })
  ),
});

/**
 * @summary Get Job Status
 */
export const SafeSynthesizerGetJobStatusParams = zod.object({
  workspace: zod.string(),
  name: zod.string(),
});

export const SafeSynthesizerGetJobStatusResponse = zod.object({
  id: zod.string(),
  name: zod.string(),
  status: zod
    .enum([
      'created',
      'pending',
      'active',
      'cancelled',
      'cancelling',
      'error',
      'completed',
      'paused',
      'pausing',
      'resuming',
    ])
    .describe(
      'Enumeration of possible job statuses.\n\nThis enum represents the various states a job can be in during its lifecycle,\nfrom creation to a terminal state.'
    ),
  status_details: zod.record(zod.string(), zod.unknown()),
  error_details: zod.record(zod.string(), zod.unknown()),
  steps: zod.array(
    zod.object({
      id: zod.string(),
      name: zod.string(),
      status: zod
        .enum([
          'created',
          'pending',
          'active',
          'cancelled',
          'cancelling',
          'error',
          'completed',
          'paused',
          'pausing',
          'resuming',
        ])
        .describe(
          'Enumeration of possible job statuses.\n\nThis enum represents the various states a job can be in during its lifecycle,\nfrom creation to a terminal state.'
        ),
      status_details: zod.record(zod.string(), zod.unknown()),
      error_details: zod.record(zod.string(), zod.unknown()),
      tasks: zod.array(
        zod.object({
          id: zod.string(),
          name: zod.string(),
          status: zod
            .enum([
              'created',
              'pending',
              'active',
              'cancelled',
              'cancelling',
              'error',
              'completed',
              'paused',
              'pausing',
              'resuming',
            ])
            .describe(
              'Enumeration of possible job statuses.\n\nThis enum represents the various states a job can be in during its lifecycle,\nfrom creation to a terminal state.'
            ),
          status_details: zod.record(zod.string(), zod.unknown()),
          error_details: zod.record(zod.string(), zod.unknown()),
          error_stack: zod.string(),
          created_at: zod.string().datetime({}),
          updated_at: zod.string().datetime({}),
        })
      ),
      created_at: zod.string().datetime({}),
      updated_at: zod.string().datetime({}),
    })
  ),
  created_at: zod.string().datetime({}),
  updated_at: zod.string().datetime({}),
});
