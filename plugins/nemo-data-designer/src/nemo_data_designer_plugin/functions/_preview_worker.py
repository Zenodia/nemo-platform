# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import tempfile
from collections.abc import Callable
from typing import Any, cast

import data_designer.config as dd
from data_designer.config.utils.io_helpers import serialize_data
from data_designer_nemo.context import DataDesignerContext
from nemo_data_designer_plugin._data_designer import create_data_designer
from nemo_data_designer_plugin.functions._preview_logs import forward_data_designer_logs
from nemo_data_designer_plugin.functions._types import (
    AnalysisFrame,
    DatasetFrame,
    DatasetMetadataFrame,
    PreviewSpec,
    ProcessorOutputFrame,
)
from pydantic import BaseModel


def make_preview_dataset(
    config_builder: dd.DataDesignerConfigBuilder,
    dd_ctx: DataDesignerContext,
    send_frame: Callable[[BaseModel], None],
    spec: PreviewSpec,
    model_providers: list[dd.ModelProvider],
    model_configs: list[dd.ModelConfig],
    num_records: int,
) -> None:
    """
    Synchronous function that runs on a worker thread under
    :func:`anyio.to_thread.run_sync`. SDK calls bridge back to the API
    process's event loop via :func:`anyio.from_thread.run` inside the
    helpers. Sends frames back to the async context via the
    ``send_frame`` callback.
    """
    with tempfile.TemporaryDirectory() as artifact_storage_tmpdir:
        data_designer = create_data_designer(
            artifact_path=artifact_storage_tmpdir,
            model_providers=model_providers,
            dd_ctx=dd_ctx,
        )
        with forward_data_designer_logs(send_frame):
            preview_results = data_designer.preview(config_builder, num_records=num_records)

        if (dataset_metadata := preview_results.dataset_metadata) is not None:
            send_frame(DatasetMetadataFrame(metadata=dataset_metadata))

        if (dataset := preview_results.dataset) is not None:
            records = cast(list[dict[str, Any]], dataset.to_dict(orient="records"))
            send_frame(DatasetFrame(records=to_jsonable_records(records)))

        for processor_name, processor_records in (preview_results.processor_artifacts or {}).items():
            send_frame(
                ProcessorOutputFrame(
                    processor_name=processor_name,
                    records=to_jsonable_records(processor_records),
                )
            )

        if (analysis := preview_results.analysis) is not None:
            send_frame(AnalysisFrame(analysis=analysis))


def to_jsonable_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return cast(list[dict[str, Any]], json.loads(serialize_data(records)))
