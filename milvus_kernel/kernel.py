import pandas as pd
from milvus import Milvus, IndexType, MetricType
from ipykernel.kernelbase import Kernel


__version__ = '0.2.0'

class MilvusKernel(Kernel):
    implementation = 'milvus_kernel'
    implementation_version = __version__
    language = 'sql'
    language_version = 'latest'
    language_info = {'name': 'sql',
                     'mimetype': 'text/x-sh',
                     'file_extension': '.sql'}
    banner = 'milvus kernel'

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self.engine = False
        
    def output(self, output):
        if not self.silent:
            display_content = {'source': 'kernel',
                               'data': {'text/html': output},
                               'metadata': {}}
            self.send_response(self.iopub_socket, 'display_data', display_content)
    
    def ok(self):
        return {'status':'ok', 'execution_count':self.execution_count, 'payload':[], 'user_expressions':{}}

    def err(self, msg):
        return {'status':'error',
                'error':msg,
                'traceback':[msg],
                'execution_count':self.execution_count,
                'payload':[],
                'user_expressions':{}}

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        self.silent = silent
        message = 'Unable to connect to Milvus server. Check that the server is running.'
        output = ''
        if not code.strip():
            return self.ok()
        sql = code.rstrip()+('' if code.rstrip().endswith(";") else ';')
        try:
            for v in sql.split(";"):
                v = v.rstrip()
                l = v.lower()
                if len(l)>0:
                    if l.startswith('milvus://'):
                        self.engine = Milvus(uri=f'tcp://{v[9:]}')
                    elif l=='help':
                        output = pd.DataFrame(
                            {'description':[
                                'Create a collection',
                                'Drop a collection',
                                'Show all collections',
                                'Create a partition',
                                'Drop a partition',
                                'Show all partitions in a collection',
                                'Create an index',
                                'Removes an index',
                                'Flush data',
                                'Compact all segments in a collection',
                                'Search vectors',
                                'Delete vectors by ID',
                                'Insert a vector',
                                'Select vector',
                                'View metric type',
                                'View index type',
                                'View a collection description',
                                'View a collection statistics',
                            ],
                             'milvus sql':[
                                 "create table test01 where dimension=128 and index_file_size=1024 and metric_type='L2'",
                                 'drop table test01',
                                 'list table',
                                 "create partition test01 where partition_tag='tag01'",
                                 "drop partition test01 where partition_tag='tag01'",
                                 'list partitions test01',
                                 "create index test01 where index_type='FLAT' and nlist=4096",
                                 'drop index test01',
                                 'flush test01, test02',
                                 'compact test01',
                                 "select 2, 3, 5 from test01 where top_k=1 and partition_tags='tag01' and nprobe=16",
                                 'delete test01 by id=1',
                                 "insert 2,3,5 from test01 where partition_tag='tag01' by id=0",
                                 'select test01 by id=1,2,3',
                                 'help -metric',
                                 'help -index',
                                 'desc test01',
                                 'stats test01',
                             ]}).to_html()
                    elif l=='help -metric':
                        output = pd.DataFrame(
                            {'description':[
                                'HAMMING', 'INVALID', 'IP', 'JACCARD', 'L2', 'SUBSTRUCTURE', 'SUPERSTRUCTURE', 'TANIMOTO'
                            ],
                             'milvus MetricType':[
                                 'MetricType.HAMMING', 'MetricType.INVALID', 'MetricType.IP', 'MetricType.JACCARD', 'MetricType.L2', 
                                 'MetricType.SUBSTRUCTURE', 'MetricType.SUPERSTRUCTURE', 'MetricType.TANIMOTO'
                             ]}).to_html()
                    elif l=='help -index':
                        output = pd.DataFrame(
                            {'description':[
                                'IVFLAT', 'ANNOY', 'FLAT', 'HNSW', 'INVALID', 'IVF_PQ', 'IVF_SQ8', 'IVF_SQ8H', 'RNSG'
                            ],
                             'milvus IndexType':[
                                 'IndexType.IVFLAT', 'IndexType.ANNOY', 'IndexType.FLAT', 'IndexType.HNSW', 'IndexType.INVALID', 
                                 'IndexType.IVF_PQ', 'IndexType.IVF_SQ8', 'IndexType.IVF_SQ8H', 'IndexType.RNSG'
                             ]}).to_html()
                    elif l.startswith('desc '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        info_col = self.engine.get_collection_info(v[4:].strip())[1]
                        info_index = self.engine.get_index_info(v[4:].strip())[1]
                        desc = (['collection_name', 'dimension', 'index_file_size', 'metric_type', 'index_type']
                                +[i for i in info_index.params]+['row_count'])
                        info = ([info_col.collection_name, info_col.dimension, info_col.index_file_size, str(info_col.metric_type),
                                str(info_index.index_type)]+[info_index.params[i] for i in info_index.params]
                                +[self.engine.get_collection_stats(v[4:].strip())[1]['row_count']])
                        output = pd.DataFrame({'description': desc, 'info': info}).to_html()
                    elif l.startswith('stats '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        temp = pd.DataFrame()
                        for i in self.engine.get_collection_stats(v[5:].strip())[1]['partitions']:
                            t = pd.DataFrame(i['segments'])
                            t['tag'] = i['tag']
                            temp = pd.concat([temp, t])
                        output = temp.to_html()
                    elif l.startswith('list table'):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        output = pd.DataFrame(self.engine.list_collections()[1], columns=['collections']).to_html()
                    elif l.startswith('create table '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        param = {'collection_name':v.split(' where ')[0][12:].strip()}
                        for i in v.split(' where ')[1].split(' and '):
                            param_list = i.split('=')
                            if param_list[0].strip()=='dimension':
                                param['dimension'] = int(param_list[1].strip())
                            elif param_list[0].strip()=='index_file_size':
                                param['index_file_size'] = int(param_list[1].strip())
                            elif param_list[0].strip()=='metric_type':
                                metric_type_dict = {
                                    'HAMMING': MetricType.HAMMING,
                                    'INVALID': MetricType.INVALID,
                                    'IP': MetricType.IP,
                                    'JACCARD': MetricType.JACCARD,
                                    'L2': MetricType.L2,
                                    'SUBSTRUCTURE': MetricType.SUBSTRUCTURE,
                                    'SUPERSTRUCTURE': MetricType.SUPERSTRUCTURE,
                                    'TANIMOTO': MetricType.TANIMOTO}
                                param['metric_type'] = metric_type_dict[param_list[1].strip().replace("'", '')]
                        output = self.engine.create_collection(param).message
                    elif l.startswith('drop table '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        output = self.engine.drop_collection(collection_name=v[10:].strip()).message
                    elif l.startswith('create partition '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        output = self.engine.create_partition(collection_name=v.split(' where ')[0][16:].strip(),
                                                              partition_tag=v.split(' where ')[1].split('=')[1].strip().replace("'", '')).message
                    elif l.startswith('drop partition '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        output = self.engine.drop_partition(collection_name=v.split(' where ')[0][14:].strip(),
                                                            partition_tag=v.split(' where ')[1].split('=')[1].strip().replace("'", '')).message
                    elif l.startswith('list partitions '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        output = self.engine.list_partitions(collection_name=v[15:].strip())[1]
                        output = pd.DataFrame([[i.collection_name, i.tag] for i in output], columns=['collections', 'tag']).to_html()
                    elif l.startswith('create index '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        param = {}
                        for i in v.split(' where ')[1].split(' and '):
                            param_list = i.split('=')
                            if param_list[0].strip()=='nlist':
                                param['nlist'] = int(param_list[1].strip())
                            elif param_list[0].strip()=='index_type':
                                index_type_dict = {
                                    'IVFLAT': IndexType.IVFLAT,
                                    'ANNOY': IndexType.ANNOY,
                                    'FLAT': IndexType.FLAT,
                                    'HNSW': IndexType.HNSW,
                                    'INVALID': IndexType.INVALID,
                                    'IVF_PQ': IndexType.IVF_PQ,
                                    'IVF_SQ8': IndexType.IVF_SQ8,
                                    'IVF_SQ8H': IndexType.IVF_SQ8H,
                                    'RNSG': IndexType.RNSG}
                                param['index_type'] = index_type_dict[param_list[1].strip().replace("'", '')]
                        output = self.engine.create_index(collection_name=v.split(' where ')[0][12:].strip(), params=param).message
                    elif l.startswith('drop index '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        output = self.engine.drop_index(collection_name=v[10:].strip()).message
                    elif l.startswith('compact '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        output = self.engine.compact(collection_name=v[7:].strip()).message
                    elif l.startswith('flush '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        collection_list = [i.strip() for i in v[7:].strip().split(',') if len(i.strip())>0]
                        output = self.engine.compact(collection_name_array=collection_list).message
                    elif l.startswith('select ') and ' where ' in l:
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        partition_tags = None
                        params = None
                        for i in v.split(' where ')[1].split(' and '):
                            param_list = i.split('=')
                            if param_list[0].strip()=='top_k':
                                top_k = int(param_list[1].strip())
                            elif param_list[0].strip()=='partition_tags':
                                partition_tags = [param_list[1].strip().replace("'", '')]
                            elif param_list[0].strip()=='nprobe':
                                params = {'nprobe': int(param_list[1].strip())}
                        query_records = [float(i.strip()) for i in v.split(' from ')[0][6:].split(',') if len(i.strip())>0]
                        output = self.engine.search(collection_name=v.split(' from ')[1].split(' where ')[0],
                                                    top_k=top_k,
                                                    query_records=query_records,
                                                    partition_tags=partition_tags,
                                                    params=params)
                    elif l.startswith('delete '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        output = self.engine.delete_entity_by_id(collection_name=v.split(' by ')[0][6:].strip(),
                                                                 id_array=[int(i.strip()) for i in v.split('=')[1].split(',') if len(i.strip())>0]).message
                    elif l.startswith('insert '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        collection_name = v.split(' from ')[1].split(' ')[0].strip() if ' where ' in l or ' by ' in l else v.split(' from ')[1].strip()
                        ids = None
                        partition_tag = None
                        if ' where ' in l:
                            partition_tag = v.split(' where ')[1]
                            if ' by ' in partition_tag:
                                partition_tag = partition_tag.split(' by ')[0]
                            partition_tag = partition_tag.split('=')[1].strip().replace("'", '')
                        if ' by ' in l:
                            ids = v.split(' by ')[1]
                            if ' where ' in ids:
                                ids = ids.split(' where ')[0]
                            ids = int(ids.split('=')[1].strip())
                        records = [float(i.strip()) for i in v.split(' from ')[0][6:].split(',') if len(i.strip())>0]
                        _, output = self.engine.insert(collection_name=collection_name, records=records, ids=ids, partition_tag=partition_tag)
                        output = pd.DataFrame(output, columns=['inserted_vector_ids']).to_html()
                    elif l.startswith('select ') and ' by ' in l:
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        _, output = self.engine.get_entity_by_id(collection_name=v.split(' by ')[0][6:].strip(),
                                                                 ids=[int(i.strip()) for i in v.split('=')[1].split(',') if len(i.strip())>0])
                        output = pd.DataFrame(output, columns=['inserted_vector_ids']).to_html()
                    else:
                        output = 'Milvus SQL Syntax errors, please check SQL Syntax.'
            self.output(output)
            return self.ok()
        except Exception as msg:
            self.output(str(msg))
            return self.err('Error executing code ' + sql)
