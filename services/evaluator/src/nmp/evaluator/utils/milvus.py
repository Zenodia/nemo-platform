# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import logging
from urllib.parse import urlparse

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def validate_milvus_connectivity(host: str, port: int = 19530):
    # Lazy import to avoid loading pymilvus at startup
    from pymilvus import connections, utility

    try:
        # Connect to Milvus server
        connections.connect(host=host, port=port)

        # Check connectivity by retrieving the server version
        server_version = utility.get_server_version()
        logger.info(f"Milvus server version: {server_version}")

    except Exception as e:
        logger.error(f"Milvus service down or unreachable: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Milvus service down or unreachable: {host}:{port}",
        )


def get_milvus_configs(milvus_url: str, collection_name: str):
    if not milvus_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: MILVUS_URL environment variable is not set",
        )

    parsed_url = urlparse(milvus_url)
    host = parsed_url.hostname
    port = parsed_url.port

    return {
        "milvus_host": host,
        "milvus_port": str(port),
        "milvus_password": "",
        "milvus_collection_name": collection_name,
    }
