# Deploying with Docker

<MICROSERVICE> is intended to be run on a system with NVIDIA Datacenter GPUs,
with the exact requirements depending on the specific model and deployment options.

For full systems hardware and software requirements see [Support
Matrix](./support-matrix).
For information about the models supported by the different containers, and the GPUs needed to run the models, see [Models](./models/models).

## Pre-requisite Software

To run LLM NIMs, you'll need a container runtime with support for NVIDIA GPUs. You can set this up with the following steps:

1. Install [Docker](https://docs.docker.com/engine/install/)
1. Install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installing-the-nvidia-container-toolkit)

## Setting up the Environment

Set the **NGC_CLI_API_KEY** environment variable to your NGC API key, as
shown in the following example.

``` bash
export NGC_CLI_API_KEY="key from ngc"
```

If you have not set up NGC, see [NGC
Setup](https://catalog.ngc.nvidia.comsetup). Don't forget to download and
install the NCG CLI (the download is on that page).

## Download Container

## Download a Model

## Launching the Container

## Health and Liveness Checks

## Stopping the Container
