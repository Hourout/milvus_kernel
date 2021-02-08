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
                        if l.count('@')>1:
                            self.output("Connection failed, The Milvus address cannot have two '@'.")
                        else:
                            self.engine = Milvus(uri=f'tcp://{v[9:]}')
                    elif l.startswith('list collections'):
                        output = str(self.engine.list_collections()[1])
#                     elif l.startswith('create collection '):
#                         v.split(' ')[2]
                        
#                     else:
#                         if self.engine:
#                             if l.startswith('select ') and ' limit ' not in l:
#                                 output = pd.read_sql(l+' limit 1000', self.engine).to_html()
#                             else:
#                                 output = pd.read_sql(l, self.engine).to_html()
#                         else:
#                             output = 'Unable to connect to Milvus server. Check that the server is running.'
            self.output(output)
            return self.ok()
        except Exception as msg:
            self.output(str(msg))
            return self.err('Error executing code ' + sql)
