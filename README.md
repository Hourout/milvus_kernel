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


## Basic operations

## Connect to the Milvus server

1. Create a client to Milvus server by using the following methods:

   ```sql
   milvus://127.0.0.1:19530
   ```

## Create/Drop collections

### Create a collection

Create collection `test01` with dimension size as 128, size of the data file for Milvus to automatically create indexes as 1024, and metric type as Euclidean distance (L2).

   ```sql
   create table test01 where dimension=128 and index_file_size=1024 and metric_type='L2'
   ```

### Drop a collection

```sql
drop table test01
```

## Create/Drop partitions in a collection

### Create a partition

You can split collections into partitions by partition tags for improved search performance. Each partition is also a collection.

```sql
create partition test01 where partition_tag='tag01'
```

verify whether the partition is created.

```sql
list partitions test01
```

### Drop a partition

```python
>>> status = client.drop_partition(collection_name='test01', partition_tag='tag01')
Status(code=0, message='OK')
```

## Create/Drop indexes in a collection

### Create an index

> Note: In production, it is recommended to create indexes before inserting vectors into the collection. Index is automatically built when vectors are being imported. However, you need to create the same index again after the vector insertion process is completed because some data files may not meet the `index_file_size` and index will not be automatically built for these data files.

1. Prepare index parameters. The following command uses `IVF_FLAT` index type as an example.

   ```python
   # Prepare index param
   >>> ivf_param = {'nlist': 4096}
   ```

2. Create an index for the collection.

   ```python
   # Create index
   >>> status = client.create_index('test01', IndexType.IVF_FLAT, ivf_param)
   Status(code=0, message='Build index successfully!')
   ```

### Drop an index

```python
>>> status = client.drop_index('test01')
Status(code=0, message='OK')
```

## Insert/Delete vectors in collections/partitions

### Insert vectors in a collection

1. Generate 20 vectors of 128 dimension.

   ```python
   >>> import random
   >>> dim = 128
   # Generate 20 vectors of 128 dimension
   >>> vectors = [[random.random() for _ in range(dim)] for _ in range(20)]
   ```

2. Insert the list of vectors. If you do not specify vector ids, Milvus automatically generates IDs for the vectors.

   ```python
   # Insert vectors
   >>> status, inserted_vector_ids = client.insert(collection_name='test01', records=vectors)
   >>> inserted_vector_ids 
   [1592028661511657000, 1592028661511657001, 1592028661511657002, 1592028661511657003, 1592028661511657004, 1592028661511657005, 1592028661511657006, 1592028661511657007, 1592028661511657008, 1592028661511657009, 1592028661511657010, 1592028661511657011, 1592028661511657012, 1592028661511657013, 1592028661511657014, 1592028661511657015, 1592028661511657016, 1592028661511657017, 1592028661511657018, 1592028661511657019]
   ```

   Alternatively, you can also provide user-defined vector ids:

   ```python
   >>> vector_ids = [id for id in range(20)]
   >>> status, inserted_vector_ids = client.insert(collection_name='test01', records=vectors, ids=vector_ids)
   ```

### Insert vectors in a partition

```python
>>> status, inserted_vector_ids = client.insert('test01', vectors, partition_tag="tag01")
```

To verify the vectors you have inserted, use `get_vector_by_id()`. Assume you have vector with the following ID.

```python
>>> status, vector = client.get_entity_by_id(collection_name='test01', ids=inserted_vector_ids[:10])
```

### Delete vectors by ID

You can delete these vectors by:

```python
>>> status = client.delete_entity_by_id('test01', inserted_vector_ids[:10])
>>> status
Status(code=0, message='OK')
```

## Flush data in one or multiple collections to disk

When performing operations related to data changes, you can flush the data from memory to disk to avoid possible data loss. Milvus also supports automatic flushing, which runs at a fixed interval to flush the data in all collections to disk. You can use the [Milvus server configuration file](https://milvus.io/docs/reference/milvus_config.md) to set the interval.

```python
>>> status = client.flush(['test01'])
>>> status
Status(code=0, message='OK')
```

## Compact all segments in a collection

A segment is a data file that Milvus automatically creates by merging inserted vector data. A collection can contain multiple segments. If some vectors are deleted from a segment, the space taken by the deleted vectors cannot be released automatically. You can compact segments in a collection to release space.

```python
>>> status = client.compact(collection_name='test01')
>>> status
Status(code=0, message='OK')
```

## Search vectors in collections/partitions

### Search vectors in a collection

1. Prepare search parameters.

```python
>>> search_param = {'nprobe': 16}
```

2. Search vectors.

```python
# create 5 vectors of 32-dimension
>>> q_records = [[random.random() for _ in range(dim)] for _ in range(5)]
# search vectors
>>> status, results = client.search(collection_name='test01', query_records=q_records, top_k=2, params=search_param)
>>> results
[
[(id:1592028661511657012, distance:19.450458526611328), (id:1592028661511657017, distance:20.13418197631836)],
[(id:1592028661511657012, distance:19.12230682373047), (id:1592028661511657018, distance:20.221458435058594)],
[(id:1592028661511657014, distance:20.423980712890625), (id:1592028661511657016, distance:20.984281539916992)],
[(id:1592028661511657018, distance:18.37057876586914), (id:1592028661511657019, distance:19.366962432861328)],
[(id:1592028661511657013, distance:19.522361755371094), (id:1592028661511657010, distance:20.304216384887695)]
]
```

### Search vectors in a partition

```python
# create 5 vectors of 32-dimension
>>> q_records = [[random.random() for _ in range(dim)] for _ in range(5)]
>>> client.search(collection_name='test01', query_records=q_records, top_k=1, partition_tags=['tag01'], params=search_param)
```

> Note: If you do not specify `partition_tags`, Milvus searches the whole collection.





## Quote 
kernel logo

<img src="https://imgconvert.csdnimg.cn/aHR0cHM6Ly9tbWJpei5xcGljLmNuL21tYml6X3BuZy9NcWdBOFlsZ2VoNHozS05uUHVuaWNVNTBnTTROVlE0U0RJVkNHcks4enFoc1FPRUdtMGtjZFBoamxiZ01zTE5wM0NUNkp5Z1M0aWNlazZHY2Q2SlhTd05BLzY0MA?x-oss-process=image/format,png" width = "32" height = "32" />

- https://blog.csdn.net/weixin_44839084/article/details/108070675
