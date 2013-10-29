#!/usr/bin/env python
import collections
import sys

from colorama import Fore, Style

from common import current_branch, branches, upstream, git_hash


def print_branch(cur, cur_hash, branch, par_map, branch_map, depth=0):
  branch_hash = git_hash(branch)
  if branch.startswith('origin'):
    color = Fore.RED
  elif branch_hash == cur_hash:
    color = Fore.CYAN
  else:
    color = Fore.GREEN

  if branch_hash == cur_hash:
    color += Style.BRIGHT
  else:
    color += Style.NORMAL

  print color + "  "*depth + branch + (" *" if branch == cur else "")
  for child in par_map.pop(branch, ()):
    print_branch(cur, cur_hash, child, par_map, branch_map, depth=depth+1)


def main(argv):
  assert len(argv) == 1, "No arguments expected"
  branch_map = {}
  par_map = collections.defaultdict(list)
  for branch in branches():
    par = upstream(branch)
    branch_map[branch] = par
    par_map[par].append(branch)

  current = current_branch()
  current_hash = git_hash(current)
  while par_map:
    for parent in par_map:
      if parent not in branch_map:
        print_branch(current, current_hash, parent, par_map, branch_map)
        break


if __name__ == '__main__':
  sys.exit(main(sys.argv))
