# LoRA Customization Job via NeMo Platform Customizer API (GPU)

This task tests submitting and running a real LoRA fine-tuning job through the NeMo Platform Customizer service. The job is dispatched through the NeMo Platform jobs pipeline to a GPU container.

You have access to the `nmp` CLI for NeMo Platform operations. Note: MCP tools are not available in this environment - you must use the CLI.

The `nmp` CLI is available at `/app/.venv/bin/nmp`. The CLI connects to the local NeMo Platform API server at http://localhost:8080 by default. CLI auth is pre-configured.

## Context

- The NeMo Platform API server is running with the jobs controller enabled
- The Docker backend is configured for GPU job execution
- The Docker socket is mounted for real container execution
- A workspace `lora-training-workspace` has been pre-created
- A model entity `smollm-135m` has been registered in the workspace

## Task

### Step 1: Prepare and upload a training dataset

1. Create a JSONL file with at least 20 prompt/completion training examples for a simple task (e.g., customer service responses). Example format:
   ```jsonl
   {"prompt": "Customer complaint: My order arrived damaged.\nResponse:", "completion": "I apologize for the inconvenience. I will arrange a replacement immediately."}
   ```

2. Upload this dataset to NeMo Platform as a fileset named `sft-training-data` in the `lora-training-workspace` workspace.

### Step 2: Submit a LoRA customization job

Create a customization job using the NeMo Platform Customizer API:

```bash
nmp customization jobs create --workspace lora-training-workspace --input-data '{
  "spec": {
    "model": "lora-training-workspace/smollm-135m",
    "dataset": "fileset://lora-training-workspace/sft-training-data",
    "training": {
      "type": "sft",
      "peft": {
        "type": "lora",
        "rank": 8,
        "alpha": 16
      },
      "epochs": 2,
      "learning_rate": 0.0001,
      "batch_size": 4
    },
    "output": {
      "name": "lora-email-model"
    }
  }
}'
```

### Step 3: Monitor the job

1. Poll the job status using `nmp customization jobs list --workspace lora-training-workspace` or `nmp customization jobs get <name> --workspace lora-training-workspace`.
2. Check status periodically until it reaches a terminal state.
3. If it fails, investigate using `nmp customization jobs get <name>` and check for error details.

### Step 4: Verify results

Once the job completes (or if it fails), document:
- The job status
- Any error messages if it failed
- The output model/adapter if it completed

## Success Criteria

The task is complete when:
- A fileset `sft-training-data` exists with training data uploaded
- A customization job was submitted via the NeMo Platform Customizer API
- The agent polled for job status and reported the outcome
- The job progressed beyond "created" status (indicating the jobs controller dispatched it)

## Notes

- The customizer dispatches training jobs through the NeMo Platform jobs pipeline to GPU containers
- The model reference format is `workspace/model-name` (e.g., `lora-training-workspace/smollm-135m`)
- The dataset reference format is `fileset://workspace/fileset-name`
- Jobs may take a few minutes to complete depending on dataset size
- If the job encounters errors, investigating and reporting the error is a valid outcome
