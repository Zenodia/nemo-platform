# Support Matrix

## Hardware

The YY.MM release of MICROSERVICE has been tested on the following NVIDIA GPUs:

- [NVIDIA A100](https://www.nvidia.com/en-us/data-center/a100/)
- [NVIDIA L4](https://www.nvidia.com/en-us/data-center/l4/)

## Software

### NVIDIA Driver

Release YY.MM is based on [CUDA
12.2.2](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html)
which requires [NVIDIA
Driver](https://www.nvidia.com/Download/index.aspx?lang=en-us) release
535 or later. However, if you are running on a [data center
GPU](https://www.nvidia.com/en-us/data-center/products/), you can use
NVIDIA driver release 450.51 (or later R450), 470.57 (or later R470),
510.47 (or later R510), 515.65 (or later R515), or 525.85 (or later
R525), or 535.86 (or later R535). The CUDA driver's compatibility
package only supports particular drivers. Thus, users should upgrade
from all R418, R440, and R460 drivers, which are not forward-compatible
with CUDA 12.2. For a complete list of supported drivers, see [CUDA
Application
Compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/index.html#use-the-right-compat-package).

### NVIDIA Container Toolkit

Your Docker environment must support NVIDIA GPUs. See the [NVIDIA
Container
Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
for more information.
