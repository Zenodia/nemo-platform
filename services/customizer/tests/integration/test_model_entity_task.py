# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for the model entity task."""

import json
import os
import tempfile

import nmp.customizer.tasks.model_entity as model_entity
import pytest
from nmp.core.files.service import FilesService
from nmp.core.models.service import ModelsService
from nmp.testing import task_harness


class TestModelEntityTask:
    """Integration tests for the model entity task module."""

    @pytest.mark.asyncio
    async def test_task_creates_model_entity(self):
        """Test that task creates a model entity with a fileset artifact."""
        workspace = "default"
        model_name = "test-created-model"
        fileset_name = "test-model-artifacts"
        base_model = "default/base-llama"

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create model_entity_config.json
            entity_config = {
                "name": model_name,
                "workspace": workspace,
                "model_entity": base_model,
                "description": "Test model entity",
                "fileset": {
                    "workspace": workspace,
                    "name": fileset_name,
                },
                "base_model": base_model,
            }
            config_path = os.path.join(tmpdir, "entity_config.json")
            with open(config_path, "w") as f:
                json.dump(entity_config, f)

            env = {
                "NEMO_JOB_ID": "test-model-entity-job-123",
                "NEMO_JOB_WORKSPACE": workspace,
                "NEMO_JOB_STEP_CONFIG_FILE_PATH": config_path,
                "NEMO_JOB_STEP": "ModelEntityCreation",
                "NEMO_JOB_TASK": "model-entity-task",
                "NEMO_JOB_PERSISTENT_JOB_STORAGE_PATH": tmpdir,
            }
            async with task_harness(
                model_entity,
                FilesService,
                ModelsService,
                config={},
                env=env,
            ) as ctx:
                # Setup: Create base model before running model entity task
                ctx.sdk.models.create(workspace="default", name="base-llama")

                # Setup: Create fileset before running model entity task
                ctx.sdk.files.filesets.create(workspace=workspace, name=fileset_name)

                # Upload a dummy file to the fileset
                ctx.sdk.files.upload_content(
                    content=b"fake model weights",
                    remote_path="model.safetensors",
                    fileset=fileset_name,
                    workspace=workspace,
                )

                result = ctx.run_task()

                assert result.exit_code == 0, f"Task failed: stdout={result.stdout}, stderr={result.stderr}"
                assert result.exception is None

                # Verify the model entity was created
                model = ctx.sdk.models.retrieve(workspace=workspace, name=model_name)
                assert model.name == model_name
                assert model.description == "Test model entity"
                assert model.base_model == base_model
                assert not model.adapters
                assert model.finetuning_type == "all_weights"

    @pytest.mark.asyncio
    async def test_task_creates_model_entity_lora(self):
        """Test that task creates a model entity with a fileset artifact."""
        workspace = "default"
        model_name = "test-created-model"
        fileset_name = "test-model-artifacts"

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "entity_config.json")
            env = {
                "NEMO_JOB_ID": "test-model-entity-job-123",
                "NEMO_JOB_WORKSPACE": workspace,
                "NEMO_JOB_STEP_CONFIG_FILE_PATH": config_path,
                "NEMO_JOB_STEP": "ModelEntityCreation",
                "NEMO_JOB_TASK": "model-entity-task",
                "NEMO_JOB_PERSISTENT_JOB_STORAGE_PATH": tmpdir,
            }
            # Create model_entity_config.json
            entity_config = {
                "name": model_name,
                "workspace": workspace,
                "model_entity": "default/base-llama",
                "description": "Test model entity",
                "fileset": {
                    "workspace": workspace,
                    "name": fileset_name,
                },
                "peft": {
                    "type": "lora",
                    "alpha": 16,
                    "rank": 8,
                },
            }
            with open(config_path, "w") as f:
                json.dump(entity_config, f)

            async with task_harness(
                model_entity,
                FilesService,
                ModelsService,
                config={},
                env=env,
            ) as ctx:
                ctx.sdk.models.create(workspace="default", name="base-llama")

                # Setup: Create fileset before running model entity task
                ctx.sdk.files.filesets.create(workspace=workspace, name=fileset_name)

                # Upload a dummy file to the fileset
                ctx.sdk.files.upload_content(
                    content=b"fake model weights",
                    remote_path="model.safetensors",
                    fileset=fileset_name,
                    workspace=workspace,
                )

                result = ctx.run_task()

                assert result.exit_code == 0, f"Task failed: stdout={result.stdout}, stderr={result.stderr}"
                assert result.exception is None

                # Verify the model entity was created
                model = ctx.sdk.models.retrieve(workspace="default", name="base-llama")

                assert len(model.adapters) == 1

                assert model.adapters[0].name == model_name
                assert model.adapters[0].description == "Test model entity"
                assert model.adapters[0].finetuning_type == "lora"
                assert model.adapters[0].lora_config is not None
                assert model.adapters[0].lora_config.alpha == 16
                assert model.adapters[0].lora_config.rank == 8

    @pytest.mark.asyncio
    async def test_task_creates_model_entity_minimal_config(self):
        """Test that task creates a model entity with minimal configuration."""
        workspace = "default"
        model_name = "test-minimal-model"
        fileset_name = "test-minimal-artifacts"

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create model_entity_config.json with minimal fields
            entity_config = {
                "name": model_name,
                "workspace": workspace,
                "model_entity": "default/model",
                "fileset": {
                    "workspace": None,  # Should use job workspace
                    "name": fileset_name,
                },
            }
            config_path = os.path.join(tmpdir, "entity_config.json")
            with open(config_path, "w") as f:
                json.dump(entity_config, f)

            env = {
                "NEMO_JOB_ID": "test-model-entity-minimal-job-123",
                "NEMO_JOB_WORKSPACE": workspace,
                "NEMO_JOB_STEP_CONFIG_FILE_PATH": config_path,
                "NEMO_JOB_STEP": "ModelEntityCreation",
                "NEMO_JOB_TASK": "model-entity-task",
                "NEMO_JOB_PERSISTENT_JOB_STORAGE_PATH": tmpdir,
            }
            async with task_harness(
                model_entity,
                FilesService,
                ModelsService,
                config={},
                env=env,
            ) as ctx:
                # Setup: Create default/model before running (referenced by model_entity)
                ctx.sdk.models.create(workspace="default", name="model")

                # Setup: Create fileset
                ctx.sdk.files.filesets.create(workspace=workspace, name=fileset_name)
                ctx.sdk.files.upload_content(
                    content=b"fake model weights",
                    remote_path="model.safetensors",
                    fileset=fileset_name,
                    workspace=workspace,
                )

                result = ctx.run_task()

                assert result.exit_code == 0, f"Task failed: stdout={result.stdout}, stderr={result.stderr}"
                assert result.exception is None

                # Verify the model entity was created
                model = ctx.sdk.models.retrieve(workspace=workspace, name=model_name)
                assert model.name == model_name
                assert model.description is None
                assert model.base_model is None
                assert not model.adapters

    @pytest.mark.asyncio
    async def test_task_fails_for_nonexistent_fileset(self):
        """Test that task fails when referenced fileset does not exist.

        The task now validates fileset existence before creating the model entity,
        catching issues early rather than at deployment time.
        """
        workspace = "default"
        model_name = "test-nonexistent-fileset-model"
        fileset_name = "nonexistent-fileset"

        with tempfile.TemporaryDirectory() as tmpdir:
            entity_config = {
                "name": model_name,
                "workspace": workspace,
                "model_entity": f"{workspace}/model",
                "fileset": {
                    "workspace": workspace,
                    "name": fileset_name,
                },
            }
            config_path = os.path.join(tmpdir, "entity_config.json")
            with open(config_path, "w") as f:
                json.dump(entity_config, f)

            env = {
                "NEMO_JOB_ID": "test-model-entity-nonexistent-job-123",
                "NEMO_JOB_WORKSPACE": workspace,
                "NEMO_JOB_STEP_CONFIG_FILE_PATH": config_path,
                "NEMO_JOB_STEP": "ModelEntityCreation",
                "NEMO_JOB_TASK": "model-entity-task",
                "NEMO_JOB_PERSISTENT_JOB_STORAGE_PATH": tmpdir,
            }
            async with task_harness(
                model_entity,
                FilesService,
                ModelsService,
                config={},
                env=env,
            ) as ctx:
                # Create default/model so failure is due to nonexistent fileset only
                ctx.sdk.models.create(workspace=workspace, name="model")

                # Do NOT create the fileset - it should not exist

                result = ctx.run_task()

                # Task should fail because fileset doesn't exist
                assert result.exit_code == 1, f"Task should have failed: stdout={result.stdout}, stderr={result.stderr}"

    @pytest.mark.asyncio
    async def test_task_overwrites_duplicate_model_name(self):
        """Test that task overwrites an existing model when duplicate name is used."""
        workspace = "default"
        model_name = "test-duplicate-model"
        fileset_name_old = "test-old-artifacts"
        fileset_name_new = "test-new-artifacts"

        with tempfile.TemporaryDirectory() as tmpdir:
            entity_config = {
                "name": model_name,
                "workspace": workspace,
                "model_entity": "default/base-model",
                "description": "Updated model description",
                "fileset": {
                    "workspace": workspace,
                    "name": fileset_name_new,
                },
                "base_model": "default/new-base-model",
            }
            config_path = os.path.join(tmpdir, "entity_config.json")
            with open(config_path, "w") as f:
                json.dump(entity_config, f)

            env = {
                "NEMO_JOB_ID": "test-model-entity-duplicate-job-123",
                "NEMO_JOB_WORKSPACE": workspace,
                "NEMO_JOB_STEP_CONFIG_FILE_PATH": config_path,
                "NEMO_JOB_STEP": "ModelEntityCreation",
                "NEMO_JOB_TASK": "model-entity-task",
                "NEMO_JOB_PERSISTENT_JOB_STORAGE_PATH": tmpdir,
            }
            async with task_harness(
                model_entity,
                FilesService,
                ModelsService,
                config={},
                env=env,
            ) as ctx:
                # Setup: Create base models referenced by config
                ctx.sdk.models.create(workspace="default", name="base-model")

                # Setup: Create filesets
                ctx.sdk.files.filesets.create(workspace=workspace, name=fileset_name_old)
                ctx.sdk.files.upload_content(
                    content=b"fake model weights",
                    remote_path="model.safetensors",
                    fileset=fileset_name_old,
                    workspace=workspace,
                )
                ctx.sdk.files.filesets.create(workspace=workspace, name=fileset_name_new)
                ctx.sdk.files.upload_content(
                    content=b"fake model weights",
                    remote_path="model.safetensors",
                    fileset=fileset_name_new,
                    workspace=workspace,
                )

                # Pre-create a model with the same name but different attributes
                ctx.sdk.models.create(
                    workspace=workspace,
                    name=model_name,
                    description="Original model description",
                    fileset=f"{workspace}/{fileset_name_old}",
                    base_model="default/old-base-model",
                )

                result = ctx.run_task()

                # Task should succeed and overwrite the existing model
                assert result.exit_code == 0, f"Task failed: stdout={result.stdout}, stderr={result.stderr}"
                assert result.exception is None

                # Verify the model entity was updated with new values
                updated_model = ctx.sdk.models.retrieve(workspace=workspace, name=model_name)
                assert updated_model.name == model_name
                assert updated_model.description == "Updated model description"
                assert updated_model.base_model == "default/new-base-model"
                assert not updated_model.adapters
                assert updated_model.finetuning_type == "all_weights"

    @pytest.mark.asyncio
    async def test_task_overwrites_duplicate_adapter_name(self):
        """Test that task overwrites an existing adapter when duplicate name is used."""
        workspace = "default"
        adapter_name = "test-lora-adapter"
        fileset_name_old = "test-old-lora-artifacts"
        fileset_name_new = "test-new-lora-artifacts"

        with tempfile.TemporaryDirectory() as tmpdir:
            entity_config = {
                "name": adapter_name,
                "workspace": workspace,
                "model_entity": "default/base-llama",
                "description": "Retrained adapter",
                "fileset": {
                    "workspace": workspace,
                    "name": fileset_name_new,
                },
                "peft": {
                    "type": "lora",
                    "alpha": 32,
                    "rank": 16,
                },
            }
            config_path = os.path.join(tmpdir, "entity_config.json")
            with open(config_path, "w") as f:
                json.dump(entity_config, f)

            env = {
                "NEMO_JOB_ID": "test-adapter-duplicate-job-123",
                "NEMO_JOB_WORKSPACE": workspace,
                "NEMO_JOB_STEP_CONFIG_FILE_PATH": config_path,
                "NEMO_JOB_STEP": "ModelEntityCreation",
                "NEMO_JOB_TASK": "model-entity-task",
                "NEMO_JOB_PERSISTENT_JOB_STORAGE_PATH": tmpdir,
            }
            async with task_harness(
                model_entity,
                FilesService,
                ModelsService,
                config={},
                env=env,
            ) as ctx:
                ctx.sdk.models.create(workspace="default", name="base-llama")

                # Setup: Create both filesets
                ctx.sdk.files.filesets.create(workspace=workspace, name=fileset_name_old)
                ctx.sdk.files.upload_content(
                    content=b"old lora weights",
                    remote_path="adapter_model.safetensors",
                    fileset=fileset_name_old,
                    workspace=workspace,
                )
                ctx.sdk.files.filesets.create(workspace=workspace, name=fileset_name_new)
                ctx.sdk.files.upload_content(
                    content=b"new lora weights",
                    remote_path="adapter_model.safetensors",
                    fileset=fileset_name_new,
                    workspace=workspace,
                )

                # Pre-create an adapter with the same name but old fileset
                ctx.sdk.models.adapters.create(
                    model_name="base-llama",
                    workspace=workspace,
                    name=adapter_name,
                    fileset=f"{workspace}/{fileset_name_old}",
                    finetuning_type="lora",
                    description="Original adapter",
                    enabled=True,
                )

                result = ctx.run_task()

                assert result.exit_code == 0, f"Task failed: stdout={result.stdout}, stderr={result.stderr}"
                assert result.exception is None

                # Verify the adapter was updated with new values
                model = ctx.sdk.models.retrieve(workspace="default", name="base-llama")
                assert len(model.adapters) == 1
                assert model.adapters[0].name == adapter_name
                assert model.adapters[0].description == "Retrained adapter"
                assert model.adapters[0].fileset == f"{workspace}/{fileset_name_new}"
                assert model.adapters[0].enabled is True
