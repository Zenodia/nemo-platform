# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import tempfile

import data_designer.config as dd
import pandas as pd
import pytest
from data_designer_nemo.errors import NDDInvalidConfigError
from nemo_data_designer_plugin.functions._types import PreviewSpec
from nemo_data_designer_plugin.jobs.spec import DataDesignerJobConfig


def test_dataframe_seeds_are_rejected() -> None:
    config = DataDesignerJobConfig(
        num_records=42,
        config=dd.DataDesignerConfig(
            columns=[
                dd.LLMTextColumnConfig(
                    name="storytime",
                    model_alias="text",
                    prompt="Tell me a story",
                )
            ],
            seed_config=dd.SeedConfig(
                source=dd.DataFrameSeedSource(df=pd.DataFrame()),
            ),
        ),
    )

    with pytest.raises(NDDInvalidConfigError) as exc_info:
        DataDesignerJobConfig.model_validate(config.model_dump())

    assert "seed data" in str(exc_info.value)


def test_local_file_seeds_are_rejected() -> None:
    with tempfile.NamedTemporaryFile(suffix=".parquet") as tmpfile:
        config = DataDesignerJobConfig(
            num_records=42,
            config=dd.DataDesignerConfig(
                columns=[
                    dd.LLMTextColumnConfig(
                        name="storytime",
                        model_alias="text",
                        prompt="Tell me a story",
                    )
                ],
                seed_config=dd.SeedConfig(
                    source=dd.LocalFileSeedSource(path=tmpfile.name),
                ),
            ),
        )

        with pytest.raises(NDDInvalidConfigError) as exc_info:
            DataDesignerJobConfig.model_validate(config.model_dump())

        assert "seed data" in str(exc_info.value)


def test_dataframe_seeds_are_rejected_with_clear_local_context_error() -> None:
    config = DataDesignerJobConfig(
        num_records=42,
        config=dd.DataDesignerConfig(
            columns=[dd.ExpressionColumnConfig(name="value", expr="1")],
            seed_config=dd.SeedConfig(
                source=dd.DataFrameSeedSource(df=pd.DataFrame(data={"value": [1, 2, 3]})),
            ),
        ),
    )
    payload = config.model_dump(mode="json")

    with pytest.raises(NDDInvalidConfigError) as job_exc_info:
        DataDesignerJobConfig.model_validate(payload, context={"is_local": True})
    with pytest.raises(NDDInvalidConfigError) as preview_exc_info:
        PreviewSpec.model_validate({"config": payload["config"]}, context={"is_local": True})

    assert "Dataframe seed sources" in str(job_exc_info.value)
    assert "missing" not in str(job_exc_info.value)
    assert "Dataframe seed sources" in str(preview_exc_info.value)
    assert "missing" not in str(preview_exc_info.value)


def test_local_context_allows_local_file_seeds() -> None:
    with tempfile.NamedTemporaryFile(suffix=".parquet") as tmpfile:
        config = DataDesignerJobConfig(
            num_records=42,
            config=dd.DataDesignerConfig(
                columns=[dd.ExpressionColumnConfig(name="value", expr="1")],
                seed_config=dd.SeedConfig(
                    source=dd.LocalFileSeedSource(path=tmpfile.name),
                ),
            ),
        )
        payload = config.model_dump(mode="json")

        DataDesignerJobConfig.model_validate(payload, context={"is_local": True})
        PreviewSpec.model_validate({"config": payload["config"]}, context={"is_local": True})
