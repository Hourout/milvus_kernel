import os
import sys
import json
import base64
import argparse

from IPython.utils.tempdir import TemporaryDirectory
from jupyter_client.kernelspec import KernelSpecManager

kernel_logo = b'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'
kernel_json = {"argv":[sys.executable, "-m", "milvus_kernel", "-f", "{connection_file}"],
               "display_name":"Milvus",
               "language":"sql"}

def install_my_kernel_spec(user=True, prefix=None):
    with TemporaryDirectory() as td:
        os.chmod(td, 0o755)
        with open(os.path.join(td, 'kernel.json'), 'w') as f:
            json.dump(kernel_json, f, sort_keys=True)
        with open(os.path.join(td, 'logo-64x64.png'), 'wb') as f:
            f.write(base64.b64decode(kernel_logo))
        print('Installing Jupyter Milvus kernel spec.')
        KernelSpecManager().install_kernel_spec(td, 'Milvus', user=user, replace=True, prefix=prefix)

def _is_root():
    try:
        return os.geteuid()==0
    except AttributeError:
        return False

def main(argv=None):
    parser = argparse.ArgumentParser(description='Install Jupyter KernelSpec for Milvus Kernel.')
    prefix_locations = parser.add_mutually_exclusive_group()
    prefix_locations.add_argument('--user',
                                  help='Install Jupyter Milvus KernelSpec in user homedirectory.',
                                  action='store_true')
    prefix_locations.add_argument('--sys-prefix',
                                  help='Install Jupyter Milvus KernelSpec in sys.prefix. Useful in conda / virtualenv',
                                  action='store_true',
                                  dest='sys_prefix')
    prefix_locations.add_argument('--prefix',
                                  help='Install Jupyter Milvus KernelSpec in this prefix',
                                  default=None)
    args = parser.parse_args(argv)

    user = False
    prefix = None
    if args.sys_prefix:
        prefix = sys.prefix
    elif args.prefix:
        prefix = args.prefix
    elif args.user or not _is_root():
        user = True

    install_my_kernel_spec(user=user, prefix=prefix)

if __name__ == '__main__':
    main()
