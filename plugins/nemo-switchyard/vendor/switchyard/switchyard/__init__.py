# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Vendored subset of the Switchyard library — `switchyard.lib` and `switchyard.telemetry` only.

This is a snapshot of github.com/NVIDIA-dev/switchyard at commit
94079222829d67fa278ac5b50799c8162e4c0409. The CLI, server, and experimental
subpackages from upstream are intentionally omitted; Platform only depends on
``switchyard.lib.*`` and ``switchyard.telemetry``. Re-export the upstream
top-level surface lazily so importers continue to work without pulling those
omitted subpackages.
"""
