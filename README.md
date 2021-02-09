# milvus_kernel

Milvus Kernel for Jupyter


![PyPI version](https://img.shields.io/pypi/pyversions/milvus_kernel.svg)
![Github license](https://img.shields.io/github/license/Hourout/milvus_kernel.svg)
[![PyPI](https://img.shields.io/pypi/v/milvus_kernel.svg)](https://pypi.python.org/pypi/milvus_kernel)
![PyPI format](https://img.shields.io/pypi/format/milvus_kernel.svg)
![contributors](https://img.shields.io/github/contributors/Hourout/milvus_kernel)
![downloads](https://img.shields.io/pypi/dm/milvus_kernel.svg)

Milvus Kernel for Jupyter

[中文介绍](document/chinese.md)

## Installation

#### step1:
```
pip install milvus_kernel
```

To get the newest one from this repo (note that we are in the alpha stage, so there may be frequent updates), type:

```
pip install git+git://github.com/Hourout/milvus_kernel.git
```

#### step2:
Add kernel to your jupyter:

```
python3 -m milvus_kernel.install
```

ALL DONE! 🎉🎉🎉

## Uninstall

#### step1:

View and remove milvus kernel
```
jupyter kernelspec list
jupyter kernelspec remove milvus
```

#### step2:
uninstall milvus kernel:

```
pip uninstall milvus-kernel
```

ALL DONE! 🎉🎉🎉


## Using

```
jupyter notebook
```
<img src="image/milvus1.png" width = "700" height = "300" />

### step1: you should set milvus host and port

### step2: write your milvus code

![](image/milvus2.png)

## Quote 
kernel logo

<img src="https://imgconvert.csdnimg.cn/aHR0cHM6Ly9tbWJpei5xcGljLmNuL21tYml6X3BuZy9NcWdBOFlsZ2VoNHozS05uUHVuaWNVNTBnTTROVlE0U0RJVkNHcks4enFoc1FPRUdtMGtjZFBoamxiZ01zTE5wM0NUNkp5Z1M0aWNlazZHY2Q2SlhTd05BLzY0MA?x-oss-process=image/format,png" width = "32" height = "32" />

- https://blog.csdn.net/weixin_44839084/article/details/108070675
