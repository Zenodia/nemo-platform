# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import argparse
import json

# Usage:
# To add a system prompt to the questions:
# python convert_jsonl.py input.jsonl output.jsonl "You are a helpful AI assistant."
#
# To run the script without a system prompt (system_prompt defaults to an empty string):
# python convert_jsonl.py input.jsonl output.jsonl


def convert_jsonl(input_file, output_file, system_prompt=""):
    prompt_prefix = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|>\n<|start_header_id|>user<|end_header_id|>\n\n"  # noqa: E501
    prompt_postfix = "<|eot_id|>\n<|start_header_id|>assistant<|end_header_id|>\n\n"
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            data = json.loads(line)

            new_data = {
                "prompt": f"{prompt_prefix}{data['prompt']}{prompt_postfix}",
                "chosen_response": f"{data['chosen_response']}<|eot_id|>\n",
                "rejected_response": f"{data['rejected_response']}<|eot_id|>\n",
            }

            outfile.write(json.dumps(new_data) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Convert a jsonl DPO data file to llama format.")
    parser.add_argument("input_file", type=str, help="Path to the input jsonl file.")
    parser.add_argument("output_file", type=str, help="Path to the output jsonl file.")
    parser.add_argument(
        "--system_prompt",
        type=str,
        default="",
        help="System prompt to add to each prompt (optional).",
    )

    args = parser.parse_args()

    convert_jsonl(args.input_file, args.output_file, args.system_prompt)


if __name__ == "__main__":
    main()
