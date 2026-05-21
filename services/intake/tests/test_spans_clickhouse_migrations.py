# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""ClickHouse migration helper tests."""

import re
from pathlib import Path

import nmp.intake.spans.clickhouse_migrations as clickhouse_migrations
import pytest
from nmp.intake.spans.clickhouse_migrations import parse_clickhouse_url


def test_parse_clickhouse_url_rejects_hostless_url():
    with pytest.raises(ValueError, match="include a host"):
        parse_clickhouse_url("http://:8123")


def test_parse_clickhouse_url_keeps_default_ports():
    assert parse_clickhouse_url("clickhouse.local").port == 8123
    assert parse_clickhouse_url("https://clickhouse.local").port == 8443


def test_spans_schema_keeps_cityhash_identity_expression():
    source = Path(clickhouse_migrations.__file__).read_text(encoding="utf-8")
    match = re.search(r"\bid\s+UInt64\s+MATERIALIZED\s+cityHash64\(([^)]*)\)", source)

    assert match is not None
    assert [part.strip() for part in match.group(1).split(",")] == [
        "workspace",
        "source_format",
        "trace_id",
        "external_span_id",
    ]
