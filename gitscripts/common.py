import subprocess
import sys

VERBOSE = '--verbose' in sys.argv

NO_BRANCH = '* (no branch)'

# Exception classes used by this module.
class CalledProcessError(Exception):
  def __init__(self, returncode, cmd, output=None, out_err=None):
    super(CalledProcessError, self).__init__()
    self.returncode = returncode
    self.cmd = cmd
    self.output = output
    self.out_err = out_err

  def __str__(self):
    return (
        'Command "%s" returned non-zero exit status %d' %
        (self.cmd, self.returncode))


def check_output(*popenargs, **kwargs):
  kwargs.setdefault('stdout', subprocess.PIPE)
  kwargs.setdefault('stderr', subprocess.PIPE)
  process = subprocess.Popen(*popenargs, **kwargs)
  output, out_err = process.communicate()
  retcode = process.poll()
  if retcode:
    cmd = kwargs.get('args')
    if cmd is None:
      cmd = popenargs[0]
    raise CalledProcessError(retcode, cmd, output=output, out_err=out_err)
  return output


def run_git(*cmd, **kwargs):
  cmd = ('git',) + cmd
  if VERBOSE:
    print cmd
  ret = check_output(cmd, **kwargs)
  ret = (ret or '').strip()
  return ret


def abbrev(ref):
  return run_git('rev-parse', '--abbrev-ref', ref)


def upstream(branch):
  try:
    return run_git('rev-parse', '--abbrev-ref', '--symbolic-full-name',
                   branch+'@{upstream}')
  except CalledProcessError:
    return None


def branches(*args):
  for line in run_git('branch', *args).splitlines():
    if line == NO_BRANCH:
      continue
    yield line.split()[-1]
