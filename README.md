# milvus_kernel

Milvus Kernel for Jupyter


![PyPI version](https://img.shields.io/pypi/pyversions/milvus_kernel.svg)
![Github license](https://img.shields.io/github/license/Hourout/milvus_kernel.svg)
[![PyPI](https://img.shields.io/pypi/v/mysql_kernel.svg)](https://pypi.python.org/pypi/milvus_kernel)
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

<img src="https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fk.kakaocdn.net%2Fdn%2FyZrl5%2FbtqwEwV2HHb%2Fd8u9PLWcIxXLJ8BkqvV881%2Fimg.jpg" width = "32" height = "32" />

- https://jeongw00.tistory.com/203
