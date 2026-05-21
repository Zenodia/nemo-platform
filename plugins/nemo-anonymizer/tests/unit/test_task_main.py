# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib
import signal

import pytest


def test_sigterm_handler_exits_nonzero() -> None:
    main_module = importlib.import_module("nemo_anonymizer_plugin.tasks.anonymizer.__main__")

    with pytest.raises(SystemExit) as exc_info:
        main_module._shutdown_handler(signal.SIGTERM, None)

    assert exc_info.value.code == 128 + signal.SIGTERM
