# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

default_adapter_config = {
    "interceptors": [
        {
            "name": "request_logging",
            "enabled": True,
            "config": {"output_dir": "output_dir", "log_failed_requests": True},
        },
        {
            "name": "caching",
            "enabled": True,
            "config": {
                "cache_dir": "output_dir",
                "reuse_cached_responses": True,
                "save_requests": True,
                "save_responses": True,
            },
        },
        {"name": "endpoint", "enabled": True, "config": {}},
        {"name": "response_logging", "enabled": True, "config": {"output_dir": "output_dir"}},
        {"name": "raise_client_errors", "enabled": True, "config": {}},
        {
            "name": "progress_tracking",
            "enabled": True,
            "config": {
                "progress_tracking_interval": 50,
                "progress_tracking_interval_seconds": 60,
                "progress_tracking_url": "${NMP_JOBS_URL}/apis/jobs/v2/workspaces/${NEMO_JOB_WORKSPACE}/jobs/${NEMO_JOB_ID}/status-details",
                "request_method": "PATCH",
            },
        },
    ],
    "post_eval_hooks": [
        {"name": "post_eval_report", "enabled": True, "config": {"report_types": ["json"]}},
        {
            "name": "progress_tracking",
            "enabled": True,
            "config": {
                "progress_tracking_interval": 50,
                "progress_tracking_interval_seconds": 60,
                "progress_tracking_url": "${NMP_JOBS_URL}/apis/jobs/v2/workspaces/${NEMO_JOB_WORKSPACE}/jobs/${NEMO_JOB_ID}/status-details",
                "request_method": "PATCH",
            },
        },
    ],
}
