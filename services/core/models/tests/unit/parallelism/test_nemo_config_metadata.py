# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for NeMo validation config list invariants (no Hugging Face I/O)."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_DATA_FILE = Path(__file__).resolve().parents[2] / "parallelism" / "nemo_validation_data.py"
_spec = spec_from_file_location("models_nemo_validation_data", _DATA_FILE)
_nemo_data = module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_nemo_data)
NEMO_CONFIGS = _nemo_data.NEMO_CONFIGS


def test_all_nemo_configs_have_valid_ids():
    """Verify all NeMo configs have unique IDs."""
    ids = [cfg["id"] for cfg in NEMO_CONFIGS]
    assert len(ids) == len(set(ids)), "Duplicate test IDs found in NEMO_CONFIGS"


def test_nemo_config_coverage():
    """Verify we're testing a comprehensive set of configs."""
    pre_train = sum(1 for cfg in NEMO_CONFIGS if cfg["task"] == "pre_train")
    lora = sum(1 for cfg in NEMO_CONFIGS if cfg["task"] == "lora")
    sft = sum(1 for cfg in NEMO_CONFIGS if cfg["task"] == "sft")

    assert pre_train >= 10, f"Expected >= 10 pre-training configs, got {pre_train}"
    assert lora >= 1, f"Expected >= 1 LoRA config, got {lora}"
    assert sft >= 1, f"Expected >= 1 SFT config, got {sft}"

    assert len(NEMO_CONFIGS) >= 15, f"Expected >= 15 active configs, got {len(NEMO_CONFIGS)}"
