# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nemo_platform import NeMoPlatform, AsyncNeMoPlatform
from nemo_platform._utils import parse_datetime
from nemo_platform.pagination import (
    SyncLogsPagination,
    AsyncLogsPagination,
    SyncDefaultPagination,
    AsyncDefaultPagination,
)
from nemo_platform.types.shared import PlatformJobLog, PlatformJobStatusResponse
from nemo_platform.types.safe_synthesizer import (
    SafeSynthesizerJob,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestJobs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create(self, client: NeMoPlatform) -> None:
        job = client.safe_synthesizer.jobs.create(
            workspace="workspace",
            spec={
                "config": {},
                "data_source": "data_source",
            },
        )
        assert_matches_type(SafeSynthesizerJob, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: NeMoPlatform) -> None:
        job = client.safe_synthesizer.jobs.create(
            workspace="workspace",
            spec={
                "config": {
                    "data": {
                        "group_training_examples_by": "group_training_examples_by",
                        "holdout": 0,
                        "max_holdout": 0,
                        "max_sequences_per_example": "auto",
                        "order_training_examples_by": "order_training_examples_by",
                        "random_state": 0,
                    },
                    "evaluation": {
                        "aia_enabled": True,
                        "enabled": True,
                        "mandatory_columns": 0,
                        "mia_enabled": True,
                        "pii_replay_columns": ["string"],
                        "pii_replay_enabled": True,
                        "pii_replay_entities": ["string"],
                        "quasi_identifier_count": 0,
                        "sqs_report_columns": 0,
                        "sqs_report_rows": 0,
                    },
                    "generation": {
                        "attention_backend": "attention_backend",
                        "enforce_timeseries_fidelity": True,
                        "invalid_fraction_threshold": 0,
                        "num_records": 0,
                        "patience": 0,
                        "repetition_penalty": 0,
                        "structured_generation_backend": "auto",
                        "structured_generation_schema_method": "regex",
                        "structured_generation_use_single_sequence": True,
                        "temperature": 0,
                        "top_p": 0,
                        "use_structured_generation": True,
                        "validation": {
                            "group_by_accept_no_delineator": True,
                            "group_by_fix_non_unique_value": True,
                            "group_by_fix_unordered_records": True,
                            "group_by_ignore_invalid_records": True,
                        },
                    },
                    "privacy": {
                        "delta": "auto",
                        "dp_enabled": True,
                        "epsilon": 0,
                        "per_sample_max_grad_norm": 0,
                    },
                    "replace_pii": {
                        "steps": [
                            {
                                "columns": {
                                    "add": [
                                        {
                                            "condition": "condition",
                                            "entity": "string",
                                            "name": "name",
                                            "position": 0,
                                            "type": "string",
                                            "value": "value",
                                        }
                                    ],
                                    "drop": [
                                        {
                                            "condition": "condition",
                                            "entity": "string",
                                            "name": "name",
                                            "position": 0,
                                            "type": "string",
                                            "value": "value",
                                        }
                                    ],
                                    "rename": [
                                        {
                                            "condition": "condition",
                                            "entity": "string",
                                            "name": "name",
                                            "position": 0,
                                            "type": "string",
                                            "value": "value",
                                        }
                                    ],
                                },
                                "rows": {
                                    "drop": [
                                        {
                                            "condition": "condition",
                                            "description": "description",
                                            "entity": "string",
                                            "fallback_value": "fallback_value",
                                            "foreach": "foreach",
                                            "name": "string",
                                            "type": "string",
                                            "value": "value",
                                        }
                                    ],
                                    "update": [
                                        {
                                            "condition": "condition",
                                            "description": "description",
                                            "entity": "string",
                                            "fallback_value": "fallback_value",
                                            "foreach": "foreach",
                                            "name": "string",
                                            "type": "string",
                                            "value": "value",
                                        }
                                    ],
                                },
                                "vars": {"foo": "string"},
                            }
                        ],
                        "globals": {
                            "classify": {
                                "classify_model_provider": "classify_model_provider",
                                "enable_classify": True,
                                "entities": ["string"],
                                "num_samples": 0,
                            },
                            "locales": ["string"],
                            "lock_columns": ["string"],
                            "ner": {
                                "enable_regexps": True,
                                "gliner": {
                                    "batch_size": 0,
                                    "chunk_length": 0,
                                    "enable_batch_mode": True,
                                    "enable_gliner": True,
                                    "gliner_model": "gliner_model",
                                },
                                "ner_entities": ["string"],
                                "ner_threshold": 0,
                            },
                            "seed": -2147483646,
                        },
                    },
                    "time_series": {
                        "is_timeseries": True,
                        "start_timestamp": "string",
                        "stop_timestamp": "string",
                        "timestamp_column": "timestamp_column",
                        "timestamp_format": "timestamp_format",
                        "timestamp_interval_seconds": 0,
                    },
                    "training": {
                        "attn_implementation": "attn_implementation",
                        "batch_size": 0,
                        "gradient_accumulation_steps": 0,
                        "learning_rate": "auto",
                        "lora_alpha_over_r": 0,
                        "lora_r": 0,
                        "lora_target_modules": ["string"],
                        "lr_scheduler": "lr_scheduler",
                        "max_vram_fraction": 0,
                        "num_input_records_to_sample": "auto",
                        "peft_implementation": "peft_implementation",
                        "pretrained_model": "pretrained_model",
                        "quantization_bits": 4,
                        "quantize_model": True,
                        "rope_scaling_factor": "auto",
                        "use_unsloth": "auto",
                        "validation_ratio": 0,
                        "validation_steps": 0,
                        "warmup_ratio": 0,
                        "weight_decay": 0,
                    },
                },
                "data_source": "data_source",
                "enable_synthesis": True,
                "hf_token_secret": "hf_token_secret",
            },
            custom_fields={"foo": "bar"},
            description="description",
            name="name",
            ownership={"foo": "bar"},
            project="project",
        )
        assert_matches_type(SafeSynthesizerJob, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: NeMoPlatform) -> None:
        response = client.safe_synthesizer.jobs.with_raw_response.create(
            workspace="workspace",
            spec={
                "config": {},
                "data_source": "data_source",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(SafeSynthesizerJob, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: NeMoPlatform) -> None:
        with client.safe_synthesizer.jobs.with_streaming_response.create(
            workspace="workspace",
            spec={
                "config": {},
                "data_source": "data_source",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(SafeSynthesizerJob, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_create(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.safe_synthesizer.jobs.with_raw_response.create(
                workspace="",
                spec={
                    "config": {},
                    "data_source": "data_source",
                },
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: NeMoPlatform) -> None:
        job = client.safe_synthesizer.jobs.retrieve(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(SafeSynthesizerJob, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: NeMoPlatform) -> None:
        response = client.safe_synthesizer.jobs.with_raw_response.retrieve(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(SafeSynthesizerJob, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: NeMoPlatform) -> None:
        with client.safe_synthesizer.jobs.with_streaming_response.retrieve(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(SafeSynthesizerJob, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.safe_synthesizer.jobs.with_raw_response.retrieve(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.safe_synthesizer.jobs.with_raw_response.retrieve(
                name="",
                workspace="workspace",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_list(self, client: NeMoPlatform) -> None:
        job = client.safe_synthesizer.jobs.list(
            workspace="workspace",
        )
        assert_matches_type(SyncDefaultPagination[SafeSynthesizerJob], job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: NeMoPlatform) -> None:
        job = client.safe_synthesizer.jobs.list(
            workspace="workspace",
            filter={
                "created_at": {
                    "gte": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "lte": parse_datetime("2019-12-27T18:11:19.117Z"),
                },
                "name": "name",
                "project": "project",
                "status": "created",
                "updated_at": {
                    "gte": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "lte": parse_datetime("2019-12-27T18:11:19.117Z"),
                },
                "workspace": "workspace",
            },
            page=1,
            page_size=1,
            sort="created_at",
        )
        assert_matches_type(SyncDefaultPagination[SafeSynthesizerJob], job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: NeMoPlatform) -> None:
        response = client.safe_synthesizer.jobs.with_raw_response.list(
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(SyncDefaultPagination[SafeSynthesizerJob], job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: NeMoPlatform) -> None:
        with client.safe_synthesizer.jobs.with_streaming_response.list(
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(SyncDefaultPagination[SafeSynthesizerJob], job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_list(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.safe_synthesizer.jobs.with_raw_response.list(
                workspace="",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_delete(self, client: NeMoPlatform) -> None:
        job = client.safe_synthesizer.jobs.delete(
            name="name",
            workspace="workspace",
        )
        assert job is None

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: NeMoPlatform) -> None:
        response = client.safe_synthesizer.jobs.with_raw_response.delete(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert job is None

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: NeMoPlatform) -> None:
        with client.safe_synthesizer.jobs.with_streaming_response.delete(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert job is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.safe_synthesizer.jobs.with_raw_response.delete(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.safe_synthesizer.jobs.with_raw_response.delete(
                name="",
                workspace="workspace",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_cancel(self, client: NeMoPlatform) -> None:
        job = client.safe_synthesizer.jobs.cancel(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(SafeSynthesizerJob, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_cancel(self, client: NeMoPlatform) -> None:
        response = client.safe_synthesizer.jobs.with_raw_response.cancel(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(SafeSynthesizerJob, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_cancel(self, client: NeMoPlatform) -> None:
        with client.safe_synthesizer.jobs.with_streaming_response.cancel(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(SafeSynthesizerJob, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_cancel(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.safe_synthesizer.jobs.with_raw_response.cancel(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.safe_synthesizer.jobs.with_raw_response.cancel(
                name="",
                workspace="workspace",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_get_logs(self, client: NeMoPlatform) -> None:
        job = client.safe_synthesizer.jobs.get_logs(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(SyncLogsPagination[PlatformJobLog], job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_get_logs_with_all_params(self, client: NeMoPlatform) -> None:
        job = client.safe_synthesizer.jobs.get_logs(
            name="name",
            workspace="workspace",
            limit=0,
            page_cursor="page_cursor",
        )
        assert_matches_type(SyncLogsPagination[PlatformJobLog], job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_get_logs(self, client: NeMoPlatform) -> None:
        response = client.safe_synthesizer.jobs.with_raw_response.get_logs(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(SyncLogsPagination[PlatformJobLog], job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_get_logs(self, client: NeMoPlatform) -> None:
        with client.safe_synthesizer.jobs.with_streaming_response.get_logs(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(SyncLogsPagination[PlatformJobLog], job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_get_logs(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.safe_synthesizer.jobs.with_raw_response.get_logs(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.safe_synthesizer.jobs.with_raw_response.get_logs(
                name="",
                workspace="workspace",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_get_status(self, client: NeMoPlatform) -> None:
        job = client.safe_synthesizer.jobs.get_status(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(PlatformJobStatusResponse, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_get_status(self, client: NeMoPlatform) -> None:
        response = client.safe_synthesizer.jobs.with_raw_response.get_status(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(PlatformJobStatusResponse, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_get_status(self, client: NeMoPlatform) -> None:
        with client.safe_synthesizer.jobs.with_streaming_response.get_status(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(PlatformJobStatusResponse, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_get_status(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.safe_synthesizer.jobs.with_raw_response.get_status(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.safe_synthesizer.jobs.with_raw_response.get_status(
                name="",
                workspace="workspace",
            )


class TestAsyncJobs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncNeMoPlatform) -> None:
        job = await async_client.safe_synthesizer.jobs.create(
            workspace="workspace",
            spec={
                "config": {},
                "data_source": "data_source",
            },
        )
        assert_matches_type(SafeSynthesizerJob, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNeMoPlatform) -> None:
        job = await async_client.safe_synthesizer.jobs.create(
            workspace="workspace",
            spec={
                "config": {
                    "data": {
                        "group_training_examples_by": "group_training_examples_by",
                        "holdout": 0,
                        "max_holdout": 0,
                        "max_sequences_per_example": "auto",
                        "order_training_examples_by": "order_training_examples_by",
                        "random_state": 0,
                    },
                    "evaluation": {
                        "aia_enabled": True,
                        "enabled": True,
                        "mandatory_columns": 0,
                        "mia_enabled": True,
                        "pii_replay_columns": ["string"],
                        "pii_replay_enabled": True,
                        "pii_replay_entities": ["string"],
                        "quasi_identifier_count": 0,
                        "sqs_report_columns": 0,
                        "sqs_report_rows": 0,
                    },
                    "generation": {
                        "attention_backend": "attention_backend",
                        "enforce_timeseries_fidelity": True,
                        "invalid_fraction_threshold": 0,
                        "num_records": 0,
                        "patience": 0,
                        "repetition_penalty": 0,
                        "structured_generation_backend": "auto",
                        "structured_generation_schema_method": "regex",
                        "structured_generation_use_single_sequence": True,
                        "temperature": 0,
                        "top_p": 0,
                        "use_structured_generation": True,
                        "validation": {
                            "group_by_accept_no_delineator": True,
                            "group_by_fix_non_unique_value": True,
                            "group_by_fix_unordered_records": True,
                            "group_by_ignore_invalid_records": True,
                        },
                    },
                    "privacy": {
                        "delta": "auto",
                        "dp_enabled": True,
                        "epsilon": 0,
                        "per_sample_max_grad_norm": 0,
                    },
                    "replace_pii": {
                        "steps": [
                            {
                                "columns": {
                                    "add": [
                                        {
                                            "condition": "condition",
                                            "entity": "string",
                                            "name": "name",
                                            "position": 0,
                                            "type": "string",
                                            "value": "value",
                                        }
                                    ],
                                    "drop": [
                                        {
                                            "condition": "condition",
                                            "entity": "string",
                                            "name": "name",
                                            "position": 0,
                                            "type": "string",
                                            "value": "value",
                                        }
                                    ],
                                    "rename": [
                                        {
                                            "condition": "condition",
                                            "entity": "string",
                                            "name": "name",
                                            "position": 0,
                                            "type": "string",
                                            "value": "value",
                                        }
                                    ],
                                },
                                "rows": {
                                    "drop": [
                                        {
                                            "condition": "condition",
                                            "description": "description",
                                            "entity": "string",
                                            "fallback_value": "fallback_value",
                                            "foreach": "foreach",
                                            "name": "string",
                                            "type": "string",
                                            "value": "value",
                                        }
                                    ],
                                    "update": [
                                        {
                                            "condition": "condition",
                                            "description": "description",
                                            "entity": "string",
                                            "fallback_value": "fallback_value",
                                            "foreach": "foreach",
                                            "name": "string",
                                            "type": "string",
                                            "value": "value",
                                        }
                                    ],
                                },
                                "vars": {"foo": "string"},
                            }
                        ],
                        "globals": {
                            "classify": {
                                "classify_model_provider": "classify_model_provider",
                                "enable_classify": True,
                                "entities": ["string"],
                                "num_samples": 0,
                            },
                            "locales": ["string"],
                            "lock_columns": ["string"],
                            "ner": {
                                "enable_regexps": True,
                                "gliner": {
                                    "batch_size": 0,
                                    "chunk_length": 0,
                                    "enable_batch_mode": True,
                                    "enable_gliner": True,
                                    "gliner_model": "gliner_model",
                                },
                                "ner_entities": ["string"],
                                "ner_threshold": 0,
                            },
                            "seed": -2147483646,
                        },
                    },
                    "time_series": {
                        "is_timeseries": True,
                        "start_timestamp": "string",
                        "stop_timestamp": "string",
                        "timestamp_column": "timestamp_column",
                        "timestamp_format": "timestamp_format",
                        "timestamp_interval_seconds": 0,
                    },
                    "training": {
                        "attn_implementation": "attn_implementation",
                        "batch_size": 0,
                        "gradient_accumulation_steps": 0,
                        "learning_rate": "auto",
                        "lora_alpha_over_r": 0,
                        "lora_r": 0,
                        "lora_target_modules": ["string"],
                        "lr_scheduler": "lr_scheduler",
                        "max_vram_fraction": 0,
                        "num_input_records_to_sample": "auto",
                        "peft_implementation": "peft_implementation",
                        "pretrained_model": "pretrained_model",
                        "quantization_bits": 4,
                        "quantize_model": True,
                        "rope_scaling_factor": "auto",
                        "use_unsloth": "auto",
                        "validation_ratio": 0,
                        "validation_steps": 0,
                        "warmup_ratio": 0,
                        "weight_decay": 0,
                    },
                },
                "data_source": "data_source",
                "enable_synthesis": True,
                "hf_token_secret": "hf_token_secret",
            },
            custom_fields={"foo": "bar"},
            description="description",
            name="name",
            ownership={"foo": "bar"},
            project="project",
        )
        assert_matches_type(SafeSynthesizerJob, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.safe_synthesizer.jobs.with_raw_response.create(
            workspace="workspace",
            spec={
                "config": {},
                "data_source": "data_source",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = await response.parse()
        assert_matches_type(SafeSynthesizerJob, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.safe_synthesizer.jobs.with_streaming_response.create(
            workspace="workspace",
            spec={
                "config": {},
                "data_source": "data_source",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(SafeSynthesizerJob, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.safe_synthesizer.jobs.with_raw_response.create(
                workspace="",
                spec={
                    "config": {},
                    "data_source": "data_source",
                },
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        job = await async_client.safe_synthesizer.jobs.retrieve(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(SafeSynthesizerJob, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.safe_synthesizer.jobs.with_raw_response.retrieve(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = await response.parse()
        assert_matches_type(SafeSynthesizerJob, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.safe_synthesizer.jobs.with_streaming_response.retrieve(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(SafeSynthesizerJob, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.safe_synthesizer.jobs.with_raw_response.retrieve(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.safe_synthesizer.jobs.with_raw_response.retrieve(
                name="",
                workspace="workspace",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncNeMoPlatform) -> None:
        job = await async_client.safe_synthesizer.jobs.list(
            workspace="workspace",
        )
        assert_matches_type(AsyncDefaultPagination[SafeSynthesizerJob], job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncNeMoPlatform) -> None:
        job = await async_client.safe_synthesizer.jobs.list(
            workspace="workspace",
            filter={
                "created_at": {
                    "gte": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "lte": parse_datetime("2019-12-27T18:11:19.117Z"),
                },
                "name": "name",
                "project": "project",
                "status": "created",
                "updated_at": {
                    "gte": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "lte": parse_datetime("2019-12-27T18:11:19.117Z"),
                },
                "workspace": "workspace",
            },
            page=1,
            page_size=1,
            sort="created_at",
        )
        assert_matches_type(AsyncDefaultPagination[SafeSynthesizerJob], job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.safe_synthesizer.jobs.with_raw_response.list(
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = await response.parse()
        assert_matches_type(AsyncDefaultPagination[SafeSynthesizerJob], job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.safe_synthesizer.jobs.with_streaming_response.list(
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(AsyncDefaultPagination[SafeSynthesizerJob], job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.safe_synthesizer.jobs.with_raw_response.list(
                workspace="",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncNeMoPlatform) -> None:
        job = await async_client.safe_synthesizer.jobs.delete(
            name="name",
            workspace="workspace",
        )
        assert job is None

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.safe_synthesizer.jobs.with_raw_response.delete(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = await response.parse()
        assert job is None

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.safe_synthesizer.jobs.with_streaming_response.delete(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert job is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.safe_synthesizer.jobs.with_raw_response.delete(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.safe_synthesizer.jobs.with_raw_response.delete(
                name="",
                workspace="workspace",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_cancel(self, async_client: AsyncNeMoPlatform) -> None:
        job = await async_client.safe_synthesizer.jobs.cancel(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(SafeSynthesizerJob, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.safe_synthesizer.jobs.with_raw_response.cancel(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = await response.parse()
        assert_matches_type(SafeSynthesizerJob, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.safe_synthesizer.jobs.with_streaming_response.cancel(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(SafeSynthesizerJob, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.safe_synthesizer.jobs.with_raw_response.cancel(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.safe_synthesizer.jobs.with_raw_response.cancel(
                name="",
                workspace="workspace",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_get_logs(self, async_client: AsyncNeMoPlatform) -> None:
        job = await async_client.safe_synthesizer.jobs.get_logs(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(AsyncLogsPagination[PlatformJobLog], job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_get_logs_with_all_params(self, async_client: AsyncNeMoPlatform) -> None:
        job = await async_client.safe_synthesizer.jobs.get_logs(
            name="name",
            workspace="workspace",
            limit=0,
            page_cursor="page_cursor",
        )
        assert_matches_type(AsyncLogsPagination[PlatformJobLog], job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_get_logs(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.safe_synthesizer.jobs.with_raw_response.get_logs(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = await response.parse()
        assert_matches_type(AsyncLogsPagination[PlatformJobLog], job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_get_logs(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.safe_synthesizer.jobs.with_streaming_response.get_logs(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(AsyncLogsPagination[PlatformJobLog], job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_get_logs(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.safe_synthesizer.jobs.with_raw_response.get_logs(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.safe_synthesizer.jobs.with_raw_response.get_logs(
                name="",
                workspace="workspace",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_get_status(self, async_client: AsyncNeMoPlatform) -> None:
        job = await async_client.safe_synthesizer.jobs.get_status(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(PlatformJobStatusResponse, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_get_status(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.safe_synthesizer.jobs.with_raw_response.get_status(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = await response.parse()
        assert_matches_type(PlatformJobStatusResponse, job, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_get_status(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.safe_synthesizer.jobs.with_streaming_response.get_status(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(PlatformJobStatusResponse, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_get_status(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.safe_synthesizer.jobs.with_raw_response.get_status(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.safe_synthesizer.jobs.with_raw_response.get_status(
                name="",
                workspace="workspace",
            )
