# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from nemoguardrails.llm.providers import get_chat_provider_names, get_llm_provider_names
from nmp.guardrails.app.constants import NIM_CHAT, NIM_LLM
from nmp.guardrails.app.services.rails import register_providers

register_providers()


def test_chat_model_registered_in_nemoguardrails():
    assert NIM_CHAT in get_chat_provider_names(), "NIM_CHAT provider not registered in NeMo Guardrails"


def test_llm_model_registered_in_nemoguardrails():
    assert NIM_LLM in get_llm_provider_names(), "NIM_LLM provider not registered in NeMo Guardrails"
