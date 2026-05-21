# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from data_designer.plugins.plugin import Plugin, PluginType

fileset_seed_datasets_plugin = Plugin(
    config_qualified_name="data_designer_nemo.fileset_file_seed_source.FilesetFileSeedSource",
    impl_qualified_name="data_designer_nemo.fileset_file_seed_reader.FilesetFileSeedReader",
    plugin_type=PluginType.SEED_READER,
)
