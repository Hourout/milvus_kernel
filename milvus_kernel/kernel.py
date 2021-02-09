import pandas as pd
from milvus import Milvus, IndexType, MetricType, Status
from ipykernel.kernelbase import Kernel


__version__ = '0.1.0'

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
                    elif l.startswith('help'):
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
                            ],
                             'milvus sql':[
                                 'create collection test01 where dimension=128 and index_file_size=1024 and metric_type=L2',
                                 'drop collection test01',
                                 'list collections',
                                 'create partition test01 where partition_tag=tag01',
                                 'drop partition test01 where partition_tag=tag01',
                                 'list partitions test01',
                                 'create index test01 where index_type=FLAT and nlist=4096',
                                 'drop index test01',
                             ]}).to_html()
                    elif l.startswith('list collections'):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        output = str(self.engine.list_collections()[1])
                    elif l.startswith('create collection '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        param = {'collection_name':v.split('where')[0][17:].strip()}
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
                    elif l.startswith('drop collection '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        output = self.engine.drop_collection(collection_name=v[15:].strip()).message
                    elif l.startswith('create partition '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        output = self.engine.create_partition(collection_name=v.split('where')[0][16:].strip(),
                                                              partition_tag=v.split('where')[1].split('=')[1].strip()).message
                    elif l.startswith('drop partition '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        output = self.engine.drop_partition(collection_name=v.split('where')[0][14:].strip(),
                                                            partition_tag=v.split('where')[1].split('=')[1].strip()).message
                    elif l.startswith('list partitions '):
                        if not self.engine:
                            self.output(message)
                            return self.ok()
                        output = str(self.engine.list_partitions(collection_name=v[15:].strip())[1])
                    elif l.startswith('create index '):
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
                        output = self.engine.create_index(collection_name=v.split(' where ')[0][12:].strip(),
                                                          params=param).message
                    elif l.startswith('drop index '):
                        output = self.engine.drop_index(collection_name=v[10:].strip()).message
                    elif l.startswith('compact '):
                        output = self.engine.compact(collection_name=v[7:].strip()).message
                    elif l.startswith('flush '):
                        collection_list = [i.strip() for i in v[7:].strip().split(',') if len(i.strip())>0]
                        output = self.engine.compact(collection_name_array=collection_list).message
            self.output(output)
            return self.ok()
        except Exception as msg:
            self.output(str(msg))
            return self.err('Error executing code ' + sql)
