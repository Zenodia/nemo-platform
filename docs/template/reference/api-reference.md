# API Reference

Use this page as a starting point for service-specific API reference content.
For a complete REST API page in the current MkDocs stack, render an OpenAPI file
with the `mkdocs-swagger-ui-tag` plugin:

```html
<swagger-ui src="./openapi.yaml"/>
```

## Examples

### List Models

=== "CLI (cURL)"

    ```bash
    curl "http://${HOSTNAME}:${SERVICE_PORT}/v1/models" \
      -H "Accept: application/json"
    ```

=== "Python"

    ```python
    import requests

    url = "http://<host>:<port>/v1/models"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers, timeout=30)
    print(response.text)
    ```

**Response**

```json
{
  "object": "list",
  "data": [
    {
      "id": "NV-Embed-QA",
      "created": 0,
      "object": "model",
      "owned_by": "organization-owner"
    }
  ]
}
```

### Service-Specific Request

=== "CLI (cURL)"

    ```bash
    curl -X "VERB" \
      "http://${HOSTNAME}:${SERVICE_PORT}/v1/ENDPOINT" \
      -H "Accept: application/json" \
      -H "Content-Type: application/json" \
      -d '{
        "arg1": "value1",
        "argN": "valueN"
      }'
    ```

=== "Python"

    ```python
    import json

    import requests

    url = "http://<host>:<port>/v1/ENDPOINT"
    payload = json.dumps(
        {
            "arg1": "value1",
            "argN": "valueN",
        }
    )
    headers = {"Content-Type": "application/json"}
    response = requests.request("VERB", url, headers=headers, data=payload, timeout=30)
    print(response.text)
    ```
