from ipykernel.kernelbase import Kernel
from pexpect import replwrap, EOF
import pexpect

from subprocess import check_output
import os.path

import re
import signal
import urllib

__version__ = '0.1'

version_pat = re.compile(r'Pike v([0-9\.]+)')


class IREPLWrapper(replwrap.REPLWrapper):
    """A subclass of REPLWrapper that gives incremental output
    specifically for bash_kernel.
    The parameters are the same as for REPLWrapper, except for one
    extra parameter:
    :param line_output_callback: a callback method to receive each batch
      of incremental output. It takes one string parameter.
    """
    def __init__(self, cmd_or_spawn, orig_prompt, prompt_change,
                 new_prompt='[PEXPECT_PROMPT>',
                 continuation_prompt='[PEXPECT_PROMPT+',
                 extra_init_cmd=None, line_output_callback=None):
        self.line_output_callback = line_output_callback
        replwrap.REPLWrapper.__init__(self, cmd_or_spawn, orig_prompt,
                                      prompt_change,
                                      extra_init_cmd=extra_init_cmd)

    def _expect_prompt(self, timeout=-1):
        if timeout is None:
            # "None" means we are executing code from a Jupyter cell by way of
            # the run_command in the do_execute() code below, so do
            # incremental output.
            while True:
                pos = self.child.expect_exact([self.prompt,
                                               self.continuation_prompt,
                                               '\r\n'],
                                              timeout=None)
                if pos == 2:
                    # End of line received
                    self.line_output_callback(self.child.before + '\n')
                else:
                    if len(self.child.before) != 0:
                        # prompt received, but partial line precedes it
                        self.line_output_callback(self.child.before)
                    break
        else:
            # Otherwise, use existing non-incremental code
            pos = replwrap.REPLWrapper._expect_prompt(self, timeout=timeout)

        # Prompt received, so return normally
        return pos


class PikeKernel(Kernel):
    implementation = 'pike_kernel'
    implementation_version = __version__

    @property
    def language_version(self):
        m = version_pat.search(self.banner)
        return m.group(1)

    _banner = None

    @property
    def banner(self):
        if self._banner is None:
            self._banner = check_output(['pike', '--version']).decode('utf-8')
        return self._banner

    language_info = {'name': 'pike',
                     'mimetype': 'text/x-pike',
                     'file_externsion': '.pike'}

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self._start_pike()

    def _start_pike(self):
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            child = pexpect.spawn("pike", echo=False, encoding='utf-8',
                                  env={'TERM': 'dumb'})
            self.pikewrapper = IREPLWrapper(
                child, '> ', None, new_prompt='> ', continuation_prompt='>> ',
                extra_init_cmd='set format sprintf "%s\\n"\n',
                line_output_callback=self.process_output)
        finally:
            signal.signal(signal.SIGINT, sig)

    def process_output(self, output):
        if not self.silent:
            # Send standard output
            stream_content = {'name': 'stdout', 'text': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        self.silent = silent
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}

        interrupted = False
        try:
            self.pikewrapper.run_command(code.rstrip(), timeout=None)
        except KeyboardInterrupt:
            self.pikewrapper.child.sendintr()
            interrupted = True
            self.pikewrapper._expect_prompt()
            output = self.pikewrapper.child.before
            self.process_output(output)
        except EOF:
            output = self.pikewrapper.child.before + 'Restarting Pike'
            self._start_pike()
            self.process_output(output)

        if interrupted:
            return {'status': 'abort', 'execution_count': self.execution_count}

        return {'status': 'ok', 'execution_count': self.execution_count,
                'payload': [], 'user_expressions': {}}
