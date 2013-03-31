#!/usr/bin/python
import subprocess
import sys

from pprint import pprint
from common import CalledProcessError, run_git, VERBOSE, abbrev

def clean_refs():
  tags = [t.strip() for t in run_git('tag', '-l', 'reup.*').split()]
  run_git('tag', '-d', *tags)


def main():
  if '--clean' in sys.argv:
    clean_refs()
    return 0

  orig_branch = abbrev('HEAD')
  if orig_branch == 'HEAD':
    orig_branch = run_git('rev-parse', 'HEAD')
  run_git('checkout', 'master')
  branch_tree = {}
  for branch in [b for b in run_git('branch').split() if '*' not in b]:
    # only local branches
    try:
      remote = run_git('config', 'branch.'+branch+'.remote')
      if remote != '.':
        continue
    except CalledProcessError:
      continue

    try:
      parent = run_git('config', 'branch.'+branch+'.merge')
      parent = abbrev(parent)
    except CalledProcessError:
      parent = None
    branch_tree[branch] = parent

  starting_refs = {}
  for branch, parent in branch_tree.iteritems():
    tag = "reup.merge_base_for_%s" % run_git('rev-parse', branch)
    tagval = None
    try:
      tagval = run_git('rev-parse', tag, stderr=subprocess.PIPE)
      print 'Found previous merge-base for %s: %s' % (branch, tagval)
    except CalledProcessError:
      pass
    if not tagval:
      run_git('tag', '-m', tag, tag, run_git('merge-base', parent, branch))
      tagval = run_git('rev-parse', tag)
    starting_refs[branch] = tagval

  if VERBOSE:
    pprint(branch_tree)
    pprint(starting_refs)

  # XXX There is a more efficient way to do this, but for now...
  while branch_tree:
    this_pass = [i for i in branch_tree.items() if i[1] not in branch_tree]
    for branch, parent in this_pass:
      try:
        run_git('rebase', '--onto', parent, starting_refs[branch], branch)
      except CalledProcessError as ex:
        print ex.output
        print ex.out_err
        raise
      del branch_tree[branch]

  clean_refs()

  run_git('checkout', orig_branch)

  return 0


if __name__ == '__main__':
  sys.exit(main())
