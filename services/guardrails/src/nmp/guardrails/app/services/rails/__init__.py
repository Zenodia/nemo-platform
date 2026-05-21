# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import logging

from nemoguardrails.llm.providers import register_chat_provider, register_llm_provider
from nmp.guardrails.app.constants import NIM_CHAT, NIM_LLM
from nmp.guardrails.app.llms.chat.nim import ChatNIM
from nmp.guardrails.app.llms.completion.nim import NIM

log = logging.getLogger(__name__)


def register_providers():
    """Register Chat/LLM providers to NeMo Guardrails."""

    register_chat_provider(NIM_CHAT, ChatNIM)
    register_llm_provider(NIM_LLM, NIM)


register_providers()
