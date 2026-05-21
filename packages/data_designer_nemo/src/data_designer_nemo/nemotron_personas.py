# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from dataclasses import dataclass
from typing import Literal

from nemo_platform import ConflictError, NeMoPlatform
from nemo_platform.types.files import NGCStorageConfigParam

logger = logging.getLogger(__name__)


@dataclass
class FilesetAsset:
    locale: str
    version: str = "0.0.1"
    filename: str = ""

    def __post_init__(self):
        # By default, the parquet filename stem exactly matches the locale.
        # If that is ever *not* the case, set `filename` when creating the FilesetAsset.
        if not self.filename:
            self.filename = f"{self.locale}.parquet"


_FILESET_ASSETS = [
    FilesetAsset(locale="en_IN", version="0.0.2"),
    FilesetAsset(locale="en_SG", version="0.0.1"),
    FilesetAsset(locale="en_US", version="0.0.2"),
    FilesetAsset(locale="fr_FR", version="0.0.1"),
    FilesetAsset(locale="hi_Deva_IN", version="0.0.2"),
    FilesetAsset(locale="hi_Latn_IN", version="0.0.2"),
    FilesetAsset(locale="ja_JP", version="0.0.2"),
    FilesetAsset(locale="pt_BR", version="0.0.1"),
]

SUPPORTED_LOCALES = {asset.locale: asset for asset in _FILESET_ASSETS}

NGC_ORG = "nvidia"
NGC_TEAM = "nemotron-personas"

WORKSPACE = "system"

_CREATED = "created"
_EXISTS = "exists"
NemotronPersonasFilesetSyncResult = Literal["created", "exists"]


def get_resource_name_for_locale(locale: str) -> str:
    """Returns the resource name for the Nemotron personas dataset
    for the given locale. This resource name is both the name of
    the NGC resource and the name of the fileset pointing to it.
    """
    return f"nemotron-personas-dataset-{locale.lower()}"


def get_file_path_for_locale(locale: str) -> str:
    """Returns the file path for the given locale. This represents both
    the remote path in the NGC resource and the path inside a fileset.
    """
    return SUPPORTED_LOCALES[locale].filename


def get_locale_fileset_file_ref(locale: str) -> str:
    """Returns the fully qualified reference to the Nemotron personas dataset
    parquet file for the given locale.
    """
    fileset = get_resource_name_for_locale(locale)
    file_path = get_file_path_for_locale(locale)

    return f"{WORKSPACE}/{fileset}#{file_path}"


def sync_nemotron_personas_fileset(
    *,
    sdk: NeMoPlatform,
    locale: str,
    api_key_secret: str,
) -> NemotronPersonasFilesetSyncResult:
    """
    Sync the NGC-backed fileset for a single Nemotron personas locale.

    Args:
        sdk: NeMoPlatform client.
        locale: Locale identifier (e.g. 'en_US').
        api_key_secret: Fully qualified secret reference for the NGC API key.

    Returns:
        "created" if fileset was created, "exists" if it already existed.
    """
    logger.info("Syncing Nemotron personas fileset", extra={"locale": locale})

    try:
        _create_fileset(sdk, locale, api_key_secret)
        logger.info("Successfully created Nemotron personas fileset", extra={"locale": locale})
        return _CREATED
    except ConflictError:
        logger.debug("Nemotron personas fileset already exists", extra={"locale": locale})
        return _EXISTS


def _create_fileset(sdk: NeMoPlatform, locale: str, api_key_secret: str) -> None:
    sdk.files.filesets.create(
        workspace=WORKSPACE,
        name=get_resource_name_for_locale(locale),
        description=f"Nemotron Personas dataset for locale: {locale!r}",
        purpose="dataset",
        storage=_get_storage_config_for_locale(locale, api_key_secret),
        cache=True,
    )


def _get_storage_config_for_locale(locale: str, api_key_secret: str) -> NGCStorageConfigParam:
    resource_name = get_resource_name_for_locale(locale)
    version = SUPPORTED_LOCALES[locale].version

    return NGCStorageConfigParam(
        api_key_secret=api_key_secret,
        org=NGC_ORG,
        team=NGC_TEAM,
        target=resource_name,
        target_type="resource",
        version=version,
    )
