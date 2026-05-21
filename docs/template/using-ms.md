# Client Examples

The Python client is uploaded to the NGC Private Registry Resources.
Since the packages are not deployed to a public package registry, 
you must download the `.whl` and `pip` files and install them from the following locations:

- [EA Participants](https://registry.ngc.nvidia.com/orgs/ohlfw0olaadg/teams/ea-participants/resources/nemo-MICROSERVICE-python-client)
- [NVIDIAN/nemo-llm](https://registry.ngc.nvidia.com/orgs/nvidian/teams/nemo-llm/resources/nemo-MICROSERVICE-python-client)

## MICROSERVICE

You must modify the `base_url` if you did not start the MICROSERVICE using the default configuration.

``` python
from nemo_MICROSERVICE_client import MICROSERVICEClient
from pprint import pprint

NAME = MICROSERVICEClient(base_url="http://localhost:1984")

# GET pipelines: list all pipeline options available
response = NAME.get_pipelines()

# GET collections: list all created collections
response = NAME.get_collections()

# CREATE a new collection - specify the pipeline type and name of the collection
response = NAME.create_collection(pipeline="dense_elasticsearch", name="testCollection")
created_collection_id = (
    response.collection.id
)  # store ID of the newly created collection

# other examples
```
