# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from nemo_platform import AsyncNeMoPlatform
from nemo_platform._exceptions import NotFoundError, PermissionDeniedError
from nemo_platform.types.models import ModelEntity
from nmp.common.entities.utils import parse_entity_ref
from nmp.customizer.app.jobs.file_io.schemas import FileSetRef


async def check_dataset_access(sdk: AsyncNeMoPlatform, dataset_uri: str, default_workspace: str) -> None:
    """Verify the caller can access the dataset fileset.

    Uses the request-scoped SDK so the call goes through AuthZ middleware,
    mirroring how ``fetch_model_entity`` validates model access.

    Raises:
        PermissionError: If the user cannot access the fileset.
        ValueError: If the fileset does not exist.
    """
    ref = FileSetRef.model_validate(dataset_uri)
    workspace = ref.workspace or default_workspace
    try:
        await sdk.files.filesets.retrieve(workspace=workspace, name=ref.name)
    except PermissionDeniedError:
        raise PermissionError(f"Access denied to dataset fileset '{workspace}/{ref.name}'") from None
    except NotFoundError:
        raise ValueError(
            f"Dataset fileset '{ref.name}' not found in workspace '{workspace}'. Verify the dataset exists."
        ) from None


async def fetch_model_entity(
    model_ref: str,
    default_workspace: str,
    sdk: AsyncNeMoPlatform,
) -> ModelEntity:
    """Retrieve a model entity by its reference string.

    Args:
        model_ref: Model reference (e.g., 'workspace/model-name' or just 'model-name').
        default_workspace: Default workspace for unqualified model references.
        sdk: SDK instance for accessing models with user context.

    Returns:
        The resolved model entity.
    """
    resolved_ref = parse_entity_ref(model_ref, default_workspace)
    try:
        return await sdk.models.retrieve(name=resolved_ref.name, workspace=resolved_ref.workspace, verbose=True)
    except PermissionDeniedError:
        raise PermissionError(f"Access denied to model '{resolved_ref.workspace}/{resolved_ref.name}'") from None
    except NotFoundError:
        raise ValueError(
            f"Model entity not found: '{resolved_ref.workspace}/{resolved_ref.name}'. Verify the model entity exists."
        ) from None
