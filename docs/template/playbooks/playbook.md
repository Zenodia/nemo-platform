# ??? Playbook

The container used in this playbook: [<container>](???).

## Notebook Requirements

- Access to <GPU model, how many, RAM, ...>
- Access to NGC ???
- Docker

## Getting <model>

To see the list of all available prebuilt models:

``` bash
ngc registry model list "${inference_ngc_org_team}/*"
```

Once you see the model you want to use,
you can get information about the model,
as shown in the following example:

```bash
ngc registry model info nvcr.io/ORG/TEAM/MODEL
```

And then download the model using the following command:

``` bash
ngc registry model download-version "ORG/TEAM/MODEL"
```
