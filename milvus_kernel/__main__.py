from ipykernel.kernelapp import IPKernelApp
from .kernel import MilvusKernel


IPKernelApp.launch_instance(kernel_class=MilvusKernel)
