#!/usr/bin/python
import subprocess
import sys


# Exception classes used by this module.
class CalledProcessError(Exception):
  def __init__(self, returncode, cmd, output=None, out_err=None):
    super(CalledProcessError).__init__(self)
    self.returncode = returncode
    self.cmd = cmd
    self.output = output
    self.out_err = out_err

  def __str__(self):
    return (
        'Command "%s" returned non-zero exit status %d' %
        (self.cmd, self.returncode))


def check_output(*popenargs, **kwargs):
  if 'stdout' in kwargs:
    raise ValueError('stdout argument not allowed, it will be overridden.')
  process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
  output, out_err = process.communicate()
  retcode = process.poll()
  if retcode:
    cmd = kwargs.get('args')
    if cmd is None:
      cmd = popenargs[0]
    raise CalledProcessError(retcode, cmd, output=output, out_err=out_err)
  return output


def run(cmd):
  if '--verbose' in sys.argv:
    print cmd
  return check_output(cmd).strip()


def main():
  orig_branch = run(('git', 'rev-parse', '--abbrev-ref', 'HEAD'))
  if orig_branch == 'HEAD':
    orig_branch = run(('git', 'rev-parse', 'HEAD'))
  run(('git', 'checkout', 'master'))
  branch_tree = {}
  for branch in [b for b in run(('git', 'branch')).split() if '*' not in b]:
    # only local branches
    try:
      remote = run(('git', 'config', 'branch.'+branch+'.remote'))
      if remote != '.':
        continue
    except CalledProcessError:
      continue

    try:
      parent = run(('git', 'config', 'branch.'+branch+'.merge'))
      parent = run(('git', 'rev-parse', '--abbrev-ref', parent))
    except CalledProcessError:
      parent = None
    branch_tree[branch] = parent

  # XXX There is a more efficient way to do this, but for now...
  while branch_tree:
    for branch in (b for b, p in branch_tree.items() if p not in branch_tree):
      run(('git', 'checkout', branch))
      try:
        run(('git', 'rebase'))
      except CalledProcessError as ex:
        print ex.output
        print ex.out_err
        raise
      del branch_tree[branch]

  run(('git', 'checkout', orig_branch))

  return 0


if __name__ == '__main__':
  sys.exit(main())
