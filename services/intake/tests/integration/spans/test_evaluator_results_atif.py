# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""ATIF ingest writes evaluator_results rows for Harbor verifier_result blocks."""

from __future__ import annotations

from fastapi.testclient import TestClient

ATIF_INGEST = "/apis/intake/v2/workspaces/default/ingest/atif"
EVAL_BASE = "/apis/intake/v2/workspaces/default/evaluator-results"


def test_atif_ingest_extracts_verifier_reward_into_evaluator_results(client: TestClient):
    body = {
        "schema_version": "ATIF-v1.6",
        "session_id": "atif-eval-session",
        "extra": {
            "task_name": "eval-task",
            "verifier": {
                "started_at": "2026-05-04T19:01:01.657282Z",
                "finished_at": "2026-05-04T19:06:45.570079Z",
            },
            "verifier_result": {"rewards": {"reward": 0.42}},
        },
        "agent": {"name": "agent-x", "version": "1.0"},
        "steps": [],
    }
    response = client.post(ATIF_INGEST, json=body)
    assert response.status_code == 201, response.text

    listed = client.get(EVAL_BASE, params={"page_size": 50})
    assert listed.status_code == 200, listed.text
    rows = listed.json()["data"]
    assert len(rows) == 1
    row = rows[0]
    assert row["name"] == "harbor.verifier"
    assert row["data_type"] == "NUMERIC"
    assert row["value"] == 0.42
    assert row["session_id"] == "atif-eval-session"
    assert row["created_by"] == "intake:atif_importer"


def test_atif_ingest_without_verifier_result_writes_no_evaluator_results(client: TestClient):
    body = {
        "schema_version": "ATIF-v1.6",
        "session_id": "atif-no-eval",
        "agent": {"name": "agent-x", "version": "1.0"},
        "steps": [],
    }
    response = client.post(ATIF_INGEST, json=body)
    assert response.status_code == 201, response.text

    listed = client.get(EVAL_BASE)
    assert listed.status_code == 200, listed.text
    assert listed.json()["pagination"]["total_results"] == 0
