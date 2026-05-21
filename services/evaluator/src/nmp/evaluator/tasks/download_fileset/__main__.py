# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import argparse
import asyncio
import json
import logging
import os
import shutil
from collections.abc import Sequence
from pathlib import Path

from nemo_platform import AsyncNeMoPlatform
from nmp.common.sdk_factory import get_async_platform_sdk
from nmp.evaluator.app.datasets.nmp_datasets.fileset import download_dataset
from nmp.evaluator.app.tasks.termination import register_task_signal_handlers
from nmp.evaluator.app.values import Dataset
from pydantic import TypeAdapter

log = logging.getLogger(__name__)

DatasetAdapter = TypeAdapter(Dataset)


def move_to_target(local_dir: str, target_dir: str) -> None:
    """Move downloaded files from scratch to shared storage."""
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    for item in Path(local_dir).iterdir():
        dest = target / item.name
        try:
            # If the destination file or directory already exists, remove it
            # and replace it with the new fileset.
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                    log.warning(
                        f"Removed existing directory when copying from local_dir to target_dir due to name collision: {dest}"
                    )
                else:
                    dest.unlink()
                    log.warning(
                        f"Removed existing file when copying from local_dir to target_dir due to name collision: {dest}"
                    )
            shutil.move(item, dest)
        except OSError as e:
            log.error(f"Failed to move {item} to {dest}: {e}")
            raise


async def main(
    args: Sequence[str] | None = None,
    *,
    sdk: AsyncNeMoPlatform | None = None,
) -> int:
    """Async implementation of the download_fileset task.

    Args:
        args: Optional list of CLI arguments (for testing). If None, uses sys.argv.
        sdk: Optional SDK instance for dependency injection (for testing).
            If None, uses get_async_platform_sdk().

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(description="Download a fileset from NeMo Platform")
    parser.add_argument(
        "--dataset",
        help="JSON string representing the dataset (FilesetRef or Fileset)",
    )
    parser.add_argument(
        "--dataset-file",
        type=str,
        help="Dataset file path to load DatasetRows.",
    )
    parser.add_argument("--local-dir", required=True, help="Local directory to download the fileset to")
    parser.add_argument(
        "--target-dir",
        required=False,
        help="Optional target directory on shared storage to move downloaded files into",
    )

    parsed_args = parser.parse_args(args)

    if parsed_args.dataset is None and parsed_args.dataset_file is None:
        parser.error("--dataset or --dataset-file is required")
    elif parsed_args.dataset and parsed_args.dataset_file:
        parser.error("--dataset and --dataset-file cannot both be set")

    try:
        effective_sdk = sdk or get_async_platform_sdk()
        local_dir = os.path.expandvars(parsed_args.local_dir)
        target_dir = os.path.expandvars(parsed_args.target_dir) if parsed_args.target_dir else None

        if parsed_args.dataset:
            dataset_json = json.loads(parsed_args.dataset)
        else:
            with open(parsed_args.dataset_file, "r") as f:
                dataset_json = json.load(f)

        dataset = DatasetAdapter.validate_python(dataset_json)

        await download_dataset(
            sdk=effective_sdk,
            dataset=dataset,
            destination=local_dir,
        )

        if target_dir and Path(local_dir).resolve() != Path(target_dir).resolve():
            move_to_target(local_dir, target_dir)
            log.info(f"Fileset moved successfully from {local_dir} to {target_dir}")
        else:
            log.info(f"Fileset downloaded successfully to: {local_dir}")

        return 0
    except Exception:
        log.exception("Error downloading fileset")
        return 1


def run(
    args: Sequence[str] | None = None,
    *,
    sdk: AsyncNeMoPlatform | None = None,
) -> int:
    """Synchronous entry point for the download_fileset task.

    Args:
        args: Optional list of CLI arguments (for testing). If None, uses sys.argv.
        sdk: Optional SDK instance for dependency injection (for testing).
            If None, uses get_async_platform_sdk().

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    register_task_signal_handlers()
    try:
        return asyncio.run(main(args, sdk=sdk))
    except KeyboardInterrupt:
        log.info("Received termination signal. Exiting task gracefully.")
        return 0
    except Exception:
        log.exception("Error in download_fileset task")
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
