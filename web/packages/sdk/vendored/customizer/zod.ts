// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// TEMP: customizer zod schemas inlined while the customizer SDK is being rebuilt.
// Source: @nemo/sdk/generated/platform/zod/customizer.ts (verbatim copy).
// Restore SDK imports (`@nemo/sdk/generated/platform/zod/customizer`) once the SDK regenerates with customizer support.

/* eslint-disable */
// Verbatim copy of generated code; eslint suppressed (typecheck still runs).

import * as zod from 'zod';

/**
 * @summary Create Job
 */
export const CustomizationCreateJobParams = zod.object({
  workspace: zod.string(),
});

export const customizationCreateJobBodySpecTrainingOnePeftOneQuantizationOnePrecisionDefault = `4bit`;
export const customizationCreateJobBodySpecTrainingOnePeftOneTypeDefault = `lora`;
export const customizationCreateJobBodySpecTrainingOnePeftOneRankDefault = 8;
export const customizationCreateJobBodySpecTrainingOnePeftOneRankMax = 256;

export const customizationCreateJobBodySpecTrainingOnePeftOneAlphaDefault = 32;

export const customizationCreateJobBodySpecTrainingOnePeftOneDropoutDefault = 0;
export const customizationCreateJobBodySpecTrainingOnePeftOneDropoutMin = 0;
export const customizationCreateJobBodySpecTrainingOnePeftOneDropoutMax = 1;

export const customizationCreateJobBodySpecTrainingOnePeftOneMergeDefault = false;
export const customizationCreateJobBodySpecTrainingOnePeftOneUseDoraDefault = false;
export const customizationCreateJobBodySpecTrainingOneLearningRateDefault = 0.0001;
export const customizationCreateJobBodySpecTrainingOneWeightDecayDefault = 0.01;
export const customizationCreateJobBodySpecTrainingOneAdamBeta1Default = 0.9;
export const customizationCreateJobBodySpecTrainingOneAdamBeta2Default = 0.999;
export const customizationCreateJobBodySpecTrainingOneWarmupStepsDefault = 0;
export const customizationCreateJobBodySpecTrainingOneWarmupStepsMin = 0;

export const customizationCreateJobBodySpecTrainingOneEpochsDefault = 1;
export const customizationCreateJobBodySpecTrainingOneEpochsExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingOneBatchSizeDefault = 32;
export const customizationCreateJobBodySpecTrainingOneBatchSizeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingOneMicroBatchSizeDefault = 1;
export const customizationCreateJobBodySpecTrainingOneMicroBatchSizeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingOneSequencePackingDefault = false;
export const customizationCreateJobBodySpecTrainingOneMaxSeqLengthDefault = 2048;
export const customizationCreateJobBodySpecTrainingOneMaxSeqLengthExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingOneParallelismNumGpusPerNodeDefault = 1;
export const customizationCreateJobBodySpecTrainingOneParallelismNumGpusPerNodeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingOneParallelismNumNodesDefault = 1;
export const customizationCreateJobBodySpecTrainingOneParallelismNumNodesExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingOneParallelismTensorParallelSizeDefault = 1;
export const customizationCreateJobBodySpecTrainingOneParallelismTensorParallelSizeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingOneParallelismPipelineParallelSizeDefault = 1;
export const customizationCreateJobBodySpecTrainingOneParallelismPipelineParallelSizeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingOneParallelismContextParallelSizeDefault = 1;
export const customizationCreateJobBodySpecTrainingOneParallelismContextParallelSizeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingOneParallelismSequenceParallelDefault = false;
export const customizationCreateJobBodySpecTrainingOneTypeDefault = `sft`;
export const customizationCreateJobBodySpecTrainingTwoPeftOneQuantizationOnePrecisionDefault = `4bit`;
export const customizationCreateJobBodySpecTrainingTwoPeftOneTypeDefault = `lora`;
export const customizationCreateJobBodySpecTrainingTwoPeftOneRankDefault = 8;
export const customizationCreateJobBodySpecTrainingTwoPeftOneRankMax = 256;

export const customizationCreateJobBodySpecTrainingTwoPeftOneAlphaDefault = 32;

export const customizationCreateJobBodySpecTrainingTwoPeftOneDropoutDefault = 0;
export const customizationCreateJobBodySpecTrainingTwoPeftOneDropoutMin = 0;
export const customizationCreateJobBodySpecTrainingTwoPeftOneDropoutMax = 1;

export const customizationCreateJobBodySpecTrainingTwoPeftOneMergeDefault = false;
export const customizationCreateJobBodySpecTrainingTwoPeftOneUseDoraDefault = false;
export const customizationCreateJobBodySpecTrainingTwoLearningRateDefault = 0.0001;
export const customizationCreateJobBodySpecTrainingTwoWeightDecayDefault = 0.01;
export const customizationCreateJobBodySpecTrainingTwoAdamBeta1Default = 0.9;
export const customizationCreateJobBodySpecTrainingTwoAdamBeta2Default = 0.999;
export const customizationCreateJobBodySpecTrainingTwoWarmupStepsDefault = 0;
export const customizationCreateJobBodySpecTrainingTwoWarmupStepsMin = 0;

export const customizationCreateJobBodySpecTrainingTwoEpochsDefault = 1;
export const customizationCreateJobBodySpecTrainingTwoEpochsExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingTwoBatchSizeDefault = 32;
export const customizationCreateJobBodySpecTrainingTwoBatchSizeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingTwoMicroBatchSizeDefault = 1;
export const customizationCreateJobBodySpecTrainingTwoMicroBatchSizeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingTwoSequencePackingDefault = false;
export const customizationCreateJobBodySpecTrainingTwoMaxSeqLengthDefault = 2048;
export const customizationCreateJobBodySpecTrainingTwoMaxSeqLengthExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingTwoParallelismNumGpusPerNodeDefault = 1;
export const customizationCreateJobBodySpecTrainingTwoParallelismNumGpusPerNodeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingTwoParallelismNumNodesDefault = 1;
export const customizationCreateJobBodySpecTrainingTwoParallelismNumNodesExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingTwoParallelismTensorParallelSizeDefault = 1;
export const customizationCreateJobBodySpecTrainingTwoParallelismTensorParallelSizeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingTwoParallelismPipelineParallelSizeDefault = 1;
export const customizationCreateJobBodySpecTrainingTwoParallelismPipelineParallelSizeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingTwoParallelismContextParallelSizeDefault = 1;
export const customizationCreateJobBodySpecTrainingTwoParallelismContextParallelSizeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingTwoParallelismSequenceParallelDefault = false;
export const customizationCreateJobBodySpecTrainingTwoTypeDefault = `distillation`;
export const customizationCreateJobBodySpecTrainingTwoTeacherPrecisionDefault = `bf16`;
export const customizationCreateJobBodySpecTrainingTwoDistillationRatioDefault = 0.5;
export const customizationCreateJobBodySpecTrainingTwoDistillationRatioMin = 0;
export const customizationCreateJobBodySpecTrainingTwoDistillationRatioMax = 1;

export const customizationCreateJobBodySpecTrainingTwoDistillationTemperatureDefault = 1;
export const customizationCreateJobBodySpecTrainingTwoDistillationTemperatureExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingThreePeftOneQuantizationOnePrecisionDefault = `4bit`;
export const customizationCreateJobBodySpecTrainingThreePeftOneTypeDefault = `lora`;
export const customizationCreateJobBodySpecTrainingThreePeftOneRankDefault = 8;
export const customizationCreateJobBodySpecTrainingThreePeftOneRankMax = 256;

export const customizationCreateJobBodySpecTrainingThreePeftOneAlphaDefault = 32;

export const customizationCreateJobBodySpecTrainingThreePeftOneDropoutDefault = 0;
export const customizationCreateJobBodySpecTrainingThreePeftOneDropoutMin = 0;
export const customizationCreateJobBodySpecTrainingThreePeftOneDropoutMax = 1;

export const customizationCreateJobBodySpecTrainingThreePeftOneMergeDefault = false;
export const customizationCreateJobBodySpecTrainingThreePeftOneUseDoraDefault = false;
export const customizationCreateJobBodySpecTrainingThreeLearningRateDefault = 0.0001;
export const customizationCreateJobBodySpecTrainingThreeWeightDecayDefault = 0.01;
export const customizationCreateJobBodySpecTrainingThreeAdamBeta1Default = 0.9;
export const customizationCreateJobBodySpecTrainingThreeAdamBeta2Default = 0.999;
export const customizationCreateJobBodySpecTrainingThreeWarmupStepsDefault = 0;
export const customizationCreateJobBodySpecTrainingThreeWarmupStepsMin = 0;

export const customizationCreateJobBodySpecTrainingThreeEpochsDefault = 1;
export const customizationCreateJobBodySpecTrainingThreeEpochsExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingThreeBatchSizeDefault = 32;
export const customizationCreateJobBodySpecTrainingThreeBatchSizeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingThreeMicroBatchSizeDefault = 1;
export const customizationCreateJobBodySpecTrainingThreeMicroBatchSizeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingThreeSequencePackingDefault = false;
export const customizationCreateJobBodySpecTrainingThreeMaxSeqLengthDefault = 2048;
export const customizationCreateJobBodySpecTrainingThreeMaxSeqLengthExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingThreeParallelismNumGpusPerNodeDefault = 1;
export const customizationCreateJobBodySpecTrainingThreeParallelismNumGpusPerNodeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingThreeParallelismNumNodesDefault = 1;
export const customizationCreateJobBodySpecTrainingThreeParallelismNumNodesExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingThreeParallelismTensorParallelSizeDefault = 1;
export const customizationCreateJobBodySpecTrainingThreeParallelismTensorParallelSizeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingThreeParallelismPipelineParallelSizeDefault = 1;
export const customizationCreateJobBodySpecTrainingThreeParallelismPipelineParallelSizeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingThreeParallelismContextParallelSizeDefault = 1;
export const customizationCreateJobBodySpecTrainingThreeParallelismContextParallelSizeExclusiveMin = 0;

export const customizationCreateJobBodySpecTrainingThreeParallelismSequenceParallelDefault = false;
export const customizationCreateJobBodySpecTrainingThreeTypeDefault = `dpo`;
export const customizationCreateJobBodySpecTrainingThreeRefPolicyKlPenaltyDefault = 0.05;
export const customizationCreateJobBodySpecTrainingThreeRefPolicyKlPenaltyMin = 0;

export const customizationCreateJobBodySpecTrainingThreePreferenceAverageLogProbsDefault = false;
export const customizationCreateJobBodySpecTrainingThreeSftAverageLogProbsDefault = false;
export const customizationCreateJobBodySpecTrainingThreePreferenceLossWeightDefault = 1;
export const customizationCreateJobBodySpecTrainingThreePreferenceLossWeightMin = 0;

export const customizationCreateJobBodySpecTrainingThreeSftLossWeightDefault = 0;
export const customizationCreateJobBodySpecTrainingThreeSftLossWeightMin = 0;

export const customizationCreateJobBodySpecTrainingThreeMaxGradNormDefault = 1;
export const customizationCreateJobBodySpecTrainingThreeMaxGradNormMin = 0;

export const customizationCreateJobBodySpecIntegrationsOneWandbOneApiKeySecretOneRegExp =
  new RegExp('^[a-z0-9_-]+(\/[a-z0-9_-]+)?$');
export const customizationCreateJobBodySpecDeploymentConfigTwoGpuDefault = 1;
export const customizationCreateJobBodySpecDeploymentConfigTwoLoraEnabledDefault = true;
export const customizationCreateJobBodySpecDeploymentConfigTwoToolCallConfigOneToolCallPluginRegExp =
  new RegExp('^[\\w\\-.]+\/[\\w\\-.]+$');
export const customizationCreateJobBodySpecOutputOneNameMax = 255;

export const customizationCreateJobBodySpecOutputOneNameRegExp = new RegExp('^[\\w\\-.]+$');

export const CustomizationCreateJobBody = zod.object({
  name: zod.string().optional(),
  description: zod.string().optional(),
  project: zod.string().optional(),
  spec: zod
    .object({
      model: zod.string().describe("Model reference (e.g., 'workspace\/model-name')."),
      dataset: zod
        .string()
        .describe(
          'Dataset URI. Supported protocol: fileset:\/\/ (e.g., fileset:\/\/workspace\/name).'
        ),
      training: zod
        .union([
          zod
            .object({
              peft: zod
                .object({
                  quantization: zod
                    .object({
                      precision: zod
                        .enum(['4bit', '8bit'])
                        .default(
                          customizationCreateJobBodySpecTrainingOnePeftOneQuantizationOnePrecisionDefault
                        )
                        .describe(
                          "Quantization precision. '4bit' (NF4) for maximum memory savings, '8bit' (LLM.int8) for a balance of quality and memory."
                        ),
                    })
                    .describe(
                      'Base model quantization for memory-efficient PEFT training.\n\nSupports two scenarios:\n- Full-precision base model: quantized on-the-fly at load time\n- Pre-quantized base model: loaded directly at the specified precision\n\nIn both cases, base model weights are frozen and only the PEFT adapter\nparameters are trained in full precision.'
                    )
                    .optional()
                    .describe(
                      'Enable quantized training to reduce GPU memory. If the base model is full-precision, it will be quantized at load time. If the base model is already pre-quantized, this configures the expected precision. The trained adapter remains full-precision.'
                    ),
                  type: zod
                    .literal('lora')
                    .default(customizationCreateJobBodySpecTrainingOnePeftOneTypeDefault),
                  rank: zod
                    .number()
                    .min(1)
                    .max(customizationCreateJobBodySpecTrainingOnePeftOneRankMax)
                    .default(customizationCreateJobBodySpecTrainingOnePeftOneRankDefault)
                    .describe(
                      'LoRA rank (low-rank dimension). Higher values increase capacity but use more memory.'
                    ),
                  alpha: zod
                    .number()
                    .min(1)
                    .default(customizationCreateJobBodySpecTrainingOnePeftOneAlphaDefault)
                    .describe('LoRA alpha scaling factor. Common practice: alpha = 2-4x rank.'),
                  dropout: zod
                    .number()
                    .min(customizationCreateJobBodySpecTrainingOnePeftOneDropoutMin)
                    .max(customizationCreateJobBodySpecTrainingOnePeftOneDropoutMax)
                    .default(customizationCreateJobBodySpecTrainingOnePeftOneDropoutDefault)
                    .describe('LoRA dropout probability for regularization.'),
                  target_modules: zod
                    .array(zod.string())
                    .optional()
                    .describe(
                      "Module name patterns to apply LoRA to (e.g., ['\*.q_proj', '\*.v_proj']). If not set, applies to all '\*proj' linear layers."
                    ),
                  merge: zod
                    .boolean()
                    .default(customizationCreateJobBodySpecTrainingOnePeftOneMergeDefault)
                    .describe(
                      'Merge LoRA weights into base model after training. Produces a full-weight checkpoint instead of an adapter.'
                    ),
                  use_dora: zod
                    .boolean()
                    .default(customizationCreateJobBodySpecTrainingOnePeftOneUseDoraDefault)
                    .describe(
                      'Enable DoRA (Weight-Decomposed Low-Rank Adaptation). Decomposes weight updates into magnitude and direction components. Can improve quality especially at low ranks, but adds training overhead.'
                    ),
                })
                .describe('LoRA adapter configuration.')
                .optional()
                .describe(
                  'PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning.'
                ),
              learning_rate: zod
                .number()
                .default(customizationCreateJobBodySpecTrainingOneLearningRateDefault)
                .describe(
                  'Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning.'
                ),
              min_learning_rate: zod
                .number()
                .optional()
                .describe(
                  'Minimum learning rate for cosine decay. Optional; used with learning rate schedules.'
                ),
              weight_decay: zod
                .number()
                .default(customizationCreateJobBodySpecTrainingOneWeightDecayDefault)
                .describe('Weight decay coefficient. Helps prevent overfitting.'),
              adam_beta1: zod
                .number()
                .default(customizationCreateJobBodySpecTrainingOneAdamBeta1Default)
                .describe('Adam beta1 parameter. Adjust for optimizer tuning.'),
              adam_beta2: zod
                .number()
                .default(customizationCreateJobBodySpecTrainingOneAdamBeta2Default)
                .describe('Adam beta2 parameter. Adjust for optimizer tuning.'),
              warmup_steps: zod
                .number()
                .min(customizationCreateJobBodySpecTrainingOneWarmupStepsMin)
                .default(customizationCreateJobBodySpecTrainingOneWarmupStepsDefault)
                .describe(
                  'Linear warmup steps. Recommended: 10% of total training steps for stable training.'
                ),
              optimizer: zod.string().optional().describe("Optimizer name (e.g., 'adamw')."),
              epochs: zod
                .number()
                .gt(customizationCreateJobBodySpecTrainingOneEpochsExclusiveMin)
                .default(customizationCreateJobBodySpecTrainingOneEpochsDefault)
                .describe(
                  'Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.'
                ),
              max_steps: zod
                .number()
                .optional()
                .describe('Max training steps. Overrides epochs if set.'),
              log_every_n_steps: zod
                .number()
                .optional()
                .describe(
                  'Logging frequency in steps. Controls how often training metrics are logged.'
                ),
              val_check_interval: zod
                .number()
                .optional()
                .describe(
                  'Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count.'
                ),
              batch_size: zod
                .number()
                .gt(customizationCreateJobBodySpecTrainingOneBatchSizeExclusiveMin)
                .default(customizationCreateJobBodySpecTrainingOneBatchSizeDefault)
                .describe(
                  'Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.'
                ),
              micro_batch_size: zod
                .number()
                .gt(customizationCreateJobBodySpecTrainingOneMicroBatchSizeExclusiveMin)
                .default(customizationCreateJobBodySpecTrainingOneMicroBatchSizeDefault)
                .describe(
                  'Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.'
                ),
              sequence_packing: zod
                .boolean()
                .default(customizationCreateJobBodySpecTrainingOneSequencePackingDefault)
                .describe('Enable sequence packing for efficiency. Can improve training speed.'),
              max_seq_length: zod
                .number()
                .gt(customizationCreateJobBodySpecTrainingOneMaxSeqLengthExclusiveMin)
                .default(customizationCreateJobBodySpecTrainingOneMaxSeqLengthDefault)
                .describe(
                  'Maximum token sequence length for training. Higher = more memory, longer training.'
                ),
              precision: zod
                .enum(['fp8', 'bf16', 'fp16', 'fp32'])
                .describe('Model precision for training.')
                .optional()
                .describe('Model precision for training. Auto-detected if unset.'),
              seed: zod.number().optional().describe('Random seed for reproducibility. Optional.'),
              parallelism: zod
                .object({
                  num_gpus_per_node: zod
                    .number()
                    .gt(
                      customizationCreateJobBodySpecTrainingOneParallelismNumGpusPerNodeExclusiveMin
                    )
                    .default(
                      customizationCreateJobBodySpecTrainingOneParallelismNumGpusPerNodeDefault
                    )
                    .describe('Number of gpus per node.'),
                  num_nodes: zod
                    .number()
                    .gt(customizationCreateJobBodySpecTrainingOneParallelismNumNodesExclusiveMin)
                    .default(customizationCreateJobBodySpecTrainingOneParallelismNumNodesDefault)
                    .describe('Number of nodes.'),
                  tensor_parallel_size: zod
                    .number()
                    .gt(
                      customizationCreateJobBodySpecTrainingOneParallelismTensorParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCreateJobBodySpecTrainingOneParallelismTensorParallelSizeDefault
                    )
                    .describe('Tensor parallel size.'),
                  pipeline_parallel_size: zod
                    .number()
                    .gt(
                      customizationCreateJobBodySpecTrainingOneParallelismPipelineParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCreateJobBodySpecTrainingOneParallelismPipelineParallelSizeDefault
                    )
                    .describe('Pipeline parallel size.'),
                  context_parallel_size: zod
                    .number()
                    .gt(
                      customizationCreateJobBodySpecTrainingOneParallelismContextParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCreateJobBodySpecTrainingOneParallelismContextParallelSizeDefault
                    )
                    .describe('Context parallel size.'),
                  expert_parallel_size: zod
                    .number()
                    .optional()
                    .describe('Expert parallel size (MoE models).'),
                  sequence_parallel: zod
                    .boolean()
                    .default(
                      customizationCreateJobBodySpecTrainingOneParallelismSequenceParallelDefault
                    )
                    .describe('Enable sequence parallelism.'),
                })
                .optional()
                .describe(
                  'Distributed training parallelism configuration.\n\nMost users only need num_gpus_per_node. Advanced users can configure\ntensor\/pipeline\/context\/expert parallelism for large models.'
                ),
              execution_profile: zod
                .string()
                .optional()
                .describe(
                  "Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default."
                ),
              type: zod
                .literal('sft')
                .default(customizationCreateJobBodySpecTrainingOneTypeDefault),
            })
            .describe('Supervised Fine-Tuning.'),
          zod
            .object({
              peft: zod
                .object({
                  quantization: zod
                    .object({
                      precision: zod
                        .enum(['4bit', '8bit'])
                        .default(
                          customizationCreateJobBodySpecTrainingTwoPeftOneQuantizationOnePrecisionDefault
                        )
                        .describe(
                          "Quantization precision. '4bit' (NF4) for maximum memory savings, '8bit' (LLM.int8) for a balance of quality and memory."
                        ),
                    })
                    .describe(
                      'Base model quantization for memory-efficient PEFT training.\n\nSupports two scenarios:\n- Full-precision base model: quantized on-the-fly at load time\n- Pre-quantized base model: loaded directly at the specified precision\n\nIn both cases, base model weights are frozen and only the PEFT adapter\nparameters are trained in full precision.'
                    )
                    .optional()
                    .describe(
                      'Enable quantized training to reduce GPU memory. If the base model is full-precision, it will be quantized at load time. If the base model is already pre-quantized, this configures the expected precision. The trained adapter remains full-precision.'
                    ),
                  type: zod
                    .literal('lora')
                    .default(customizationCreateJobBodySpecTrainingTwoPeftOneTypeDefault),
                  rank: zod
                    .number()
                    .min(1)
                    .max(customizationCreateJobBodySpecTrainingTwoPeftOneRankMax)
                    .default(customizationCreateJobBodySpecTrainingTwoPeftOneRankDefault)
                    .describe(
                      'LoRA rank (low-rank dimension). Higher values increase capacity but use more memory.'
                    ),
                  alpha: zod
                    .number()
                    .min(1)
                    .default(customizationCreateJobBodySpecTrainingTwoPeftOneAlphaDefault)
                    .describe('LoRA alpha scaling factor. Common practice: alpha = 2-4x rank.'),
                  dropout: zod
                    .number()
                    .min(customizationCreateJobBodySpecTrainingTwoPeftOneDropoutMin)
                    .max(customizationCreateJobBodySpecTrainingTwoPeftOneDropoutMax)
                    .default(customizationCreateJobBodySpecTrainingTwoPeftOneDropoutDefault)
                    .describe('LoRA dropout probability for regularization.'),
                  target_modules: zod
                    .array(zod.string())
                    .optional()
                    .describe(
                      "Module name patterns to apply LoRA to (e.g., ['\*.q_proj', '\*.v_proj']). If not set, applies to all '\*proj' linear layers."
                    ),
                  merge: zod
                    .boolean()
                    .default(customizationCreateJobBodySpecTrainingTwoPeftOneMergeDefault)
                    .describe(
                      'Merge LoRA weights into base model after training. Produces a full-weight checkpoint instead of an adapter.'
                    ),
                  use_dora: zod
                    .boolean()
                    .default(customizationCreateJobBodySpecTrainingTwoPeftOneUseDoraDefault)
                    .describe(
                      'Enable DoRA (Weight-Decomposed Low-Rank Adaptation). Decomposes weight updates into magnitude and direction components. Can improve quality especially at low ranks, but adds training overhead.'
                    ),
                })
                .describe('LoRA adapter configuration.')
                .optional()
                .describe(
                  'PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning.'
                ),
              learning_rate: zod
                .number()
                .default(customizationCreateJobBodySpecTrainingTwoLearningRateDefault)
                .describe(
                  'Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning.'
                ),
              min_learning_rate: zod
                .number()
                .optional()
                .describe(
                  'Minimum learning rate for cosine decay. Optional; used with learning rate schedules.'
                ),
              weight_decay: zod
                .number()
                .default(customizationCreateJobBodySpecTrainingTwoWeightDecayDefault)
                .describe('Weight decay coefficient. Helps prevent overfitting.'),
              adam_beta1: zod
                .number()
                .default(customizationCreateJobBodySpecTrainingTwoAdamBeta1Default)
                .describe('Adam beta1 parameter. Adjust for optimizer tuning.'),
              adam_beta2: zod
                .number()
                .default(customizationCreateJobBodySpecTrainingTwoAdamBeta2Default)
                .describe('Adam beta2 parameter. Adjust for optimizer tuning.'),
              warmup_steps: zod
                .number()
                .min(customizationCreateJobBodySpecTrainingTwoWarmupStepsMin)
                .default(customizationCreateJobBodySpecTrainingTwoWarmupStepsDefault)
                .describe(
                  'Linear warmup steps. Recommended: 10% of total training steps for stable training.'
                ),
              optimizer: zod.string().optional().describe("Optimizer name (e.g., 'adamw')."),
              epochs: zod
                .number()
                .gt(customizationCreateJobBodySpecTrainingTwoEpochsExclusiveMin)
                .default(customizationCreateJobBodySpecTrainingTwoEpochsDefault)
                .describe(
                  'Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.'
                ),
              max_steps: zod
                .number()
                .optional()
                .describe('Max training steps. Overrides epochs if set.'),
              log_every_n_steps: zod
                .number()
                .optional()
                .describe(
                  'Logging frequency in steps. Controls how often training metrics are logged.'
                ),
              val_check_interval: zod
                .number()
                .optional()
                .describe(
                  'Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count.'
                ),
              batch_size: zod
                .number()
                .gt(customizationCreateJobBodySpecTrainingTwoBatchSizeExclusiveMin)
                .default(customizationCreateJobBodySpecTrainingTwoBatchSizeDefault)
                .describe(
                  'Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.'
                ),
              micro_batch_size: zod
                .number()
                .gt(customizationCreateJobBodySpecTrainingTwoMicroBatchSizeExclusiveMin)
                .default(customizationCreateJobBodySpecTrainingTwoMicroBatchSizeDefault)
                .describe(
                  'Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.'
                ),
              sequence_packing: zod
                .boolean()
                .default(customizationCreateJobBodySpecTrainingTwoSequencePackingDefault)
                .describe('Enable sequence packing for efficiency. Can improve training speed.'),
              max_seq_length: zod
                .number()
                .gt(customizationCreateJobBodySpecTrainingTwoMaxSeqLengthExclusiveMin)
                .default(customizationCreateJobBodySpecTrainingTwoMaxSeqLengthDefault)
                .describe(
                  'Maximum token sequence length for training. Higher = more memory, longer training.'
                ),
              precision: zod
                .enum(['fp8', 'bf16', 'fp16', 'fp32'])
                .describe('Model precision for training.')
                .optional()
                .describe('Model precision for training. Auto-detected if unset.'),
              seed: zod.number().optional().describe('Random seed for reproducibility. Optional.'),
              parallelism: zod
                .object({
                  num_gpus_per_node: zod
                    .number()
                    .gt(
                      customizationCreateJobBodySpecTrainingTwoParallelismNumGpusPerNodeExclusiveMin
                    )
                    .default(
                      customizationCreateJobBodySpecTrainingTwoParallelismNumGpusPerNodeDefault
                    )
                    .describe('Number of gpus per node.'),
                  num_nodes: zod
                    .number()
                    .gt(customizationCreateJobBodySpecTrainingTwoParallelismNumNodesExclusiveMin)
                    .default(customizationCreateJobBodySpecTrainingTwoParallelismNumNodesDefault)
                    .describe('Number of nodes.'),
                  tensor_parallel_size: zod
                    .number()
                    .gt(
                      customizationCreateJobBodySpecTrainingTwoParallelismTensorParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCreateJobBodySpecTrainingTwoParallelismTensorParallelSizeDefault
                    )
                    .describe('Tensor parallel size.'),
                  pipeline_parallel_size: zod
                    .number()
                    .gt(
                      customizationCreateJobBodySpecTrainingTwoParallelismPipelineParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCreateJobBodySpecTrainingTwoParallelismPipelineParallelSizeDefault
                    )
                    .describe('Pipeline parallel size.'),
                  context_parallel_size: zod
                    .number()
                    .gt(
                      customizationCreateJobBodySpecTrainingTwoParallelismContextParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCreateJobBodySpecTrainingTwoParallelismContextParallelSizeDefault
                    )
                    .describe('Context parallel size.'),
                  expert_parallel_size: zod
                    .number()
                    .optional()
                    .describe('Expert parallel size (MoE models).'),
                  sequence_parallel: zod
                    .boolean()
                    .default(
                      customizationCreateJobBodySpecTrainingTwoParallelismSequenceParallelDefault
                    )
                    .describe('Enable sequence parallelism.'),
                })
                .optional()
                .describe(
                  'Distributed training parallelism configuration.\n\nMost users only need num_gpus_per_node. Advanced users can configure\ntensor\/pipeline\/context\/expert parallelism for large models.'
                ),
              execution_profile: zod
                .string()
                .optional()
                .describe(
                  "Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default."
                ),
              type: zod
                .literal('distillation')
                .default(customizationCreateJobBodySpecTrainingTwoTypeDefault),
              teacher_model: zod
                .string()
                .describe(
                  "Teacher model URN (e.g., 'workspace\/model-name'). Must have the same vocabulary as the student model."
                ),
              teacher_precision: zod
                .enum(['bf16', 'fp16', 'fp32'])
                .default(customizationCreateJobBodySpecTrainingTwoTeacherPrecisionDefault)
                .describe(
                  'Precision for loading the frozen teacher model. Lower precision reduces memory but may affect logit quality.'
                ),
              distillation_ratio: zod
                .number()
                .min(customizationCreateJobBodySpecTrainingTwoDistillationRatioMin)
                .max(customizationCreateJobBodySpecTrainingTwoDistillationRatioMax)
                .default(customizationCreateJobBodySpecTrainingTwoDistillationRatioDefault)
                .describe('Balance between CE loss and KD loss. 0.0 = CE only, 1.0 = KD only.'),
              distillation_temperature: zod
                .number()
                .gt(customizationCreateJobBodySpecTrainingTwoDistillationTemperatureExclusiveMin)
                .default(customizationCreateJobBodySpecTrainingTwoDistillationTemperatureDefault)
                .describe('Softmax temperature for KD. Higher = softer probability distributions.'),
            })
            .describe(
              "Knowledge Distillation with a teacher model.\n\nCustomizer's differentiator — not available in Unsloth.\nTrains the student model to match the teacher's output distribution."
            ),
          zod
            .object({
              peft: zod
                .object({
                  quantization: zod
                    .object({
                      precision: zod
                        .enum(['4bit', '8bit'])
                        .default(
                          customizationCreateJobBodySpecTrainingThreePeftOneQuantizationOnePrecisionDefault
                        )
                        .describe(
                          "Quantization precision. '4bit' (NF4) for maximum memory savings, '8bit' (LLM.int8) for a balance of quality and memory."
                        ),
                    })
                    .describe(
                      'Base model quantization for memory-efficient PEFT training.\n\nSupports two scenarios:\n- Full-precision base model: quantized on-the-fly at load time\n- Pre-quantized base model: loaded directly at the specified precision\n\nIn both cases, base model weights are frozen and only the PEFT adapter\nparameters are trained in full precision.'
                    )
                    .optional()
                    .describe(
                      'Enable quantized training to reduce GPU memory. If the base model is full-precision, it will be quantized at load time. If the base model is already pre-quantized, this configures the expected precision. The trained adapter remains full-precision.'
                    ),
                  type: zod
                    .literal('lora')
                    .default(customizationCreateJobBodySpecTrainingThreePeftOneTypeDefault),
                  rank: zod
                    .number()
                    .min(1)
                    .max(customizationCreateJobBodySpecTrainingThreePeftOneRankMax)
                    .default(customizationCreateJobBodySpecTrainingThreePeftOneRankDefault)
                    .describe(
                      'LoRA rank (low-rank dimension). Higher values increase capacity but use more memory.'
                    ),
                  alpha: zod
                    .number()
                    .min(1)
                    .default(customizationCreateJobBodySpecTrainingThreePeftOneAlphaDefault)
                    .describe('LoRA alpha scaling factor. Common practice: alpha = 2-4x rank.'),
                  dropout: zod
                    .number()
                    .min(customizationCreateJobBodySpecTrainingThreePeftOneDropoutMin)
                    .max(customizationCreateJobBodySpecTrainingThreePeftOneDropoutMax)
                    .default(customizationCreateJobBodySpecTrainingThreePeftOneDropoutDefault)
                    .describe('LoRA dropout probability for regularization.'),
                  target_modules: zod
                    .array(zod.string())
                    .optional()
                    .describe(
                      "Module name patterns to apply LoRA to (e.g., ['\*.q_proj', '\*.v_proj']). If not set, applies to all '\*proj' linear layers."
                    ),
                  merge: zod
                    .boolean()
                    .default(customizationCreateJobBodySpecTrainingThreePeftOneMergeDefault)
                    .describe(
                      'Merge LoRA weights into base model after training. Produces a full-weight checkpoint instead of an adapter.'
                    ),
                  use_dora: zod
                    .boolean()
                    .default(customizationCreateJobBodySpecTrainingThreePeftOneUseDoraDefault)
                    .describe(
                      'Enable DoRA (Weight-Decomposed Low-Rank Adaptation). Decomposes weight updates into magnitude and direction components. Can improve quality especially at low ranks, but adds training overhead.'
                    ),
                })
                .describe('LoRA adapter configuration.')
                .optional()
                .describe(
                  'PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning.'
                ),
              learning_rate: zod
                .number()
                .default(customizationCreateJobBodySpecTrainingThreeLearningRateDefault)
                .describe(
                  'Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning.'
                ),
              min_learning_rate: zod
                .number()
                .optional()
                .describe(
                  'Minimum learning rate for cosine decay. Optional; used with learning rate schedules.'
                ),
              weight_decay: zod
                .number()
                .default(customizationCreateJobBodySpecTrainingThreeWeightDecayDefault)
                .describe('Weight decay coefficient. Helps prevent overfitting.'),
              adam_beta1: zod
                .number()
                .default(customizationCreateJobBodySpecTrainingThreeAdamBeta1Default)
                .describe('Adam beta1 parameter. Adjust for optimizer tuning.'),
              adam_beta2: zod
                .number()
                .default(customizationCreateJobBodySpecTrainingThreeAdamBeta2Default)
                .describe('Adam beta2 parameter. Adjust for optimizer tuning.'),
              warmup_steps: zod
                .number()
                .min(customizationCreateJobBodySpecTrainingThreeWarmupStepsMin)
                .default(customizationCreateJobBodySpecTrainingThreeWarmupStepsDefault)
                .describe(
                  'Linear warmup steps. Recommended: 10% of total training steps for stable training.'
                ),
              optimizer: zod.string().optional().describe("Optimizer name (e.g., 'adamw')."),
              epochs: zod
                .number()
                .gt(customizationCreateJobBodySpecTrainingThreeEpochsExclusiveMin)
                .default(customizationCreateJobBodySpecTrainingThreeEpochsDefault)
                .describe(
                  'Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.'
                ),
              max_steps: zod
                .number()
                .optional()
                .describe('Max training steps. Overrides epochs if set.'),
              log_every_n_steps: zod
                .number()
                .optional()
                .describe(
                  'Logging frequency in steps. Controls how often training metrics are logged.'
                ),
              val_check_interval: zod
                .number()
                .optional()
                .describe(
                  'Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count.'
                ),
              batch_size: zod
                .number()
                .gt(customizationCreateJobBodySpecTrainingThreeBatchSizeExclusiveMin)
                .default(customizationCreateJobBodySpecTrainingThreeBatchSizeDefault)
                .describe(
                  'Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.'
                ),
              micro_batch_size: zod
                .number()
                .gt(customizationCreateJobBodySpecTrainingThreeMicroBatchSizeExclusiveMin)
                .default(customizationCreateJobBodySpecTrainingThreeMicroBatchSizeDefault)
                .describe(
                  'Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.'
                ),
              sequence_packing: zod
                .boolean()
                .default(customizationCreateJobBodySpecTrainingThreeSequencePackingDefault)
                .describe('Enable sequence packing for efficiency. Can improve training speed.'),
              max_seq_length: zod
                .number()
                .gt(customizationCreateJobBodySpecTrainingThreeMaxSeqLengthExclusiveMin)
                .default(customizationCreateJobBodySpecTrainingThreeMaxSeqLengthDefault)
                .describe(
                  'Maximum token sequence length for training. Higher = more memory, longer training.'
                ),
              precision: zod
                .enum(['fp8', 'bf16', 'fp16', 'fp32'])
                .describe('Model precision for training.')
                .optional()
                .describe('Model precision for training. Auto-detected if unset.'),
              seed: zod.number().optional().describe('Random seed for reproducibility. Optional.'),
              parallelism: zod
                .object({
                  num_gpus_per_node: zod
                    .number()
                    .gt(
                      customizationCreateJobBodySpecTrainingThreeParallelismNumGpusPerNodeExclusiveMin
                    )
                    .default(
                      customizationCreateJobBodySpecTrainingThreeParallelismNumGpusPerNodeDefault
                    )
                    .describe('Number of gpus per node.'),
                  num_nodes: zod
                    .number()
                    .gt(customizationCreateJobBodySpecTrainingThreeParallelismNumNodesExclusiveMin)
                    .default(customizationCreateJobBodySpecTrainingThreeParallelismNumNodesDefault)
                    .describe('Number of nodes.'),
                  tensor_parallel_size: zod
                    .number()
                    .gt(
                      customizationCreateJobBodySpecTrainingThreeParallelismTensorParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCreateJobBodySpecTrainingThreeParallelismTensorParallelSizeDefault
                    )
                    .describe('Tensor parallel size.'),
                  pipeline_parallel_size: zod
                    .number()
                    .gt(
                      customizationCreateJobBodySpecTrainingThreeParallelismPipelineParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCreateJobBodySpecTrainingThreeParallelismPipelineParallelSizeDefault
                    )
                    .describe('Pipeline parallel size.'),
                  context_parallel_size: zod
                    .number()
                    .gt(
                      customizationCreateJobBodySpecTrainingThreeParallelismContextParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCreateJobBodySpecTrainingThreeParallelismContextParallelSizeDefault
                    )
                    .describe('Context parallel size.'),
                  expert_parallel_size: zod
                    .number()
                    .optional()
                    .describe('Expert parallel size (MoE models).'),
                  sequence_parallel: zod
                    .boolean()
                    .default(
                      customizationCreateJobBodySpecTrainingThreeParallelismSequenceParallelDefault
                    )
                    .describe('Enable sequence parallelism.'),
                })
                .optional()
                .describe(
                  'Distributed training parallelism configuration.\n\nMost users only need num_gpus_per_node. Advanced users can configure\ntensor\/pipeline\/context\/expert parallelism for large models.'
                ),
              execution_profile: zod
                .string()
                .optional()
                .describe(
                  "Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default."
                ),
              type: zod
                .literal('dpo')
                .default(customizationCreateJobBodySpecTrainingThreeTypeDefault),
              ref_policy_kl_penalty: zod
                .number()
                .min(customizationCreateJobBodySpecTrainingThreeRefPolicyKlPenaltyMin)
                .default(customizationCreateJobBodySpecTrainingThreeRefPolicyKlPenaltyDefault)
                .describe('KL penalty coefficient (beta in DPO paper).'),
              preference_average_log_probs: zod
                .boolean()
                .default(
                  customizationCreateJobBodySpecTrainingThreePreferenceAverageLogProbsDefault
                )
                .describe('Average log probabilities for preference loss calculation.'),
              sft_average_log_probs: zod
                .boolean()
                .default(customizationCreateJobBodySpecTrainingThreeSftAverageLogProbsDefault)
                .describe('Average log probabilities for SFT regularization loss.'),
              preference_loss_weight: zod
                .number()
                .min(customizationCreateJobBodySpecTrainingThreePreferenceLossWeightMin)
                .default(customizationCreateJobBodySpecTrainingThreePreferenceLossWeightDefault)
                .describe('Weight for the preference (DPO) loss term.'),
              sft_loss_weight: zod
                .number()
                .min(customizationCreateJobBodySpecTrainingThreeSftLossWeightMin)
                .default(customizationCreateJobBodySpecTrainingThreeSftLossWeightDefault)
                .describe('Weight for SFT regularization loss (0 = disabled).'),
              max_grad_norm: zod
                .number()
                .min(customizationCreateJobBodySpecTrainingThreeMaxGradNormMin)
                .default(customizationCreateJobBodySpecTrainingThreeMaxGradNormDefault)
                .describe('Maximum gradient norm for clipping.'),
            })
            .describe('Direct Preference Optimization.'),
        ])
        .describe('Training method and hyperparameters.'),
      integrations: zod
        .object({
          wandb: zod
            .object({
              project: zod
                .string()
                .optional()
                .describe(
                  'W&B project name (groups related runs). Defaults to output.name if not set.'
                ),
              name: zod
                .string()
                .optional()
                .describe('W&B run name. Defaults to job_id if not provided.'),
              entity: zod.string().optional().describe('W&B entity (team or username).'),
              tags: zod.array(zod.string()).optional().describe('W&B tags for filtering runs.'),
              notes: zod.string().optional().describe('W&B notes\/description for the run.'),
              base_url: zod
                .string()
                .optional()
                .describe(
                  "Base URL for self-hosted W&B server (e.g., 'https:\/\/wandb.mycompany.com'). If not provided, uses the default W&B cloud service."
                ),
              api_key_secret: zod
                .string()
                .regex(customizationCreateJobBodySpecIntegrationsOneWandbOneApiKeySecretOneRegExp)
                .describe(
                  "Reference to a secret. Format: 'secret_name' (uses request workspace) or 'workspace\/secret_name' (explicit workspace)."
                )
                .optional()
                .describe(
                  "Reference to a secret containing the WANDB_API_KEY. Format: 'secret_name' (uses request workspace) or 'workspace\/secret_name' (explicit workspace)."
                ),
            })
            .describe(
              'Weights & Biases integration configuration.\n\nTo use W&B, provide an api_key_secret referencing a secret that contains\nthe WANDB_API_KEY value. Optionally provide base_url for self-hosted W&B servers.'
            )
            .optional()
            .describe('Weights & Biases integration configuration.'),
          mlflow: zod
            .object({
              experiment_name: zod
                .string()
                .optional()
                .describe(
                  'MLflow experiment name (groups related runs). Defaults to output.name if not set.'
                ),
              run_name: zod
                .string()
                .optional()
                .describe('MLflow run name. Defaults to job_id if not provided.'),
              tags: zod
                .record(zod.string(), zod.string())
                .optional()
                .describe('MLflow tags as key-value pairs for filtering runs.'),
              description: zod.string().optional().describe('MLflow run description.'),
              tracking_uri: zod
                .string()
                .optional()
                .describe(
                  "MLflow tracking server URI (e.g., 'http:\/\/mlflow.mycompany.com:5000'). Can also be set via MLFLOW_TRACKING_URI environment variable."
                ),
            })
            .describe('MLflow integration configuration.')
            .optional()
            .describe('MLflow integration configuration.'),
        })
        .describe(
          'Third-party integration configurations.\n\nEach integration type has its own optional field. To enable an integration,\nprovide its configuration object. Omit or set to None to disable.'
        )
        .optional()
        .describe('Third-party integrations (e.g., Weights & Biases, MLflow).'),
      deployment_config: zod
        .union([
          zod.string().describe('A reference to DeploymentParams.'),
          zod
            .object({
              gpu: zod
                .number()
                .default(customizationCreateJobBodySpecDeploymentConfigTwoGpuDefault)
                .describe('Number of GPUs required for the deployment'),
              additional_envs: zod
                .record(zod.string(), zod.string())
                .optional()
                .describe('Additional environment variables for the deployment'),
              disk_size: zod.string().optional().describe('Disk size for the deployment'),
              image_name: zod
                .string()
                .optional()
                .describe('Container image name from NGC. If not specified, defaults to multi-llm'),
              image_tag: zod.string().optional().describe('Container image tag from NGC'),
              lora_enabled: zod
                .boolean()
                .default(customizationCreateJobBodySpecDeploymentConfigTwoLoraEnabledDefault)
                .describe(
                  'When automatically deploying a full SFT training, this parameter being set to true will allow subsequent LoRA adapters to be trained and deployed against it.'
                ),
              tool_call_config: zod
                .object({
                  tool_call_parser: zod
                    .string()
                    .optional()
                    .describe(
                      "Name of the tool call parser to use (e.g., 'openai', 'hermes', 'pythonic', 'llama3_json', 'mistral')."
                    ),
                  tool_call_plugin: zod
                    .string()
                    .regex(
                      customizationCreateJobBodySpecDeploymentConfigTwoToolCallConfigOneToolCallPluginRegExp
                    )
                    .optional()
                    .describe(
                      "Reference to a fileset containing the custom tool call plugin Python file. Expected format: '{workspace}\/{fileset_name}'."
                    ),
                  auto_tool_choice: zod
                    .boolean()
                    .optional()
                    .describe('Whether to enable automatic tool choice.'),
                })
                .describe('Tool calling configuration for NIM deployments.')
                .optional()
                .describe('Tool calling configuration override for the NIM deployment.'),
            })
            .describe('Inline deployment parameters for creating a new ModelDeploymentConfig.'),
        ])
        .optional()
        .describe(
          "Deployment configuration for auto-deploying the model after training. Pass a string to reference an existing ModelDeploymentConfig by name (e.g., 'my-config' or 'workspace\/my-config'). An object provides inline NIM deployment parameters. Omit to skip deployment."
        ),
      custom_fields: zod
        .record(zod.string(), zod.unknown())
        .optional()
        .describe('Custom user-defined fields.'),
      output: zod
        .object({
          name: zod
            .string()
            .max(customizationCreateJobBodySpecOutputOneNameMax)
            .regex(customizationCreateJobBodySpecOutputOneNameRegExp)
            .describe(
              'Name of the output artifact. Used to identify it during deployment and inference.'
            ),
        })
        .describe('Output artifact configuration provided by the user.')
        .optional()
        .describe(
          'Output artifact configuration. If omitted, name is auto-generated as `{model}-{dataset}-<random-hex>`. The output type (model vs adapter) is always inferred from the training configuration.'
        ),
    })
    .describe('Input schema for creating customization jobs.'),
  ownership: zod.record(zod.string(), zod.unknown()).optional(),
  custom_fields: zod.record(zod.string(), zod.unknown()).optional(),
});

/**
 * @summary List Jobs
 */
export const CustomizationListJobsParams = zod.object({
  workspace: zod.string(),
});

export const customizationListJobsQueryPageDefault = 1;
export const customizationListJobsQueryPageExclusiveMin = 0;

export const customizationListJobsQueryPageSizeDefault = 10;
export const customizationListJobsQueryPageSizeExclusiveMin = 0;

export const customizationListJobsQuerySortDefault = `-created_at`;

export const CustomizationListJobsQueryParams = zod.object({
  page: zod
    .number()
    .gt(customizationListJobsQueryPageExclusiveMin)
    .default(customizationListJobsQueryPageDefault)
    .describe('Page number.'),
  page_size: zod
    .number()
    .gt(customizationListJobsQueryPageSizeExclusiveMin)
    .default(customizationListJobsQueryPageSizeDefault)
    .describe('Page size.'),
  sort: zod
    .enum(['created_at', '-created_at', 'updated_at', '-updated_at'])
    .default(customizationListJobsQuerySortDefault)
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

export const customizationListJobsResponseDataItemSpecTrainingOnePeftOneQuantizationOnePrecisionDefault = `4bit`;
export const customizationListJobsResponseDataItemSpecTrainingOnePeftOneTypeDefault = `lora`;
export const customizationListJobsResponseDataItemSpecTrainingOnePeftOneRankDefault = 8;
export const customizationListJobsResponseDataItemSpecTrainingOnePeftOneRankMax = 256;

export const customizationListJobsResponseDataItemSpecTrainingOnePeftOneAlphaDefault = 32;

export const customizationListJobsResponseDataItemSpecTrainingOnePeftOneDropoutDefault = 0;
export const customizationListJobsResponseDataItemSpecTrainingOnePeftOneDropoutMin = 0;
export const customizationListJobsResponseDataItemSpecTrainingOnePeftOneDropoutMax = 1;

export const customizationListJobsResponseDataItemSpecTrainingOnePeftOneMergeDefault = false;
export const customizationListJobsResponseDataItemSpecTrainingOnePeftOneUseDoraDefault = false;
export const customizationListJobsResponseDataItemSpecTrainingOneLearningRateDefault = 0.0001;
export const customizationListJobsResponseDataItemSpecTrainingOneWeightDecayDefault = 0.01;
export const customizationListJobsResponseDataItemSpecTrainingOneAdamBeta1Default = 0.9;
export const customizationListJobsResponseDataItemSpecTrainingOneAdamBeta2Default = 0.999;
export const customizationListJobsResponseDataItemSpecTrainingOneWarmupStepsDefault = 0;
export const customizationListJobsResponseDataItemSpecTrainingOneWarmupStepsMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingOneEpochsDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingOneEpochsExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingOneBatchSizeDefault = 32;
export const customizationListJobsResponseDataItemSpecTrainingOneBatchSizeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingOneMicroBatchSizeDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingOneMicroBatchSizeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingOneSequencePackingDefault = false;
export const customizationListJobsResponseDataItemSpecTrainingOneMaxSeqLengthDefault = 2048;
export const customizationListJobsResponseDataItemSpecTrainingOneMaxSeqLengthExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingOneParallelismNumGpusPerNodeDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingOneParallelismNumGpusPerNodeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingOneParallelismNumNodesDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingOneParallelismNumNodesExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingOneParallelismTensorParallelSizeDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingOneParallelismTensorParallelSizeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingOneParallelismPipelineParallelSizeDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingOneParallelismPipelineParallelSizeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingOneParallelismContextParallelSizeDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingOneParallelismContextParallelSizeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingOneParallelismSequenceParallelDefault = false;
export const customizationListJobsResponseDataItemSpecTrainingOneTypeDefault = `sft`;
export const customizationListJobsResponseDataItemSpecTrainingTwoPeftOneQuantizationOnePrecisionDefault = `4bit`;
export const customizationListJobsResponseDataItemSpecTrainingTwoPeftOneTypeDefault = `lora`;
export const customizationListJobsResponseDataItemSpecTrainingTwoPeftOneRankDefault = 8;
export const customizationListJobsResponseDataItemSpecTrainingTwoPeftOneRankMax = 256;

export const customizationListJobsResponseDataItemSpecTrainingTwoPeftOneAlphaDefault = 32;

export const customizationListJobsResponseDataItemSpecTrainingTwoPeftOneDropoutDefault = 0;
export const customizationListJobsResponseDataItemSpecTrainingTwoPeftOneDropoutMin = 0;
export const customizationListJobsResponseDataItemSpecTrainingTwoPeftOneDropoutMax = 1;

export const customizationListJobsResponseDataItemSpecTrainingTwoPeftOneMergeDefault = false;
export const customizationListJobsResponseDataItemSpecTrainingTwoPeftOneUseDoraDefault = false;
export const customizationListJobsResponseDataItemSpecTrainingTwoLearningRateDefault = 0.0001;
export const customizationListJobsResponseDataItemSpecTrainingTwoWeightDecayDefault = 0.01;
export const customizationListJobsResponseDataItemSpecTrainingTwoAdamBeta1Default = 0.9;
export const customizationListJobsResponseDataItemSpecTrainingTwoAdamBeta2Default = 0.999;
export const customizationListJobsResponseDataItemSpecTrainingTwoWarmupStepsDefault = 0;
export const customizationListJobsResponseDataItemSpecTrainingTwoWarmupStepsMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingTwoEpochsDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingTwoEpochsExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingTwoBatchSizeDefault = 32;
export const customizationListJobsResponseDataItemSpecTrainingTwoBatchSizeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingTwoMicroBatchSizeDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingTwoMicroBatchSizeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingTwoSequencePackingDefault = false;
export const customizationListJobsResponseDataItemSpecTrainingTwoMaxSeqLengthDefault = 2048;
export const customizationListJobsResponseDataItemSpecTrainingTwoMaxSeqLengthExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingTwoParallelismNumGpusPerNodeDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingTwoParallelismNumGpusPerNodeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingTwoParallelismNumNodesDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingTwoParallelismNumNodesExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingTwoParallelismTensorParallelSizeDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingTwoParallelismTensorParallelSizeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingTwoParallelismPipelineParallelSizeDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingTwoParallelismPipelineParallelSizeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingTwoParallelismContextParallelSizeDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingTwoParallelismContextParallelSizeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingTwoParallelismSequenceParallelDefault = false;
export const customizationListJobsResponseDataItemSpecTrainingTwoTypeDefault = `distillation`;
export const customizationListJobsResponseDataItemSpecTrainingTwoTeacherPrecisionDefault = `bf16`;
export const customizationListJobsResponseDataItemSpecTrainingTwoDistillationRatioDefault = 0.5;
export const customizationListJobsResponseDataItemSpecTrainingTwoDistillationRatioMin = 0;
export const customizationListJobsResponseDataItemSpecTrainingTwoDistillationRatioMax = 1;

export const customizationListJobsResponseDataItemSpecTrainingTwoDistillationTemperatureDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingTwoDistillationTemperatureExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingThreePeftOneQuantizationOnePrecisionDefault = `4bit`;
export const customizationListJobsResponseDataItemSpecTrainingThreePeftOneTypeDefault = `lora`;
export const customizationListJobsResponseDataItemSpecTrainingThreePeftOneRankDefault = 8;
export const customizationListJobsResponseDataItemSpecTrainingThreePeftOneRankMax = 256;

export const customizationListJobsResponseDataItemSpecTrainingThreePeftOneAlphaDefault = 32;

export const customizationListJobsResponseDataItemSpecTrainingThreePeftOneDropoutDefault = 0;
export const customizationListJobsResponseDataItemSpecTrainingThreePeftOneDropoutMin = 0;
export const customizationListJobsResponseDataItemSpecTrainingThreePeftOneDropoutMax = 1;

export const customizationListJobsResponseDataItemSpecTrainingThreePeftOneMergeDefault = false;
export const customizationListJobsResponseDataItemSpecTrainingThreePeftOneUseDoraDefault = false;
export const customizationListJobsResponseDataItemSpecTrainingThreeLearningRateDefault = 0.0001;
export const customizationListJobsResponseDataItemSpecTrainingThreeWeightDecayDefault = 0.01;
export const customizationListJobsResponseDataItemSpecTrainingThreeAdamBeta1Default = 0.9;
export const customizationListJobsResponseDataItemSpecTrainingThreeAdamBeta2Default = 0.999;
export const customizationListJobsResponseDataItemSpecTrainingThreeWarmupStepsDefault = 0;
export const customizationListJobsResponseDataItemSpecTrainingThreeWarmupStepsMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingThreeEpochsDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingThreeEpochsExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingThreeBatchSizeDefault = 32;
export const customizationListJobsResponseDataItemSpecTrainingThreeBatchSizeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingThreeMicroBatchSizeDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingThreeMicroBatchSizeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingThreeSequencePackingDefault = false;
export const customizationListJobsResponseDataItemSpecTrainingThreeMaxSeqLengthDefault = 2048;
export const customizationListJobsResponseDataItemSpecTrainingThreeMaxSeqLengthExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingThreeParallelismNumGpusPerNodeDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingThreeParallelismNumGpusPerNodeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingThreeParallelismNumNodesDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingThreeParallelismNumNodesExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingThreeParallelismTensorParallelSizeDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingThreeParallelismTensorParallelSizeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingThreeParallelismPipelineParallelSizeDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingThreeParallelismPipelineParallelSizeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingThreeParallelismContextParallelSizeDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingThreeParallelismContextParallelSizeExclusiveMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingThreeParallelismSequenceParallelDefault = false;
export const customizationListJobsResponseDataItemSpecTrainingThreeTypeDefault = `dpo`;
export const customizationListJobsResponseDataItemSpecTrainingThreeRefPolicyKlPenaltyDefault = 0.05;
export const customizationListJobsResponseDataItemSpecTrainingThreeRefPolicyKlPenaltyMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingThreePreferenceAverageLogProbsDefault = false;
export const customizationListJobsResponseDataItemSpecTrainingThreeSftAverageLogProbsDefault = false;
export const customizationListJobsResponseDataItemSpecTrainingThreePreferenceLossWeightDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingThreePreferenceLossWeightMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingThreeSftLossWeightDefault = 0;
export const customizationListJobsResponseDataItemSpecTrainingThreeSftLossWeightMin = 0;

export const customizationListJobsResponseDataItemSpecTrainingThreeMaxGradNormDefault = 1;
export const customizationListJobsResponseDataItemSpecTrainingThreeMaxGradNormMin = 0;

export const customizationListJobsResponseDataItemSpecIntegrationsOneWandbOneApiKeySecretOneRegExp =
  new RegExp('^[a-z0-9_-]+(\/[a-z0-9_-]+)?$');
export const customizationListJobsResponseDataItemSpecDeploymentConfigTwoGpuDefault = 1;
export const customizationListJobsResponseDataItemSpecDeploymentConfigTwoLoraEnabledDefault = true;
export const customizationListJobsResponseDataItemSpecDeploymentConfigTwoToolCallConfigOneToolCallPluginRegExp =
  new RegExp('^[\\w\\-.]+\/[\\w\\-.]+$');
export const customizationListJobsResponseDataItemSpecOutputOneNameMax = 255;

export const customizationListJobsResponseDataItemSpecOutputOneNameRegExp = new RegExp(
  '^[\\w\\-.]+$'
);
export const customizationListJobsResponseDataItemSpecOutputOneFilesetMax = 255;

export const customizationListJobsResponseDataItemSpecOutputOneFilesetRegExp = new RegExp(
  '^[\\w\\-.]+$'
);

export const CustomizationListJobsResponse = zod.object({
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
          model: zod.string().describe("Model reference (e.g., 'workspace\/model-name')."),
          dataset: zod
            .string()
            .describe(
              'Dataset URI. Supported protocol: fileset:\/\/ (e.g., fileset:\/\/workspace\/name).'
            ),
          training: zod
            .union([
              zod
                .object({
                  peft: zod
                    .object({
                      quantization: zod
                        .object({
                          precision: zod
                            .enum(['4bit', '8bit'])
                            .default(
                              customizationListJobsResponseDataItemSpecTrainingOnePeftOneQuantizationOnePrecisionDefault
                            )
                            .describe(
                              "Quantization precision. '4bit' (NF4) for maximum memory savings, '8bit' (LLM.int8) for a balance of quality and memory."
                            ),
                        })
                        .describe(
                          'Base model quantization for memory-efficient PEFT training.\n\nSupports two scenarios:\n- Full-precision base model: quantized on-the-fly at load time\n- Pre-quantized base model: loaded directly at the specified precision\n\nIn both cases, base model weights are frozen and only the PEFT adapter\nparameters are trained in full precision.'
                        )
                        .optional()
                        .describe(
                          'Enable quantized training to reduce GPU memory. If the base model is full-precision, it will be quantized at load time. If the base model is already pre-quantized, this configures the expected precision. The trained adapter remains full-precision.'
                        ),
                      type: zod
                        .literal('lora')
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingOnePeftOneTypeDefault
                        ),
                      rank: zod
                        .number()
                        .min(1)
                        .max(customizationListJobsResponseDataItemSpecTrainingOnePeftOneRankMax)
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingOnePeftOneRankDefault
                        )
                        .describe(
                          'LoRA rank (low-rank dimension). Higher values increase capacity but use more memory.'
                        ),
                      alpha: zod
                        .number()
                        .min(1)
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingOnePeftOneAlphaDefault
                        )
                        .describe('LoRA alpha scaling factor. Common practice: alpha = 2-4x rank.'),
                      dropout: zod
                        .number()
                        .min(customizationListJobsResponseDataItemSpecTrainingOnePeftOneDropoutMin)
                        .max(customizationListJobsResponseDataItemSpecTrainingOnePeftOneDropoutMax)
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingOnePeftOneDropoutDefault
                        )
                        .describe('LoRA dropout probability for regularization.'),
                      target_modules: zod
                        .array(zod.string())
                        .optional()
                        .describe(
                          "Module name patterns to apply LoRA to (e.g., ['\*.q_proj', '\*.v_proj']). If not set, applies to all '\*proj' linear layers."
                        ),
                      merge: zod
                        .boolean()
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingOnePeftOneMergeDefault
                        )
                        .describe(
                          'Merge LoRA weights into base model after training. Produces a full-weight checkpoint instead of an adapter.'
                        ),
                      use_dora: zod
                        .boolean()
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingOnePeftOneUseDoraDefault
                        )
                        .describe(
                          'Enable DoRA (Weight-Decomposed Low-Rank Adaptation). Decomposes weight updates into magnitude and direction components. Can improve quality especially at low ranks, but adds training overhead.'
                        ),
                    })
                    .describe('LoRA adapter configuration.')
                    .optional()
                    .describe(
                      'PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning.'
                    ),
                  learning_rate: zod
                    .number()
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingOneLearningRateDefault
                    )
                    .describe(
                      'Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning.'
                    ),
                  min_learning_rate: zod
                    .number()
                    .optional()
                    .describe(
                      'Minimum learning rate for cosine decay. Optional; used with learning rate schedules.'
                    ),
                  weight_decay: zod
                    .number()
                    .default(customizationListJobsResponseDataItemSpecTrainingOneWeightDecayDefault)
                    .describe('Weight decay coefficient. Helps prevent overfitting.'),
                  adam_beta1: zod
                    .number()
                    .default(customizationListJobsResponseDataItemSpecTrainingOneAdamBeta1Default)
                    .describe('Adam beta1 parameter. Adjust for optimizer tuning.'),
                  adam_beta2: zod
                    .number()
                    .default(customizationListJobsResponseDataItemSpecTrainingOneAdamBeta2Default)
                    .describe('Adam beta2 parameter. Adjust for optimizer tuning.'),
                  warmup_steps: zod
                    .number()
                    .min(customizationListJobsResponseDataItemSpecTrainingOneWarmupStepsMin)
                    .default(customizationListJobsResponseDataItemSpecTrainingOneWarmupStepsDefault)
                    .describe(
                      'Linear warmup steps. Recommended: 10% of total training steps for stable training.'
                    ),
                  optimizer: zod.string().optional().describe("Optimizer name (e.g., 'adamw')."),
                  epochs: zod
                    .number()
                    .gt(customizationListJobsResponseDataItemSpecTrainingOneEpochsExclusiveMin)
                    .default(customizationListJobsResponseDataItemSpecTrainingOneEpochsDefault)
                    .describe(
                      'Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.'
                    ),
                  max_steps: zod
                    .number()
                    .optional()
                    .describe('Max training steps. Overrides epochs if set.'),
                  log_every_n_steps: zod
                    .number()
                    .optional()
                    .describe(
                      'Logging frequency in steps. Controls how often training metrics are logged.'
                    ),
                  val_check_interval: zod
                    .number()
                    .optional()
                    .describe(
                      'Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count.'
                    ),
                  batch_size: zod
                    .number()
                    .gt(customizationListJobsResponseDataItemSpecTrainingOneBatchSizeExclusiveMin)
                    .default(customizationListJobsResponseDataItemSpecTrainingOneBatchSizeDefault)
                    .describe(
                      'Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.'
                    ),
                  micro_batch_size: zod
                    .number()
                    .gt(
                      customizationListJobsResponseDataItemSpecTrainingOneMicroBatchSizeExclusiveMin
                    )
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingOneMicroBatchSizeDefault
                    )
                    .describe(
                      'Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.'
                    ),
                  sequence_packing: zod
                    .boolean()
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingOneSequencePackingDefault
                    )
                    .describe(
                      'Enable sequence packing for efficiency. Can improve training speed.'
                    ),
                  max_seq_length: zod
                    .number()
                    .gt(
                      customizationListJobsResponseDataItemSpecTrainingOneMaxSeqLengthExclusiveMin
                    )
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingOneMaxSeqLengthDefault
                    )
                    .describe(
                      'Maximum token sequence length for training. Higher = more memory, longer training.'
                    ),
                  precision: zod
                    .enum(['fp8', 'bf16', 'fp16', 'fp32'])
                    .describe('Model precision for training.')
                    .optional()
                    .describe('Model precision for training. Auto-detected if unset.'),
                  seed: zod
                    .number()
                    .optional()
                    .describe('Random seed for reproducibility. Optional.'),
                  parallelism: zod
                    .object({
                      num_gpus_per_node: zod
                        .number()
                        .gt(
                          customizationListJobsResponseDataItemSpecTrainingOneParallelismNumGpusPerNodeExclusiveMin
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingOneParallelismNumGpusPerNodeDefault
                        )
                        .describe('Number of gpus per node.'),
                      num_nodes: zod
                        .number()
                        .gt(
                          customizationListJobsResponseDataItemSpecTrainingOneParallelismNumNodesExclusiveMin
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingOneParallelismNumNodesDefault
                        )
                        .describe('Number of nodes.'),
                      tensor_parallel_size: zod
                        .number()
                        .gt(
                          customizationListJobsResponseDataItemSpecTrainingOneParallelismTensorParallelSizeExclusiveMin
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingOneParallelismTensorParallelSizeDefault
                        )
                        .describe('Tensor parallel size.'),
                      pipeline_parallel_size: zod
                        .number()
                        .gt(
                          customizationListJobsResponseDataItemSpecTrainingOneParallelismPipelineParallelSizeExclusiveMin
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingOneParallelismPipelineParallelSizeDefault
                        )
                        .describe('Pipeline parallel size.'),
                      context_parallel_size: zod
                        .number()
                        .gt(
                          customizationListJobsResponseDataItemSpecTrainingOneParallelismContextParallelSizeExclusiveMin
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingOneParallelismContextParallelSizeDefault
                        )
                        .describe('Context parallel size.'),
                      expert_parallel_size: zod
                        .number()
                        .optional()
                        .describe('Expert parallel size (MoE models).'),
                      sequence_parallel: zod
                        .boolean()
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingOneParallelismSequenceParallelDefault
                        )
                        .describe('Enable sequence parallelism.'),
                    })
                    .optional()
                    .describe(
                      'Distributed training parallelism configuration.\n\nMost users only need num_gpus_per_node. Advanced users can configure\ntensor\/pipeline\/context\/expert parallelism for large models.'
                    ),
                  execution_profile: zod
                    .string()
                    .optional()
                    .describe(
                      "Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default."
                    ),
                  type: zod
                    .literal('sft')
                    .default(customizationListJobsResponseDataItemSpecTrainingOneTypeDefault),
                })
                .describe('Supervised Fine-Tuning.'),
              zod
                .object({
                  peft: zod
                    .object({
                      quantization: zod
                        .object({
                          precision: zod
                            .enum(['4bit', '8bit'])
                            .default(
                              customizationListJobsResponseDataItemSpecTrainingTwoPeftOneQuantizationOnePrecisionDefault
                            )
                            .describe(
                              "Quantization precision. '4bit' (NF4) for maximum memory savings, '8bit' (LLM.int8) for a balance of quality and memory."
                            ),
                        })
                        .describe(
                          'Base model quantization for memory-efficient PEFT training.\n\nSupports two scenarios:\n- Full-precision base model: quantized on-the-fly at load time\n- Pre-quantized base model: loaded directly at the specified precision\n\nIn both cases, base model weights are frozen and only the PEFT adapter\nparameters are trained in full precision.'
                        )
                        .optional()
                        .describe(
                          'Enable quantized training to reduce GPU memory. If the base model is full-precision, it will be quantized at load time. If the base model is already pre-quantized, this configures the expected precision. The trained adapter remains full-precision.'
                        ),
                      type: zod
                        .literal('lora')
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingTwoPeftOneTypeDefault
                        ),
                      rank: zod
                        .number()
                        .min(1)
                        .max(customizationListJobsResponseDataItemSpecTrainingTwoPeftOneRankMax)
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingTwoPeftOneRankDefault
                        )
                        .describe(
                          'LoRA rank (low-rank dimension). Higher values increase capacity but use more memory.'
                        ),
                      alpha: zod
                        .number()
                        .min(1)
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingTwoPeftOneAlphaDefault
                        )
                        .describe('LoRA alpha scaling factor. Common practice: alpha = 2-4x rank.'),
                      dropout: zod
                        .number()
                        .min(customizationListJobsResponseDataItemSpecTrainingTwoPeftOneDropoutMin)
                        .max(customizationListJobsResponseDataItemSpecTrainingTwoPeftOneDropoutMax)
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingTwoPeftOneDropoutDefault
                        )
                        .describe('LoRA dropout probability for regularization.'),
                      target_modules: zod
                        .array(zod.string())
                        .optional()
                        .describe(
                          "Module name patterns to apply LoRA to (e.g., ['\*.q_proj', '\*.v_proj']). If not set, applies to all '\*proj' linear layers."
                        ),
                      merge: zod
                        .boolean()
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingTwoPeftOneMergeDefault
                        )
                        .describe(
                          'Merge LoRA weights into base model after training. Produces a full-weight checkpoint instead of an adapter.'
                        ),
                      use_dora: zod
                        .boolean()
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingTwoPeftOneUseDoraDefault
                        )
                        .describe(
                          'Enable DoRA (Weight-Decomposed Low-Rank Adaptation). Decomposes weight updates into magnitude and direction components. Can improve quality especially at low ranks, but adds training overhead.'
                        ),
                    })
                    .describe('LoRA adapter configuration.')
                    .optional()
                    .describe(
                      'PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning.'
                    ),
                  learning_rate: zod
                    .number()
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingTwoLearningRateDefault
                    )
                    .describe(
                      'Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning.'
                    ),
                  min_learning_rate: zod
                    .number()
                    .optional()
                    .describe(
                      'Minimum learning rate for cosine decay. Optional; used with learning rate schedules.'
                    ),
                  weight_decay: zod
                    .number()
                    .default(customizationListJobsResponseDataItemSpecTrainingTwoWeightDecayDefault)
                    .describe('Weight decay coefficient. Helps prevent overfitting.'),
                  adam_beta1: zod
                    .number()
                    .default(customizationListJobsResponseDataItemSpecTrainingTwoAdamBeta1Default)
                    .describe('Adam beta1 parameter. Adjust for optimizer tuning.'),
                  adam_beta2: zod
                    .number()
                    .default(customizationListJobsResponseDataItemSpecTrainingTwoAdamBeta2Default)
                    .describe('Adam beta2 parameter. Adjust for optimizer tuning.'),
                  warmup_steps: zod
                    .number()
                    .min(customizationListJobsResponseDataItemSpecTrainingTwoWarmupStepsMin)
                    .default(customizationListJobsResponseDataItemSpecTrainingTwoWarmupStepsDefault)
                    .describe(
                      'Linear warmup steps. Recommended: 10% of total training steps for stable training.'
                    ),
                  optimizer: zod.string().optional().describe("Optimizer name (e.g., 'adamw')."),
                  epochs: zod
                    .number()
                    .gt(customizationListJobsResponseDataItemSpecTrainingTwoEpochsExclusiveMin)
                    .default(customizationListJobsResponseDataItemSpecTrainingTwoEpochsDefault)
                    .describe(
                      'Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.'
                    ),
                  max_steps: zod
                    .number()
                    .optional()
                    .describe('Max training steps. Overrides epochs if set.'),
                  log_every_n_steps: zod
                    .number()
                    .optional()
                    .describe(
                      'Logging frequency in steps. Controls how often training metrics are logged.'
                    ),
                  val_check_interval: zod
                    .number()
                    .optional()
                    .describe(
                      'Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count.'
                    ),
                  batch_size: zod
                    .number()
                    .gt(customizationListJobsResponseDataItemSpecTrainingTwoBatchSizeExclusiveMin)
                    .default(customizationListJobsResponseDataItemSpecTrainingTwoBatchSizeDefault)
                    .describe(
                      'Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.'
                    ),
                  micro_batch_size: zod
                    .number()
                    .gt(
                      customizationListJobsResponseDataItemSpecTrainingTwoMicroBatchSizeExclusiveMin
                    )
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingTwoMicroBatchSizeDefault
                    )
                    .describe(
                      'Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.'
                    ),
                  sequence_packing: zod
                    .boolean()
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingTwoSequencePackingDefault
                    )
                    .describe(
                      'Enable sequence packing for efficiency. Can improve training speed.'
                    ),
                  max_seq_length: zod
                    .number()
                    .gt(
                      customizationListJobsResponseDataItemSpecTrainingTwoMaxSeqLengthExclusiveMin
                    )
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingTwoMaxSeqLengthDefault
                    )
                    .describe(
                      'Maximum token sequence length for training. Higher = more memory, longer training.'
                    ),
                  precision: zod
                    .enum(['fp8', 'bf16', 'fp16', 'fp32'])
                    .describe('Model precision for training.')
                    .optional()
                    .describe('Model precision for training. Auto-detected if unset.'),
                  seed: zod
                    .number()
                    .optional()
                    .describe('Random seed for reproducibility. Optional.'),
                  parallelism: zod
                    .object({
                      num_gpus_per_node: zod
                        .number()
                        .gt(
                          customizationListJobsResponseDataItemSpecTrainingTwoParallelismNumGpusPerNodeExclusiveMin
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingTwoParallelismNumGpusPerNodeDefault
                        )
                        .describe('Number of gpus per node.'),
                      num_nodes: zod
                        .number()
                        .gt(
                          customizationListJobsResponseDataItemSpecTrainingTwoParallelismNumNodesExclusiveMin
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingTwoParallelismNumNodesDefault
                        )
                        .describe('Number of nodes.'),
                      tensor_parallel_size: zod
                        .number()
                        .gt(
                          customizationListJobsResponseDataItemSpecTrainingTwoParallelismTensorParallelSizeExclusiveMin
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingTwoParallelismTensorParallelSizeDefault
                        )
                        .describe('Tensor parallel size.'),
                      pipeline_parallel_size: zod
                        .number()
                        .gt(
                          customizationListJobsResponseDataItemSpecTrainingTwoParallelismPipelineParallelSizeExclusiveMin
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingTwoParallelismPipelineParallelSizeDefault
                        )
                        .describe('Pipeline parallel size.'),
                      context_parallel_size: zod
                        .number()
                        .gt(
                          customizationListJobsResponseDataItemSpecTrainingTwoParallelismContextParallelSizeExclusiveMin
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingTwoParallelismContextParallelSizeDefault
                        )
                        .describe('Context parallel size.'),
                      expert_parallel_size: zod
                        .number()
                        .optional()
                        .describe('Expert parallel size (MoE models).'),
                      sequence_parallel: zod
                        .boolean()
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingTwoParallelismSequenceParallelDefault
                        )
                        .describe('Enable sequence parallelism.'),
                    })
                    .optional()
                    .describe(
                      'Distributed training parallelism configuration.\n\nMost users only need num_gpus_per_node. Advanced users can configure\ntensor\/pipeline\/context\/expert parallelism for large models.'
                    ),
                  execution_profile: zod
                    .string()
                    .optional()
                    .describe(
                      "Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default."
                    ),
                  type: zod
                    .literal('distillation')
                    .default(customizationListJobsResponseDataItemSpecTrainingTwoTypeDefault),
                  teacher_model: zod
                    .string()
                    .describe(
                      "Teacher model URN (e.g., 'workspace\/model-name'). Must have the same vocabulary as the student model."
                    ),
                  teacher_precision: zod
                    .enum(['bf16', 'fp16', 'fp32'])
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingTwoTeacherPrecisionDefault
                    )
                    .describe(
                      'Precision for loading the frozen teacher model. Lower precision reduces memory but may affect logit quality.'
                    ),
                  distillation_ratio: zod
                    .number()
                    .min(customizationListJobsResponseDataItemSpecTrainingTwoDistillationRatioMin)
                    .max(customizationListJobsResponseDataItemSpecTrainingTwoDistillationRatioMax)
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingTwoDistillationRatioDefault
                    )
                    .describe('Balance between CE loss and KD loss. 0.0 = CE only, 1.0 = KD only.'),
                  distillation_temperature: zod
                    .number()
                    .gt(
                      customizationListJobsResponseDataItemSpecTrainingTwoDistillationTemperatureExclusiveMin
                    )
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingTwoDistillationTemperatureDefault
                    )
                    .describe(
                      'Softmax temperature for KD. Higher = softer probability distributions.'
                    ),
                })
                .describe(
                  "Knowledge Distillation with a teacher model.\n\nCustomizer's differentiator — not available in Unsloth.\nTrains the student model to match the teacher's output distribution."
                ),
              zod
                .object({
                  peft: zod
                    .object({
                      quantization: zod
                        .object({
                          precision: zod
                            .enum(['4bit', '8bit'])
                            .default(
                              customizationListJobsResponseDataItemSpecTrainingThreePeftOneQuantizationOnePrecisionDefault
                            )
                            .describe(
                              "Quantization precision. '4bit' (NF4) for maximum memory savings, '8bit' (LLM.int8) for a balance of quality and memory."
                            ),
                        })
                        .describe(
                          'Base model quantization for memory-efficient PEFT training.\n\nSupports two scenarios:\n- Full-precision base model: quantized on-the-fly at load time\n- Pre-quantized base model: loaded directly at the specified precision\n\nIn both cases, base model weights are frozen and only the PEFT adapter\nparameters are trained in full precision.'
                        )
                        .optional()
                        .describe(
                          'Enable quantized training to reduce GPU memory. If the base model is full-precision, it will be quantized at load time. If the base model is already pre-quantized, this configures the expected precision. The trained adapter remains full-precision.'
                        ),
                      type: zod
                        .literal('lora')
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingThreePeftOneTypeDefault
                        ),
                      rank: zod
                        .number()
                        .min(1)
                        .max(customizationListJobsResponseDataItemSpecTrainingThreePeftOneRankMax)
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingThreePeftOneRankDefault
                        )
                        .describe(
                          'LoRA rank (low-rank dimension). Higher values increase capacity but use more memory.'
                        ),
                      alpha: zod
                        .number()
                        .min(1)
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingThreePeftOneAlphaDefault
                        )
                        .describe('LoRA alpha scaling factor. Common practice: alpha = 2-4x rank.'),
                      dropout: zod
                        .number()
                        .min(
                          customizationListJobsResponseDataItemSpecTrainingThreePeftOneDropoutMin
                        )
                        .max(
                          customizationListJobsResponseDataItemSpecTrainingThreePeftOneDropoutMax
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingThreePeftOneDropoutDefault
                        )
                        .describe('LoRA dropout probability for regularization.'),
                      target_modules: zod
                        .array(zod.string())
                        .optional()
                        .describe(
                          "Module name patterns to apply LoRA to (e.g., ['\*.q_proj', '\*.v_proj']). If not set, applies to all '\*proj' linear layers."
                        ),
                      merge: zod
                        .boolean()
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingThreePeftOneMergeDefault
                        )
                        .describe(
                          'Merge LoRA weights into base model after training. Produces a full-weight checkpoint instead of an adapter.'
                        ),
                      use_dora: zod
                        .boolean()
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingThreePeftOneUseDoraDefault
                        )
                        .describe(
                          'Enable DoRA (Weight-Decomposed Low-Rank Adaptation). Decomposes weight updates into magnitude and direction components. Can improve quality especially at low ranks, but adds training overhead.'
                        ),
                    })
                    .describe('LoRA adapter configuration.')
                    .optional()
                    .describe(
                      'PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning.'
                    ),
                  learning_rate: zod
                    .number()
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingThreeLearningRateDefault
                    )
                    .describe(
                      'Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning.'
                    ),
                  min_learning_rate: zod
                    .number()
                    .optional()
                    .describe(
                      'Minimum learning rate for cosine decay. Optional; used with learning rate schedules.'
                    ),
                  weight_decay: zod
                    .number()
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingThreeWeightDecayDefault
                    )
                    .describe('Weight decay coefficient. Helps prevent overfitting.'),
                  adam_beta1: zod
                    .number()
                    .default(customizationListJobsResponseDataItemSpecTrainingThreeAdamBeta1Default)
                    .describe('Adam beta1 parameter. Adjust for optimizer tuning.'),
                  adam_beta2: zod
                    .number()
                    .default(customizationListJobsResponseDataItemSpecTrainingThreeAdamBeta2Default)
                    .describe('Adam beta2 parameter. Adjust for optimizer tuning.'),
                  warmup_steps: zod
                    .number()
                    .min(customizationListJobsResponseDataItemSpecTrainingThreeWarmupStepsMin)
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingThreeWarmupStepsDefault
                    )
                    .describe(
                      'Linear warmup steps. Recommended: 10% of total training steps for stable training.'
                    ),
                  optimizer: zod.string().optional().describe("Optimizer name (e.g., 'adamw')."),
                  epochs: zod
                    .number()
                    .gt(customizationListJobsResponseDataItemSpecTrainingThreeEpochsExclusiveMin)
                    .default(customizationListJobsResponseDataItemSpecTrainingThreeEpochsDefault)
                    .describe(
                      'Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.'
                    ),
                  max_steps: zod
                    .number()
                    .optional()
                    .describe('Max training steps. Overrides epochs if set.'),
                  log_every_n_steps: zod
                    .number()
                    .optional()
                    .describe(
                      'Logging frequency in steps. Controls how often training metrics are logged.'
                    ),
                  val_check_interval: zod
                    .number()
                    .optional()
                    .describe(
                      'Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count.'
                    ),
                  batch_size: zod
                    .number()
                    .gt(customizationListJobsResponseDataItemSpecTrainingThreeBatchSizeExclusiveMin)
                    .default(customizationListJobsResponseDataItemSpecTrainingThreeBatchSizeDefault)
                    .describe(
                      'Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.'
                    ),
                  micro_batch_size: zod
                    .number()
                    .gt(
                      customizationListJobsResponseDataItemSpecTrainingThreeMicroBatchSizeExclusiveMin
                    )
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingThreeMicroBatchSizeDefault
                    )
                    .describe(
                      'Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.'
                    ),
                  sequence_packing: zod
                    .boolean()
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingThreeSequencePackingDefault
                    )
                    .describe(
                      'Enable sequence packing for efficiency. Can improve training speed.'
                    ),
                  max_seq_length: zod
                    .number()
                    .gt(
                      customizationListJobsResponseDataItemSpecTrainingThreeMaxSeqLengthExclusiveMin
                    )
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingThreeMaxSeqLengthDefault
                    )
                    .describe(
                      'Maximum token sequence length for training. Higher = more memory, longer training.'
                    ),
                  precision: zod
                    .enum(['fp8', 'bf16', 'fp16', 'fp32'])
                    .describe('Model precision for training.')
                    .optional()
                    .describe('Model precision for training. Auto-detected if unset.'),
                  seed: zod
                    .number()
                    .optional()
                    .describe('Random seed for reproducibility. Optional.'),
                  parallelism: zod
                    .object({
                      num_gpus_per_node: zod
                        .number()
                        .gt(
                          customizationListJobsResponseDataItemSpecTrainingThreeParallelismNumGpusPerNodeExclusiveMin
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingThreeParallelismNumGpusPerNodeDefault
                        )
                        .describe('Number of gpus per node.'),
                      num_nodes: zod
                        .number()
                        .gt(
                          customizationListJobsResponseDataItemSpecTrainingThreeParallelismNumNodesExclusiveMin
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingThreeParallelismNumNodesDefault
                        )
                        .describe('Number of nodes.'),
                      tensor_parallel_size: zod
                        .number()
                        .gt(
                          customizationListJobsResponseDataItemSpecTrainingThreeParallelismTensorParallelSizeExclusiveMin
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingThreeParallelismTensorParallelSizeDefault
                        )
                        .describe('Tensor parallel size.'),
                      pipeline_parallel_size: zod
                        .number()
                        .gt(
                          customizationListJobsResponseDataItemSpecTrainingThreeParallelismPipelineParallelSizeExclusiveMin
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingThreeParallelismPipelineParallelSizeDefault
                        )
                        .describe('Pipeline parallel size.'),
                      context_parallel_size: zod
                        .number()
                        .gt(
                          customizationListJobsResponseDataItemSpecTrainingThreeParallelismContextParallelSizeExclusiveMin
                        )
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingThreeParallelismContextParallelSizeDefault
                        )
                        .describe('Context parallel size.'),
                      expert_parallel_size: zod
                        .number()
                        .optional()
                        .describe('Expert parallel size (MoE models).'),
                      sequence_parallel: zod
                        .boolean()
                        .default(
                          customizationListJobsResponseDataItemSpecTrainingThreeParallelismSequenceParallelDefault
                        )
                        .describe('Enable sequence parallelism.'),
                    })
                    .optional()
                    .describe(
                      'Distributed training parallelism configuration.\n\nMost users only need num_gpus_per_node. Advanced users can configure\ntensor\/pipeline\/context\/expert parallelism for large models.'
                    ),
                  execution_profile: zod
                    .string()
                    .optional()
                    .describe(
                      "Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default."
                    ),
                  type: zod
                    .literal('dpo')
                    .default(customizationListJobsResponseDataItemSpecTrainingThreeTypeDefault),
                  ref_policy_kl_penalty: zod
                    .number()
                    .min(
                      customizationListJobsResponseDataItemSpecTrainingThreeRefPolicyKlPenaltyMin
                    )
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingThreeRefPolicyKlPenaltyDefault
                    )
                    .describe('KL penalty coefficient (beta in DPO paper).'),
                  preference_average_log_probs: zod
                    .boolean()
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingThreePreferenceAverageLogProbsDefault
                    )
                    .describe('Average log probabilities for preference loss calculation.'),
                  sft_average_log_probs: zod
                    .boolean()
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingThreeSftAverageLogProbsDefault
                    )
                    .describe('Average log probabilities for SFT regularization loss.'),
                  preference_loss_weight: zod
                    .number()
                    .min(
                      customizationListJobsResponseDataItemSpecTrainingThreePreferenceLossWeightMin
                    )
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingThreePreferenceLossWeightDefault
                    )
                    .describe('Weight for the preference (DPO) loss term.'),
                  sft_loss_weight: zod
                    .number()
                    .min(customizationListJobsResponseDataItemSpecTrainingThreeSftLossWeightMin)
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingThreeSftLossWeightDefault
                    )
                    .describe('Weight for SFT regularization loss (0 = disabled).'),
                  max_grad_norm: zod
                    .number()
                    .min(customizationListJobsResponseDataItemSpecTrainingThreeMaxGradNormMin)
                    .default(
                      customizationListJobsResponseDataItemSpecTrainingThreeMaxGradNormDefault
                    )
                    .describe('Maximum gradient norm for clipping.'),
                })
                .describe('Direct Preference Optimization.'),
            ])
            .describe('Training method and hyperparameters.'),
          integrations: zod
            .object({
              wandb: zod
                .object({
                  project: zod
                    .string()
                    .optional()
                    .describe(
                      'W&B project name (groups related runs). Defaults to output.name if not set.'
                    ),
                  name: zod
                    .string()
                    .optional()
                    .describe('W&B run name. Defaults to job_id if not provided.'),
                  entity: zod.string().optional().describe('W&B entity (team or username).'),
                  tags: zod.array(zod.string()).optional().describe('W&B tags for filtering runs.'),
                  notes: zod.string().optional().describe('W&B notes\/description for the run.'),
                  base_url: zod
                    .string()
                    .optional()
                    .describe(
                      "Base URL for self-hosted W&B server (e.g., 'https:\/\/wandb.mycompany.com'). If not provided, uses the default W&B cloud service."
                    ),
                  api_key_secret: zod
                    .string()
                    .regex(
                      customizationListJobsResponseDataItemSpecIntegrationsOneWandbOneApiKeySecretOneRegExp
                    )
                    .describe(
                      "Reference to a secret. Format: 'secret_name' (uses request workspace) or 'workspace\/secret_name' (explicit workspace)."
                    )
                    .optional()
                    .describe(
                      "Reference to a secret containing the WANDB_API_KEY. Format: 'secret_name' (uses request workspace) or 'workspace\/secret_name' (explicit workspace)."
                    ),
                })
                .describe(
                  'Weights & Biases integration configuration.\n\nTo use W&B, provide an api_key_secret referencing a secret that contains\nthe WANDB_API_KEY value. Optionally provide base_url for self-hosted W&B servers.'
                )
                .optional()
                .describe('Weights & Biases integration configuration.'),
              mlflow: zod
                .object({
                  experiment_name: zod
                    .string()
                    .optional()
                    .describe(
                      'MLflow experiment name (groups related runs). Defaults to output.name if not set.'
                    ),
                  run_name: zod
                    .string()
                    .optional()
                    .describe('MLflow run name. Defaults to job_id if not provided.'),
                  tags: zod
                    .record(zod.string(), zod.string())
                    .optional()
                    .describe('MLflow tags as key-value pairs for filtering runs.'),
                  description: zod.string().optional().describe('MLflow run description.'),
                  tracking_uri: zod
                    .string()
                    .optional()
                    .describe(
                      "MLflow tracking server URI (e.g., 'http:\/\/mlflow.mycompany.com:5000'). Can also be set via MLFLOW_TRACKING_URI environment variable."
                    ),
                })
                .describe('MLflow integration configuration.')
                .optional()
                .describe('MLflow integration configuration.'),
            })
            .describe(
              'Third-party integration configurations.\n\nEach integration type has its own optional field. To enable an integration,\nprovide its configuration object. Omit or set to None to disable.'
            )
            .optional()
            .describe('Third-party integrations (e.g., Weights & Biases, MLflow).'),
          deployment_config: zod
            .union([
              zod.string().describe('A reference to DeploymentParams.'),
              zod
                .object({
                  gpu: zod
                    .number()
                    .default(customizationListJobsResponseDataItemSpecDeploymentConfigTwoGpuDefault)
                    .describe('Number of GPUs required for the deployment'),
                  additional_envs: zod
                    .record(zod.string(), zod.string())
                    .optional()
                    .describe('Additional environment variables for the deployment'),
                  disk_size: zod.string().optional().describe('Disk size for the deployment'),
                  image_name: zod
                    .string()
                    .optional()
                    .describe(
                      'Container image name from NGC. If not specified, defaults to multi-llm'
                    ),
                  image_tag: zod.string().optional().describe('Container image tag from NGC'),
                  lora_enabled: zod
                    .boolean()
                    .default(
                      customizationListJobsResponseDataItemSpecDeploymentConfigTwoLoraEnabledDefault
                    )
                    .describe(
                      'When automatically deploying a full SFT training, this parameter being set to true will allow subsequent LoRA adapters to be trained and deployed against it.'
                    ),
                  tool_call_config: zod
                    .object({
                      tool_call_parser: zod
                        .string()
                        .optional()
                        .describe(
                          "Name of the tool call parser to use (e.g., 'openai', 'hermes', 'pythonic', 'llama3_json', 'mistral')."
                        ),
                      tool_call_plugin: zod
                        .string()
                        .regex(
                          customizationListJobsResponseDataItemSpecDeploymentConfigTwoToolCallConfigOneToolCallPluginRegExp
                        )
                        .optional()
                        .describe(
                          "Reference to a fileset containing the custom tool call plugin Python file. Expected format: '{workspace}\/{fileset_name}'."
                        ),
                      auto_tool_choice: zod
                        .boolean()
                        .optional()
                        .describe('Whether to enable automatic tool choice.'),
                    })
                    .describe('Tool calling configuration for NIM deployments.')
                    .optional()
                    .describe('Tool calling configuration override for the NIM deployment.'),
                })
                .describe('Inline deployment parameters for creating a new ModelDeploymentConfig.'),
            ])
            .optional()
            .describe(
              "Deployment configuration for auto-deploying the model after training. Pass a string to reference an existing ModelDeploymentConfig by name (e.g., 'my-config' or 'workspace\/my-config'). An object provides inline NIM deployment parameters. Omit to skip deployment."
            ),
          custom_fields: zod
            .record(zod.string(), zod.unknown())
            .optional()
            .describe('Custom user-defined fields.'),
          output: zod
            .object({
              name: zod
                .string()
                .max(customizationListJobsResponseDataItemSpecOutputOneNameMax)
                .regex(customizationListJobsResponseDataItemSpecOutputOneNameRegExp)
                .describe(
                  'Name of the output artifact. Used to identify it during deployment and inference.'
                ),
              type: zod
                .enum(['adapter', 'model'])
                .describe('Output artifact type.')
                .describe(
                  'Output artifact type. Either `model` (full fine-tuned weights) or `adapter` (LoRA adapter weights).'
                ),
              fileset: zod
                .string()
                .max(customizationListJobsResponseDataItemSpecOutputOneFilesetMax)
                .regex(customizationListJobsResponseDataItemSpecOutputOneFilesetRegExp)
                .describe('FileSet name where output artifacts are stored.'),
            })
            .describe('Resolved output artifact details returned by the server.')
            .describe('Output artifact created by this job.'),
        })
        .describe('Customization job details returned by the server.'),
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
 * @summary Get Job Result
 */
export const CustomizationGetJobResultParams = zod.object({
  workspace: zod.string(),
  job: zod.string(),
  name: zod.string(),
});

export const CustomizationGetJobResultResponse = zod.object({
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
export const CustomizationDownloadJobResultParams = zod.object({
  workspace: zod.string(),
  job: zod.string(),
  name: zod.string(),
});

/**
 * @summary Get Job
 */
export const CustomizationGetJobParams = zod.object({
  workspace: zod.string(),
  name: zod.string(),
});

export const customizationGetJobResponseSpecTrainingOnePeftOneQuantizationOnePrecisionDefault = `4bit`;
export const customizationGetJobResponseSpecTrainingOnePeftOneTypeDefault = `lora`;
export const customizationGetJobResponseSpecTrainingOnePeftOneRankDefault = 8;
export const customizationGetJobResponseSpecTrainingOnePeftOneRankMax = 256;

export const customizationGetJobResponseSpecTrainingOnePeftOneAlphaDefault = 32;

export const customizationGetJobResponseSpecTrainingOnePeftOneDropoutDefault = 0;
export const customizationGetJobResponseSpecTrainingOnePeftOneDropoutMin = 0;
export const customizationGetJobResponseSpecTrainingOnePeftOneDropoutMax = 1;

export const customizationGetJobResponseSpecTrainingOnePeftOneMergeDefault = false;
export const customizationGetJobResponseSpecTrainingOnePeftOneUseDoraDefault = false;
export const customizationGetJobResponseSpecTrainingOneLearningRateDefault = 0.0001;
export const customizationGetJobResponseSpecTrainingOneWeightDecayDefault = 0.01;
export const customizationGetJobResponseSpecTrainingOneAdamBeta1Default = 0.9;
export const customizationGetJobResponseSpecTrainingOneAdamBeta2Default = 0.999;
export const customizationGetJobResponseSpecTrainingOneWarmupStepsDefault = 0;
export const customizationGetJobResponseSpecTrainingOneWarmupStepsMin = 0;

export const customizationGetJobResponseSpecTrainingOneEpochsDefault = 1;
export const customizationGetJobResponseSpecTrainingOneEpochsExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingOneBatchSizeDefault = 32;
export const customizationGetJobResponseSpecTrainingOneBatchSizeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingOneMicroBatchSizeDefault = 1;
export const customizationGetJobResponseSpecTrainingOneMicroBatchSizeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingOneSequencePackingDefault = false;
export const customizationGetJobResponseSpecTrainingOneMaxSeqLengthDefault = 2048;
export const customizationGetJobResponseSpecTrainingOneMaxSeqLengthExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingOneParallelismNumGpusPerNodeDefault = 1;
export const customizationGetJobResponseSpecTrainingOneParallelismNumGpusPerNodeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingOneParallelismNumNodesDefault = 1;
export const customizationGetJobResponseSpecTrainingOneParallelismNumNodesExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingOneParallelismTensorParallelSizeDefault = 1;
export const customizationGetJobResponseSpecTrainingOneParallelismTensorParallelSizeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingOneParallelismPipelineParallelSizeDefault = 1;
export const customizationGetJobResponseSpecTrainingOneParallelismPipelineParallelSizeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingOneParallelismContextParallelSizeDefault = 1;
export const customizationGetJobResponseSpecTrainingOneParallelismContextParallelSizeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingOneParallelismSequenceParallelDefault = false;
export const customizationGetJobResponseSpecTrainingOneTypeDefault = `sft`;
export const customizationGetJobResponseSpecTrainingTwoPeftOneQuantizationOnePrecisionDefault = `4bit`;
export const customizationGetJobResponseSpecTrainingTwoPeftOneTypeDefault = `lora`;
export const customizationGetJobResponseSpecTrainingTwoPeftOneRankDefault = 8;
export const customizationGetJobResponseSpecTrainingTwoPeftOneRankMax = 256;

export const customizationGetJobResponseSpecTrainingTwoPeftOneAlphaDefault = 32;

export const customizationGetJobResponseSpecTrainingTwoPeftOneDropoutDefault = 0;
export const customizationGetJobResponseSpecTrainingTwoPeftOneDropoutMin = 0;
export const customizationGetJobResponseSpecTrainingTwoPeftOneDropoutMax = 1;

export const customizationGetJobResponseSpecTrainingTwoPeftOneMergeDefault = false;
export const customizationGetJobResponseSpecTrainingTwoPeftOneUseDoraDefault = false;
export const customizationGetJobResponseSpecTrainingTwoLearningRateDefault = 0.0001;
export const customizationGetJobResponseSpecTrainingTwoWeightDecayDefault = 0.01;
export const customizationGetJobResponseSpecTrainingTwoAdamBeta1Default = 0.9;
export const customizationGetJobResponseSpecTrainingTwoAdamBeta2Default = 0.999;
export const customizationGetJobResponseSpecTrainingTwoWarmupStepsDefault = 0;
export const customizationGetJobResponseSpecTrainingTwoWarmupStepsMin = 0;

export const customizationGetJobResponseSpecTrainingTwoEpochsDefault = 1;
export const customizationGetJobResponseSpecTrainingTwoEpochsExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingTwoBatchSizeDefault = 32;
export const customizationGetJobResponseSpecTrainingTwoBatchSizeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingTwoMicroBatchSizeDefault = 1;
export const customizationGetJobResponseSpecTrainingTwoMicroBatchSizeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingTwoSequencePackingDefault = false;
export const customizationGetJobResponseSpecTrainingTwoMaxSeqLengthDefault = 2048;
export const customizationGetJobResponseSpecTrainingTwoMaxSeqLengthExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingTwoParallelismNumGpusPerNodeDefault = 1;
export const customizationGetJobResponseSpecTrainingTwoParallelismNumGpusPerNodeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingTwoParallelismNumNodesDefault = 1;
export const customizationGetJobResponseSpecTrainingTwoParallelismNumNodesExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingTwoParallelismTensorParallelSizeDefault = 1;
export const customizationGetJobResponseSpecTrainingTwoParallelismTensorParallelSizeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingTwoParallelismPipelineParallelSizeDefault = 1;
export const customizationGetJobResponseSpecTrainingTwoParallelismPipelineParallelSizeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingTwoParallelismContextParallelSizeDefault = 1;
export const customizationGetJobResponseSpecTrainingTwoParallelismContextParallelSizeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingTwoParallelismSequenceParallelDefault = false;
export const customizationGetJobResponseSpecTrainingTwoTypeDefault = `distillation`;
export const customizationGetJobResponseSpecTrainingTwoTeacherPrecisionDefault = `bf16`;
export const customizationGetJobResponseSpecTrainingTwoDistillationRatioDefault = 0.5;
export const customizationGetJobResponseSpecTrainingTwoDistillationRatioMin = 0;
export const customizationGetJobResponseSpecTrainingTwoDistillationRatioMax = 1;

export const customizationGetJobResponseSpecTrainingTwoDistillationTemperatureDefault = 1;
export const customizationGetJobResponseSpecTrainingTwoDistillationTemperatureExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingThreePeftOneQuantizationOnePrecisionDefault = `4bit`;
export const customizationGetJobResponseSpecTrainingThreePeftOneTypeDefault = `lora`;
export const customizationGetJobResponseSpecTrainingThreePeftOneRankDefault = 8;
export const customizationGetJobResponseSpecTrainingThreePeftOneRankMax = 256;

export const customizationGetJobResponseSpecTrainingThreePeftOneAlphaDefault = 32;

export const customizationGetJobResponseSpecTrainingThreePeftOneDropoutDefault = 0;
export const customizationGetJobResponseSpecTrainingThreePeftOneDropoutMin = 0;
export const customizationGetJobResponseSpecTrainingThreePeftOneDropoutMax = 1;

export const customizationGetJobResponseSpecTrainingThreePeftOneMergeDefault = false;
export const customizationGetJobResponseSpecTrainingThreePeftOneUseDoraDefault = false;
export const customizationGetJobResponseSpecTrainingThreeLearningRateDefault = 0.0001;
export const customizationGetJobResponseSpecTrainingThreeWeightDecayDefault = 0.01;
export const customizationGetJobResponseSpecTrainingThreeAdamBeta1Default = 0.9;
export const customizationGetJobResponseSpecTrainingThreeAdamBeta2Default = 0.999;
export const customizationGetJobResponseSpecTrainingThreeWarmupStepsDefault = 0;
export const customizationGetJobResponseSpecTrainingThreeWarmupStepsMin = 0;

export const customizationGetJobResponseSpecTrainingThreeEpochsDefault = 1;
export const customizationGetJobResponseSpecTrainingThreeEpochsExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingThreeBatchSizeDefault = 32;
export const customizationGetJobResponseSpecTrainingThreeBatchSizeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingThreeMicroBatchSizeDefault = 1;
export const customizationGetJobResponseSpecTrainingThreeMicroBatchSizeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingThreeSequencePackingDefault = false;
export const customizationGetJobResponseSpecTrainingThreeMaxSeqLengthDefault = 2048;
export const customizationGetJobResponseSpecTrainingThreeMaxSeqLengthExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingThreeParallelismNumGpusPerNodeDefault = 1;
export const customizationGetJobResponseSpecTrainingThreeParallelismNumGpusPerNodeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingThreeParallelismNumNodesDefault = 1;
export const customizationGetJobResponseSpecTrainingThreeParallelismNumNodesExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingThreeParallelismTensorParallelSizeDefault = 1;
export const customizationGetJobResponseSpecTrainingThreeParallelismTensorParallelSizeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingThreeParallelismPipelineParallelSizeDefault = 1;
export const customizationGetJobResponseSpecTrainingThreeParallelismPipelineParallelSizeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingThreeParallelismContextParallelSizeDefault = 1;
export const customizationGetJobResponseSpecTrainingThreeParallelismContextParallelSizeExclusiveMin = 0;

export const customizationGetJobResponseSpecTrainingThreeParallelismSequenceParallelDefault = false;
export const customizationGetJobResponseSpecTrainingThreeTypeDefault = `dpo`;
export const customizationGetJobResponseSpecTrainingThreeRefPolicyKlPenaltyDefault = 0.05;
export const customizationGetJobResponseSpecTrainingThreeRefPolicyKlPenaltyMin = 0;

export const customizationGetJobResponseSpecTrainingThreePreferenceAverageLogProbsDefault = false;
export const customizationGetJobResponseSpecTrainingThreeSftAverageLogProbsDefault = false;
export const customizationGetJobResponseSpecTrainingThreePreferenceLossWeightDefault = 1;
export const customizationGetJobResponseSpecTrainingThreePreferenceLossWeightMin = 0;

export const customizationGetJobResponseSpecTrainingThreeSftLossWeightDefault = 0;
export const customizationGetJobResponseSpecTrainingThreeSftLossWeightMin = 0;

export const customizationGetJobResponseSpecTrainingThreeMaxGradNormDefault = 1;
export const customizationGetJobResponseSpecTrainingThreeMaxGradNormMin = 0;

export const customizationGetJobResponseSpecIntegrationsOneWandbOneApiKeySecretOneRegExp =
  new RegExp('^[a-z0-9_-]+(\/[a-z0-9_-]+)?$');
export const customizationGetJobResponseSpecDeploymentConfigTwoGpuDefault = 1;
export const customizationGetJobResponseSpecDeploymentConfigTwoLoraEnabledDefault = true;
export const customizationGetJobResponseSpecDeploymentConfigTwoToolCallConfigOneToolCallPluginRegExp =
  new RegExp('^[\\w\\-.]+\/[\\w\\-.]+$');
export const customizationGetJobResponseSpecOutputOneNameMax = 255;

export const customizationGetJobResponseSpecOutputOneNameRegExp = new RegExp('^[\\w\\-.]+$');
export const customizationGetJobResponseSpecOutputOneFilesetMax = 255;

export const customizationGetJobResponseSpecOutputOneFilesetRegExp = new RegExp('^[\\w\\-.]+$');

export const CustomizationGetJobResponse = zod.object({
  id: zod.string().optional(),
  name: zod.string(),
  description: zod.string().optional(),
  project: zod.string().optional(),
  workspace: zod.string().optional(),
  created_at: zod.string().optional(),
  updated_at: zod.string().optional(),
  spec: zod
    .object({
      model: zod.string().describe("Model reference (e.g., 'workspace\/model-name')."),
      dataset: zod
        .string()
        .describe(
          'Dataset URI. Supported protocol: fileset:\/\/ (e.g., fileset:\/\/workspace\/name).'
        ),
      training: zod
        .union([
          zod
            .object({
              peft: zod
                .object({
                  quantization: zod
                    .object({
                      precision: zod
                        .enum(['4bit', '8bit'])
                        .default(
                          customizationGetJobResponseSpecTrainingOnePeftOneQuantizationOnePrecisionDefault
                        )
                        .describe(
                          "Quantization precision. '4bit' (NF4) for maximum memory savings, '8bit' (LLM.int8) for a balance of quality and memory."
                        ),
                    })
                    .describe(
                      'Base model quantization for memory-efficient PEFT training.\n\nSupports two scenarios:\n- Full-precision base model: quantized on-the-fly at load time\n- Pre-quantized base model: loaded directly at the specified precision\n\nIn both cases, base model weights are frozen and only the PEFT adapter\nparameters are trained in full precision.'
                    )
                    .optional()
                    .describe(
                      'Enable quantized training to reduce GPU memory. If the base model is full-precision, it will be quantized at load time. If the base model is already pre-quantized, this configures the expected precision. The trained adapter remains full-precision.'
                    ),
                  type: zod
                    .literal('lora')
                    .default(customizationGetJobResponseSpecTrainingOnePeftOneTypeDefault),
                  rank: zod
                    .number()
                    .min(1)
                    .max(customizationGetJobResponseSpecTrainingOnePeftOneRankMax)
                    .default(customizationGetJobResponseSpecTrainingOnePeftOneRankDefault)
                    .describe(
                      'LoRA rank (low-rank dimension). Higher values increase capacity but use more memory.'
                    ),
                  alpha: zod
                    .number()
                    .min(1)
                    .default(customizationGetJobResponseSpecTrainingOnePeftOneAlphaDefault)
                    .describe('LoRA alpha scaling factor. Common practice: alpha = 2-4x rank.'),
                  dropout: zod
                    .number()
                    .min(customizationGetJobResponseSpecTrainingOnePeftOneDropoutMin)
                    .max(customizationGetJobResponseSpecTrainingOnePeftOneDropoutMax)
                    .default(customizationGetJobResponseSpecTrainingOnePeftOneDropoutDefault)
                    .describe('LoRA dropout probability for regularization.'),
                  target_modules: zod
                    .array(zod.string())
                    .optional()
                    .describe(
                      "Module name patterns to apply LoRA to (e.g., ['\*.q_proj', '\*.v_proj']). If not set, applies to all '\*proj' linear layers."
                    ),
                  merge: zod
                    .boolean()
                    .default(customizationGetJobResponseSpecTrainingOnePeftOneMergeDefault)
                    .describe(
                      'Merge LoRA weights into base model after training. Produces a full-weight checkpoint instead of an adapter.'
                    ),
                  use_dora: zod
                    .boolean()
                    .default(customizationGetJobResponseSpecTrainingOnePeftOneUseDoraDefault)
                    .describe(
                      'Enable DoRA (Weight-Decomposed Low-Rank Adaptation). Decomposes weight updates into magnitude and direction components. Can improve quality especially at low ranks, but adds training overhead.'
                    ),
                })
                .describe('LoRA adapter configuration.')
                .optional()
                .describe(
                  'PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning.'
                ),
              learning_rate: zod
                .number()
                .default(customizationGetJobResponseSpecTrainingOneLearningRateDefault)
                .describe(
                  'Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning.'
                ),
              min_learning_rate: zod
                .number()
                .optional()
                .describe(
                  'Minimum learning rate for cosine decay. Optional; used with learning rate schedules.'
                ),
              weight_decay: zod
                .number()
                .default(customizationGetJobResponseSpecTrainingOneWeightDecayDefault)
                .describe('Weight decay coefficient. Helps prevent overfitting.'),
              adam_beta1: zod
                .number()
                .default(customizationGetJobResponseSpecTrainingOneAdamBeta1Default)
                .describe('Adam beta1 parameter. Adjust for optimizer tuning.'),
              adam_beta2: zod
                .number()
                .default(customizationGetJobResponseSpecTrainingOneAdamBeta2Default)
                .describe('Adam beta2 parameter. Adjust for optimizer tuning.'),
              warmup_steps: zod
                .number()
                .min(customizationGetJobResponseSpecTrainingOneWarmupStepsMin)
                .default(customizationGetJobResponseSpecTrainingOneWarmupStepsDefault)
                .describe(
                  'Linear warmup steps. Recommended: 10% of total training steps for stable training.'
                ),
              optimizer: zod.string().optional().describe("Optimizer name (e.g., 'adamw')."),
              epochs: zod
                .number()
                .gt(customizationGetJobResponseSpecTrainingOneEpochsExclusiveMin)
                .default(customizationGetJobResponseSpecTrainingOneEpochsDefault)
                .describe(
                  'Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.'
                ),
              max_steps: zod
                .number()
                .optional()
                .describe('Max training steps. Overrides epochs if set.'),
              log_every_n_steps: zod
                .number()
                .optional()
                .describe(
                  'Logging frequency in steps. Controls how often training metrics are logged.'
                ),
              val_check_interval: zod
                .number()
                .optional()
                .describe(
                  'Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count.'
                ),
              batch_size: zod
                .number()
                .gt(customizationGetJobResponseSpecTrainingOneBatchSizeExclusiveMin)
                .default(customizationGetJobResponseSpecTrainingOneBatchSizeDefault)
                .describe(
                  'Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.'
                ),
              micro_batch_size: zod
                .number()
                .gt(customizationGetJobResponseSpecTrainingOneMicroBatchSizeExclusiveMin)
                .default(customizationGetJobResponseSpecTrainingOneMicroBatchSizeDefault)
                .describe(
                  'Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.'
                ),
              sequence_packing: zod
                .boolean()
                .default(customizationGetJobResponseSpecTrainingOneSequencePackingDefault)
                .describe('Enable sequence packing for efficiency. Can improve training speed.'),
              max_seq_length: zod
                .number()
                .gt(customizationGetJobResponseSpecTrainingOneMaxSeqLengthExclusiveMin)
                .default(customizationGetJobResponseSpecTrainingOneMaxSeqLengthDefault)
                .describe(
                  'Maximum token sequence length for training. Higher = more memory, longer training.'
                ),
              precision: zod
                .enum(['fp8', 'bf16', 'fp16', 'fp32'])
                .describe('Model precision for training.')
                .optional()
                .describe('Model precision for training. Auto-detected if unset.'),
              seed: zod.number().optional().describe('Random seed for reproducibility. Optional.'),
              parallelism: zod
                .object({
                  num_gpus_per_node: zod
                    .number()
                    .gt(
                      customizationGetJobResponseSpecTrainingOneParallelismNumGpusPerNodeExclusiveMin
                    )
                    .default(
                      customizationGetJobResponseSpecTrainingOneParallelismNumGpusPerNodeDefault
                    )
                    .describe('Number of gpus per node.'),
                  num_nodes: zod
                    .number()
                    .gt(customizationGetJobResponseSpecTrainingOneParallelismNumNodesExclusiveMin)
                    .default(customizationGetJobResponseSpecTrainingOneParallelismNumNodesDefault)
                    .describe('Number of nodes.'),
                  tensor_parallel_size: zod
                    .number()
                    .gt(
                      customizationGetJobResponseSpecTrainingOneParallelismTensorParallelSizeExclusiveMin
                    )
                    .default(
                      customizationGetJobResponseSpecTrainingOneParallelismTensorParallelSizeDefault
                    )
                    .describe('Tensor parallel size.'),
                  pipeline_parallel_size: zod
                    .number()
                    .gt(
                      customizationGetJobResponseSpecTrainingOneParallelismPipelineParallelSizeExclusiveMin
                    )
                    .default(
                      customizationGetJobResponseSpecTrainingOneParallelismPipelineParallelSizeDefault
                    )
                    .describe('Pipeline parallel size.'),
                  context_parallel_size: zod
                    .number()
                    .gt(
                      customizationGetJobResponseSpecTrainingOneParallelismContextParallelSizeExclusiveMin
                    )
                    .default(
                      customizationGetJobResponseSpecTrainingOneParallelismContextParallelSizeDefault
                    )
                    .describe('Context parallel size.'),
                  expert_parallel_size: zod
                    .number()
                    .optional()
                    .describe('Expert parallel size (MoE models).'),
                  sequence_parallel: zod
                    .boolean()
                    .default(
                      customizationGetJobResponseSpecTrainingOneParallelismSequenceParallelDefault
                    )
                    .describe('Enable sequence parallelism.'),
                })
                .optional()
                .describe(
                  'Distributed training parallelism configuration.\n\nMost users only need num_gpus_per_node. Advanced users can configure\ntensor\/pipeline\/context\/expert parallelism for large models.'
                ),
              execution_profile: zod
                .string()
                .optional()
                .describe(
                  "Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default."
                ),
              type: zod
                .literal('sft')
                .default(customizationGetJobResponseSpecTrainingOneTypeDefault),
            })
            .describe('Supervised Fine-Tuning.'),
          zod
            .object({
              peft: zod
                .object({
                  quantization: zod
                    .object({
                      precision: zod
                        .enum(['4bit', '8bit'])
                        .default(
                          customizationGetJobResponseSpecTrainingTwoPeftOneQuantizationOnePrecisionDefault
                        )
                        .describe(
                          "Quantization precision. '4bit' (NF4) for maximum memory savings, '8bit' (LLM.int8) for a balance of quality and memory."
                        ),
                    })
                    .describe(
                      'Base model quantization for memory-efficient PEFT training.\n\nSupports two scenarios:\n- Full-precision base model: quantized on-the-fly at load time\n- Pre-quantized base model: loaded directly at the specified precision\n\nIn both cases, base model weights are frozen and only the PEFT adapter\nparameters are trained in full precision.'
                    )
                    .optional()
                    .describe(
                      'Enable quantized training to reduce GPU memory. If the base model is full-precision, it will be quantized at load time. If the base model is already pre-quantized, this configures the expected precision. The trained adapter remains full-precision.'
                    ),
                  type: zod
                    .literal('lora')
                    .default(customizationGetJobResponseSpecTrainingTwoPeftOneTypeDefault),
                  rank: zod
                    .number()
                    .min(1)
                    .max(customizationGetJobResponseSpecTrainingTwoPeftOneRankMax)
                    .default(customizationGetJobResponseSpecTrainingTwoPeftOneRankDefault)
                    .describe(
                      'LoRA rank (low-rank dimension). Higher values increase capacity but use more memory.'
                    ),
                  alpha: zod
                    .number()
                    .min(1)
                    .default(customizationGetJobResponseSpecTrainingTwoPeftOneAlphaDefault)
                    .describe('LoRA alpha scaling factor. Common practice: alpha = 2-4x rank.'),
                  dropout: zod
                    .number()
                    .min(customizationGetJobResponseSpecTrainingTwoPeftOneDropoutMin)
                    .max(customizationGetJobResponseSpecTrainingTwoPeftOneDropoutMax)
                    .default(customizationGetJobResponseSpecTrainingTwoPeftOneDropoutDefault)
                    .describe('LoRA dropout probability for regularization.'),
                  target_modules: zod
                    .array(zod.string())
                    .optional()
                    .describe(
                      "Module name patterns to apply LoRA to (e.g., ['\*.q_proj', '\*.v_proj']). If not set, applies to all '\*proj' linear layers."
                    ),
                  merge: zod
                    .boolean()
                    .default(customizationGetJobResponseSpecTrainingTwoPeftOneMergeDefault)
                    .describe(
                      'Merge LoRA weights into base model after training. Produces a full-weight checkpoint instead of an adapter.'
                    ),
                  use_dora: zod
                    .boolean()
                    .default(customizationGetJobResponseSpecTrainingTwoPeftOneUseDoraDefault)
                    .describe(
                      'Enable DoRA (Weight-Decomposed Low-Rank Adaptation). Decomposes weight updates into magnitude and direction components. Can improve quality especially at low ranks, but adds training overhead.'
                    ),
                })
                .describe('LoRA adapter configuration.')
                .optional()
                .describe(
                  'PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning.'
                ),
              learning_rate: zod
                .number()
                .default(customizationGetJobResponseSpecTrainingTwoLearningRateDefault)
                .describe(
                  'Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning.'
                ),
              min_learning_rate: zod
                .number()
                .optional()
                .describe(
                  'Minimum learning rate for cosine decay. Optional; used with learning rate schedules.'
                ),
              weight_decay: zod
                .number()
                .default(customizationGetJobResponseSpecTrainingTwoWeightDecayDefault)
                .describe('Weight decay coefficient. Helps prevent overfitting.'),
              adam_beta1: zod
                .number()
                .default(customizationGetJobResponseSpecTrainingTwoAdamBeta1Default)
                .describe('Adam beta1 parameter. Adjust for optimizer tuning.'),
              adam_beta2: zod
                .number()
                .default(customizationGetJobResponseSpecTrainingTwoAdamBeta2Default)
                .describe('Adam beta2 parameter. Adjust for optimizer tuning.'),
              warmup_steps: zod
                .number()
                .min(customizationGetJobResponseSpecTrainingTwoWarmupStepsMin)
                .default(customizationGetJobResponseSpecTrainingTwoWarmupStepsDefault)
                .describe(
                  'Linear warmup steps. Recommended: 10% of total training steps for stable training.'
                ),
              optimizer: zod.string().optional().describe("Optimizer name (e.g., 'adamw')."),
              epochs: zod
                .number()
                .gt(customizationGetJobResponseSpecTrainingTwoEpochsExclusiveMin)
                .default(customizationGetJobResponseSpecTrainingTwoEpochsDefault)
                .describe(
                  'Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.'
                ),
              max_steps: zod
                .number()
                .optional()
                .describe('Max training steps. Overrides epochs if set.'),
              log_every_n_steps: zod
                .number()
                .optional()
                .describe(
                  'Logging frequency in steps. Controls how often training metrics are logged.'
                ),
              val_check_interval: zod
                .number()
                .optional()
                .describe(
                  'Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count.'
                ),
              batch_size: zod
                .number()
                .gt(customizationGetJobResponseSpecTrainingTwoBatchSizeExclusiveMin)
                .default(customizationGetJobResponseSpecTrainingTwoBatchSizeDefault)
                .describe(
                  'Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.'
                ),
              micro_batch_size: zod
                .number()
                .gt(customizationGetJobResponseSpecTrainingTwoMicroBatchSizeExclusiveMin)
                .default(customizationGetJobResponseSpecTrainingTwoMicroBatchSizeDefault)
                .describe(
                  'Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.'
                ),
              sequence_packing: zod
                .boolean()
                .default(customizationGetJobResponseSpecTrainingTwoSequencePackingDefault)
                .describe('Enable sequence packing for efficiency. Can improve training speed.'),
              max_seq_length: zod
                .number()
                .gt(customizationGetJobResponseSpecTrainingTwoMaxSeqLengthExclusiveMin)
                .default(customizationGetJobResponseSpecTrainingTwoMaxSeqLengthDefault)
                .describe(
                  'Maximum token sequence length for training. Higher = more memory, longer training.'
                ),
              precision: zod
                .enum(['fp8', 'bf16', 'fp16', 'fp32'])
                .describe('Model precision for training.')
                .optional()
                .describe('Model precision for training. Auto-detected if unset.'),
              seed: zod.number().optional().describe('Random seed for reproducibility. Optional.'),
              parallelism: zod
                .object({
                  num_gpus_per_node: zod
                    .number()
                    .gt(
                      customizationGetJobResponseSpecTrainingTwoParallelismNumGpusPerNodeExclusiveMin
                    )
                    .default(
                      customizationGetJobResponseSpecTrainingTwoParallelismNumGpusPerNodeDefault
                    )
                    .describe('Number of gpus per node.'),
                  num_nodes: zod
                    .number()
                    .gt(customizationGetJobResponseSpecTrainingTwoParallelismNumNodesExclusiveMin)
                    .default(customizationGetJobResponseSpecTrainingTwoParallelismNumNodesDefault)
                    .describe('Number of nodes.'),
                  tensor_parallel_size: zod
                    .number()
                    .gt(
                      customizationGetJobResponseSpecTrainingTwoParallelismTensorParallelSizeExclusiveMin
                    )
                    .default(
                      customizationGetJobResponseSpecTrainingTwoParallelismTensorParallelSizeDefault
                    )
                    .describe('Tensor parallel size.'),
                  pipeline_parallel_size: zod
                    .number()
                    .gt(
                      customizationGetJobResponseSpecTrainingTwoParallelismPipelineParallelSizeExclusiveMin
                    )
                    .default(
                      customizationGetJobResponseSpecTrainingTwoParallelismPipelineParallelSizeDefault
                    )
                    .describe('Pipeline parallel size.'),
                  context_parallel_size: zod
                    .number()
                    .gt(
                      customizationGetJobResponseSpecTrainingTwoParallelismContextParallelSizeExclusiveMin
                    )
                    .default(
                      customizationGetJobResponseSpecTrainingTwoParallelismContextParallelSizeDefault
                    )
                    .describe('Context parallel size.'),
                  expert_parallel_size: zod
                    .number()
                    .optional()
                    .describe('Expert parallel size (MoE models).'),
                  sequence_parallel: zod
                    .boolean()
                    .default(
                      customizationGetJobResponseSpecTrainingTwoParallelismSequenceParallelDefault
                    )
                    .describe('Enable sequence parallelism.'),
                })
                .optional()
                .describe(
                  'Distributed training parallelism configuration.\n\nMost users only need num_gpus_per_node. Advanced users can configure\ntensor\/pipeline\/context\/expert parallelism for large models.'
                ),
              execution_profile: zod
                .string()
                .optional()
                .describe(
                  "Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default."
                ),
              type: zod
                .literal('distillation')
                .default(customizationGetJobResponseSpecTrainingTwoTypeDefault),
              teacher_model: zod
                .string()
                .describe(
                  "Teacher model URN (e.g., 'workspace\/model-name'). Must have the same vocabulary as the student model."
                ),
              teacher_precision: zod
                .enum(['bf16', 'fp16', 'fp32'])
                .default(customizationGetJobResponseSpecTrainingTwoTeacherPrecisionDefault)
                .describe(
                  'Precision for loading the frozen teacher model. Lower precision reduces memory but may affect logit quality.'
                ),
              distillation_ratio: zod
                .number()
                .min(customizationGetJobResponseSpecTrainingTwoDistillationRatioMin)
                .max(customizationGetJobResponseSpecTrainingTwoDistillationRatioMax)
                .default(customizationGetJobResponseSpecTrainingTwoDistillationRatioDefault)
                .describe('Balance between CE loss and KD loss. 0.0 = CE only, 1.0 = KD only.'),
              distillation_temperature: zod
                .number()
                .gt(customizationGetJobResponseSpecTrainingTwoDistillationTemperatureExclusiveMin)
                .default(customizationGetJobResponseSpecTrainingTwoDistillationTemperatureDefault)
                .describe('Softmax temperature for KD. Higher = softer probability distributions.'),
            })
            .describe(
              "Knowledge Distillation with a teacher model.\n\nCustomizer's differentiator — not available in Unsloth.\nTrains the student model to match the teacher's output distribution."
            ),
          zod
            .object({
              peft: zod
                .object({
                  quantization: zod
                    .object({
                      precision: zod
                        .enum(['4bit', '8bit'])
                        .default(
                          customizationGetJobResponseSpecTrainingThreePeftOneQuantizationOnePrecisionDefault
                        )
                        .describe(
                          "Quantization precision. '4bit' (NF4) for maximum memory savings, '8bit' (LLM.int8) for a balance of quality and memory."
                        ),
                    })
                    .describe(
                      'Base model quantization for memory-efficient PEFT training.\n\nSupports two scenarios:\n- Full-precision base model: quantized on-the-fly at load time\n- Pre-quantized base model: loaded directly at the specified precision\n\nIn both cases, base model weights are frozen and only the PEFT adapter\nparameters are trained in full precision.'
                    )
                    .optional()
                    .describe(
                      'Enable quantized training to reduce GPU memory. If the base model is full-precision, it will be quantized at load time. If the base model is already pre-quantized, this configures the expected precision. The trained adapter remains full-precision.'
                    ),
                  type: zod
                    .literal('lora')
                    .default(customizationGetJobResponseSpecTrainingThreePeftOneTypeDefault),
                  rank: zod
                    .number()
                    .min(1)
                    .max(customizationGetJobResponseSpecTrainingThreePeftOneRankMax)
                    .default(customizationGetJobResponseSpecTrainingThreePeftOneRankDefault)
                    .describe(
                      'LoRA rank (low-rank dimension). Higher values increase capacity but use more memory.'
                    ),
                  alpha: zod
                    .number()
                    .min(1)
                    .default(customizationGetJobResponseSpecTrainingThreePeftOneAlphaDefault)
                    .describe('LoRA alpha scaling factor. Common practice: alpha = 2-4x rank.'),
                  dropout: zod
                    .number()
                    .min(customizationGetJobResponseSpecTrainingThreePeftOneDropoutMin)
                    .max(customizationGetJobResponseSpecTrainingThreePeftOneDropoutMax)
                    .default(customizationGetJobResponseSpecTrainingThreePeftOneDropoutDefault)
                    .describe('LoRA dropout probability for regularization.'),
                  target_modules: zod
                    .array(zod.string())
                    .optional()
                    .describe(
                      "Module name patterns to apply LoRA to (e.g., ['\*.q_proj', '\*.v_proj']). If not set, applies to all '\*proj' linear layers."
                    ),
                  merge: zod
                    .boolean()
                    .default(customizationGetJobResponseSpecTrainingThreePeftOneMergeDefault)
                    .describe(
                      'Merge LoRA weights into base model after training. Produces a full-weight checkpoint instead of an adapter.'
                    ),
                  use_dora: zod
                    .boolean()
                    .default(customizationGetJobResponseSpecTrainingThreePeftOneUseDoraDefault)
                    .describe(
                      'Enable DoRA (Weight-Decomposed Low-Rank Adaptation). Decomposes weight updates into magnitude and direction components. Can improve quality especially at low ranks, but adds training overhead.'
                    ),
                })
                .describe('LoRA adapter configuration.')
                .optional()
                .describe(
                  'PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning.'
                ),
              learning_rate: zod
                .number()
                .default(customizationGetJobResponseSpecTrainingThreeLearningRateDefault)
                .describe(
                  'Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning.'
                ),
              min_learning_rate: zod
                .number()
                .optional()
                .describe(
                  'Minimum learning rate for cosine decay. Optional; used with learning rate schedules.'
                ),
              weight_decay: zod
                .number()
                .default(customizationGetJobResponseSpecTrainingThreeWeightDecayDefault)
                .describe('Weight decay coefficient. Helps prevent overfitting.'),
              adam_beta1: zod
                .number()
                .default(customizationGetJobResponseSpecTrainingThreeAdamBeta1Default)
                .describe('Adam beta1 parameter. Adjust for optimizer tuning.'),
              adam_beta2: zod
                .number()
                .default(customizationGetJobResponseSpecTrainingThreeAdamBeta2Default)
                .describe('Adam beta2 parameter. Adjust for optimizer tuning.'),
              warmup_steps: zod
                .number()
                .min(customizationGetJobResponseSpecTrainingThreeWarmupStepsMin)
                .default(customizationGetJobResponseSpecTrainingThreeWarmupStepsDefault)
                .describe(
                  'Linear warmup steps. Recommended: 10% of total training steps for stable training.'
                ),
              optimizer: zod.string().optional().describe("Optimizer name (e.g., 'adamw')."),
              epochs: zod
                .number()
                .gt(customizationGetJobResponseSpecTrainingThreeEpochsExclusiveMin)
                .default(customizationGetJobResponseSpecTrainingThreeEpochsDefault)
                .describe(
                  'Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.'
                ),
              max_steps: zod
                .number()
                .optional()
                .describe('Max training steps. Overrides epochs if set.'),
              log_every_n_steps: zod
                .number()
                .optional()
                .describe(
                  'Logging frequency in steps. Controls how often training metrics are logged.'
                ),
              val_check_interval: zod
                .number()
                .optional()
                .describe(
                  'Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count.'
                ),
              batch_size: zod
                .number()
                .gt(customizationGetJobResponseSpecTrainingThreeBatchSizeExclusiveMin)
                .default(customizationGetJobResponseSpecTrainingThreeBatchSizeDefault)
                .describe(
                  'Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.'
                ),
              micro_batch_size: zod
                .number()
                .gt(customizationGetJobResponseSpecTrainingThreeMicroBatchSizeExclusiveMin)
                .default(customizationGetJobResponseSpecTrainingThreeMicroBatchSizeDefault)
                .describe(
                  'Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.'
                ),
              sequence_packing: zod
                .boolean()
                .default(customizationGetJobResponseSpecTrainingThreeSequencePackingDefault)
                .describe('Enable sequence packing for efficiency. Can improve training speed.'),
              max_seq_length: zod
                .number()
                .gt(customizationGetJobResponseSpecTrainingThreeMaxSeqLengthExclusiveMin)
                .default(customizationGetJobResponseSpecTrainingThreeMaxSeqLengthDefault)
                .describe(
                  'Maximum token sequence length for training. Higher = more memory, longer training.'
                ),
              precision: zod
                .enum(['fp8', 'bf16', 'fp16', 'fp32'])
                .describe('Model precision for training.')
                .optional()
                .describe('Model precision for training. Auto-detected if unset.'),
              seed: zod.number().optional().describe('Random seed for reproducibility. Optional.'),
              parallelism: zod
                .object({
                  num_gpus_per_node: zod
                    .number()
                    .gt(
                      customizationGetJobResponseSpecTrainingThreeParallelismNumGpusPerNodeExclusiveMin
                    )
                    .default(
                      customizationGetJobResponseSpecTrainingThreeParallelismNumGpusPerNodeDefault
                    )
                    .describe('Number of gpus per node.'),
                  num_nodes: zod
                    .number()
                    .gt(customizationGetJobResponseSpecTrainingThreeParallelismNumNodesExclusiveMin)
                    .default(customizationGetJobResponseSpecTrainingThreeParallelismNumNodesDefault)
                    .describe('Number of nodes.'),
                  tensor_parallel_size: zod
                    .number()
                    .gt(
                      customizationGetJobResponseSpecTrainingThreeParallelismTensorParallelSizeExclusiveMin
                    )
                    .default(
                      customizationGetJobResponseSpecTrainingThreeParallelismTensorParallelSizeDefault
                    )
                    .describe('Tensor parallel size.'),
                  pipeline_parallel_size: zod
                    .number()
                    .gt(
                      customizationGetJobResponseSpecTrainingThreeParallelismPipelineParallelSizeExclusiveMin
                    )
                    .default(
                      customizationGetJobResponseSpecTrainingThreeParallelismPipelineParallelSizeDefault
                    )
                    .describe('Pipeline parallel size.'),
                  context_parallel_size: zod
                    .number()
                    .gt(
                      customizationGetJobResponseSpecTrainingThreeParallelismContextParallelSizeExclusiveMin
                    )
                    .default(
                      customizationGetJobResponseSpecTrainingThreeParallelismContextParallelSizeDefault
                    )
                    .describe('Context parallel size.'),
                  expert_parallel_size: zod
                    .number()
                    .optional()
                    .describe('Expert parallel size (MoE models).'),
                  sequence_parallel: zod
                    .boolean()
                    .default(
                      customizationGetJobResponseSpecTrainingThreeParallelismSequenceParallelDefault
                    )
                    .describe('Enable sequence parallelism.'),
                })
                .optional()
                .describe(
                  'Distributed training parallelism configuration.\n\nMost users only need num_gpus_per_node. Advanced users can configure\ntensor\/pipeline\/context\/expert parallelism for large models.'
                ),
              execution_profile: zod
                .string()
                .optional()
                .describe(
                  "Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default."
                ),
              type: zod
                .literal('dpo')
                .default(customizationGetJobResponseSpecTrainingThreeTypeDefault),
              ref_policy_kl_penalty: zod
                .number()
                .min(customizationGetJobResponseSpecTrainingThreeRefPolicyKlPenaltyMin)
                .default(customizationGetJobResponseSpecTrainingThreeRefPolicyKlPenaltyDefault)
                .describe('KL penalty coefficient (beta in DPO paper).'),
              preference_average_log_probs: zod
                .boolean()
                .default(
                  customizationGetJobResponseSpecTrainingThreePreferenceAverageLogProbsDefault
                )
                .describe('Average log probabilities for preference loss calculation.'),
              sft_average_log_probs: zod
                .boolean()
                .default(customizationGetJobResponseSpecTrainingThreeSftAverageLogProbsDefault)
                .describe('Average log probabilities for SFT regularization loss.'),
              preference_loss_weight: zod
                .number()
                .min(customizationGetJobResponseSpecTrainingThreePreferenceLossWeightMin)
                .default(customizationGetJobResponseSpecTrainingThreePreferenceLossWeightDefault)
                .describe('Weight for the preference (DPO) loss term.'),
              sft_loss_weight: zod
                .number()
                .min(customizationGetJobResponseSpecTrainingThreeSftLossWeightMin)
                .default(customizationGetJobResponseSpecTrainingThreeSftLossWeightDefault)
                .describe('Weight for SFT regularization loss (0 = disabled).'),
              max_grad_norm: zod
                .number()
                .min(customizationGetJobResponseSpecTrainingThreeMaxGradNormMin)
                .default(customizationGetJobResponseSpecTrainingThreeMaxGradNormDefault)
                .describe('Maximum gradient norm for clipping.'),
            })
            .describe('Direct Preference Optimization.'),
        ])
        .describe('Training method and hyperparameters.'),
      integrations: zod
        .object({
          wandb: zod
            .object({
              project: zod
                .string()
                .optional()
                .describe(
                  'W&B project name (groups related runs). Defaults to output.name if not set.'
                ),
              name: zod
                .string()
                .optional()
                .describe('W&B run name. Defaults to job_id if not provided.'),
              entity: zod.string().optional().describe('W&B entity (team or username).'),
              tags: zod.array(zod.string()).optional().describe('W&B tags for filtering runs.'),
              notes: zod.string().optional().describe('W&B notes\/description for the run.'),
              base_url: zod
                .string()
                .optional()
                .describe(
                  "Base URL for self-hosted W&B server (e.g., 'https:\/\/wandb.mycompany.com'). If not provided, uses the default W&B cloud service."
                ),
              api_key_secret: zod
                .string()
                .regex(customizationGetJobResponseSpecIntegrationsOneWandbOneApiKeySecretOneRegExp)
                .describe(
                  "Reference to a secret. Format: 'secret_name' (uses request workspace) or 'workspace\/secret_name' (explicit workspace)."
                )
                .optional()
                .describe(
                  "Reference to a secret containing the WANDB_API_KEY. Format: 'secret_name' (uses request workspace) or 'workspace\/secret_name' (explicit workspace)."
                ),
            })
            .describe(
              'Weights & Biases integration configuration.\n\nTo use W&B, provide an api_key_secret referencing a secret that contains\nthe WANDB_API_KEY value. Optionally provide base_url for self-hosted W&B servers.'
            )
            .optional()
            .describe('Weights & Biases integration configuration.'),
          mlflow: zod
            .object({
              experiment_name: zod
                .string()
                .optional()
                .describe(
                  'MLflow experiment name (groups related runs). Defaults to output.name if not set.'
                ),
              run_name: zod
                .string()
                .optional()
                .describe('MLflow run name. Defaults to job_id if not provided.'),
              tags: zod
                .record(zod.string(), zod.string())
                .optional()
                .describe('MLflow tags as key-value pairs for filtering runs.'),
              description: zod.string().optional().describe('MLflow run description.'),
              tracking_uri: zod
                .string()
                .optional()
                .describe(
                  "MLflow tracking server URI (e.g., 'http:\/\/mlflow.mycompany.com:5000'). Can also be set via MLFLOW_TRACKING_URI environment variable."
                ),
            })
            .describe('MLflow integration configuration.')
            .optional()
            .describe('MLflow integration configuration.'),
        })
        .describe(
          'Third-party integration configurations.\n\nEach integration type has its own optional field. To enable an integration,\nprovide its configuration object. Omit or set to None to disable.'
        )
        .optional()
        .describe('Third-party integrations (e.g., Weights & Biases, MLflow).'),
      deployment_config: zod
        .union([
          zod.string().describe('A reference to DeploymentParams.'),
          zod
            .object({
              gpu: zod
                .number()
                .default(customizationGetJobResponseSpecDeploymentConfigTwoGpuDefault)
                .describe('Number of GPUs required for the deployment'),
              additional_envs: zod
                .record(zod.string(), zod.string())
                .optional()
                .describe('Additional environment variables for the deployment'),
              disk_size: zod.string().optional().describe('Disk size for the deployment'),
              image_name: zod
                .string()
                .optional()
                .describe('Container image name from NGC. If not specified, defaults to multi-llm'),
              image_tag: zod.string().optional().describe('Container image tag from NGC'),
              lora_enabled: zod
                .boolean()
                .default(customizationGetJobResponseSpecDeploymentConfigTwoLoraEnabledDefault)
                .describe(
                  'When automatically deploying a full SFT training, this parameter being set to true will allow subsequent LoRA adapters to be trained and deployed against it.'
                ),
              tool_call_config: zod
                .object({
                  tool_call_parser: zod
                    .string()
                    .optional()
                    .describe(
                      "Name of the tool call parser to use (e.g., 'openai', 'hermes', 'pythonic', 'llama3_json', 'mistral')."
                    ),
                  tool_call_plugin: zod
                    .string()
                    .regex(
                      customizationGetJobResponseSpecDeploymentConfigTwoToolCallConfigOneToolCallPluginRegExp
                    )
                    .optional()
                    .describe(
                      "Reference to a fileset containing the custom tool call plugin Python file. Expected format: '{workspace}\/{fileset_name}'."
                    ),
                  auto_tool_choice: zod
                    .boolean()
                    .optional()
                    .describe('Whether to enable automatic tool choice.'),
                })
                .describe('Tool calling configuration for NIM deployments.')
                .optional()
                .describe('Tool calling configuration override for the NIM deployment.'),
            })
            .describe('Inline deployment parameters for creating a new ModelDeploymentConfig.'),
        ])
        .optional()
        .describe(
          "Deployment configuration for auto-deploying the model after training. Pass a string to reference an existing ModelDeploymentConfig by name (e.g., 'my-config' or 'workspace\/my-config'). An object provides inline NIM deployment parameters. Omit to skip deployment."
        ),
      custom_fields: zod
        .record(zod.string(), zod.unknown())
        .optional()
        .describe('Custom user-defined fields.'),
      output: zod
        .object({
          name: zod
            .string()
            .max(customizationGetJobResponseSpecOutputOneNameMax)
            .regex(customizationGetJobResponseSpecOutputOneNameRegExp)
            .describe(
              'Name of the output artifact. Used to identify it during deployment and inference.'
            ),
          type: zod
            .enum(['adapter', 'model'])
            .describe('Output artifact type.')
            .describe(
              'Output artifact type. Either `model` (full fine-tuned weights) or `adapter` (LoRA adapter weights).'
            ),
          fileset: zod
            .string()
            .max(customizationGetJobResponseSpecOutputOneFilesetMax)
            .regex(customizationGetJobResponseSpecOutputOneFilesetRegExp)
            .describe('FileSet name where output artifacts are stored.'),
        })
        .describe('Resolved output artifact details returned by the server.')
        .describe('Output artifact created by this job.'),
    })
    .describe('Customization job details returned by the server.'),
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
export const CustomizationDeleteJobParams = zod.object({
  workspace: zod.string(),
  name: zod.string(),
});

/**
 * @summary Cancel Job
 */
export const CustomizationCancelJobParams = zod.object({
  workspace: zod.string(),
  name: zod.string(),
});

export const customizationCancelJobResponseSpecTrainingOnePeftOneQuantizationOnePrecisionDefault = `4bit`;
export const customizationCancelJobResponseSpecTrainingOnePeftOneTypeDefault = `lora`;
export const customizationCancelJobResponseSpecTrainingOnePeftOneRankDefault = 8;
export const customizationCancelJobResponseSpecTrainingOnePeftOneRankMax = 256;

export const customizationCancelJobResponseSpecTrainingOnePeftOneAlphaDefault = 32;

export const customizationCancelJobResponseSpecTrainingOnePeftOneDropoutDefault = 0;
export const customizationCancelJobResponseSpecTrainingOnePeftOneDropoutMin = 0;
export const customizationCancelJobResponseSpecTrainingOnePeftOneDropoutMax = 1;

export const customizationCancelJobResponseSpecTrainingOnePeftOneMergeDefault = false;
export const customizationCancelJobResponseSpecTrainingOnePeftOneUseDoraDefault = false;
export const customizationCancelJobResponseSpecTrainingOneLearningRateDefault = 0.0001;
export const customizationCancelJobResponseSpecTrainingOneWeightDecayDefault = 0.01;
export const customizationCancelJobResponseSpecTrainingOneAdamBeta1Default = 0.9;
export const customizationCancelJobResponseSpecTrainingOneAdamBeta2Default = 0.999;
export const customizationCancelJobResponseSpecTrainingOneWarmupStepsDefault = 0;
export const customizationCancelJobResponseSpecTrainingOneWarmupStepsMin = 0;

export const customizationCancelJobResponseSpecTrainingOneEpochsDefault = 1;
export const customizationCancelJobResponseSpecTrainingOneEpochsExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingOneBatchSizeDefault = 32;
export const customizationCancelJobResponseSpecTrainingOneBatchSizeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingOneMicroBatchSizeDefault = 1;
export const customizationCancelJobResponseSpecTrainingOneMicroBatchSizeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingOneSequencePackingDefault = false;
export const customizationCancelJobResponseSpecTrainingOneMaxSeqLengthDefault = 2048;
export const customizationCancelJobResponseSpecTrainingOneMaxSeqLengthExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingOneParallelismNumGpusPerNodeDefault = 1;
export const customizationCancelJobResponseSpecTrainingOneParallelismNumGpusPerNodeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingOneParallelismNumNodesDefault = 1;
export const customizationCancelJobResponseSpecTrainingOneParallelismNumNodesExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingOneParallelismTensorParallelSizeDefault = 1;
export const customizationCancelJobResponseSpecTrainingOneParallelismTensorParallelSizeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingOneParallelismPipelineParallelSizeDefault = 1;
export const customizationCancelJobResponseSpecTrainingOneParallelismPipelineParallelSizeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingOneParallelismContextParallelSizeDefault = 1;
export const customizationCancelJobResponseSpecTrainingOneParallelismContextParallelSizeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingOneParallelismSequenceParallelDefault = false;
export const customizationCancelJobResponseSpecTrainingOneTypeDefault = `sft`;
export const customizationCancelJobResponseSpecTrainingTwoPeftOneQuantizationOnePrecisionDefault = `4bit`;
export const customizationCancelJobResponseSpecTrainingTwoPeftOneTypeDefault = `lora`;
export const customizationCancelJobResponseSpecTrainingTwoPeftOneRankDefault = 8;
export const customizationCancelJobResponseSpecTrainingTwoPeftOneRankMax = 256;

export const customizationCancelJobResponseSpecTrainingTwoPeftOneAlphaDefault = 32;

export const customizationCancelJobResponseSpecTrainingTwoPeftOneDropoutDefault = 0;
export const customizationCancelJobResponseSpecTrainingTwoPeftOneDropoutMin = 0;
export const customizationCancelJobResponseSpecTrainingTwoPeftOneDropoutMax = 1;

export const customizationCancelJobResponseSpecTrainingTwoPeftOneMergeDefault = false;
export const customizationCancelJobResponseSpecTrainingTwoPeftOneUseDoraDefault = false;
export const customizationCancelJobResponseSpecTrainingTwoLearningRateDefault = 0.0001;
export const customizationCancelJobResponseSpecTrainingTwoWeightDecayDefault = 0.01;
export const customizationCancelJobResponseSpecTrainingTwoAdamBeta1Default = 0.9;
export const customizationCancelJobResponseSpecTrainingTwoAdamBeta2Default = 0.999;
export const customizationCancelJobResponseSpecTrainingTwoWarmupStepsDefault = 0;
export const customizationCancelJobResponseSpecTrainingTwoWarmupStepsMin = 0;

export const customizationCancelJobResponseSpecTrainingTwoEpochsDefault = 1;
export const customizationCancelJobResponseSpecTrainingTwoEpochsExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingTwoBatchSizeDefault = 32;
export const customizationCancelJobResponseSpecTrainingTwoBatchSizeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingTwoMicroBatchSizeDefault = 1;
export const customizationCancelJobResponseSpecTrainingTwoMicroBatchSizeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingTwoSequencePackingDefault = false;
export const customizationCancelJobResponseSpecTrainingTwoMaxSeqLengthDefault = 2048;
export const customizationCancelJobResponseSpecTrainingTwoMaxSeqLengthExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingTwoParallelismNumGpusPerNodeDefault = 1;
export const customizationCancelJobResponseSpecTrainingTwoParallelismNumGpusPerNodeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingTwoParallelismNumNodesDefault = 1;
export const customizationCancelJobResponseSpecTrainingTwoParallelismNumNodesExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingTwoParallelismTensorParallelSizeDefault = 1;
export const customizationCancelJobResponseSpecTrainingTwoParallelismTensorParallelSizeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingTwoParallelismPipelineParallelSizeDefault = 1;
export const customizationCancelJobResponseSpecTrainingTwoParallelismPipelineParallelSizeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingTwoParallelismContextParallelSizeDefault = 1;
export const customizationCancelJobResponseSpecTrainingTwoParallelismContextParallelSizeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingTwoParallelismSequenceParallelDefault = false;
export const customizationCancelJobResponseSpecTrainingTwoTypeDefault = `distillation`;
export const customizationCancelJobResponseSpecTrainingTwoTeacherPrecisionDefault = `bf16`;
export const customizationCancelJobResponseSpecTrainingTwoDistillationRatioDefault = 0.5;
export const customizationCancelJobResponseSpecTrainingTwoDistillationRatioMin = 0;
export const customizationCancelJobResponseSpecTrainingTwoDistillationRatioMax = 1;

export const customizationCancelJobResponseSpecTrainingTwoDistillationTemperatureDefault = 1;
export const customizationCancelJobResponseSpecTrainingTwoDistillationTemperatureExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingThreePeftOneQuantizationOnePrecisionDefault = `4bit`;
export const customizationCancelJobResponseSpecTrainingThreePeftOneTypeDefault = `lora`;
export const customizationCancelJobResponseSpecTrainingThreePeftOneRankDefault = 8;
export const customizationCancelJobResponseSpecTrainingThreePeftOneRankMax = 256;

export const customizationCancelJobResponseSpecTrainingThreePeftOneAlphaDefault = 32;

export const customizationCancelJobResponseSpecTrainingThreePeftOneDropoutDefault = 0;
export const customizationCancelJobResponseSpecTrainingThreePeftOneDropoutMin = 0;
export const customizationCancelJobResponseSpecTrainingThreePeftOneDropoutMax = 1;

export const customizationCancelJobResponseSpecTrainingThreePeftOneMergeDefault = false;
export const customizationCancelJobResponseSpecTrainingThreePeftOneUseDoraDefault = false;
export const customizationCancelJobResponseSpecTrainingThreeLearningRateDefault = 0.0001;
export const customizationCancelJobResponseSpecTrainingThreeWeightDecayDefault = 0.01;
export const customizationCancelJobResponseSpecTrainingThreeAdamBeta1Default = 0.9;
export const customizationCancelJobResponseSpecTrainingThreeAdamBeta2Default = 0.999;
export const customizationCancelJobResponseSpecTrainingThreeWarmupStepsDefault = 0;
export const customizationCancelJobResponseSpecTrainingThreeWarmupStepsMin = 0;

export const customizationCancelJobResponseSpecTrainingThreeEpochsDefault = 1;
export const customizationCancelJobResponseSpecTrainingThreeEpochsExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingThreeBatchSizeDefault = 32;
export const customizationCancelJobResponseSpecTrainingThreeBatchSizeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingThreeMicroBatchSizeDefault = 1;
export const customizationCancelJobResponseSpecTrainingThreeMicroBatchSizeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingThreeSequencePackingDefault = false;
export const customizationCancelJobResponseSpecTrainingThreeMaxSeqLengthDefault = 2048;
export const customizationCancelJobResponseSpecTrainingThreeMaxSeqLengthExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingThreeParallelismNumGpusPerNodeDefault = 1;
export const customizationCancelJobResponseSpecTrainingThreeParallelismNumGpusPerNodeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingThreeParallelismNumNodesDefault = 1;
export const customizationCancelJobResponseSpecTrainingThreeParallelismNumNodesExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingThreeParallelismTensorParallelSizeDefault = 1;
export const customizationCancelJobResponseSpecTrainingThreeParallelismTensorParallelSizeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingThreeParallelismPipelineParallelSizeDefault = 1;
export const customizationCancelJobResponseSpecTrainingThreeParallelismPipelineParallelSizeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingThreeParallelismContextParallelSizeDefault = 1;
export const customizationCancelJobResponseSpecTrainingThreeParallelismContextParallelSizeExclusiveMin = 0;

export const customizationCancelJobResponseSpecTrainingThreeParallelismSequenceParallelDefault = false;
export const customizationCancelJobResponseSpecTrainingThreeTypeDefault = `dpo`;
export const customizationCancelJobResponseSpecTrainingThreeRefPolicyKlPenaltyDefault = 0.05;
export const customizationCancelJobResponseSpecTrainingThreeRefPolicyKlPenaltyMin = 0;

export const customizationCancelJobResponseSpecTrainingThreePreferenceAverageLogProbsDefault = false;
export const customizationCancelJobResponseSpecTrainingThreeSftAverageLogProbsDefault = false;
export const customizationCancelJobResponseSpecTrainingThreePreferenceLossWeightDefault = 1;
export const customizationCancelJobResponseSpecTrainingThreePreferenceLossWeightMin = 0;

export const customizationCancelJobResponseSpecTrainingThreeSftLossWeightDefault = 0;
export const customizationCancelJobResponseSpecTrainingThreeSftLossWeightMin = 0;

export const customizationCancelJobResponseSpecTrainingThreeMaxGradNormDefault = 1;
export const customizationCancelJobResponseSpecTrainingThreeMaxGradNormMin = 0;

export const customizationCancelJobResponseSpecIntegrationsOneWandbOneApiKeySecretOneRegExp =
  new RegExp('^[a-z0-9_-]+(\/[a-z0-9_-]+)?$');
export const customizationCancelJobResponseSpecDeploymentConfigTwoGpuDefault = 1;
export const customizationCancelJobResponseSpecDeploymentConfigTwoLoraEnabledDefault = true;
export const customizationCancelJobResponseSpecDeploymentConfigTwoToolCallConfigOneToolCallPluginRegExp =
  new RegExp('^[\\w\\-.]+\/[\\w\\-.]+$');
export const customizationCancelJobResponseSpecOutputOneNameMax = 255;

export const customizationCancelJobResponseSpecOutputOneNameRegExp = new RegExp('^[\\w\\-.]+$');
export const customizationCancelJobResponseSpecOutputOneFilesetMax = 255;

export const customizationCancelJobResponseSpecOutputOneFilesetRegExp = new RegExp('^[\\w\\-.]+$');

export const CustomizationCancelJobResponse = zod.object({
  id: zod.string().optional(),
  name: zod.string(),
  description: zod.string().optional(),
  project: zod.string().optional(),
  workspace: zod.string().optional(),
  created_at: zod.string().optional(),
  updated_at: zod.string().optional(),
  spec: zod
    .object({
      model: zod.string().describe("Model reference (e.g., 'workspace\/model-name')."),
      dataset: zod
        .string()
        .describe(
          'Dataset URI. Supported protocol: fileset:\/\/ (e.g., fileset:\/\/workspace\/name).'
        ),
      training: zod
        .union([
          zod
            .object({
              peft: zod
                .object({
                  quantization: zod
                    .object({
                      precision: zod
                        .enum(['4bit', '8bit'])
                        .default(
                          customizationCancelJobResponseSpecTrainingOnePeftOneQuantizationOnePrecisionDefault
                        )
                        .describe(
                          "Quantization precision. '4bit' (NF4) for maximum memory savings, '8bit' (LLM.int8) for a balance of quality and memory."
                        ),
                    })
                    .describe(
                      'Base model quantization for memory-efficient PEFT training.\n\nSupports two scenarios:\n- Full-precision base model: quantized on-the-fly at load time\n- Pre-quantized base model: loaded directly at the specified precision\n\nIn both cases, base model weights are frozen and only the PEFT adapter\nparameters are trained in full precision.'
                    )
                    .optional()
                    .describe(
                      'Enable quantized training to reduce GPU memory. If the base model is full-precision, it will be quantized at load time. If the base model is already pre-quantized, this configures the expected precision. The trained adapter remains full-precision.'
                    ),
                  type: zod
                    .literal('lora')
                    .default(customizationCancelJobResponseSpecTrainingOnePeftOneTypeDefault),
                  rank: zod
                    .number()
                    .min(1)
                    .max(customizationCancelJobResponseSpecTrainingOnePeftOneRankMax)
                    .default(customizationCancelJobResponseSpecTrainingOnePeftOneRankDefault)
                    .describe(
                      'LoRA rank (low-rank dimension). Higher values increase capacity but use more memory.'
                    ),
                  alpha: zod
                    .number()
                    .min(1)
                    .default(customizationCancelJobResponseSpecTrainingOnePeftOneAlphaDefault)
                    .describe('LoRA alpha scaling factor. Common practice: alpha = 2-4x rank.'),
                  dropout: zod
                    .number()
                    .min(customizationCancelJobResponseSpecTrainingOnePeftOneDropoutMin)
                    .max(customizationCancelJobResponseSpecTrainingOnePeftOneDropoutMax)
                    .default(customizationCancelJobResponseSpecTrainingOnePeftOneDropoutDefault)
                    .describe('LoRA dropout probability for regularization.'),
                  target_modules: zod
                    .array(zod.string())
                    .optional()
                    .describe(
                      "Module name patterns to apply LoRA to (e.g., ['\*.q_proj', '\*.v_proj']). If not set, applies to all '\*proj' linear layers."
                    ),
                  merge: zod
                    .boolean()
                    .default(customizationCancelJobResponseSpecTrainingOnePeftOneMergeDefault)
                    .describe(
                      'Merge LoRA weights into base model after training. Produces a full-weight checkpoint instead of an adapter.'
                    ),
                  use_dora: zod
                    .boolean()
                    .default(customizationCancelJobResponseSpecTrainingOnePeftOneUseDoraDefault)
                    .describe(
                      'Enable DoRA (Weight-Decomposed Low-Rank Adaptation). Decomposes weight updates into magnitude and direction components. Can improve quality especially at low ranks, but adds training overhead.'
                    ),
                })
                .describe('LoRA adapter configuration.')
                .optional()
                .describe(
                  'PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning.'
                ),
              learning_rate: zod
                .number()
                .default(customizationCancelJobResponseSpecTrainingOneLearningRateDefault)
                .describe(
                  'Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning.'
                ),
              min_learning_rate: zod
                .number()
                .optional()
                .describe(
                  'Minimum learning rate for cosine decay. Optional; used with learning rate schedules.'
                ),
              weight_decay: zod
                .number()
                .default(customizationCancelJobResponseSpecTrainingOneWeightDecayDefault)
                .describe('Weight decay coefficient. Helps prevent overfitting.'),
              adam_beta1: zod
                .number()
                .default(customizationCancelJobResponseSpecTrainingOneAdamBeta1Default)
                .describe('Adam beta1 parameter. Adjust for optimizer tuning.'),
              adam_beta2: zod
                .number()
                .default(customizationCancelJobResponseSpecTrainingOneAdamBeta2Default)
                .describe('Adam beta2 parameter. Adjust for optimizer tuning.'),
              warmup_steps: zod
                .number()
                .min(customizationCancelJobResponseSpecTrainingOneWarmupStepsMin)
                .default(customizationCancelJobResponseSpecTrainingOneWarmupStepsDefault)
                .describe(
                  'Linear warmup steps. Recommended: 10% of total training steps for stable training.'
                ),
              optimizer: zod.string().optional().describe("Optimizer name (e.g., 'adamw')."),
              epochs: zod
                .number()
                .gt(customizationCancelJobResponseSpecTrainingOneEpochsExclusiveMin)
                .default(customizationCancelJobResponseSpecTrainingOneEpochsDefault)
                .describe(
                  'Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.'
                ),
              max_steps: zod
                .number()
                .optional()
                .describe('Max training steps. Overrides epochs if set.'),
              log_every_n_steps: zod
                .number()
                .optional()
                .describe(
                  'Logging frequency in steps. Controls how often training metrics are logged.'
                ),
              val_check_interval: zod
                .number()
                .optional()
                .describe(
                  'Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count.'
                ),
              batch_size: zod
                .number()
                .gt(customizationCancelJobResponseSpecTrainingOneBatchSizeExclusiveMin)
                .default(customizationCancelJobResponseSpecTrainingOneBatchSizeDefault)
                .describe(
                  'Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.'
                ),
              micro_batch_size: zod
                .number()
                .gt(customizationCancelJobResponseSpecTrainingOneMicroBatchSizeExclusiveMin)
                .default(customizationCancelJobResponseSpecTrainingOneMicroBatchSizeDefault)
                .describe(
                  'Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.'
                ),
              sequence_packing: zod
                .boolean()
                .default(customizationCancelJobResponseSpecTrainingOneSequencePackingDefault)
                .describe('Enable sequence packing for efficiency. Can improve training speed.'),
              max_seq_length: zod
                .number()
                .gt(customizationCancelJobResponseSpecTrainingOneMaxSeqLengthExclusiveMin)
                .default(customizationCancelJobResponseSpecTrainingOneMaxSeqLengthDefault)
                .describe(
                  'Maximum token sequence length for training. Higher = more memory, longer training.'
                ),
              precision: zod
                .enum(['fp8', 'bf16', 'fp16', 'fp32'])
                .describe('Model precision for training.')
                .optional()
                .describe('Model precision for training. Auto-detected if unset.'),
              seed: zod.number().optional().describe('Random seed for reproducibility. Optional.'),
              parallelism: zod
                .object({
                  num_gpus_per_node: zod
                    .number()
                    .gt(
                      customizationCancelJobResponseSpecTrainingOneParallelismNumGpusPerNodeExclusiveMin
                    )
                    .default(
                      customizationCancelJobResponseSpecTrainingOneParallelismNumGpusPerNodeDefault
                    )
                    .describe('Number of gpus per node.'),
                  num_nodes: zod
                    .number()
                    .gt(
                      customizationCancelJobResponseSpecTrainingOneParallelismNumNodesExclusiveMin
                    )
                    .default(
                      customizationCancelJobResponseSpecTrainingOneParallelismNumNodesDefault
                    )
                    .describe('Number of nodes.'),
                  tensor_parallel_size: zod
                    .number()
                    .gt(
                      customizationCancelJobResponseSpecTrainingOneParallelismTensorParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCancelJobResponseSpecTrainingOneParallelismTensorParallelSizeDefault
                    )
                    .describe('Tensor parallel size.'),
                  pipeline_parallel_size: zod
                    .number()
                    .gt(
                      customizationCancelJobResponseSpecTrainingOneParallelismPipelineParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCancelJobResponseSpecTrainingOneParallelismPipelineParallelSizeDefault
                    )
                    .describe('Pipeline parallel size.'),
                  context_parallel_size: zod
                    .number()
                    .gt(
                      customizationCancelJobResponseSpecTrainingOneParallelismContextParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCancelJobResponseSpecTrainingOneParallelismContextParallelSizeDefault
                    )
                    .describe('Context parallel size.'),
                  expert_parallel_size: zod
                    .number()
                    .optional()
                    .describe('Expert parallel size (MoE models).'),
                  sequence_parallel: zod
                    .boolean()
                    .default(
                      customizationCancelJobResponseSpecTrainingOneParallelismSequenceParallelDefault
                    )
                    .describe('Enable sequence parallelism.'),
                })
                .optional()
                .describe(
                  'Distributed training parallelism configuration.\n\nMost users only need num_gpus_per_node. Advanced users can configure\ntensor\/pipeline\/context\/expert parallelism for large models.'
                ),
              execution_profile: zod
                .string()
                .optional()
                .describe(
                  "Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default."
                ),
              type: zod
                .literal('sft')
                .default(customizationCancelJobResponseSpecTrainingOneTypeDefault),
            })
            .describe('Supervised Fine-Tuning.'),
          zod
            .object({
              peft: zod
                .object({
                  quantization: zod
                    .object({
                      precision: zod
                        .enum(['4bit', '8bit'])
                        .default(
                          customizationCancelJobResponseSpecTrainingTwoPeftOneQuantizationOnePrecisionDefault
                        )
                        .describe(
                          "Quantization precision. '4bit' (NF4) for maximum memory savings, '8bit' (LLM.int8) for a balance of quality and memory."
                        ),
                    })
                    .describe(
                      'Base model quantization for memory-efficient PEFT training.\n\nSupports two scenarios:\n- Full-precision base model: quantized on-the-fly at load time\n- Pre-quantized base model: loaded directly at the specified precision\n\nIn both cases, base model weights are frozen and only the PEFT adapter\nparameters are trained in full precision.'
                    )
                    .optional()
                    .describe(
                      'Enable quantized training to reduce GPU memory. If the base model is full-precision, it will be quantized at load time. If the base model is already pre-quantized, this configures the expected precision. The trained adapter remains full-precision.'
                    ),
                  type: zod
                    .literal('lora')
                    .default(customizationCancelJobResponseSpecTrainingTwoPeftOneTypeDefault),
                  rank: zod
                    .number()
                    .min(1)
                    .max(customizationCancelJobResponseSpecTrainingTwoPeftOneRankMax)
                    .default(customizationCancelJobResponseSpecTrainingTwoPeftOneRankDefault)
                    .describe(
                      'LoRA rank (low-rank dimension). Higher values increase capacity but use more memory.'
                    ),
                  alpha: zod
                    .number()
                    .min(1)
                    .default(customizationCancelJobResponseSpecTrainingTwoPeftOneAlphaDefault)
                    .describe('LoRA alpha scaling factor. Common practice: alpha = 2-4x rank.'),
                  dropout: zod
                    .number()
                    .min(customizationCancelJobResponseSpecTrainingTwoPeftOneDropoutMin)
                    .max(customizationCancelJobResponseSpecTrainingTwoPeftOneDropoutMax)
                    .default(customizationCancelJobResponseSpecTrainingTwoPeftOneDropoutDefault)
                    .describe('LoRA dropout probability for regularization.'),
                  target_modules: zod
                    .array(zod.string())
                    .optional()
                    .describe(
                      "Module name patterns to apply LoRA to (e.g., ['\*.q_proj', '\*.v_proj']). If not set, applies to all '\*proj' linear layers."
                    ),
                  merge: zod
                    .boolean()
                    .default(customizationCancelJobResponseSpecTrainingTwoPeftOneMergeDefault)
                    .describe(
                      'Merge LoRA weights into base model after training. Produces a full-weight checkpoint instead of an adapter.'
                    ),
                  use_dora: zod
                    .boolean()
                    .default(customizationCancelJobResponseSpecTrainingTwoPeftOneUseDoraDefault)
                    .describe(
                      'Enable DoRA (Weight-Decomposed Low-Rank Adaptation). Decomposes weight updates into magnitude and direction components. Can improve quality especially at low ranks, but adds training overhead.'
                    ),
                })
                .describe('LoRA adapter configuration.')
                .optional()
                .describe(
                  'PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning.'
                ),
              learning_rate: zod
                .number()
                .default(customizationCancelJobResponseSpecTrainingTwoLearningRateDefault)
                .describe(
                  'Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning.'
                ),
              min_learning_rate: zod
                .number()
                .optional()
                .describe(
                  'Minimum learning rate for cosine decay. Optional; used with learning rate schedules.'
                ),
              weight_decay: zod
                .number()
                .default(customizationCancelJobResponseSpecTrainingTwoWeightDecayDefault)
                .describe('Weight decay coefficient. Helps prevent overfitting.'),
              adam_beta1: zod
                .number()
                .default(customizationCancelJobResponseSpecTrainingTwoAdamBeta1Default)
                .describe('Adam beta1 parameter. Adjust for optimizer tuning.'),
              adam_beta2: zod
                .number()
                .default(customizationCancelJobResponseSpecTrainingTwoAdamBeta2Default)
                .describe('Adam beta2 parameter. Adjust for optimizer tuning.'),
              warmup_steps: zod
                .number()
                .min(customizationCancelJobResponseSpecTrainingTwoWarmupStepsMin)
                .default(customizationCancelJobResponseSpecTrainingTwoWarmupStepsDefault)
                .describe(
                  'Linear warmup steps. Recommended: 10% of total training steps for stable training.'
                ),
              optimizer: zod.string().optional().describe("Optimizer name (e.g., 'adamw')."),
              epochs: zod
                .number()
                .gt(customizationCancelJobResponseSpecTrainingTwoEpochsExclusiveMin)
                .default(customizationCancelJobResponseSpecTrainingTwoEpochsDefault)
                .describe(
                  'Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.'
                ),
              max_steps: zod
                .number()
                .optional()
                .describe('Max training steps. Overrides epochs if set.'),
              log_every_n_steps: zod
                .number()
                .optional()
                .describe(
                  'Logging frequency in steps. Controls how often training metrics are logged.'
                ),
              val_check_interval: zod
                .number()
                .optional()
                .describe(
                  'Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count.'
                ),
              batch_size: zod
                .number()
                .gt(customizationCancelJobResponseSpecTrainingTwoBatchSizeExclusiveMin)
                .default(customizationCancelJobResponseSpecTrainingTwoBatchSizeDefault)
                .describe(
                  'Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.'
                ),
              micro_batch_size: zod
                .number()
                .gt(customizationCancelJobResponseSpecTrainingTwoMicroBatchSizeExclusiveMin)
                .default(customizationCancelJobResponseSpecTrainingTwoMicroBatchSizeDefault)
                .describe(
                  'Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.'
                ),
              sequence_packing: zod
                .boolean()
                .default(customizationCancelJobResponseSpecTrainingTwoSequencePackingDefault)
                .describe('Enable sequence packing for efficiency. Can improve training speed.'),
              max_seq_length: zod
                .number()
                .gt(customizationCancelJobResponseSpecTrainingTwoMaxSeqLengthExclusiveMin)
                .default(customizationCancelJobResponseSpecTrainingTwoMaxSeqLengthDefault)
                .describe(
                  'Maximum token sequence length for training. Higher = more memory, longer training.'
                ),
              precision: zod
                .enum(['fp8', 'bf16', 'fp16', 'fp32'])
                .describe('Model precision for training.')
                .optional()
                .describe('Model precision for training. Auto-detected if unset.'),
              seed: zod.number().optional().describe('Random seed for reproducibility. Optional.'),
              parallelism: zod
                .object({
                  num_gpus_per_node: zod
                    .number()
                    .gt(
                      customizationCancelJobResponseSpecTrainingTwoParallelismNumGpusPerNodeExclusiveMin
                    )
                    .default(
                      customizationCancelJobResponseSpecTrainingTwoParallelismNumGpusPerNodeDefault
                    )
                    .describe('Number of gpus per node.'),
                  num_nodes: zod
                    .number()
                    .gt(
                      customizationCancelJobResponseSpecTrainingTwoParallelismNumNodesExclusiveMin
                    )
                    .default(
                      customizationCancelJobResponseSpecTrainingTwoParallelismNumNodesDefault
                    )
                    .describe('Number of nodes.'),
                  tensor_parallel_size: zod
                    .number()
                    .gt(
                      customizationCancelJobResponseSpecTrainingTwoParallelismTensorParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCancelJobResponseSpecTrainingTwoParallelismTensorParallelSizeDefault
                    )
                    .describe('Tensor parallel size.'),
                  pipeline_parallel_size: zod
                    .number()
                    .gt(
                      customizationCancelJobResponseSpecTrainingTwoParallelismPipelineParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCancelJobResponseSpecTrainingTwoParallelismPipelineParallelSizeDefault
                    )
                    .describe('Pipeline parallel size.'),
                  context_parallel_size: zod
                    .number()
                    .gt(
                      customizationCancelJobResponseSpecTrainingTwoParallelismContextParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCancelJobResponseSpecTrainingTwoParallelismContextParallelSizeDefault
                    )
                    .describe('Context parallel size.'),
                  expert_parallel_size: zod
                    .number()
                    .optional()
                    .describe('Expert parallel size (MoE models).'),
                  sequence_parallel: zod
                    .boolean()
                    .default(
                      customizationCancelJobResponseSpecTrainingTwoParallelismSequenceParallelDefault
                    )
                    .describe('Enable sequence parallelism.'),
                })
                .optional()
                .describe(
                  'Distributed training parallelism configuration.\n\nMost users only need num_gpus_per_node. Advanced users can configure\ntensor\/pipeline\/context\/expert parallelism for large models.'
                ),
              execution_profile: zod
                .string()
                .optional()
                .describe(
                  "Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default."
                ),
              type: zod
                .literal('distillation')
                .default(customizationCancelJobResponseSpecTrainingTwoTypeDefault),
              teacher_model: zod
                .string()
                .describe(
                  "Teacher model URN (e.g., 'workspace\/model-name'). Must have the same vocabulary as the student model."
                ),
              teacher_precision: zod
                .enum(['bf16', 'fp16', 'fp32'])
                .default(customizationCancelJobResponseSpecTrainingTwoTeacherPrecisionDefault)
                .describe(
                  'Precision for loading the frozen teacher model. Lower precision reduces memory but may affect logit quality.'
                ),
              distillation_ratio: zod
                .number()
                .min(customizationCancelJobResponseSpecTrainingTwoDistillationRatioMin)
                .max(customizationCancelJobResponseSpecTrainingTwoDistillationRatioMax)
                .default(customizationCancelJobResponseSpecTrainingTwoDistillationRatioDefault)
                .describe('Balance between CE loss and KD loss. 0.0 = CE only, 1.0 = KD only.'),
              distillation_temperature: zod
                .number()
                .gt(
                  customizationCancelJobResponseSpecTrainingTwoDistillationTemperatureExclusiveMin
                )
                .default(
                  customizationCancelJobResponseSpecTrainingTwoDistillationTemperatureDefault
                )
                .describe('Softmax temperature for KD. Higher = softer probability distributions.'),
            })
            .describe(
              "Knowledge Distillation with a teacher model.\n\nCustomizer's differentiator — not available in Unsloth.\nTrains the student model to match the teacher's output distribution."
            ),
          zod
            .object({
              peft: zod
                .object({
                  quantization: zod
                    .object({
                      precision: zod
                        .enum(['4bit', '8bit'])
                        .default(
                          customizationCancelJobResponseSpecTrainingThreePeftOneQuantizationOnePrecisionDefault
                        )
                        .describe(
                          "Quantization precision. '4bit' (NF4) for maximum memory savings, '8bit' (LLM.int8) for a balance of quality and memory."
                        ),
                    })
                    .describe(
                      'Base model quantization for memory-efficient PEFT training.\n\nSupports two scenarios:\n- Full-precision base model: quantized on-the-fly at load time\n- Pre-quantized base model: loaded directly at the specified precision\n\nIn both cases, base model weights are frozen and only the PEFT adapter\nparameters are trained in full precision.'
                    )
                    .optional()
                    .describe(
                      'Enable quantized training to reduce GPU memory. If the base model is full-precision, it will be quantized at load time. If the base model is already pre-quantized, this configures the expected precision. The trained adapter remains full-precision.'
                    ),
                  type: zod
                    .literal('lora')
                    .default(customizationCancelJobResponseSpecTrainingThreePeftOneTypeDefault),
                  rank: zod
                    .number()
                    .min(1)
                    .max(customizationCancelJobResponseSpecTrainingThreePeftOneRankMax)
                    .default(customizationCancelJobResponseSpecTrainingThreePeftOneRankDefault)
                    .describe(
                      'LoRA rank (low-rank dimension). Higher values increase capacity but use more memory.'
                    ),
                  alpha: zod
                    .number()
                    .min(1)
                    .default(customizationCancelJobResponseSpecTrainingThreePeftOneAlphaDefault)
                    .describe('LoRA alpha scaling factor. Common practice: alpha = 2-4x rank.'),
                  dropout: zod
                    .number()
                    .min(customizationCancelJobResponseSpecTrainingThreePeftOneDropoutMin)
                    .max(customizationCancelJobResponseSpecTrainingThreePeftOneDropoutMax)
                    .default(customizationCancelJobResponseSpecTrainingThreePeftOneDropoutDefault)
                    .describe('LoRA dropout probability for regularization.'),
                  target_modules: zod
                    .array(zod.string())
                    .optional()
                    .describe(
                      "Module name patterns to apply LoRA to (e.g., ['\*.q_proj', '\*.v_proj']). If not set, applies to all '\*proj' linear layers."
                    ),
                  merge: zod
                    .boolean()
                    .default(customizationCancelJobResponseSpecTrainingThreePeftOneMergeDefault)
                    .describe(
                      'Merge LoRA weights into base model after training. Produces a full-weight checkpoint instead of an adapter.'
                    ),
                  use_dora: zod
                    .boolean()
                    .default(customizationCancelJobResponseSpecTrainingThreePeftOneUseDoraDefault)
                    .describe(
                      'Enable DoRA (Weight-Decomposed Low-Rank Adaptation). Decomposes weight updates into magnitude and direction components. Can improve quality especially at low ranks, but adds training overhead.'
                    ),
                })
                .describe('LoRA adapter configuration.')
                .optional()
                .describe(
                  'PEFT adapter configuration. If set, trains a parameter-efficient adapter. If omitted, performs full-weight fine-tuning.'
                ),
              learning_rate: zod
                .number()
                .default(customizationCancelJobResponseSpecTrainingThreeLearningRateDefault)
                .describe(
                  'Peak learning rate. Optimal value will depend on training type and PEFT. For SFT without LoRA, start with 5e-5. If using LoRA start with 1e-4.  Lowering the value can enable for slower, more precise training; Raising the value speeds up learning.'
                ),
              min_learning_rate: zod
                .number()
                .optional()
                .describe(
                  'Minimum learning rate for cosine decay. Optional; used with learning rate schedules.'
                ),
              weight_decay: zod
                .number()
                .default(customizationCancelJobResponseSpecTrainingThreeWeightDecayDefault)
                .describe('Weight decay coefficient. Helps prevent overfitting.'),
              adam_beta1: zod
                .number()
                .default(customizationCancelJobResponseSpecTrainingThreeAdamBeta1Default)
                .describe('Adam beta1 parameter. Adjust for optimizer tuning.'),
              adam_beta2: zod
                .number()
                .default(customizationCancelJobResponseSpecTrainingThreeAdamBeta2Default)
                .describe('Adam beta2 parameter. Adjust for optimizer tuning.'),
              warmup_steps: zod
                .number()
                .min(customizationCancelJobResponseSpecTrainingThreeWarmupStepsMin)
                .default(customizationCancelJobResponseSpecTrainingThreeWarmupStepsDefault)
                .describe(
                  'Linear warmup steps. Recommended: 10% of total training steps for stable training.'
                ),
              optimizer: zod.string().optional().describe("Optimizer name (e.g., 'adamw')."),
              epochs: zod
                .number()
                .gt(customizationCancelJobResponseSpecTrainingThreeEpochsExclusiveMin)
                .default(customizationCancelJobResponseSpecTrainingThreeEpochsDefault)
                .describe(
                  'Number of complete passes through the dataset. The ideal number of epochs depends on the training method, the number of training samples, and size of the model. Start with 3 for a reasonable value. Monitor the validation and training loss curves. If both are still decreasing, you can increase this number.'
                ),
              max_steps: zod
                .number()
                .optional()
                .describe('Max training steps. Overrides epochs if set.'),
              log_every_n_steps: zod
                .number()
                .optional()
                .describe(
                  'Logging frequency in steps. Controls how often training metrics are logged.'
                ),
              val_check_interval: zod
                .number()
                .optional()
                .describe(
                  'Validation interval. Float <= 1.0 is fraction of epoch; > 1.0 is step count.'
                ),
              batch_size: zod
                .number()
                .gt(customizationCancelJobResponseSpecTrainingThreeBatchSizeExclusiveMin)
                .default(customizationCancelJobResponseSpecTrainingThreeBatchSizeDefault)
                .describe(
                  'Global batch size across all GPUs. Higher = faster but more memory. If OOM, reduce this first.'
                ),
              micro_batch_size: zod
                .number()
                .gt(customizationCancelJobResponseSpecTrainingThreeMicroBatchSizeExclusiveMin)
                .default(customizationCancelJobResponseSpecTrainingThreeMicroBatchSizeDefault)
                .describe(
                  'Per-GPU micro batch size. Keep small (1-2) for large models to avoid OOM.'
                ),
              sequence_packing: zod
                .boolean()
                .default(customizationCancelJobResponseSpecTrainingThreeSequencePackingDefault)
                .describe('Enable sequence packing for efficiency. Can improve training speed.'),
              max_seq_length: zod
                .number()
                .gt(customizationCancelJobResponseSpecTrainingThreeMaxSeqLengthExclusiveMin)
                .default(customizationCancelJobResponseSpecTrainingThreeMaxSeqLengthDefault)
                .describe(
                  'Maximum token sequence length for training. Higher = more memory, longer training.'
                ),
              precision: zod
                .enum(['fp8', 'bf16', 'fp16', 'fp32'])
                .describe('Model precision for training.')
                .optional()
                .describe('Model precision for training. Auto-detected if unset.'),
              seed: zod.number().optional().describe('Random seed for reproducibility. Optional.'),
              parallelism: zod
                .object({
                  num_gpus_per_node: zod
                    .number()
                    .gt(
                      customizationCancelJobResponseSpecTrainingThreeParallelismNumGpusPerNodeExclusiveMin
                    )
                    .default(
                      customizationCancelJobResponseSpecTrainingThreeParallelismNumGpusPerNodeDefault
                    )
                    .describe('Number of gpus per node.'),
                  num_nodes: zod
                    .number()
                    .gt(
                      customizationCancelJobResponseSpecTrainingThreeParallelismNumNodesExclusiveMin
                    )
                    .default(
                      customizationCancelJobResponseSpecTrainingThreeParallelismNumNodesDefault
                    )
                    .describe('Number of nodes.'),
                  tensor_parallel_size: zod
                    .number()
                    .gt(
                      customizationCancelJobResponseSpecTrainingThreeParallelismTensorParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCancelJobResponseSpecTrainingThreeParallelismTensorParallelSizeDefault
                    )
                    .describe('Tensor parallel size.'),
                  pipeline_parallel_size: zod
                    .number()
                    .gt(
                      customizationCancelJobResponseSpecTrainingThreeParallelismPipelineParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCancelJobResponseSpecTrainingThreeParallelismPipelineParallelSizeDefault
                    )
                    .describe('Pipeline parallel size.'),
                  context_parallel_size: zod
                    .number()
                    .gt(
                      customizationCancelJobResponseSpecTrainingThreeParallelismContextParallelSizeExclusiveMin
                    )
                    .default(
                      customizationCancelJobResponseSpecTrainingThreeParallelismContextParallelSizeDefault
                    )
                    .describe('Context parallel size.'),
                  expert_parallel_size: zod
                    .number()
                    .optional()
                    .describe('Expert parallel size (MoE models).'),
                  sequence_parallel: zod
                    .boolean()
                    .default(
                      customizationCancelJobResponseSpecTrainingThreeParallelismSequenceParallelDefault
                    )
                    .describe('Enable sequence parallelism.'),
                })
                .optional()
                .describe(
                  'Distributed training parallelism configuration.\n\nMost users only need num_gpus_per_node. Advanced users can configure\ntensor\/pipeline\/context\/expert parallelism for large models.'
                ),
              execution_profile: zod
                .string()
                .optional()
                .describe(
                  "Execution profile for the GPU training step. Maps to an operator-configured profile (e.g., 'a100', 'high_priority'). If omitted, uses the service-level default."
                ),
              type: zod
                .literal('dpo')
                .default(customizationCancelJobResponseSpecTrainingThreeTypeDefault),
              ref_policy_kl_penalty: zod
                .number()
                .min(customizationCancelJobResponseSpecTrainingThreeRefPolicyKlPenaltyMin)
                .default(customizationCancelJobResponseSpecTrainingThreeRefPolicyKlPenaltyDefault)
                .describe('KL penalty coefficient (beta in DPO paper).'),
              preference_average_log_probs: zod
                .boolean()
                .default(
                  customizationCancelJobResponseSpecTrainingThreePreferenceAverageLogProbsDefault
                )
                .describe('Average log probabilities for preference loss calculation.'),
              sft_average_log_probs: zod
                .boolean()
                .default(customizationCancelJobResponseSpecTrainingThreeSftAverageLogProbsDefault)
                .describe('Average log probabilities for SFT regularization loss.'),
              preference_loss_weight: zod
                .number()
                .min(customizationCancelJobResponseSpecTrainingThreePreferenceLossWeightMin)
                .default(customizationCancelJobResponseSpecTrainingThreePreferenceLossWeightDefault)
                .describe('Weight for the preference (DPO) loss term.'),
              sft_loss_weight: zod
                .number()
                .min(customizationCancelJobResponseSpecTrainingThreeSftLossWeightMin)
                .default(customizationCancelJobResponseSpecTrainingThreeSftLossWeightDefault)
                .describe('Weight for SFT regularization loss (0 = disabled).'),
              max_grad_norm: zod
                .number()
                .min(customizationCancelJobResponseSpecTrainingThreeMaxGradNormMin)
                .default(customizationCancelJobResponseSpecTrainingThreeMaxGradNormDefault)
                .describe('Maximum gradient norm for clipping.'),
            })
            .describe('Direct Preference Optimization.'),
        ])
        .describe('Training method and hyperparameters.'),
      integrations: zod
        .object({
          wandb: zod
            .object({
              project: zod
                .string()
                .optional()
                .describe(
                  'W&B project name (groups related runs). Defaults to output.name if not set.'
                ),
              name: zod
                .string()
                .optional()
                .describe('W&B run name. Defaults to job_id if not provided.'),
              entity: zod.string().optional().describe('W&B entity (team or username).'),
              tags: zod.array(zod.string()).optional().describe('W&B tags for filtering runs.'),
              notes: zod.string().optional().describe('W&B notes\/description for the run.'),
              base_url: zod
                .string()
                .optional()
                .describe(
                  "Base URL for self-hosted W&B server (e.g., 'https:\/\/wandb.mycompany.com'). If not provided, uses the default W&B cloud service."
                ),
              api_key_secret: zod
                .string()
                .regex(
                  customizationCancelJobResponseSpecIntegrationsOneWandbOneApiKeySecretOneRegExp
                )
                .describe(
                  "Reference to a secret. Format: 'secret_name' (uses request workspace) or 'workspace\/secret_name' (explicit workspace)."
                )
                .optional()
                .describe(
                  "Reference to a secret containing the WANDB_API_KEY. Format: 'secret_name' (uses request workspace) or 'workspace\/secret_name' (explicit workspace)."
                ),
            })
            .describe(
              'Weights & Biases integration configuration.\n\nTo use W&B, provide an api_key_secret referencing a secret that contains\nthe WANDB_API_KEY value. Optionally provide base_url for self-hosted W&B servers.'
            )
            .optional()
            .describe('Weights & Biases integration configuration.'),
          mlflow: zod
            .object({
              experiment_name: zod
                .string()
                .optional()
                .describe(
                  'MLflow experiment name (groups related runs). Defaults to output.name if not set.'
                ),
              run_name: zod
                .string()
                .optional()
                .describe('MLflow run name. Defaults to job_id if not provided.'),
              tags: zod
                .record(zod.string(), zod.string())
                .optional()
                .describe('MLflow tags as key-value pairs for filtering runs.'),
              description: zod.string().optional().describe('MLflow run description.'),
              tracking_uri: zod
                .string()
                .optional()
                .describe(
                  "MLflow tracking server URI (e.g., 'http:\/\/mlflow.mycompany.com:5000'). Can also be set via MLFLOW_TRACKING_URI environment variable."
                ),
            })
            .describe('MLflow integration configuration.')
            .optional()
            .describe('MLflow integration configuration.'),
        })
        .describe(
          'Third-party integration configurations.\n\nEach integration type has its own optional field. To enable an integration,\nprovide its configuration object. Omit or set to None to disable.'
        )
        .optional()
        .describe('Third-party integrations (e.g., Weights & Biases, MLflow).'),
      deployment_config: zod
        .union([
          zod.string().describe('A reference to DeploymentParams.'),
          zod
            .object({
              gpu: zod
                .number()
                .default(customizationCancelJobResponseSpecDeploymentConfigTwoGpuDefault)
                .describe('Number of GPUs required for the deployment'),
              additional_envs: zod
                .record(zod.string(), zod.string())
                .optional()
                .describe('Additional environment variables for the deployment'),
              disk_size: zod.string().optional().describe('Disk size for the deployment'),
              image_name: zod
                .string()
                .optional()
                .describe('Container image name from NGC. If not specified, defaults to multi-llm'),
              image_tag: zod.string().optional().describe('Container image tag from NGC'),
              lora_enabled: zod
                .boolean()
                .default(customizationCancelJobResponseSpecDeploymentConfigTwoLoraEnabledDefault)
                .describe(
                  'When automatically deploying a full SFT training, this parameter being set to true will allow subsequent LoRA adapters to be trained and deployed against it.'
                ),
              tool_call_config: zod
                .object({
                  tool_call_parser: zod
                    .string()
                    .optional()
                    .describe(
                      "Name of the tool call parser to use (e.g., 'openai', 'hermes', 'pythonic', 'llama3_json', 'mistral')."
                    ),
                  tool_call_plugin: zod
                    .string()
                    .regex(
                      customizationCancelJobResponseSpecDeploymentConfigTwoToolCallConfigOneToolCallPluginRegExp
                    )
                    .optional()
                    .describe(
                      "Reference to a fileset containing the custom tool call plugin Python file. Expected format: '{workspace}\/{fileset_name}'."
                    ),
                  auto_tool_choice: zod
                    .boolean()
                    .optional()
                    .describe('Whether to enable automatic tool choice.'),
                })
                .describe('Tool calling configuration for NIM deployments.')
                .optional()
                .describe('Tool calling configuration override for the NIM deployment.'),
            })
            .describe('Inline deployment parameters for creating a new ModelDeploymentConfig.'),
        ])
        .optional()
        .describe(
          "Deployment configuration for auto-deploying the model after training. Pass a string to reference an existing ModelDeploymentConfig by name (e.g., 'my-config' or 'workspace\/my-config'). An object provides inline NIM deployment parameters. Omit to skip deployment."
        ),
      custom_fields: zod
        .record(zod.string(), zod.unknown())
        .optional()
        .describe('Custom user-defined fields.'),
      output: zod
        .object({
          name: zod
            .string()
            .max(customizationCancelJobResponseSpecOutputOneNameMax)
            .regex(customizationCancelJobResponseSpecOutputOneNameRegExp)
            .describe(
              'Name of the output artifact. Used to identify it during deployment and inference.'
            ),
          type: zod
            .enum(['adapter', 'model'])
            .describe('Output artifact type.')
            .describe(
              'Output artifact type. Either `model` (full fine-tuned weights) or `adapter` (LoRA adapter weights).'
            ),
          fileset: zod
            .string()
            .max(customizationCancelJobResponseSpecOutputOneFilesetMax)
            .regex(customizationCancelJobResponseSpecOutputOneFilesetRegExp)
            .describe('FileSet name where output artifacts are stored.'),
        })
        .describe('Resolved output artifact details returned by the server.')
        .describe('Output artifact created by this job.'),
    })
    .describe('Customization job details returned by the server.'),
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
export const CustomizationGetJobLogsParams = zod.object({
  workspace: zod.string(),
  name: zod.string(),
});

export const CustomizationGetJobLogsQueryParams = zod.object({
  limit: zod.number().optional(),
  page_cursor: zod.string().optional(),
});

export const CustomizationGetJobLogsResponse = zod.object({
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
export const CustomizationListJobResultsParams = zod.object({
  workspace: zod.string(),
  name: zod.string(),
});

export const CustomizationListJobResultsResponse = zod.object({
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
export const CustomizationGetJobStatusParams = zod.object({
  workspace: zod.string(),
  name: zod.string(),
});

export const CustomizationGetJobStatusResponse = zod.object({
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
