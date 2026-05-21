# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Safe Synthesizer service entry point."""

import uvicorn
from nmp.safe_synthesizer.config import config
from nmp.safe_synthesizer.service import SafeSynthesizerService

# Global service instance for platform integration
service = SafeSynthesizerService()


def run_standalone():
    """Run the safe synthesizer service as a standalone server."""
    uvicorn.run(service.app, host=config.host, port=config.port)


if __name__ == "__main__":
    run_standalone()
