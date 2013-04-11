#!/usr/bin/python
import sys

from pprint import pprint

from bclean import bclean
from squash import squash
from common import CalledProcessError, run_git, VERBOSE, upstream
from common import branches, current_branch, get_or_create_merge_base_tag
from common import clean_refs, git_hash

def main():
  if '--clean' in sys.argv:
    clean_refs()
    return 0

  orig_branch = current_branch()
  if orig_branch == 'HEAD':
    orig_branch = git_hash('HEAD')

  run_git('fetch', 'origin', stderr=None)
  branch_tree = {}
  for branch in branches():
    parent = upstream(branch)
    if not parent:
      print 'Skipping %s: No upstream specified' % branch
      continue
    branch_tree[branch] = parent

  starting_refs = {}
  for branch, parent in branch_tree.iteritems():
    starting_refs[branch] = get_or_create_merge_base_tag(branch, parent)

  if VERBOSE:
    pprint(branch_tree)
    pprint(starting_refs)

  # XXX There is a more efficient way to do this, but for now...
  while branch_tree:
    this_pass = [i for i in branch_tree.items() if i[1] not in branch_tree]
    for branch, parent in this_pass:
      if git_hash(parent) != git_hash(starting_refs[branch]):
        print 'Rebasing:', branch
        try:
          run_git('rebase', '--onto', parent, starting_refs[branch], branch)
        except CalledProcessError:
          print "Failed! Attempting to squash", branch, "...",
          squash_branch = branch+"_squash_attempt"
          run_git('rebase', '--abort')
          run_git('checkout', '-b', squash_branch)
          squash()
          try:
            run_git('rebase', '--onto', parent, starting_refs[branch],
                    squash_branch)
            print 'Success!!'
          except CalledProcessError:
            run_git('rebase', '--abort')
            print 'Failure :('
            return 1
          finally:
            run_git('checkout', branch)
            run_git('branch', '-D', squash_branch)
          squash()
          run_git('rebase', '--onto', parent, starting_refs[branch], branch)
      del branch_tree[branch]

  clean_refs()

  bclean()

  if orig_branch in branches():
    run_git('checkout', orig_branch)

  return 0


if __name__ == '__main__':
  sys.exit(main())
