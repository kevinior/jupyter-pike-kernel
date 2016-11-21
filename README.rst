A simple IPython kernel for the `Pike programming language <http://pike.lysator.liu.se>`_.

This requires IPython 3.

To install::

    pip install pike_kernel
    python -m pike_kernel.install

To use it, run one of:

.. code:: shell

    ipython notebook
    # In the notebook interface, select Pike from the 'New' menu
    ipython qtconsole --kernel pike
    ipython console --kernel pike

For details of how this works, see the Jupyter docs on `wrapper kernels
<http://jupyter-client.readthedocs.org/en/latest/wrapperkernels.html>`_, and
Pexpect's docs on the `replwrap module
<http://pexpect.readthedocs.org/en/latest/api/replwrap.html>`_

Mostly copied from `Thomas Kluyver's bash kernel <https://github.com/takluyver/bash_kernel>`_.
