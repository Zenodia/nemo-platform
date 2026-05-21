# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any

import pytest
from nemo_evaluator_sdk.values.params import (
    InferenceParams as SDKInferenceParams,
)
from nemo_evaluator_sdk.values.params import RunConfigOnlineModel
from nmp.common.inference import InferenceParams as CommonInferenceParams
from pydantic import BaseModel, ValidationError


def _normalize_field_contract(model: type[BaseModel]) -> dict[str, dict[str, Any]]:
    return {
        name: {
            "annotation": field.annotation,
            "default": field.default,
            "default_factory": field.default_factory,
            "alias": field.alias,
            "validation_alias": field.validation_alias,
            "serialization_alias": field.serialization_alias,
        }
        for name, field in model.model_fields.items()
    }


class TestInferenceParamsContract:
    def test_inference_params_contract_matches_nmp_common(self):
        expected_model_fields = CommonInferenceParams.model_fields
        expected_model_fields.pop("model")
        assert list(SDKInferenceParams.model_fields) == list(expected_model_fields)
        assert _normalize_field_contract(SDKInferenceParams) == _normalize_field_contract(CommonInferenceParams)
        assert dict(SDKInferenceParams.model_config) == dict(CommonInferenceParams.model_config)
        assert callable(getattr(SDKInferenceParams, "check_max_tokens", None))
        assert callable(getattr(CommonInferenceParams, "check_max_tokens", None))

    @pytest.mark.parametrize("model_cls", [SDKInferenceParams, CommonInferenceParams])
    def test_inference_params_enforces_same_token_limit_invariant(self, model_cls: type[BaseModel]):
        with pytest.raises(ValidationError, match="max_tokens and max_completion_tokens cannot both be configured"):
            model_cls(max_tokens=1, max_completion_tokens=1)


class TestRunConfigOnlineModelInferenceCoercion:
    def test_evaluation_job_params_coerces_nmp_common_inference_params(self):
        common_params = CommonInferenceParams.model_validate(
            {
                "temperature": 0.25,
                "max_tokens": 12,
                "extra_body": {"nvext": {"max_thinking_tokens": 64}},
            }
        )

        params = RunConfigOnlineModel.model_validate({"inference": common_params})

        assert isinstance(params.inference, SDKInferenceParams)
        assert params.inference.model_dump(mode="python") == common_params.model_dump(mode="python", exclude={"model"})

    def test_evaluation_job_params_rejects_incompatible_foreign_model(self):
        class ForeignInferenceParams(BaseModel):
            temperature: str = "hot"

        with pytest.raises(ValidationError, match="Input should be a valid number"):
            RunConfigOnlineModel.model_validate({"inference": ForeignInferenceParams()})
