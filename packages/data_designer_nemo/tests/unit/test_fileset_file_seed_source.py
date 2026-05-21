# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from data_designer_nemo.fileset_file_seed_source import (
    EMPTY_FILESET,
    EMPTY_PATH_FRAGMENT,
    FILESET_TOO_MANY_SLASHES,
    MISSING_FRAGMENT_DELIMITER,
    FilesetFileSeedSource,
)


@pytest.mark.parametrize(
    "path, err_msg",
    [
        #
        # good
        #
        ("fileset#path/to/data.parquet", None),
        ("workspace/fileset#path/to/data.parquet", None),
        ("workspace/fileset#path/to#some/data.parquet", None),
        #
        # bad
        #
        ("workspace/fileset", MISSING_FRAGMENT_DELIMITER),
        ("fileset#", EMPTY_PATH_FRAGMENT),
        ("too/many/slashes#path/to/data.parquet", FILESET_TOO_MANY_SLASHES),
        ("#path/to/data.parquet", EMPTY_FILESET),
    ],
)
def test_path_fragment_validation(path: str, err_msg: str | None) -> None:
    if err_msg:
        with pytest.raises(ValueError) as exc_info:
            FilesetFileSeedSource(path=path)
        assert err_msg in str(exc_info.value)
    else:
        source = FilesetFileSeedSource(path=path)
        assert source.path == path
