# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Preference datasets for DPO training.

This module re-exports preference datasets from nemo_rl and provides extended versions
of HelpSteer3Dataset and Tulu3PreferenceDataset that support loading from local files.
"""

from nemo_rl.data.datasets.preference_datasets import BinaryPreferenceDataset, PreferenceDataset
from nemo_rl.data.datasets.utils import get_extra_kwargs

# Extended versions that support loading from local files
from nmp.customizer.tasks.training.backends.nemo_rl.preference_datasets.helpsteer3 import HelpSteer3Dataset
from nmp.customizer.tasks.training.backends.nemo_rl.preference_datasets.tulu3 import Tulu3PreferenceDataset


def load_preference_dataset(
    data_config,
) -> PreferenceDataset | HelpSteer3Dataset | BinaryPreferenceDataset | Tulu3PreferenceDataset:
    """Loads preference dataset."""
    dataset_name = data_config["dataset_name"]

    if dataset_name == "HelpSteer3":
        if "train_data_path" not in data_config:
            raise ValueError(f"train_data_path is required for dataset_name={dataset_name}.")
        if "val_data_path" not in data_config:
            raise ValueError(f"val_data_path is required for dataset_name={dataset_name}.")
        base_dataset = HelpSteer3Dataset(
            train_data_path=data_config["train_data_path"],
            val_data_path=data_config["val_data_path"],
        )
    elif dataset_name == "Tulu3Preference":
        if "train_data_path" not in data_config:
            raise ValueError(f"train_data_path is required for dataset_name={dataset_name}.")
        if "val_data_path" not in data_config:
            raise ValueError(f"val_data_path is required for dataset_name={dataset_name}.")
        base_dataset = Tulu3PreferenceDataset(
            train_data_path=data_config["train_data_path"],
            val_data_path=data_config["val_data_path"],
        )
    # fall back to load from JSON file
    elif dataset_name == "BinaryPreferenceDataset":
        if "train_data_path" not in data_config:
            raise ValueError("train_data_path is required for dataset_name=BinaryPreferenceDataset.")
        extra_kwargs = get_extra_kwargs(
            data_config,
            [
                "val_data_path",
                "prompt_key",
                "chosen_key",
                "rejected_key",
                "train_split",
                "val_split",
            ],
        )
        base_dataset = BinaryPreferenceDataset(
            train_data_path=data_config["train_data_path"],
            **extra_kwargs,
        )
    elif dataset_name == "PreferenceDataset":
        if "train_data_path" not in data_config:
            raise ValueError("train_data_path is required for dataset_name=PreferenceDataset.")
        extra_kwargs = get_extra_kwargs(
            data_config,
            [
                "val_data_path",
                "train_split",
                "val_split",
            ],
        )
        base_dataset = PreferenceDataset(
            train_data_path=data_config["train_data_path"],
            **extra_kwargs,
        )
    else:
        raise ValueError(
            f"Unsupported {dataset_name=}. "
            "Please either set dataset_name in {'HelpSteer3', 'Tulu3Preference'} to use a built-in dataset "
            "or set dataset_name in {'PreferenceDataset', 'BinaryPreferenceDataset'} to load from local JSONL file or HuggingFace."
        )

    return base_dataset


__all__ = [
    "BinaryPreferenceDataset",
    "HelpSteer3Dataset",
    "PreferenceDataset",
    "Tulu3PreferenceDataset",
]
