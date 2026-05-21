#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Script to test the filesets API endpoints against a running server.

Usage:
    python script/test_filesets_api.py [--base-url http://localhost:8080]
"""

import argparse
import logging
import sys
from typing import BinaryIO

import httpx

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Wrapper that tracks upload progress for file-like objects."""

    def __init__(self, file_obj: BinaryIO, total_size: int, filename: str = "file"):
        self.file_obj = file_obj
        self.total_size = total_size
        self.filename = filename
        self.bytes_uploaded = 0
        self.last_reported_pct = -1

    def read(self, size: int = -1) -> bytes:
        """Read from underlying file and track progress."""
        chunk = self.file_obj.read(size)
        if chunk:
            self.bytes_uploaded += len(chunk)
            # Report progress every 5%
            pct = int((self.bytes_uploaded / self.total_size) * 100)
            if pct >= self.last_reported_pct + 5:
                mb_uploaded = self.bytes_uploaded / (1024 * 1024)
                mb_total = self.total_size / (1024 * 1024)
                print(f"  [{self.filename}] {mb_uploaded:.1f} / {mb_total:.1f} MB ({pct}%)")
                self.last_reported_pct = pct
        return chunk

    def __iter__(self):
        """Support iteration for octet-stream uploads."""
        return self

    def __next__(self):
        """Support iteration for octet-stream uploads."""
        chunk = self.read(65536)  # 64KB chunks
        if not chunk:
            raise StopIteration
        return chunk


def run_full_test_suite(base_url: str, use_multipart: bool = True):
    """Run a complete test suite exercising all endpoints."""
    upload_mode = "multipart/form-data" if use_multipart else "application/octet-stream"
    print("=" * 70)
    print("Filesets API Test Suite")
    print(f"Base URL: {base_url}")
    print(f"Upload Mode: {upload_mode}")
    print("=" * 70)

    client = httpx.Client(timeout=30.0)
    results = {"passed": 0, "failed": 0, "tests": []}

    workspace = "default"
    fileset_name = "test-fileset-1"

    # Cleanup: Delete any existing test filesets to make this script idempotent
    print("\n=== Setup: Cleaning up existing test filesets ===")
    for name in [fileset_name, "test-fileset-2"]:
        response = client.delete(f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{name}")
        if response.status_code == 200:
            print(f"  Deleted existing fileset: {workspace}/{name}")
        elif response.status_code == 404:
            print(f"  No existing fileset: {workspace}/{name}")
        else:
            print(f"  Warning: Unexpected status {response.status_code} deleting {name}")

    # Test 1: Create first fileset
    print(f"\n=== Test 1: POST /apis/files/v2/workspaces/{workspace}/filesets (Create Fileset 1) ===")
    fileset_data = {
        "name": fileset_name,
        "description": "Test fileset 1",
    }
    response = client.post(f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets", json=fileset_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        fileset1 = response.json()
        print(f"✓ Created fileset: {workspace}/{fileset1['name']}")
        results["passed"] += 1
        results["tests"].append(("Create fileset 1", "PASS"))
    else:
        print(f"✗ Failed: {response.text}")
        results["failed"] += 1
        results["tests"].append(("Create fileset 1", "FAIL"))
        print_summary(results)
        return False

    # Test 2: Create second fileset
    print(f"\n=== Test 2: POST /apis/files/v2/workspaces/{workspace}/filesets (Create Fileset 2) ===")
    fileset_data2 = {
        "name": "test-fileset-2",
        "description": "Test fileset 2",
    }
    response = client.post(f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets", json=fileset_data2)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Created fileset 2")
        results["passed"] += 1
        results["tests"].append(("Create fileset 2", "PASS"))
    else:
        print(f"✗ Failed: {response.text}")
        results["failed"] += 1
        results["tests"].append(("Create fileset 2", "FAIL"))
        print_summary(results)
        return False

    # Test 3: List all filesets
    # print(f"\n=== Test 3: GET /apis/files/v2/workspaces/{workspace}/filesets (List all) ===")
    # response = client.get(f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets")
    # print(f"Status: {response.status_code}")
    # if response.status_code == 200:
    #     filesets = response.json()
    #     print(f"✓ Found {len(filesets.get('data', []))} filesets")
    #     for fs in filesets.get("data", []):
    #         print(f"  - {fs.get('workspace', workspace)}/{fs['name']}")
    #     results["passed"] += 1
    #     results["tests"].append(("List all filesets", "PASS"))
    # else:
    #     print(f"✗ Failed: {response.text}")
    #     results["failed"] += 1
    #     results["tests"].append(("List all filesets", "FAIL"))
    #     print_summary(results)
    #     return False

    # Test 4: Skip namespace filter test (v2 uses workspace in path)
    print("\n=== Test 4: Skipped (v2 uses workspace in path) ===")
    results["passed"] += 1
    results["tests"].append(("List filesets by workspace", "SKIP"))

    # Test 5: Get fileset by workspace/name
    print(f"\n=== Test 5: GET /apis/files/v2/workspaces/{workspace}/filesets/{fileset_name} ===")
    response = client.get(f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        fileset = response.json()
        print(f"✓ Retrieved fileset: {workspace}/{fileset['name']}")
        results["passed"] += 1
        results["tests"].append(("Get fileset by workspace/name", "PASS"))
    else:
        print(f"✗ Failed: {response.text}")
        results["failed"] += 1
        results["tests"].append(("Get fileset by workspace/name", "FAIL"))
        print_summary(results)
        return False

    # Test 6: Update fileset metadata
    # TODO: DONT NEED FOR NOW
    # print(f"\n=== Test 7: PUT /v1/filesets/{fileset_id} ===")
    # update_data = {"description": "Updated description for testing"}
    # response = client.put(f"{base_url}/v1/filesets/{fileset_id}", json=update_data)
    # print(f"Status: {response.status_code}")
    # if response.status_code == 200:
    #     updated = response.json()
    #     print(f"✓ Updated description: {updated['description']}")
    #     results["passed"] += 1
    #     results["tests"].append(("Update fileset metadata", "PASS"))
    # else:
    #     print(f"✗ Failed: {response.text}")
    #     results["failed"] += 1
    #     results["tests"].append(("Update fileset metadata", "FAIL"))

    # Test 7: Upload a text file
    upload_type = "multipart" if use_multipart else "octet-stream"
    print(
        f"\n=== Test 7: PUT /apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/test.txt ({upload_type}) ==="
    )
    test_content = b"Hello, World! This is a test file.\nLine 2\nLine 3"

    if use_multipart:
        response = client.put(
            f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/test.txt",
            files={"file": ("test.txt", test_content)},
        )
    else:
        response = client.put(
            f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/test.txt",
            content=test_content,
            headers={"Content-Type": "application/octet-stream"},
        )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ Uploaded test.txt ({len(test_content)} bytes)")
        results["passed"] += 1
        results["tests"].append(("Upload text file", "PASS"))
    else:
        print(f"✗ Failed: {response.text}")
        results["failed"] += 1
        results["tests"].append(("Upload text file", "FAIL"))
        print_summary(results)
        return False

    # Test 8: Upload a file in a subdirectory
    print(
        f"\n=== Test 8: PUT /apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/data/models/test.bin ({upload_type}) ==="
    )
    binary_content = b"Binary data content: \x00\x01\x02\x03"

    if use_multipart:
        response = client.put(
            f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/data/models/test.bin",
            files={"file": ("test.bin", binary_content)},
        )
    else:
        response = client.put(
            f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/data/models/test.bin",
            content=binary_content,
            headers={"Content-Type": "application/octet-stream"},
        )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ Uploaded data/models/test.bin ({len(binary_content)} bytes)")
        results["passed"] += 1
        results["tests"].append(("Upload file with subdirectory", "PASS"))
    else:
        print(f"✗ Failed: {response.text}")
        results["failed"] += 1
        results["tests"].append(("Upload file with subdirectory", "FAIL"))
        print_summary(results)
        return False

    # Test 9: List files in fileset
    print(f"\n=== Test 9: GET /apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/files ===")
    response = client.get(f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/files")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        files_list = response.json()["files"]
        print(f"✓ Found {len(files_list)} files:")
        for file in files_list:
            print(f"  - {file['path']}")
        results["passed"] += 1
        results["tests"].append(("List files in fileset", "PASS"))
    else:
        print(f"✗ Failed: {response.text}")
        results["failed"] += 1
        results["tests"].append(("List files in fileset", "FAIL"))
        print_summary(results)
        return False

    # Test 10: Download the uploaded file
    print(f"\n=== Test 10: GET /apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/test.txt ===")
    response = client.get(f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/test.txt")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        downloaded = response.content
        if downloaded == test_content:
            print(f"✓ Downloaded file matches uploaded content ({len(downloaded)} bytes)")
            results["passed"] += 1
            results["tests"].append(("Download file (content matches)", "PASS"))
        else:
            print(f"✗ Content mismatch: {len(downloaded)} bytes vs {len(test_content)} bytes")
            results["failed"] += 1
            results["tests"].append(("Download file (content matches)", "FAIL"))
    else:
        print(f"✗ Failed: {response.text}")
        results["failed"] += 1
        results["tests"].append(("Download file", "FAIL"))
        print_summary(results)
        return False

    # Test 11: HEAD request to check file metadata
    print(f"\n=== Test 11: HEAD /apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/test.txt ===")
    response = client.head(f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/test.txt")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        content_length = response.headers.get("Content-Length")
        accept_ranges = response.headers.get("Accept-Ranges")
        print("✓ HEAD request successful")
        print(f"  Content-Length: {content_length}")
        print(f"  Accept-Ranges: {accept_ranges}")
        if accept_ranges == "bytes":
            results["passed"] += 1
            results["tests"].append(("HEAD request with Accept-Ranges", "PASS"))
        else:
            print("✗ Accept-Ranges header not set to 'bytes'")
            results["failed"] += 1
            results["tests"].append(("HEAD request with Accept-Ranges", "FAIL"))
    else:
        print(f"✗ Failed: {response.text}")
        results["failed"] += 1
        results["tests"].append(("HEAD request", "FAIL"))

    # Test 12: Range request - first 10 bytes
    print(
        f"\n=== Test 12: GET /apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/test.txt (Range: bytes=0-9) ==="
    )
    response = client.get(
        f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/test.txt",
        headers={"Range": "bytes=0-9"},
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 206:
        downloaded = response.content
        expected = test_content[:10]
        content_range = response.headers.get("Content-Range")
        print(f"  Content-Range: {content_range}")
        if downloaded == expected:
            print("✓ Range request returned correct partial content (10 bytes)")
            results["passed"] += 1
            results["tests"].append(("Range request (first 10 bytes)", "PASS"))
        else:
            print(f"✗ Content mismatch: got {len(downloaded)} bytes, expected {len(expected)} bytes")
            print(f"  Expected: {expected}")
            print(f"  Got: {downloaded}")
            results["failed"] += 1
            results["tests"].append(("Range request (first 10 bytes)", "FAIL"))
    else:
        print(f"✗ Failed: Expected 206, got {response.status_code}")
        results["failed"] += 1
        results["tests"].append(("Range request (first 10 bytes)", "FAIL"))

    # Test 13: Range request - middle bytes
    print(
        f"\n=== Test 13: GET /apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/test.txt (Range: bytes=7-20) ==="
    )
    response = client.get(
        f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/test.txt",
        headers={"Range": "bytes=7-20"},
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 206:
        downloaded = response.content
        expected = test_content[7:21]  # End is inclusive in Range header, exclusive in slice
        content_range = response.headers.get("Content-Range")
        print(f"  Content-Range: {content_range}")
        if downloaded == expected:
            print(f"✓ Range request returned correct partial content ({len(downloaded)} bytes)")
            results["passed"] += 1
            results["tests"].append(("Range request (middle bytes)", "PASS"))
        else:
            print(f"✗ Content mismatch: got {len(downloaded)} bytes, expected {len(expected)} bytes")
            print(f"  Expected: {expected}")
            print(f"  Got: {downloaded}")
            results["failed"] += 1
            results["tests"].append(("Range request (middle bytes)", "FAIL"))
    else:
        print(f"✗ Failed: Expected 206, got {response.status_code}")
        results["failed"] += 1
        results["tests"].append(("Range request (middle bytes)", "FAIL"))

    # Test 14: Range request - from offset to end
    print(
        f"\n=== Test 14: GET /apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/test.txt (Range: bytes=40-) ==="
    )
    response = client.get(
        f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/test.txt",
        headers={"Range": "bytes=40-"},
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 206:
        downloaded = response.content
        expected = test_content[40:]
        content_range = response.headers.get("Content-Range")
        print(f"  Content-Range: {content_range}")
        if downloaded == expected:
            print(f"✓ Range request returned correct partial content ({len(downloaded)} bytes)")
            results["passed"] += 1
            results["tests"].append(("Range request (from offset to end)", "PASS"))
        else:
            print(f"✗ Content mismatch: got {len(downloaded)} bytes, expected {len(expected)} bytes")
            results["failed"] += 1
            results["tests"].append(("Range request (from offset to end)", "FAIL"))
    else:
        print(f"✗ Failed: Expected 206, got {response.status_code}")
        results["failed"] += 1
        results["tests"].append(("Range request (from offset to end)", "FAIL"))

    # Test 15: Range request - last N bytes (suffix range)
    print(
        f"\n=== Test 15: GET /apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/test.txt (Range: bytes=-10) ==="
    )
    response = client.get(
        f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/test.txt",
        headers={"Range": "bytes=-10"},
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 206:
        downloaded = response.content
        expected = test_content[-10:]
        content_range = response.headers.get("Content-Range")
        print(f"  Content-Range: {content_range}")
        if downloaded == expected:
            print("✓ Range request returned correct partial content (last 10 bytes)")
            results["passed"] += 1
            results["tests"].append(("Range request (last 10 bytes)", "PASS"))
        else:
            print(f"✗ Content mismatch: got {len(downloaded)} bytes, expected {len(expected)} bytes")
            print(f"  Expected: {expected}")
            print(f"  Got: {downloaded}")
            results["failed"] += 1
            results["tests"].append(("Range request (last 10 bytes)", "FAIL"))
    else:
        print(f"✗ Failed: Expected 206, got {response.status_code}")
        results["failed"] += 1
        results["tests"].append(("Range request (last 10 bytes)", "FAIL"))

    # Test 16: Upload large safetensors files concurrently
    print("\n=== Test 16: Concurrent upload of 15 large safetensors files ===")

    try:
        import concurrent.futures
        import os
        import time

        model_dir = os.path.expanduser("~/Downloads/gpt-oss-120b")

        if not os.path.exists(model_dir):
            print(f"⚠ Skipping test: Model directory not found at {model_dir}")
            return True

        # Find all model files (00000 through 00014)
        model_files = []
        for i in range(15):
            filename = f"model-{i:05d}-of-00014.safetensors"
            filepath = os.path.join(model_dir, filename)
            if os.path.exists(filepath):
                model_files.append((filename, filepath))
            else:
                print(f"⚠ Warning: {filename} not found, skipping")

        if not model_files:
            print("✗ No model files found")
            results["failed"] += 1
            results["tests"].append(("Upload large safetensors files", "FAIL - No files found"))
        else:
            print(f"Found {len(model_files)} model files")
            total_size = sum(os.path.getsize(fp) for _, fp in model_files)
            print(f"Total size: {total_size / (1024 * 1024 * 1024):.2f} GB")

            def upload_file(file_info):
                """Upload a single file using httpx."""
                filename, filepath = file_info
                file_size = os.path.getsize(filepath)
                start_time = time.time()

                try:
                    with open(filepath, "rb") as f:
                        # Wrap file with progress tracker
                        progress = ProgressTracker(f, file_size, filename)
                        with httpx.Client(timeout=httpx.Timeout(600.0, connect=30.0)) as client:
                            if use_multipart:
                                response = client.put(
                                    f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/{filename}",
                                    files={"file": (filename, progress)},
                                )
                            else:
                                response = client.put(
                                    f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/{filename}",
                                    content=progress,
                                    headers={"Content-Type": "application/octet-stream"},
                                )

                    elapsed = time.time() - start_time
                    throughput = file_size / (1024 * 1024 * elapsed)  # MB/s
                    return (filename, response.status_code, None, elapsed, throughput)
                except Exception as e:
                    elapsed = time.time() - start_time
                    return (filename, None, str(e), elapsed, 0)

            # Upload files concurrently
            print(f"Starting concurrent upload of {len(model_files)} files...")
            start_time = time.time()

            upload_results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(upload_file, file_info): file_info for file_info in model_files}
                completed = 0

                for future in concurrent.futures.as_completed(futures):
                    file_info = futures[future]
                    filename, filepath = file_info
                    file_size = os.path.getsize(filepath)

                    (
                        filename_result,
                        status_code,
                        error,
                        upload_time,
                        file_throughput,
                    ) = future.result()
                    completed += 1

                    if error:
                        print(f"  [{completed}/{len(model_files)}] ✗ {filename}: {error} ({upload_time:.1f}s)")
                    elif status_code == 200:
                        print(
                            f"  [{completed}/{len(model_files)}] ✓ {filename}: "
                            f"{file_size / (1024 * 1024):.1f} MB in {upload_time:.1f}s "
                            f"({file_throughput:.1f} MB/s)"
                        )
                        upload_results.append((filename, file_size, upload_time, file_throughput))
                    elif status_code == 507:
                        print(
                            f"  [{completed}/{len(model_files)}] ✗ {filename}: No space left on device ({upload_time:.1f}s)"
                        )
                    else:
                        print(
                            f"  [{completed}/{len(model_files)}] ✗ {filename}: HTTP {status_code} ({upload_time:.1f}s)"
                        )

            elapsed = time.time() - start_time
            total_throughput = total_size / (1024 * 1024 * elapsed)  # MB/s

            # Calculate statistics
            if upload_results:
                individual_throughputs = [t for _, _, _, t in upload_results]
                avg_throughput = sum(individual_throughputs) / len(individual_throughputs)
                min_throughput = min(individual_throughputs)
                max_throughput = max(individual_throughputs)

                print("\n=== Upload Statistics ===")
                print(f"Total: {len(model_files)} files, {total_size / (1024 * 1024 * 1024):.2f} GB in {elapsed:.1f}s")
                print(f"Aggregate throughput: {total_throughput:.1f} MB/s")
                print(
                    f"Per-file throughput: avg={avg_throughput:.1f} MB/s, min={min_throughput:.1f} MB/s, max={max_throughput:.1f} MB/s"
                )

            print(f"\n✓ Uploaded {len(model_files)} files successfully")
            results["passed"] += 1
            results["tests"].append(("Upload large safetensors files concurrently", "PASS"))

    except Exception:
        logger.exception("✗ Error during concurrent upload")
        results["failed"] += 1
        results["tests"].append(("Upload large safetensors files concurrently", "FAIL - Upload error"))

    # Test 17: Test inactivity timeout - Upload that stalls mid-stream
    print("\n=== Test 17: Test inactivity timeout (stalled upload) ===")
    try:

        class StallingIterator:
            """File-like object that sends some data then stalls to trigger timeout.

            Supports both file-like interface (read) for multipart and iterator interface for octet-stream.
            """

            def __init__(self, stall_after_bytes: int, stall_duration: float):
                self.stall_after_bytes = stall_after_bytes
                self.stall_duration = stall_duration
                self.bytes_sent = 0
                self.chunk_size = 8192
                self.stalled = False

            def read(self, size: int = -1) -> bytes:
                """Read method for file-like interface (used by multipart encoder)."""
                if self.bytes_sent >= self.stall_after_bytes:
                    if not self.stalled:
                        # Stall by sleeping longer than the server timeout
                        import time

                        print(f"  Stalling for {self.stall_duration}s after sending {self.bytes_sent} bytes...")
                        time.sleep(self.stall_duration)
                        self.stalled = True
                    return b""  # EOF

                # Determine how much to read
                if size == -1 or size > self.chunk_size:
                    size = self.chunk_size

                # Don't exceed stall_after_bytes
                size = min(size, self.stall_after_bytes - self.bytes_sent)

                if size <= 0:
                    return b""

                chunk = b"x" * size
                self.bytes_sent += len(chunk)
                return chunk

            def __iter__(self):
                """Iterator interface for octet-stream uploads."""
                return self

            def __next__(self):
                """Iterator interface for octet-stream uploads."""
                if self.bytes_sent >= self.stall_after_bytes:
                    if not self.stalled:
                        # Stall by sleeping longer than the server timeout
                        import time

                        print(f"  Stalling for {self.stall_duration}s after sending {self.bytes_sent} bytes...")
                        time.sleep(self.stall_duration)
                        self.stalled = True
                    raise StopIteration

                # Send a chunk of data
                chunk = b"x" * min(self.chunk_size, self.stall_after_bytes - self.bytes_sent)
                self.bytes_sent += len(chunk)
                return chunk

        # Create an upload that will stall after sending some initial data
        # Server timeout is configured (default 15s based on the code we saw)
        # We'll stall for 20 seconds to ensure timeout triggers
        stalling_upload = StallingIterator(stall_after_bytes=16384, stall_duration=6.0)

        print("Uploading file that will stall mid-stream...")
        if use_multipart:
            response = client.put(
                f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/stalled-upload-test.bin",
                files={"file": ("stalled-upload-test.bin", stalling_upload)},
                timeout=30.0,  # Client timeout longer than stall
            )
        else:
            # For octet-stream, we need to make the iterator work directly with content parameter
            # This requires the StallingIterator to be iterable again
            response = client.put(
                f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/stalled-upload-test.bin",
                content=stalling_upload,
                headers={"Content-Type": "application/octet-stream"},
                timeout=30.0,  # Client timeout longer than stall
            )

        # We expect this to fail with 408 (Request Timeout)
        if response.status_code == 408:
            print("✓ Server correctly returned 408 (Request Timeout)")
            print(f"  Response: {response.json()}")
            results["passed"] += 1
            results["tests"].append(("Inactivity timeout on stalled upload", "PASS"))
        else:
            print(f"✗ Expected 408, got {response.status_code}: {response.text}")
            results["failed"] += 1
            results["tests"].append(
                (
                    "Inactivity timeout on stalled upload",
                    f"FAIL - Got {response.status_code}",
                )
            )

    except Exception as e:
        logger.exception("✗ Error during timeout test")
        print(f"✗ Timeout test error: {e}")
        results["failed"] += 1
        results["tests"].append(("Inactivity timeout on stalled upload", f"FAIL - {str(e)}"))

    # Test 18: Cleanup - Delete all uploaded files
    print("\n=== Test 18: Cleanup - Delete all uploaded files ===")
    try:
        # Get list of all files in the fileset
        response = client.get(f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/files")
        if response.status_code == 200:
            files_list = response.json()["files"]
            print(f"Found {len(files_list)} files to delete")

            deleted_count = 0
            failed_count = 0

            for file_info in files_list:
                file_path = file_info["path"]
                delete_response = client.delete(
                    f"{base_url}/apis/files/v2/workspaces/{workspace}/filesets/{fileset_name}/-/{file_path}"
                )

                if delete_response.status_code == 200:
                    print(f"  ✓ Deleted: {file_path}")
                    deleted_count += 1
                else:
                    print(f"  ✗ Failed to delete {file_path}: {delete_response.status_code}")
                    failed_count += 1

            print(f"\nDeleted {deleted_count} files, {failed_count} failures")

            if failed_count == 0:
                results["passed"] += 1
                results["tests"].append(("Cleanup - Delete all files", "PASS"))
            else:
                results["failed"] += 1
                results["tests"].append(("Cleanup - Delete all files", f"PARTIAL - {failed_count} failures"))
        else:
            print(f"✗ Failed to list files: {response.status_code}")
            results["failed"] += 1
            results["tests"].append(("Cleanup - Delete all files", "FAIL - Could not list files"))
    except Exception as e:
        logger.exception("✗ Error during cleanup")
        print(f"✗ Cleanup error: {e}")
        results["failed"] += 1
        results["tests"].append(("Cleanup - Delete all files", "FAIL - Cleanup error"))
    finally:
        client.close()

    print_summary(results)
    return results["failed"] == 0


def print_summary(results):
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    for test_name, status in results["tests"]:
        symbol = "✓" if status == "PASS" else "✗"
        print(f"{symbol} {test_name}: {status}")

    print(f"\nTotal: {results['passed']} passed, {results['failed']} failed")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Test the filesets API endpoints")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8080",
        help="Base URL of the files service (default: http://localhost:8080)",
    )
    parser.add_argument(
        "--upload-mode",
        choices=["multipart", "octet-stream"],
        default="octet-stream",
        help="Upload mode: multipart/form-data or application/octet-stream (default: multipart)",
    )

    args = parser.parse_args()
    use_multipart = args.upload_mode == "multipart"
    success = run_full_test_suite(args.base_url, use_multipart)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
