from ipykernel.kernelapp import IPKernelApp
from .kernel import PikeKernel
IPKernelApp.launch_instance(kernel_class=PikeKernel)
