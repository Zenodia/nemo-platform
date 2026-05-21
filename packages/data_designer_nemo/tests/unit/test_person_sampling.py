# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import AsyncMock, MagicMock

import data_designer.config as dd
import pytest
from data_designer_nemo.errors import NDDInternalError
from data_designer_nemo.person_sampling import (
    ensure_nemotron_personas_filesets,
)
from nemo_platform import AsyncNeMoPlatform, NotFoundError, PermissionDeniedError


def _make_person_sampler_column(name: str, locale: str) -> dd.SamplerColumnConfig:
    return dd.SamplerColumnConfig(
        name=name,
        sampler_type=dd.SamplerType.PERSON,
        params=dd.PersonSamplerParams(locale=locale),
    )


def _make_config(*columns: dd.SamplerColumnConfig) -> dd.DataDesignerConfig:
    builder = dd.DataDesignerConfigBuilder()
    for column in columns:
        builder.add_column(column_config=column)
    return builder.build()


@pytest.mark.asyncio
async def test_ensure_nemotron_personas_filesets_checks_each_locale() -> None:
    sdk = AsyncMock(spec=AsyncNeMoPlatform)
    sdk.files.filesets.retrieve = AsyncMock()
    config = _make_config(
        _make_person_sampler_column("person_us", "en_US"),
        _make_person_sampler_column("person_jp", "ja_JP"),
    )

    await ensure_nemotron_personas_filesets(config, sdk)

    assert sdk.files.filesets.retrieve.await_count == 2


@pytest.mark.asyncio
async def test_ensure_nemotron_personas_filesets_raises_error_for_missing_fileset() -> None:
    sdk = AsyncMock(spec=AsyncNeMoPlatform)
    sdk.files.filesets.retrieve.side_effect = NotFoundError("missing", response=MagicMock(), body=None)
    config = _make_config(_make_person_sampler_column("person", "en_US"))

    with pytest.raises(NDDInternalError):
        await ensure_nemotron_personas_filesets(config, sdk)


@pytest.mark.asyncio
async def test_ensure_nemotron_personas_filesets_raises_error_for_permission_error() -> None:
    sdk = AsyncMock(spec=AsyncNeMoPlatform)
    sdk.files.filesets.retrieve.side_effect = PermissionDeniedError("denied", response=MagicMock(), body=None)
    config = _make_config(_make_person_sampler_column("person", "en_US"))

    with pytest.raises(NDDInternalError):
        await ensure_nemotron_personas_filesets(config, sdk)


@pytest.mark.asyncio
async def test_ensure_nemotron_personas_filesets_raises_internal_error_on_other_errors() -> None:
    sdk = AsyncMock(spec=AsyncNeMoPlatform)
    sdk.files.filesets.retrieve.side_effect = RuntimeError("something went wrong")
    config = _make_config(_make_person_sampler_column("person", "en_US"))

    with pytest.raises(NDDInternalError):
        await ensure_nemotron_personas_filesets(config, sdk)
