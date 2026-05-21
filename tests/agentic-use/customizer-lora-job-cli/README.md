# LoRA Customization Job (CLI, GPU)

Tests the agent's ability to set up and submit a real LoRA fine-tuning job through the NeMo Platform Customizer service using the CLI.

## What This Tests

- Creating workspaces and filesets via NeMo Platform CLI
- Preparing and uploading SFT training data in JSONL format
- Submitting a LoRA customization job with correct hyperparameters
- Monitoring job progress

## GPU Requirements

This eval requires **1 GPU** allocated to the Harbor container. The customization job performs actual LoRA fine-tuning on the GPU.

If the NeMo Platform job executor is not configured to run inside the Harbor container, the eval still validates correct job submission. To enable end-to-end training, ensure the job dispatcher backend is configured for local GPU execution.

## Flow Reference

Implements flow **17a: Basic LoRA Customization Job** from `../agentic_flows/customizer.md`.
