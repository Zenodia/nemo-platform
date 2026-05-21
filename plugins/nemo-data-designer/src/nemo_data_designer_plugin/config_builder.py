# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import data_designer.config as dd


# TODO: this is a bug in the library that was fixed in 0.6.0; we can remove this once we're on that version
def config_builder_from_config(config: dd.DataDesignerConfig) -> dd.DataDesignerConfigBuilder:
    config_builder = dd.DataDesignerConfigBuilder.from_config(config.to_dict())

    for processor in config.processors or []:
        config_builder.add_processor(processor)

    for profiler in config.profilers or []:
        config_builder.add_profiler(profiler)

    return config_builder
