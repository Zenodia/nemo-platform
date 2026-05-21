# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Data exporter for Intake entries using EntityClient pattern."""

import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from nmp.common.entities.client import EntityClient
from nmp.intake.app.utils.datastore import DataStoreClient
from nmp.intake.app.utils.exports import extract_datastore_path, extract_nds_path
from nmp.intake.entities import Entry, ExportConfig

logger = logging.getLogger(__name__)


class DataExporter:
    """Export entries to various formats and destinations."""

    def __init__(self, entities_client: EntityClient):
        """Initialize exporter with EntityClient."""
        self.entities_client = entities_client
        self.datastore_client = DataStoreClient()

    async def export_entries(
        self,
        config: ExportConfig,
    ) -> List[Dict[str, Any]]:
        """Export entries matching config.

        Args:
            config: Export configuration with filters, search, and format options

        Returns:
            List of entry dictionaries ready for export
        """
        # Extract filter and search from config, merge them for EntityClient
        filter_obj = dict(config.filters) if config.filters else {}
        search_obj = config.search or {}
        combined_filter = {**filter_obj, **search_obj}

        # Extract workspace from filter since it needs to be passed as a direct parameter
        workspace_filter = combined_filter.pop("workspace", None) if combined_filter else None

        # Query entries using EntityClient
        page_size = config.limit if config.limit else 10000
        result = await self.entities_client.list(
            Entry,
            page=1,
            page_size=page_size,
            workspace=workspace_filter,
            filter_obj=combined_filter if combined_filter else None,
        )

        entries = result.data

        # Apply limit if specified
        if config.limit:
            entries = entries[: config.limit]

        # Transform entries to export format
        export_data = []
        for entry in entries:
            export_entry = self._transform_entry(entry, config.format_options)
            export_data.append(export_entry)

        return export_data

    def _transform_entry(self, entry: Entry, format_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Transform entry to export format.

        Args:
            entry: Entry entity to transform
            format_options: Optional transformation options

        Returns:
            Dictionary ready for export
        """
        entry_dict = entry.model_dump(mode="json")

        # Add messages array for OpenAI/Customizer compatibility
        try:
            # Get data from the serialized dict to handle both Pydantic and dict types
            data_dict = entry_dict.get("data", {})
            if isinstance(data_dict, dict):
                request = data_dict.get("request", {})
                response = data_dict.get("response", {})

                if isinstance(request, dict) and isinstance(response, dict):
                    request_messages = request.get("messages", [])
                    choices = response.get("choices", [])

                    if request_messages and choices and isinstance(choices, list) and len(choices) > 0:
                        response_message = choices[0].get("message")
                        if response_message:
                            # Add top-level messages array for compatibility
                            entry_dict["messages"] = [*request_messages, response_message]

                # Add tools if present in request
                if isinstance(request, dict) and request.get("tools"):
                    entry_dict["tools"] = request["tools"]
        except Exception as e:
            logger.warning(f"Failed to add messages/tools to entry {entry.external_id}: {e}")

        return entry_dict

    async def preview_export(
        self,
        config: ExportConfig,
    ) -> List[Dict[str, Any]]:
        """Preview export data without writing (max 100 records).

        Args:
            config: Export configuration

        Returns:
            List of up to 100 entry dictionaries
        """
        # Limit preview to 100 records
        preview_config = config.model_copy()
        preview_config.limit = min(config.limit or 100, 100)

        return await self.export_entries(preview_config)

    # TODO(v2): FILES
    async def write_to_file(
        self,
        entries: List[Dict[str, Any]],
        file_path: str,
    ) -> int:
        """Write entries to a local JSONL file.

        Args:
            entries: List of entry dictionaries
            file_path: Path to output file

        Returns:
            Number of records written
        """
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        logger.info(f"Wrote {len(entries)} entries to {file_path}")
        return len(entries)

    # TODO(v2): FILES
    # TODO(v2): SERVICE-CALL
    async def write_to_hf_dataset(
        self,
        entries: List[Dict[str, Any]],
        uri: str,
    ) -> int:
        """Write entries to a HuggingFace dataset.

        Args:
            entries: List of entry dictionaries
            uri: HuggingFace dataset URI in format hf://datasets/namespace/name/path/to/file.jsonl

        Returns:
            Number of records written

        Raises:
            ValueError: If no entries provided or URI is invalid
        """
        if len(entries) == 0:
            raise ValueError("No entries found. Cannot create empty file.")

        dataset_id, path_in_repo = extract_datastore_path(uri)
        logger.info("Attempting to export %d entries to HuggingFace dataset %s", len(entries), dataset_id)

        # Check if dataset exists (run in executor since HfApi is synchronous)
        loop = asyncio.get_event_loop()
        is_existing_dataset = await loop.run_in_executor(None, self.datastore_client.dataset_exists, dataset_id)

        # Create dataset if it doesn't exist
        if not is_existing_dataset:
            logger.info("Creating new dataset with ID: %s", dataset_id)
            try:
                # Create dataset in HuggingFace
                await loop.run_in_executor(None, self.datastore_client.create_dataset, dataset_id)

                # TODO(v2): Re-enable dataset registration once datasets service is up
                # namespace, name = dataset_id.split("/")
                # await self.entity_store_client.register_dataset(
                #     namespace=namespace, name=name, files_url=f"hf://datasets/{dataset_id}"
                # )
            except Exception as e:
                logger.error("Failed to create dataset %s: %s", dataset_id, str(e))
                # Clean up HuggingFace repo if creation fails
                await loop.run_in_executor(None, self.datastore_client.delete_dataset, dataset_id)
                raise Exception(f"Failed to create dataset: {str(e)}")

        # Create temporary file with JSONL content
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as tmp:
            for entry in entries:
                json_str = json.dumps(entry)
                tmp.write(json_str + "\n")
            tmp_path = tmp.name

        try:
            # Upload file to dataset (run in executor since HfApi is synchronous)
            await loop.run_in_executor(
                None,
                self.datastore_client.upload_file,
                tmp_path,
                dataset_id,
                path_in_repo,
                f"Export {len(entries)} entries",
            )
            logger.info("Successfully exported %d entries to HuggingFace dataset %s", len(entries), dataset_id)
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)

        return len(entries)

    # TODO(v2): FILES
    # TODO(v2): SERVICE-CALL
    async def write_to_nds_dataset(
        self,
        entries: List[Dict[str, Any]],
        uri: str,
    ) -> int:
        """Write entries to a NeMo Datastore dataset.

        Args:
            entries: List of entry dictionaries
            uri: NeMo Datastore URI in format nds://workspace/dataset_name

        Returns:
            Number of records written

        Raises:
            ValueError: If no entries provided or URI is invalid
        """
        if len(entries) == 0:
            raise ValueError("No entries found matching the export criteria. Please verify your filters and try again.")

        workspace, dataset_name = extract_nds_path(uri)
        dataset_id = f"{workspace}/{dataset_name}"

        logger.info("Attempting to export %d entries to NDS dataset %s", len(entries), dataset_id)

        # Create temporary file with JSONL content
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as tmp_file:
            for entry in entries:
                json_str = json.dumps(entry)
                tmp_file.write(json_str + "\n")
            tmp_path = tmp_file.name

        try:
            # Run synchronous operations in executor
            loop = asyncio.get_event_loop()

            # Create the dataset if it doesn't exist
            await loop.run_in_executor(None, self.datastore_client.create_dataset, dataset_id)

            # Upload the file to the dataset
            await loop.run_in_executor(
                None,
                self.datastore_client.upload_file,
                tmp_path,
                dataset_id,
                "data.jsonl",
                f"Export {len(entries)} entries from Intake",
            )

            logger.info("Successfully exported %d entries to NDS dataset %s", len(entries), dataset_id)
            return len(entries)

        except Exception as e:
            logger.error("Failed to export to NDS dataset %s: %s", dataset_id, str(e))
            raise Exception(f"Failed to export to NDS dataset: {str(e)}")
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
