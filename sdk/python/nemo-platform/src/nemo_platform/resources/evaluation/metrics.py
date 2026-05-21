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

from typing import Any, Dict, List, Union, Iterable, cast
from typing_extensions import Literal, overload

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ..._utils import path_template, maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...pagination import SyncDefaultPagination, AsyncDefaultPagination
from ...types.files import SecretRef
from ..._base_client import AsyncPaginator, make_request_options
from ...types.evaluation import (
    metric_list_params,
    metric_create_params,
    metric_evaluate_params,
)
from ...types.files.secret_ref import SecretRef
from ...types.shared.delete_response import DeleteResponse
from ...types.evaluation.remote_score_param import RemoteScoreParam
from ...types.evaluation.metrics_list_response import Data
from ...types.evaluation.inference_params_param import InferenceParamsParam
from ...types.evaluation.metric_create_response import MetricCreateResponse
from ...types.evaluation.reasoning_params_param import ReasoningParamsParam
from ...types.evaluation.metric_retrieve_response import MetricRetrieveResponse
from ...types.evaluation.metric_evaluation_response import MetricEvaluationResponse
from ...types.evaluation.evaluate_dataset_rows_param import EvaluateDatasetRowsParam
from ..._exceptions import ConflictError

__all__ = ["MetricsResource", "AsyncMetricsResource"]


class MetricsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MetricsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return MetricsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MetricsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return MetricsResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        model: metric_create_params.LLMJudgeMetricParamModel,
        scores: Iterable[metric_create_params.LLMJudgeMetricParamScore],
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        optional_fields: SequenceNotStr[str] | Omit = omit,
        prompt_template: Union[str, Dict[str, object]] | Omit = omit,
        reasoning: ReasoningParamsParam | Omit = omit,
        structured_output: Dict[str, object] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        system_prompt: str | Omit = omit,
        type: Literal["llm-judge"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          model: The model configuration.

          scores: Definitions of scores that will be extracted from the judge's output.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures will be ignored and the result will be marked as NaN.
              If False (default), request failures will raise an exception.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          optional_fields: Prompt template fields that should remain in the inferred input schema but not
              be required. Use this for fields like 'reference' when the metric can still run
              without them.

          prompt_template: The prompt template for the judge. Can be either a simple string or a structured
              object (e.g., OpenAI messages format). Use Jinja template variables like
              {{sample.output_text}} to use the model output within the template or
              {{item.xxx}} to reference input columns from the dataset.

          reasoning: Custom settings that control the model's reasoning behavior.

          structured_output: JSON schema to apply structured output for the judge model evaluation.
              Structured output is derived from scores when omitted. Use this option if there
              are custom requirements for the output of the judge.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          system_prompt: Initial instructions that define the judge model's role and behavior for the
              conversation. This is prepended to the messages as a system message.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.TopicAdherenceMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        metric_mode: Literal["f1", "precision", "recall"] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["topic_adherence"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          metric_mode: The mode for computing topic adherence score.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.AgentGoalAccuracyMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["agent_goal_accuracy"] | Omit = omit,
        use_reference: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          use_reference: Whether to use reference for goal accuracy evaluation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.AnswerAccuracyMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["answer_accuracy"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.ContextRelevanceMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["context_relevance"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.ResponseGroundednessMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["response_groundedness"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.ContextRecallMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["context_recall"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.ContextPrecisionMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["context_precision"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.ContextEntityRecallMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["context_entity_recall"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        embeddings_model: metric_create_params.ResponseRelevancyMetricParamEmbeddingsModel,
        judge_model: metric_create_params.ResponseRelevancyMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        strictness: int | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["response_relevancy"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          embeddings_model: The embeddings model configuration.

          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          strictness: Number of parallel questions generated. NIM can only generate 1.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.FaithfulnessMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["faithfulness"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.NoiseSensitivityMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["noise_sensitivity"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        description: str | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["tool_call_accuracy"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          description: Human-readable description of the metric.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        references: SequenceNotStr[str],
        candidate: str | Omit = omit,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["bleu"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          references: The templates for the ground truth references to calculate BLEU metric with.

          candidate: The template for the candidate to calculate BLEU metric on. If not provided, the
              output text from the model is used.

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        reference: str,
        candidate: str | Omit = omit,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["exact-match"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          reference: The template for the ground truth reference to calculate the exact match metric
              with.

          candidate: The template for the candidate to evaluate the exact match metric on. If not
              provided, the output text from the model is used.

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        reference: str,
        candidate: str | Omit = omit,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["f1"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          reference: The template for the ground truth reference to calculate the F1 metric with.

          candidate: The template for the candidate to evaluate the F1 metric on. If not provided,
              the output text from the model is used.

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        left_template: str,
        operation: Literal[
            "equals",
            "==",
            "!=",
            "<>",
            "not equals",
            ">=",
            "gte",
            "greater than or equal",
            ">",
            "gt",
            "greater than",
            "<=",
            "lte",
            "less than or equal",
            "<",
            "lt",
            "less than",
            "absolute difference",
        ],
        right_template: str,
        description: str | Omit = omit,
        epsilon: float | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["number-check"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          left_template: The template to use for rendering the left value of the operator to compute the
              metric.

          operation: The operation to compute for the metric.

          right_template: The template to use for rendering the right value of the operator to compute the
              metric.

          description: Human-readable description of the metric.

          epsilon: Specify the tolerance for the absolute difference of values.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        body: Dict[str, object],
        scores: Iterable[RemoteScoreParam],
        url: str,
        api_key_secret: SecretRef | Omit = omit,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        max_retries: int | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        timeout_seconds: float | Omit = omit,
        type: Literal["remote"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          body: Jinja template for request payload

          scores: List of scores to extract from the remote response

          url: The URL of the remote endpoint.

          api_key_secret: Reference to a secret. Format: 'secret_name' (uses request workspace) or
              'workspace/secret_name' (explicit workspace).

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          max_retries: Maximum number of retry attempts.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          timeout_seconds: Request timeout in seconds.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        evaluator_name: str,
        url: str,
        api_key_secret: SecretRef | Omit = omit,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        max_retries: int | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        timeout_seconds: float | Omit = omit,
        type: Literal["nemo-agent-toolkit-remote"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          evaluator_name: The name of the evaluator (also used as the score name).

          url: The URL of the remote endpoint.

          api_key_secret: Reference to a secret. Format: 'secret_name' (uses request workspace) or
              'workspace/secret_name' (explicit workspace).

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          max_retries: Maximum number of retry attempts.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          timeout_seconds: Request timeout in seconds.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        reference: str,
        candidate: str | Omit = omit,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["rouge"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          reference: The template for the ground truth reference to evaluate the ROUGE metric with.

          candidate: The template for the candidate to evaluate the ROUGE metric on. If not provided,
              the output text from the model is used.

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        left_template: str,
        operation: Literal[
            "equals", "==", "!=", "<>", "not equals", "contains", "not contains", "startswith", "endswith"
        ],
        right_template: str,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["string-check"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          left_template: The template to use for rendering the left value of the operator to compute the
              metric.

          operation: The operation to compute for the metric.

          right_template: The template to use for rendering the right value of the operator to compute the
              metric.

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        reference: str,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["tool-calling"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          reference: The template for the ground truth reference to evaluate tool calling accuracy.

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        model: metric_create_params.LLMJudgeMetricParamModel | Omit = omit,
        scores: Iterable[metric_create_params.LLMJudgeMetricParamScore] | Iterable[RemoteScoreParam] | Omit = omit,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        optional_fields: SequenceNotStr[str] | Omit = omit,
        prompt_template: Union[str, Dict[str, object]] | Omit = omit,
        reasoning: ReasoningParamsParam | Omit = omit,
        structured_output: Dict[str, object] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        system_prompt: str | Omit = omit,
        type: Literal["llm-judge"]
        | Literal["topic_adherence"]
        | Literal["agent_goal_accuracy"]
        | Literal["answer_accuracy"]
        | Literal["context_relevance"]
        | Literal["response_groundedness"]
        | Literal["context_recall"]
        | Literal["context_precision"]
        | Literal["context_entity_recall"]
        | Literal["response_relevancy"]
        | Literal["faithfulness"]
        | Literal["noise_sensitivity"]
        | Literal["tool_call_accuracy"]
        | Literal["bleu"]
        | Literal["exact-match"]
        | Literal["f1"]
        | Literal["number-check"]
        | Literal["remote"]
        | Literal["nemo-agent-toolkit-remote"]
        | Literal["rouge"]
        | Literal["string-check"]
        | Literal["tool-calling"]
        | Omit = omit,
        judge_model: metric_create_params.TopicAdherenceMetricParamJudgeModel
        | metric_create_params.AgentGoalAccuracyMetricParamJudgeModel
        | metric_create_params.AnswerAccuracyMetricParamJudgeModel
        | metric_create_params.ContextRelevanceMetricParamJudgeModel
        | metric_create_params.ResponseGroundednessMetricParamJudgeModel
        | metric_create_params.ContextRecallMetricParamJudgeModel
        | metric_create_params.ContextPrecisionMetricParamJudgeModel
        | metric_create_params.ContextEntityRecallMetricParamJudgeModel
        | metric_create_params.ResponseRelevancyMetricParamJudgeModel
        | metric_create_params.FaithfulnessMetricParamJudgeModel
        | metric_create_params.NoiseSensitivityMetricParamJudgeModel
        | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        metric_mode: Literal["f1", "precision", "recall"] | Omit = omit,
        use_reference: bool | Omit = omit,
        embeddings_model: metric_create_params.ResponseRelevancyMetricParamEmbeddingsModel | Omit = omit,
        strictness: int | Omit = omit,
        references: SequenceNotStr[str] | Omit = omit,
        candidate: str | Omit = omit,
        reference: str | Omit = omit,
        left_template: str | Omit = omit,
        operation: Literal[
            "equals",
            "==",
            "!=",
            "<>",
            "not equals",
            ">=",
            "gte",
            "greater than or equal",
            ">",
            "gt",
            "greater than",
            "<=",
            "lte",
            "less than or equal",
            "<",
            "lt",
            "less than",
            "absolute difference",
        ]
        | Literal["equals", "==", "!=", "<>", "not equals", "contains", "not contains", "startswith", "endswith"]
        | Omit = omit,
        right_template: str | Omit = omit,
        epsilon: float | Omit = omit,
        body: Dict[str, object] | Omit = omit,
        url: str | Omit = omit,
        api_key_secret: SecretRef | Omit = omit,
        max_retries: int | Omit = omit,
        timeout_seconds: float | Omit = omit,
        evaluator_name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        try:
            if workspace is None:
                workspace = self._client._get_workspace_path_param()
            if not workspace:
                raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
            if not name:
                raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
            return cast(
                MetricCreateResponse,
                self._post(
                    path_template(
                        "/apis/evaluation/v2/workspaces/{workspace}/metrics/{name}", workspace=workspace, name=name
                    ),
                    body=maybe_transform(
                        {
                            "model": model,
                            "scores": scores,
                            "description": description,
                            "ignore_request_failure": ignore_request_failure,
                            "inference": inference,
                            "labels": labels,
                            "optional_fields": optional_fields,
                            "prompt_template": prompt_template,
                            "reasoning": reasoning,
                            "structured_output": structured_output,
                            "supported_job_types": supported_job_types,
                            "system_prompt": system_prompt,
                            "type": type,
                            "judge_model": judge_model,
                            "input_template": input_template,
                            "metric_mode": metric_mode,
                            "use_reference": use_reference,
                            "embeddings_model": embeddings_model,
                            "strictness": strictness,
                            "references": references,
                            "candidate": candidate,
                            "reference": reference,
                            "left_template": left_template,
                            "operation": operation,
                            "right_template": right_template,
                            "epsilon": epsilon,
                            "body": body,
                            "url": url,
                            "api_key_secret": api_key_secret,
                            "max_retries": max_retries,
                            "timeout_seconds": timeout_seconds,
                            "evaluator_name": evaluator_name,
                        },
                        metric_create_params.MetricCreateParams,
                    ),
                    options=make_request_options(
                        extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                    ),
                    cast_to=cast(
                        Any, MetricCreateResponse
                    ),  # Union types cannot be passed in as arguments in the type system
                ),
            )
        except ConflictError:
            if not exist_ok:
                raise
            return self.retrieve(name = name, workspace = workspace)

    def retrieve(
        self,
        name: str,
        *,
        workspace: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricRetrieveResponse:
        """
        Get a specific evaluation metric by workspace and metric name.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return cast(
            MetricRetrieveResponse,
            self._get(
                path_template(
                    "/apis/evaluation/v2/workspaces/{workspace}/metrics/{name}", workspace=workspace, name=name
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, MetricRetrieveResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def list(
        self,
        *,
        workspace: str | None = None,
        filter: metric_list_params.Filter | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: Literal["-created_at", "created_at", "-updated_at", "updated_at", "-name", "name"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncDefaultPagination[Data]:
        """
        List evaluation metrics.

        Args:
          filter: Filter metrics by name, description, type, project, and dates. Supports JSON
              filter syntax with operators: $eq, $like, $lt, $lte, $gt, $gte, $in, $nin, $and,
              $or, $not. Also supports text filter syntax.

          page: Page number.

          page_size: Page size.

          sort: The field to sort by. To sort in decreasing order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        return self._get_api_list(
            path_template("/apis/evaluation/v2/workspaces/{workspace}/metrics", workspace=workspace),
            page=SyncDefaultPagination[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    metric_list_params.MetricListParams,
                ),
            ),
            model=cast(Any, Data),  # Union types cannot be passed in as arguments in the type system
        )

    def delete(
        self,
        name: str,
        *,
        workspace: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeleteResponse:
        """Delete a custom evaluation metric.

        Predefined metrics cannot be deleted.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._delete(
            path_template("/apis/evaluation/v2/workspaces/{workspace}/metrics/{name}", workspace=workspace, name=name),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )

    def evaluate(
        self,
        *,
        workspace: str | None = None,
        dataset: EvaluateDatasetRowsParam,
        metric: metric_evaluate_params.Metric,
        aggregate_fields: List[
            Literal[
                "nan_count",
                "sum",
                "mean",
                "min",
                "max",
                "std_dev",
                "variance",
                "score_type",
                "percentiles",
                "histogram",
                "rubric_distribution",
                "mode_category",
            ]
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricEvaluationResponse:
        """
        Run a synchronous metric evaluation on a dataset.

        This endpoint evaluates the given dataset using the specified metric and returns
        results immediately. Use this for quick, interactive evaluations with small
        datasets (up to 10 rows). For larger evaluations, use the async job-based
        evaluation endpoints.

        The metric can be specified either as a URN reference to a stored metric (e.g.,
        "workspace/metric_name") or as an inline metric definition.

        The dataset must be provided inline with rows.

        **Aggregate Score Fields:** The `name` and `count` fields are always included in
        aggregate scores. By default, additional fields returned are: nan_count, sum,
        mean, min, max. Use the `aggregate_fields` query parameter to customize which
        optional fields are included (e.g., std_dev, variance, percentiles, histogram,
        rubric_distribution, mode_category).

        Args:
          dataset: Inline dataset for evaluation with a maximum of 10 rows.

          metric: The metric to use for evaluation. Can be a reference (workspace/metric_name) or
              an inline metric definition.

          aggregate_fields: Aggregate score fields to include in the response (comma-separated or repeated).
              Default: ('nan_count', 'sum', 'mean', 'min', 'max'). Available: ('nan_count',
              'sum', 'mean', 'min', 'max', 'std_dev', 'variance', 'score_type', 'percentiles',
              'histogram', 'rubric_distribution', 'mode_category').

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        return self._post(
            path_template("/apis/evaluation/v2/workspaces/{workspace}/metric-evaluate", workspace=workspace),
            body=maybe_transform(
                {
                    "dataset": dataset,
                    "metric": metric,
                },
                metric_evaluate_params.MetricEvaluateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"aggregate_fields": aggregate_fields}, metric_evaluate_params.MetricEvaluateParams
                ),
            ),
            cast_to=MetricEvaluationResponse,
        )


class AsyncMetricsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMetricsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncMetricsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMetricsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncMetricsResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        model: metric_create_params.LLMJudgeMetricParamModel,
        scores: Iterable[metric_create_params.LLMJudgeMetricParamScore],
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        optional_fields: SequenceNotStr[str] | Omit = omit,
        prompt_template: Union[str, Dict[str, object]] | Omit = omit,
        reasoning: ReasoningParamsParam | Omit = omit,
        structured_output: Dict[str, object] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        system_prompt: str | Omit = omit,
        type: Literal["llm-judge"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          model: The model configuration.

          scores: Definitions of scores that will be extracted from the judge's output.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures will be ignored and the result will be marked as NaN.
              If False (default), request failures will raise an exception.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          optional_fields: Prompt template fields that should remain in the inferred input schema but not
              be required. Use this for fields like 'reference' when the metric can still run
              without them.

          prompt_template: The prompt template for the judge. Can be either a simple string or a structured
              object (e.g., OpenAI messages format). Use Jinja template variables like
              {{sample.output_text}} to use the model output within the template or
              {{item.xxx}} to reference input columns from the dataset.

          reasoning: Custom settings that control the model's reasoning behavior.

          structured_output: JSON schema to apply structured output for the judge model evaluation.
              Structured output is derived from scores when omitted. Use this option if there
              are custom requirements for the output of the judge.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          system_prompt: Initial instructions that define the judge model's role and behavior for the
              conversation. This is prepended to the messages as a system message.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.TopicAdherenceMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        metric_mode: Literal["f1", "precision", "recall"] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["topic_adherence"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          metric_mode: The mode for computing topic adherence score.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.AgentGoalAccuracyMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["agent_goal_accuracy"] | Omit = omit,
        use_reference: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          use_reference: Whether to use reference for goal accuracy evaluation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.AnswerAccuracyMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["answer_accuracy"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.ContextRelevanceMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["context_relevance"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.ResponseGroundednessMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["response_groundedness"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.ContextRecallMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["context_recall"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.ContextPrecisionMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["context_precision"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.ContextEntityRecallMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["context_entity_recall"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        embeddings_model: metric_create_params.ResponseRelevancyMetricParamEmbeddingsModel,
        judge_model: metric_create_params.ResponseRelevancyMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        strictness: int | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["response_relevancy"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          embeddings_model: The embeddings model configuration.

          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          strictness: Number of parallel questions generated. NIM can only generate 1.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.FaithfulnessMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["faithfulness"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        judge_model: metric_create_params.NoiseSensitivityMetricParamJudgeModel,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["noise_sensitivity"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          judge_model: The judge model configuration.

          description: Human-readable description of the metric.

          ignore_request_failure: If True, request failures to the judge model are ignored and the metric result
              is marked as NaN. Parse/output formatting failures are always converted to NaN.

          inference: Parameters for model inference. Extra fields can be supplied for additional
              options applied to the inference request directly. Fields not supported by the
              model may cause inference errors during evaluation.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        description: str | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["tool_call_accuracy"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          description: Human-readable description of the metric.

          input_template: Optional Jinja template for rendering the input payload for RAGAS evaluation.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        references: SequenceNotStr[str],
        candidate: str | Omit = omit,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["bleu"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          references: The templates for the ground truth references to calculate BLEU metric with.

          candidate: The template for the candidate to calculate BLEU metric on. If not provided, the
              output text from the model is used.

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        reference: str,
        candidate: str | Omit = omit,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["exact-match"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          reference: The template for the ground truth reference to calculate the exact match metric
              with.

          candidate: The template for the candidate to evaluate the exact match metric on. If not
              provided, the output text from the model is used.

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        reference: str,
        candidate: str | Omit = omit,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["f1"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          reference: The template for the ground truth reference to calculate the F1 metric with.

          candidate: The template for the candidate to evaluate the F1 metric on. If not provided,
              the output text from the model is used.

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        left_template: str,
        operation: Literal[
            "equals",
            "==",
            "!=",
            "<>",
            "not equals",
            ">=",
            "gte",
            "greater than or equal",
            ">",
            "gt",
            "greater than",
            "<=",
            "lte",
            "less than or equal",
            "<",
            "lt",
            "less than",
            "absolute difference",
        ],
        right_template: str,
        description: str | Omit = omit,
        epsilon: float | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["number-check"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          left_template: The template to use for rendering the left value of the operator to compute the
              metric.

          operation: The operation to compute for the metric.

          right_template: The template to use for rendering the right value of the operator to compute the
              metric.

          description: Human-readable description of the metric.

          epsilon: Specify the tolerance for the absolute difference of values.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        body: Dict[str, object],
        scores: Iterable[RemoteScoreParam],
        url: str,
        api_key_secret: SecretRef | Omit = omit,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        max_retries: int | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        timeout_seconds: float | Omit = omit,
        type: Literal["remote"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          body: Jinja template for request payload

          scores: List of scores to extract from the remote response

          url: The URL of the remote endpoint.

          api_key_secret: Reference to a secret. Format: 'secret_name' (uses request workspace) or
              'workspace/secret_name' (explicit workspace).

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          max_retries: Maximum number of retry attempts.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          timeout_seconds: Request timeout in seconds.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        evaluator_name: str,
        url: str,
        api_key_secret: SecretRef | Omit = omit,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        max_retries: int | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        timeout_seconds: float | Omit = omit,
        type: Literal["nemo-agent-toolkit-remote"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          evaluator_name: The name of the evaluator (also used as the score name).

          url: The URL of the remote endpoint.

          api_key_secret: Reference to a secret. Format: 'secret_name' (uses request workspace) or
              'workspace/secret_name' (explicit workspace).

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          max_retries: Maximum number of retry attempts.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          timeout_seconds: Request timeout in seconds.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        reference: str,
        candidate: str | Omit = omit,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["rouge"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          reference: The template for the ground truth reference to evaluate the ROUGE metric with.

          candidate: The template for the candidate to evaluate the ROUGE metric on. If not provided,
              the output text from the model is used.

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        left_template: str,
        operation: Literal[
            "equals", "==", "!=", "<>", "not equals", "contains", "not contains", "startswith", "endswith"
        ],
        right_template: str,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["string-check"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          left_template: The template to use for rendering the left value of the operator to compute the
              metric.

          operation: The operation to compute for the metric.

          right_template: The template to use for rendering the right value of the operator to compute the
              metric.

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        reference: str,
        description: str | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        type: Literal["tool-calling"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        """
        Create a new custom evaluation metric.

        Metrics can be reused across multiple evaluations. The metric type determines
        the evaluation method (currently only LLM-as-a-Judge is supported).

        Args:
          reference: The template for the ground truth reference to evaluate tool calling accuracy.

          description: Human-readable description of the metric.

          labels: Labels are key-value pairs that can be used for grouping and filtering.

          supported_job_types: A metric can evaluate model outputs for online evaluations or pre-generated
              outputs for offline evaluations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    async def create(
        self,
        name: str,
        *,
        workspace: str | None = None,
        model: metric_create_params.LLMJudgeMetricParamModel | Omit = omit,
        scores: Iterable[metric_create_params.LLMJudgeMetricParamScore] | Iterable[RemoteScoreParam] | Omit = omit,
        description: str | Omit = omit,
        ignore_request_failure: bool | Omit = omit,
        inference: InferenceParamsParam | Omit = omit,
        labels: Dict[str, str] | Omit = omit,
        optional_fields: SequenceNotStr[str] | Omit = omit,
        prompt_template: Union[str, Dict[str, object]] | Omit = omit,
        reasoning: ReasoningParamsParam | Omit = omit,
        structured_output: Dict[str, object] | Omit = omit,
        supported_job_types: List[Literal["online", "offline"]] | Omit = omit,
        system_prompt: str | Omit = omit,
        type: Literal["llm-judge"]
        | Literal["topic_adherence"]
        | Literal["agent_goal_accuracy"]
        | Literal["answer_accuracy"]
        | Literal["context_relevance"]
        | Literal["response_groundedness"]
        | Literal["context_recall"]
        | Literal["context_precision"]
        | Literal["context_entity_recall"]
        | Literal["response_relevancy"]
        | Literal["faithfulness"]
        | Literal["noise_sensitivity"]
        | Literal["tool_call_accuracy"]
        | Literal["bleu"]
        | Literal["exact-match"]
        | Literal["f1"]
        | Literal["number-check"]
        | Literal["remote"]
        | Literal["nemo-agent-toolkit-remote"]
        | Literal["rouge"]
        | Literal["string-check"]
        | Literal["tool-calling"]
        | Omit = omit,
        judge_model: metric_create_params.TopicAdherenceMetricParamJudgeModel
        | metric_create_params.AgentGoalAccuracyMetricParamJudgeModel
        | metric_create_params.AnswerAccuracyMetricParamJudgeModel
        | metric_create_params.ContextRelevanceMetricParamJudgeModel
        | metric_create_params.ResponseGroundednessMetricParamJudgeModel
        | metric_create_params.ContextRecallMetricParamJudgeModel
        | metric_create_params.ContextPrecisionMetricParamJudgeModel
        | metric_create_params.ContextEntityRecallMetricParamJudgeModel
        | metric_create_params.ResponseRelevancyMetricParamJudgeModel
        | metric_create_params.FaithfulnessMetricParamJudgeModel
        | metric_create_params.NoiseSensitivityMetricParamJudgeModel
        | Omit = omit,
        input_template: Dict[str, object] | Omit = omit,
        metric_mode: Literal["f1", "precision", "recall"] | Omit = omit,
        use_reference: bool | Omit = omit,
        embeddings_model: metric_create_params.ResponseRelevancyMetricParamEmbeddingsModel | Omit = omit,
        strictness: int | Omit = omit,
        references: SequenceNotStr[str] | Omit = omit,
        candidate: str | Omit = omit,
        reference: str | Omit = omit,
        left_template: str | Omit = omit,
        operation: Literal[
            "equals",
            "==",
            "!=",
            "<>",
            "not equals",
            ">=",
            "gte",
            "greater than or equal",
            ">",
            "gt",
            "greater than",
            "<=",
            "lte",
            "less than or equal",
            "<",
            "lt",
            "less than",
            "absolute difference",
        ]
        | Literal["equals", "==", "!=", "<>", "not equals", "contains", "not contains", "startswith", "endswith"]
        | Omit = omit,
        right_template: str | Omit = omit,
        epsilon: float | Omit = omit,
        body: Dict[str, object] | Omit = omit,
        url: str | Omit = omit,
        api_key_secret: SecretRef | Omit = omit,
        max_retries: int | Omit = omit,
        timeout_seconds: float | Omit = omit,
        evaluator_name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        exist_ok: bool = False,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricCreateResponse:
        try:
            if workspace is None:
                workspace = self._client._get_workspace_path_param()
            if not workspace:
                raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
            if not name:
                raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
            return cast(
                MetricCreateResponse,
                await self._post(
                    path_template(
                        "/apis/evaluation/v2/workspaces/{workspace}/metrics/{name}", workspace=workspace, name=name
                    ),
                    body=await async_maybe_transform(
                        {
                            "model": model,
                            "scores": scores,
                            "description": description,
                            "ignore_request_failure": ignore_request_failure,
                            "inference": inference,
                            "labels": labels,
                            "optional_fields": optional_fields,
                            "prompt_template": prompt_template,
                            "reasoning": reasoning,
                            "structured_output": structured_output,
                            "supported_job_types": supported_job_types,
                            "system_prompt": system_prompt,
                            "type": type,
                            "judge_model": judge_model,
                            "input_template": input_template,
                            "metric_mode": metric_mode,
                            "use_reference": use_reference,
                            "embeddings_model": embeddings_model,
                            "strictness": strictness,
                            "references": references,
                            "candidate": candidate,
                            "reference": reference,
                            "left_template": left_template,
                            "operation": operation,
                            "right_template": right_template,
                            "epsilon": epsilon,
                            "body": body,
                            "url": url,
                            "api_key_secret": api_key_secret,
                            "max_retries": max_retries,
                            "timeout_seconds": timeout_seconds,
                            "evaluator_name": evaluator_name,
                        },
                        metric_create_params.MetricCreateParams,
                    ),
                    options=make_request_options(
                        extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                    ),
                    cast_to=cast(
                        Any, MetricCreateResponse
                    ),  # Union types cannot be passed in as arguments in the type system
                ),
            )
        except ConflictError:
            if not exist_ok:
                raise
            return await self.retrieve(name = name, workspace = workspace)

    async def retrieve(
        self,
        name: str,
        *,
        workspace: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricRetrieveResponse:
        """
        Get a specific evaluation metric by workspace and metric name.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return cast(
            MetricRetrieveResponse,
            await self._get(
                path_template(
                    "/apis/evaluation/v2/workspaces/{workspace}/metrics/{name}", workspace=workspace, name=name
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, MetricRetrieveResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def list(
        self,
        *,
        workspace: str | None = None,
        filter: metric_list_params.Filter | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: Literal["-created_at", "created_at", "-updated_at", "updated_at", "-name", "name"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Data, AsyncDefaultPagination[Data]]:
        """
        List evaluation metrics.

        Args:
          filter: Filter metrics by name, description, type, project, and dates. Supports JSON
              filter syntax with operators: $eq, $like, $lt, $lte, $gt, $gte, $in, $nin, $and,
              $or, $not. Also supports text filter syntax.

          page: Page number.

          page_size: Page size.

          sort: The field to sort by. To sort in decreasing order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        return self._get_api_list(
            path_template("/apis/evaluation/v2/workspaces/{workspace}/metrics", workspace=workspace),
            page=AsyncDefaultPagination[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    metric_list_params.MetricListParams,
                ),
            ),
            model=cast(Any, Data),  # Union types cannot be passed in as arguments in the type system
        )

    async def delete(
        self,
        name: str,
        *,
        workspace: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeleteResponse:
        """Delete a custom evaluation metric.

        Predefined metrics cannot be deleted.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._delete(
            path_template("/apis/evaluation/v2/workspaces/{workspace}/metrics/{name}", workspace=workspace, name=name),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )

    async def evaluate(
        self,
        *,
        workspace: str | None = None,
        dataset: EvaluateDatasetRowsParam,
        metric: metric_evaluate_params.Metric,
        aggregate_fields: List[
            Literal[
                "nan_count",
                "sum",
                "mean",
                "min",
                "max",
                "std_dev",
                "variance",
                "score_type",
                "percentiles",
                "histogram",
                "rubric_distribution",
                "mode_category",
            ]
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetricEvaluationResponse:
        """
        Run a synchronous metric evaluation on a dataset.

        This endpoint evaluates the given dataset using the specified metric and returns
        results immediately. Use this for quick, interactive evaluations with small
        datasets (up to 10 rows). For larger evaluations, use the async job-based
        evaluation endpoints.

        The metric can be specified either as a URN reference to a stored metric (e.g.,
        "workspace/metric_name") or as an inline metric definition.

        The dataset must be provided inline with rows.

        **Aggregate Score Fields:** The `name` and `count` fields are always included in
        aggregate scores. By default, additional fields returned are: nan_count, sum,
        mean, min, max. Use the `aggregate_fields` query parameter to customize which
        optional fields are included (e.g., std_dev, variance, percentiles, histogram,
        rubric_distribution, mode_category).

        Args:
          dataset: Inline dataset for evaluation with a maximum of 10 rows.

          metric: The metric to use for evaluation. Can be a reference (workspace/metric_name) or
              an inline metric definition.

          aggregate_fields: Aggregate score fields to include in the response (comma-separated or repeated).
              Default: ('nan_count', 'sum', 'mean', 'min', 'max'). Available: ('nan_count',
              'sum', 'mean', 'min', 'max', 'std_dev', 'variance', 'score_type', 'percentiles',
              'histogram', 'rubric_distribution', 'mode_category').

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if workspace is None:
            workspace = self._client._get_workspace_path_param()
        if not workspace:
            raise ValueError(f"Expected a non-empty value for `workspace` but received {workspace!r}")
        return await self._post(
            path_template("/apis/evaluation/v2/workspaces/{workspace}/metric-evaluate", workspace=workspace),
            body=await async_maybe_transform(
                {
                    "dataset": dataset,
                    "metric": metric,
                },
                metric_evaluate_params.MetricEvaluateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"aggregate_fields": aggregate_fields}, metric_evaluate_params.MetricEvaluateParams
                ),
            ),
            cast_to=MetricEvaluationResponse,
        )


class MetricsResourceWithRawResponse:
    def __init__(self, metrics: MetricsResource) -> None:
        self._metrics = metrics

        self.create = to_raw_response_wrapper(
            metrics.create,
        )
        self.retrieve = to_raw_response_wrapper(
            metrics.retrieve,
        )
        self.list = to_raw_response_wrapper(
            metrics.list,
        )
        self.delete = to_raw_response_wrapper(
            metrics.delete,
        )
        self.evaluate = to_raw_response_wrapper(
            metrics.evaluate,
        )


class AsyncMetricsResourceWithRawResponse:
    def __init__(self, metrics: AsyncMetricsResource) -> None:
        self._metrics = metrics

        self.create = async_to_raw_response_wrapper(
            metrics.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            metrics.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            metrics.list,
        )
        self.delete = async_to_raw_response_wrapper(
            metrics.delete,
        )
        self.evaluate = async_to_raw_response_wrapper(
            metrics.evaluate,
        )


class MetricsResourceWithStreamingResponse:
    def __init__(self, metrics: MetricsResource) -> None:
        self._metrics = metrics

        self.create = to_streamed_response_wrapper(
            metrics.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            metrics.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            metrics.list,
        )
        self.delete = to_streamed_response_wrapper(
            metrics.delete,
        )
        self.evaluate = to_streamed_response_wrapper(
            metrics.evaluate,
        )


class AsyncMetricsResourceWithStreamingResponse:
    def __init__(self, metrics: AsyncMetricsResource) -> None:
        self._metrics = metrics

        self.create = async_to_streamed_response_wrapper(
            metrics.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            metrics.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            metrics.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            metrics.delete,
        )
        self.evaluate = async_to_streamed_response_wrapper(
            metrics.evaluate,
        )
