#!/usr/bin/python
import subprocess
import sys


def check_output(*popenargs, **kwargs):
  if 'stdout' in kwargs:
    raise ValueError('stdout argument not allowed, it will be overridden.')
  process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
  output, unused_err = process.communicate()
  retcode = process.poll()
  if retcode:
    cmd = kwargs.get('args')
    if cmd is None:
      cmd = popenargs[0]
    raise subprocess.CalledProcessError(retcode, cmd, output=output)
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
    except subprocess.CalledProcessError:
      continue

    try:
      parent = run(('git', 'config', 'branch.'+branch+'.merge'))
      parent = run(('git', 'rev-parse', '--abbrev-ref', parent))
    except subprocess.CalledProcessError:
      parent = None
    branch_tree[branch] = parent

  # XXX There is a more efficient way to do this, but for now...
  while branch_tree:
    for branch in (b for b, p in branch_tree.items() if p not in branch_tree):
      run(('git', 'checkout', branch))
      run(('git', 'rebase'))
      del branch_tree[branch]

  run(('git', 'checkout', orig_branch))

  return 0


if __name__ == '__main__':
  sys.exit(main())
