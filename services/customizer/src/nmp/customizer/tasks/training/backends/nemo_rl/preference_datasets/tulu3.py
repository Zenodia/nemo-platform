# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Extended Tulu3 dataset with support for loading from local files."""

from typing import Optional

from nemo_rl.data.datasets.preference_datasets.tulu3 import (
    Tulu3PreferenceDataset as BaseTulu3PreferenceDataset,
)
from nemo_rl.data.datasets.preference_datasets.tulu3 import to_preference_data_format
from nemo_rl.data.datasets.utils import load_dataset_from_path
from nemo_rl.data.interfaces import TaskDataSpec


class Tulu3PreferenceDataset(BaseTulu3PreferenceDataset):
    """Tulu3 preference dataset for DPO training.

    This class extends the base Tulu3PreferenceDataset to support loading from local files
    in addition to downloading from HuggingFace.

    This class supports two modes of loading:
    1. From HuggingFace: If no data paths are provided, downloads from
       "allenai/llama-3.1-tulu-3-8b-preference-mixture"
    2. From local files: If train_data_path is provided, loads from JSON/JSONL files

    The input JSONL files should contain valid JSON objects formatted like this:
    {
        "chosen": list[dict],    # Full conversation with preferred response as last message
        "rejected": list[dict],  # Full conversation with rejected response as last message
    }

    Each message in the conversation should have "role" and "content" keys.
    The last message must be from "assistant" role.

    Args:
        train_data_path: Optional path to the JSON/JSONL file containing training data.
            If None, downloads from HuggingFace.
        val_data_path: Optional path to the JSON/JSONL file containing validation data.
        train_split: Split name for the training data, used for HuggingFace datasets.
            Defaults to "train" for local files, None for HuggingFace.
        val_split: Split name for the validation data, used for HuggingFace datasets.
            Defaults to "train" for local files, None for HuggingFace.
    """

    def __init__(
        self,
        train_data_path: Optional[str] = None,
        val_data_path: Optional[str] = None,
        train_split: Optional[str] = None,
        val_split: Optional[str] = None,
    ) -> None:
        if train_data_path is not None:
            # Load from local files - custom behavior
            train_ds = load_dataset_from_path(train_data_path, train_split)
            if val_data_path:
                val_ds = load_dataset_from_path(val_data_path, val_split)
            else:
                val_ds = None

            # Format the datasets
            train_ds = train_ds.map(to_preference_data_format)
            if val_ds is not None:
                val_ds = val_ds.map(to_preference_data_format)

            self.formatted_ds = {
                "train": train_ds,
                "validation": val_ds,
            }
            self.task_spec = TaskDataSpec(task_name="Tulu3Preference")
        else:
            # Download from HuggingFace - use base class behavior
            super().__init__()
