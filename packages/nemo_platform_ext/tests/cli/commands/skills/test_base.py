# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the skills base module."""

from nemo_platform_ext.cli.commands.skills.base import Scope


def test_scope_enum_has_project_and_user():
    assert Scope.PROJECT.value == "project"
    assert Scope.USER.value == "user"


def test_scope_enum_members():
    assert set(Scope) == {Scope.PROJECT, Scope.USER}
