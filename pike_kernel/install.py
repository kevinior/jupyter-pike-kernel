import json
import os
import sys
import getopt

from jupyter_client.kernelspec import KernelSpecManager
from IPython.utils.tempdir import TemporaryDirectory

kernel_json = {"argv": [sys.executable,
                        "-m", "pike_kernel",
                        "-f", "{connection_file}"],
               "display_name": "Pike",
               "language": "pike"
               }


def install_my_kernel_spec(user=True, prefix=None):
    with TemporaryDirectory() as td:
        os.chmod(td, 0o755)
        with open(os.path.join(td, 'kernel.json'), 'w') as f:
            json.dump(kernel_json, f, sort_keys=True)

        print('Installing IPython kernel spec')
        KernelSpecManager().install_kernel_spec(td, 'pike', user=user,
                                                replace=True, prefix=prefix)


def _is_root():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False


def main(argv=[]):
    prefix = None
    user = not _is_root()

    opts, _ = getopt.getopt(argv[1:], '', ['user', 'prefix='])
    for k, v in opts:
        if k == '--user':
            user = True
        elif k == '--prefix':
            prefix = v
            user = False

    install_my_kernel_spec(user=user, prefix=prefix)

if __name__ == '__main__':
    main(argv=sys.argv)
