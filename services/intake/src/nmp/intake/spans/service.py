# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Application service for Intake trace spans."""

from __future__ import annotations

from nmp.common.api.common import PaginatedResult
from nmp.intake.spans.domain import (
    EvaluatorResult,
    EvaluatorResultListFilter,
    IntakeSpan,
    SpanListFilter,
    TraceBatch,
)
from nmp.intake.spans.evaluator_results_repository import EvaluatorResultsRepository
from nmp.intake.spans.span_repository import SpanRepository


class SpanNotFoundError(Exception):
    def __init__(self, workspace: str, span_id: str) -> None:
        super().__init__(f"Span {workspace}/{span_id} not found")
        self.workspace = workspace
        self.span_id = span_id


class EvaluatorResultNotFoundError(Exception):
    def __init__(self, workspace: str, evaluator_result_id: str) -> None:
        super().__init__(f"Evaluator result {workspace}/{evaluator_result_id} not found")
        self.workspace = workspace
        self.evaluator_result_id = evaluator_result_id


class IntakeSpansService:
    def __init__(
        self,
        span_repository: SpanRepository,
        evaluator_results_repository: EvaluatorResultsRepository,
    ) -> None:
        self._spans = span_repository
        self._evaluator_results = evaluator_results_repository

    async def ingest_batch(self, batch: TraceBatch) -> None:
        await self._spans.save_spans(batch.spans)
        if batch.evaluator_results:
            await self._evaluator_results.save_evaluator_results(batch.evaluator_results)

    async def list_spans(
        self,
        *,
        filters: SpanListFilter,
        page: int,
        page_size: int,
        sort: str,
    ) -> PaginatedResult[IntakeSpan]:
        return await self._spans.list_spans(filters=filters, page=page, page_size=page_size, sort=sort)

    async def get_span(self, *, workspace: str, span_id: str) -> IntakeSpan:
        span = await self._spans.get_span(workspace=workspace, span_id=span_id)
        if span is None:
            raise SpanNotFoundError(workspace, span_id)
        return span

    async def create_evaluator_result(self, result: EvaluatorResult) -> EvaluatorResult:
        """Persist one evaluator_result. Loose target — no span existence check."""

        await self._evaluator_results.save_evaluator_results([result])
        return result

    async def list_evaluator_results(
        self,
        *,
        filters: EvaluatorResultListFilter,
        page: int,
        page_size: int,
        sort: str,
    ) -> PaginatedResult[EvaluatorResult]:
        return await self._evaluator_results.list_evaluator_results(
            filters=filters, page=page, page_size=page_size, sort=sort
        )

    async def get_evaluator_result(self, *, workspace: str, evaluator_result_id: str) -> EvaluatorResult:
        result = await self._evaluator_results.get_evaluator_result(
            workspace=workspace, evaluator_result_id=evaluator_result_id
        )
        if result is None:
            raise EvaluatorResultNotFoundError(workspace, evaluator_result_id)
        return result

    async def list_evaluator_results_for_span(self, *, workspace: str, span_id: str) -> list[EvaluatorResult]:
        return await self._evaluator_results.list_evaluator_results_for_span(workspace=workspace, span_id=span_id)
