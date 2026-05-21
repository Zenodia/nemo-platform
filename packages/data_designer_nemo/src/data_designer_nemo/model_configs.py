# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import data_designer.config as dd
from data_designer_nemo.errors import NDDInvalidConfigError


def get_model_configs(dd_config: dd.DataDesignerConfig) -> list[dd.ModelConfig]:
    """Returns the list of model configs required by the given DataDesignerConfig.

    Returns:
        A list of model configs

    Raises:
        NDDInvalidConfigError if a column or profiler references an unrecognized alias
    """
    all_known_model_configs = {mc.alias: mc for mc in dd_config.model_configs or []}

    used_aliases = set[str]()
    for column_config in dd_config.columns:
        model_alias = getattr(column_config, "model_alias", None)
        if isinstance(model_alias, str):
            used_aliases.add(model_alias)
    for profiler in dd_config.profilers or []:
        used_aliases.add(profiler.model_alias)

    unrecognized_aliases = [alias for alias in used_aliases if alias not in all_known_model_configs]
    if len(unrecognized_aliases) > 0:
        raise NDDInvalidConfigError(f"Unrecognized model aliases in config: {','.join(unrecognized_aliases)}")

    return [all_known_model_configs[alias] for alias in used_aliases]
