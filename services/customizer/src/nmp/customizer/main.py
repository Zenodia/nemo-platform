# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Customizer service entry point."""

import uvicorn
from nmp.customizer.config import config
from nmp.customizer.service import CustomizerService

# Global service instance for platform integration
service = CustomizerService()


def run_standalone():
    """Run the customizer service as a standalone server."""
    uvicorn.run(service.app, host="0.0.0.0", port=config.port)


if __name__ == "__main__":
    run_standalone()
