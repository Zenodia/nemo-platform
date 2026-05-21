# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json

import numpy as np
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("nvidia/helpsteer3", split="train")

# Filter valid entries
valid_entries = [
    entry
    for entry in dataset
    if all(k in entry for k in ("context", "response1", "response2"))
    and entry["context"]
    and entry["response1"]
    and entry["response2"]
]

# Take 2000 examples
sampled_data = valid_entries[:2000]

# Prepare the final dataset format
formatted_data = [
    {"prompt": entry["context"], "chosen_response": entry["response1"], "rejected_response": entry["response2"]}
    for entry in sampled_data
]

# Shuffle and split with numpy
formatted_data = np.array(formatted_data, dtype=object)
np.random.seed(42)
np.random.shuffle(formatted_data)

n = len(formatted_data)
train_end = int(0.7 * n)
val_end = train_end + int(0.15 * n)

train_data = formatted_data[:train_end]
val_data = formatted_data[train_end:val_end]
test_data = formatted_data[val_end:]


# Save to JSONL
def save_jsonl(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")


save_jsonl(train_data, "training.jsonl")
save_jsonl(val_data, "validation.jsonl")
save_jsonl(test_data, "testing.jsonl")


print(f"Saved {len(train_data)} training, {len(val_data)} validation, and {len(test_data)} test examples.")
