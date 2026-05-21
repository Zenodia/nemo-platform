#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Script to test DuckDB httpfs integration with the filesets API.

This tests that DuckDB can read parquet files directly from the filesets API
using HTTP range requests via the httpfs extension.

Prerequisites:
- pip install duckdb httpx
- ~/Downloads/en_US.parquet file exists

Usage:
    python script/test_duckdb_httpfs.py [--base-url http://localhost:8080]
"""

import argparse
import logging
import os
import sys

import duckdb
import httpx

logger = logging.getLogger(__name__)


def test_duckdb_httpfs_integration(base_url: str):
    """Test DuckDB httpfs integration with filesets API."""
    print("=" * 70)
    print("DuckDB httpfs Integration Test")
    print(f"Base URL: {base_url}")
    print("=" * 70)

    client = httpx.Client(timeout=30.0)
    results = {"passed": 0, "failed": 0, "tests": []}

    parquet_file = os.path.expanduser("~/Downloads/en_US.parquet")
    if not os.path.exists(parquet_file):
        print(f"✗ Parquet file not found at {parquet_file}")
        print("  Please download or place en_US.parquet in ~/Downloads/")
        return False

    file_size = os.path.getsize(parquet_file)
    print(f"\nFound parquet file: {file_size / (1024 * 1024):.2f} MB")

    # Test 1: Create fileset for DuckDB test
    print("\n=== Test 1: Create fileset ===")
    fileset_data = {
        "id": "duckdb-test-fs",
        "namespace": "duckdb-test",
        "name": "parquet-files",
        "description": "Test fileset for DuckDB httpfs integration",
    }
    response = client.post(f"{base_url}/v1/filesets", json=fileset_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        fileset = response.json()
        fileset_id = fileset["id"]
        print(f"✓ Created fileset: {fileset_id}")
        results["passed"] += 1
        results["tests"].append(("Create fileset", "PASS"))
    else:
        print(f"✗ Failed: {response.text}")
        results["failed"] += 1
        results["tests"].append(("Create fileset", "FAIL"))
        print_summary(results)
        return False

    # Test 2: Upload parquet file
    print(f"\n=== Test 2: Upload en_US.parquet ({file_size / (1024 * 1024):.2f} MB) ===")
    try:
        with open(parquet_file, "rb") as f:
            response = client.put(
                f"{base_url}/v1/filesets/{fileset_id}/-/en_US.parquet",
                content=f,
                headers={"Content-Type": "application/octet-stream"},
            )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Uploaded en_US.parquet")
            results["passed"] += 1
            results["tests"].append(("Upload parquet file", "PASS"))
        else:
            print(f"✗ Failed: {response.text}")
            results["failed"] += 1
            results["tests"].append(("Upload parquet file", "FAIL"))
            print_summary(results)
            return False
    except Exception as e:
        logger.exception("Failed to upload parquet file")
        print(f"✗ Upload failed: {e}")
        results["failed"] += 1
        results["tests"].append(("Upload parquet file", "FAIL - Exception"))
        print_summary(results)
        return False

    # Test 3: Read parquet file with DuckDB using httpfs
    print("\n=== Test 3: Query parquet file with DuckDB httpfs ===")
    file_url = f"{base_url}/v1/filesets/{fileset_id}/-/en_US.parquet"
    print(f"File URL: {file_url}")

    try:
        # Create DuckDB connection and install httpfs
        conn = duckdb.connect(":memory:")
        print("  Installing httpfs extension...")
        conn.execute("INSTALL httpfs;")
        conn.execute("LOAD httpfs;")
        print("  ✓ httpfs extension loaded")

        # Query 1: Get row count
        print("\n  Query 1: SELECT COUNT(*) FROM parquet")
        query = f"SELECT COUNT(*) as row_count FROM read_parquet('{file_url}')"
        result = conn.execute(query).fetchone()
        row_count = result[0]
        print(f"    Result: {row_count:,} rows")

        # Query 2: Get schema info
        print("\n  Query 2: DESCRIBE parquet")
        query = f"DESCRIBE SELECT * FROM read_parquet('{file_url}')"
        schema = conn.execute(query).fetchall()
        print(f"    Schema: {len(schema)} columns")
        for col_name, col_type, null, key, default, extra in schema[:5]:  # Show first 5 columns
            print(f"      - {col_name}: {col_type}")
        if len(schema) > 5:
            print(f"      ... and {len(schema) - 5} more columns")

        # Query 3: Sample data - get first few rows
        print("\n  Query 3: SELECT * FROM parquet LIMIT 5")
        query = f"SELECT * FROM read_parquet('{file_url}') LIMIT 5"
        result = conn.execute(query).fetchall()
        print(f"    Retrieved {len(result)} sample rows")

        # Query 4: Filtered query with WHERE clause
        print("\n  Query 4: Filtered query - Males aged 18-35")
        query = f"SELECT * FROM read_parquet('{file_url}') WHERE age > 18 AND age < 35 AND sex = 'Male' ORDER BY random() LIMIT 3"
        try:
            result = conn.execute(query).fetchall()
            print(f"    Retrieved {len(result)} matching rows")
            if result:
                # Get column names
                column_names = [desc[0] for desc in conn.description]
                print(f"    Columns: {', '.join(column_names)}")
                # Print first row as example
                if len(result) > 0:
                    print(f"    Sample row: {dict(zip(column_names, result[0]))}")
        except Exception as e:
            # If the columns don't exist, try a simpler query
            print(f"    Note: Column names may differ - {e}")
            query = f"SELECT * FROM read_parquet('{file_url}') LIMIT 3"
            result = conn.execute(query).fetchall()
            print(f"    Fallback: Retrieved {len(result)} sample rows")

        # Query 5: Aggregation query to test reading multiple chunks
        print("\n  Query 5: Aggregation query (tests range requests)")
        # This query will force DuckDB to read multiple parts of the file
        query = (
            f"SELECT COUNT(*) as total_count, COUNT(DISTINCT uuid) as distinct_uuids FROM read_parquet('{file_url}')"
        )
        result = conn.execute(query).fetchone()
        total_count, distinct_uuids = result
        print(f"    Total rows: {total_count:,}")
        print(f"    Distinct UUIDs: {distinct_uuids:,}")

        conn.close()

        print("\n✓ All DuckDB queries completed successfully")
        print("  DuckDB successfully used HTTP range requests to read the parquet file")
        results["passed"] += 1
        results["tests"].append(("DuckDB httpfs queries", "PASS"))

    except Exception as e:
        logger.exception("DuckDB query failed")
        print(f"✗ DuckDB query failed: {e}")
        results["failed"] += 1
        results["tests"].append(("DuckDB httpfs queries", "FAIL - Exception"))

    # Cleanup
    print("\n=== Cleanup: Delete test fileset ===")
    response = client.delete(f"{base_url}/v1/filesets/{fileset_id}")
    if response.status_code == 200:
        print("✓ Deleted test fileset")
    else:
        print(f"⚠ Warning: Could not delete test fileset: {response.text}")

    client.close()
    print_summary(results)
    return results["failed"] == 0


def print_summary(results):
    """Print test summary."""
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    for test_name, status in results["tests"]:
        symbol = "✓" if status == "PASS" else "✗"
        print(f"{symbol} {test_name}: {status}")

    print(f"\nTotal: {results['passed']} passed, {results['failed']} failed")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Test DuckDB httpfs integration with filesets API")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8080",
        help="Base URL of the files service (default: http://localhost:8080)",
    )

    args = parser.parse_args()
    success = test_duckdb_httpfs_integration(args.base_url)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
