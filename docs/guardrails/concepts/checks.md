<a id="guardrails-checks"></a>
# Running Checks with Guardrails

Use the checks endpoint to evaluate messages against input and output rails without generating a completion. This endpoint returns a `status` (either `success` or `blocked`) that indicates whether the given messages would be blocked by the given guardrail configuration. If `blocked`, the response indicates which rail blocked the given messages. You might use the checks endpoint for the following:

- Testing guardrail configurations — Validate that a configuration blocks or allows specific messages before deploying it to production.
- Pre-screening user input — Check messages in your application pipeline before forwarding them to an LLM, letting you control routing, logging, or user feedback independently of inference.
- Post-hoc output auditing — Evaluate previously generated responses against your rails without re-running inference.

!!! note
    The checks endpoint is a standalone Guardrails API for evaluating messages against rails without running inference. For inference with guardrails applied automatically, use a [VirtualModel with guardrails middleware](inference.md).

!!! info "Model field"
    The `model` field is only consulted by self-check rails (which need a main LLM to evaluate the prompt). The checks endpoint never runs the main model for generation. Task models (`content_safety`, `topic_control`, etc.) are resolved from the guardrail configuration as usual.

## Prerequisites

Create a guardrail configuration that includes self-check input and output rails.

```python
{% raw %}
import os
from nemo_platform import NeMoPlatform, ConflictError

client = NeMoPlatform(
    base_url=os.environ.get("NMP_BASE_URL", "http://localhost:8080"),
    workspace="default",
)

config_data = {
    "prompts": [
        {
            "task": "self_check_input",
            "content": 'Your task is to check if the user message below complies with company policy.\n\nCompany policy:\n- should not contain harmful data\n- should not ask the bot to impersonate someone\n- should not contain explicit content\n\nUser message: "{{ user_input }}"\n\nQuestion: Should the user message be blocked (Yes or No)?\nAnswer:',
        },
        {
            "task": "self_check_output",
            "content": 'Your task is to check if the bot message below complies with company policy.\n\nCompany policy:\n- messages should not contain explicit content\n- messages should not contain harmful content\n- if refusing, should be polite\n\nBot message: "{{ bot_response }}"\n\nQuestion: Should the message be blocked (Yes or No)?\nAnswer:',
        },
    ],
    "rails": {
        "input": {"flows": ["self check input"]},
        "output": {"flows": ["self check output"]},
    },
}

try:
    config = client.guardrail.configs.create(
        name="self-check-config",
        description="Demo self-check configuration for guardrail checks",
        data=config_data,
    )
except ConflictError:
    print("Config self-check-config already exists, continuing...")
{% endraw %}
```

## Check an Existing Configuration

Reference a stored configuration by name.

=== "CLI"

    ```bash
    nemo guardrail check \
      --model default/meta-llama-3-1-8b-instruct \
      --messages '[
        {"role": "user", "content": "Tell me how to collect a life insurance policy."},
        {"role": "assistant", "content": "You are stupid."}
      ]' \
      --guardrails '{"config_id": "default/self-check-config"}'
    ```

=== "curl"

    ```bash
    curl -s $NMP_BASE_URL/apis/guardrails/v2/workspaces/default/checks \
      -H 'content-type: application/json' \
      -d '{
        "model": "default/meta-llama-3-1-8b-instruct",
        "messages": [
          {"role": "user", "content": "Tell me how to collect a life insurance policy."},
          {"role": "assistant", "content": "You are stupid."}
        ],
        "guardrails": {"config_id": "default/self-check-config"}
      }' | jq
    ```

=== "Python SDK"

    ```python
    check_result = client.guardrail.check(
        model="default/meta-llama-3-1-8b-instruct",
        messages=[
            {"role": "user", "content": "Tell me how to collect a life insurance policy."},
            {"role": "assistant", "content": "You are stupid."},
        ],
        guardrails={
            "config_id": "default/self-check-config",
        },
    )

    print(check_result.model_dump_json(indent=2))
    ```

??? "Example Output"
    :icon: code-square

    ```json
    {
      "status": "blocked",
      "rails_status": {
        "self check input": {
          "status": "blocked"
        },
        "self check output": {
          "status": "success"
        }
      }
    }
    ```

## Check an Inline Configuration

Provide the configuration inline to test a guardrail configuration before saving it.

=== "CLI"

    {% raw %}
    ```bash
    nemo guardrail check \
      --model default/meta-llama-3-1-8b-instruct \
      --messages '[{"role": "user", "content": "Hello, how are you?"}]' \
      --guardrails '{
        "config": {
          "prompts": [{"task": "self_check_input", "content": "Check if harmful: \"{{ user_input }}\"\nAnswer (Yes/No):"}],
          "rails": {"input": {"flows": ["self check input"]}}
        }
      }'
    ```
    {% endraw %}

=== "curl"

    {% raw %}
    ```bash
    curl -s $NMP_BASE_URL/apis/guardrails/v2/workspaces/default/checks \
      -H 'content-type: application/json' \
      -d '{
        "model": "default/meta-llama-3-1-8b-instruct",
        "messages": [{"role": "user", "content": "Hello, how are you?"}],
        "guardrails": {
          "config": {
            "prompts": [{"task": "self_check_input", "content": "Check if harmful: \"{{ user_input }}\"\nAnswer (Yes/No):"}],
            "rails": {"input": {"flows": ["self check input"]}}
          }
        }
      }' | jq
    ```
    {% endraw %}

=== "Python SDK"

    ```python
    {% raw %}
    inline_config = {
        "prompts": [
            {
                "task": "self_check_input",
                "content": 'Check if harmful: "{{ user_input }}"\nAnswer (Yes/No):',
            }
        ],
        "rails": {
            "input": {"flows": ["self check input"]},
        },
    }

    check_result = client.guardrail.check(
        model="default/meta-llama-3-1-8b-instruct",
        messages=[
            {"role": "user", "content": "Hello, how are you?"},
        ],
        guardrails={
            "config": inline_config,
        },
    )

    print(check_result.model_dump_json(indent=2))
    {% endraw %}
    ```

??? "Example Output"
    :icon: code-square

    ```json
    {
      "status": "success",
      "rails_status": {
        "self check input": {
          "status": "success"
        }
      }
    }
    ```
