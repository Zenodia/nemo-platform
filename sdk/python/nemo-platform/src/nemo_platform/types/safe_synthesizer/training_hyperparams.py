# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["TrainingHyperparams"]


class TrainingHyperparams(BaseModel):
    """Hyperparameters that control the training process behavior.

    This class contains all the fine-tuning hyperparameters that control how the model
    learns, including learning rates, batch sizes, LoRA configuration, and optimization
    settings. These parameters directly affect training performance and quality.
    """

    attn_implementation: Optional[str] = None
    """The attention implementation to use for model loading.

    Default uses Flash Attention 3 via the HuggingFace Kernels Hub (requires the
    'kernels' pip package; falls back to 'sdpa' if the 'kernels' package is not
    installed). Other common values: 'flash_attention_2' (requires flash-attn pip
    package), 'sdpa' (PyTorch scaled dot product attention), 'eager' (standard
    PyTorch). Custom HuggingFace Kernels Hub paths (e.g.
    'kernels-community/flash-attn2') are also supported.
    """

    batch_size: Optional[int] = None
    """The batch size per device for training. Must be >= 1."""

    gradient_accumulation_steps: Optional[int] = None
    """
    Number of update steps to accumulate the gradients for, before performing a
    backward/update pass. This technique increases the effective batch size that
    will fit into GPU memory. Must be >= 1.
    """

    learning_rate: Union[Literal["auto"], float, None] = None
    """The initial learning rate for `AdamW` optimizer.

    Must be in (0, 1). Setting to 'auto' uses a model-specific default if one
    exists.
    """

    lora_alpha_over_r: Optional[float] = None
    """The ratio of the LoRA scaling factor (alpha) to the LoRA rank.

    Empirically, this parameter works well when set to 0.5, 1, or 2. Must be in
    [0.5, 3].
    """

    lora_r: Optional[int] = None
    """The rank of the LoRA update matrices.

    Lower rank results in smaller update matrices with fewer trainable parameters.
    Must be > 0.
    """

    lora_target_modules: Optional[List[str]] = None
    """The list of transformer modules to apply LoRA to.

    Possible modules: 'q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj',
    'up_proj', 'down_proj'.
    """

    lr_scheduler: Optional[str] = None
    """The scheduler type to use.

    See the HuggingFace documentation of `SchedulerType` for all possible values.
    """

    max_vram_fraction: Optional[float] = None
    """The fraction of the total VRAM to use for training.

    Modify this to allow longer sequences. Must be in [0, 1].
    """

    num_input_records_to_sample: Union[Literal["auto"], int, None] = None
    """Number of records the model will see during training.

    This parameter is a proxy for training time. For example, if its value is the
    same size as the input dataset, this is like training for a single epoch. If its
    value is larger, this is like training for multiple (possibly fractional)
    epochs. If its value is smaller, this is like training for a fraction of an
    epoch. Supports 'auto' where a reasonable value is chosen based on other config
    params and data.
    """

    peft_implementation: Optional[str] = None
    """The PEFT (Parameter-Efficient Fine-Tuning) implementation to use.

    Options: 'lora' for Low-Rank Adaptation, 'QLORA' for Quantized LoRA.
    """

    pretrained_model: Optional[str] = None
    """Pretrained model to use for fine-tuning.

    Defaults to SmolLM3. May be a Hugging Face model ID (loaded from the Hugging
    Face Hub or cache) or a local path. See security note in docs before using
    untrusted sources.
    """

    quantization_bits: Optional[Literal[4, 8]] = None
    """The number of bits to use for quantization if `quantize_model` is `True`.

    Accepts 8 or 4.
    """

    quantize_model: Optional[bool] = None
    """Whether to quantize the model during training.

    This can reduce memory usage and potentially speed up training, but may also
    impact model accuracy.
    """

    rope_scaling_factor: Union[Literal["auto"], int, None] = None
    """Scale the base LLM's context length by this factor using RoPE scaling.

    Must be >= 1 or 'auto'.
    """

    use_unsloth: Union[Literal["auto"], bool, None] = None
    """Whether to use Unsloth for optimized training."""

    validation_ratio: Optional[float] = None
    """The fraction of the training data used for validation.

    Must be in [0, 1]. If set to 0, no validation will be performed. If set larger
    than 0, validation loss will be computed and reported throughout training.
    """

    validation_steps: Optional[int] = None
    """The number of steps between validation checks for the HF Trainer arguments.

    Must be > 0.
    """

    warmup_ratio: Optional[float] = None
    """
    Ratio of total training steps used for a linear warmup from 0 to the learning
    rate. Must be > 0.
    """

    weight_decay: Optional[float] = None
    """
    The weight decay to apply to all layers except all bias and LayerNorm weights in
    the AdamW optimizer. Must be in (0, 1).
    """
