# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
"""Evaluator service entry point."""

import uvicorn
from nmp.evaluator.service import EvaluatorService

# Global service instance for platform integration
service = EvaluatorService()

# Expose the FastAPI app for uvicorn
app = service.app


def run_standalone():
    """Run the evaluator service as a standalone server."""
    uvicorn.run(service.app, host="0.0.0.0", port=7331)


if __name__ == "__main__":
    run_standalone()
