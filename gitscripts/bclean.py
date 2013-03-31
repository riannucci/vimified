#!/usr/bin/env python
#git branch --merged master | awk '!/\\<master\\>/{print $NF}' | xargs git branch -d

import sys
import collections

from common import run_git, VERBOSE, CalledProcessError, abbrev

def main():
  all_branches = [x.split()[-1] for x in run_git('branch').splitlines()]
  merged_raw = run_git('branch', '--merged', 'master').splitlines()
  merged = [x.split()[-1] for x in merged_raw if 'master' not in x]
  if VERBOSE:
    print all_branches
    print merged

  upstreams = {}
  downstreams = collections.defaultdict(list)
  for branch in all_branches:
    try:
      remote = run_git('config', 'branch.%s.remote' % branch)
      if remote != '.':
        continue
      upstream = abbrev(run_git('config', 'branch.%s.merge' % branch))
      upstreams[branch] = upstream
      downstreams[upstream].append(branch)
    except CalledProcessError:
      pass

  if VERBOSE:
    print upstreams
    print downstreams

  for branch in merged:
    for down in downstreams[branch]:
      if down not in merged:
        run_git('branch', '--set-upstream-to', upstreams[branch], down)
        print ('Reparented %s to track %s (was tracking %s)'
               % (down, upstreams[branch], branch))
    print run_git('branch', '-d', branch)

  return 0


if __name__ == '__main__':
  sys.exit(main())
