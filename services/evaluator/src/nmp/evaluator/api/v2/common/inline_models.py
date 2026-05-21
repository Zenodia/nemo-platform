# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Service API wrappers for inline SDK model and agent definitions."""

from typing import Any

from nemo_evaluator_sdk.values import Agent as SDKAgent
from nemo_evaluator_sdk.values import Model as SDKModel
from nmp.common.api.common import SecretRef as ApiSecretRef
from pydantic import Field, model_validator

# Subclasses :class:`SDKModel` / :class:`SDKAgent` solely to swap the SDK's
# relaxed ``SecretRef`` pattern that allows uppercase secret names for
# the strict service ``ApiSecretRef`` on ``api_key_secret``,
# so the public API spec keeps the lowercase-only contract
# while the SDK can accept uppercase secret names.


class Model(SDKModel):
    """Model definition for use without persisting to the Models API."""

    # Keep the OpenAPI $defs key as `Model`, not the qualified service path —
    # downstream spec post-processing keys off the original SDK module name.
    __module__ = "nemo_evaluator_sdk.values.models"

    api_key_secret: ApiSecretRef | None = Field(
        default=None,
        description=SDKModel.model_fields["api_key_secret"].description,
    )

    @model_validator(mode="before")
    @classmethod
    def coerce_sdk_model(cls, value: Any) -> Any:
        """Re-validate SDK model instances against this stricter wrapper.

        Pydantic does not implicitly downcast a parent-class instance to a
        subclass, so callers passing already-built ``SDKModel`` values (for
        example, app-layer or entity-layer values flowing into a response
        schema) are dumped to a dict here and re-validated under the strict
        ``ApiSecretRef`` pattern.
        """
        if isinstance(value, SDKModel) and not isinstance(value, cls):
            return value.model_dump(mode="python")
        return value


class Agent(SDKAgent):
    """Agent definition for inference in online evaluation jobs.

    An agent is an endpoint that accepts a request and returns a response,
    potentially with a trajectory. Two formats are supported:

    - ``generic``: configurable HTTP POST with Jinja-templated body and
      JSONPath extraction for response and trajectory.
    - ``nemo_agent_toolkit``: NeMo Agent Toolkit SSE streaming protocol
      (``/generate/full?filter_steps=none``).
    """

    # Keep the OpenAPI $defs key as `Agent`, not the qualified service path.
    __module__ = "nemo_evaluator_sdk.values.agents"

    api_key_secret: ApiSecretRef | None = Field(
        default=None,
        description=SDKAgent.model_fields["api_key_secret"].description,
    )

    @model_validator(mode="before")
    @classmethod
    def coerce_sdk_agent(cls, value: Any) -> Any:
        """Re-validate SDK agent instances against this stricter wrapper.

        See :meth:`Model.coerce_sdk_model` for the rationale.
        """
        if isinstance(value, SDKAgent) and not isinstance(value, cls):
            return value.model_dump(mode="python")
        return value


__all__ = ["Agent", "Model"]
