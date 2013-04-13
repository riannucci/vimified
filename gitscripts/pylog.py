#!/usr/bin/env python
import sys

from common import current_branch, branches, tags

def main():
  BRIGHT = '\x1b[1m'
  CYAN = '\x1b[36m'
  GREEN = '\x1b[32m'
  MAGENTA = '\x1b[35m'
  RED = '\x1b[31m'
  RESET = '\x1b[m'
  current = current_branch()
  all_branches = set(branches())
  if current in all_branches:
    all_branches.remove(current)
  all_tags = set(tags())
  try:
    for line in sys.stdin.readlines():
      start = line.find(GREEN+' (')
      end   = line.find(')', start)
      if start != -1 and end != -1:
        start += len(GREEN) + 2
        branch_list = line[start:end].split(', ')
        if branch_list:
          colored_branches = []
          for b in branch_list:
            if b == current:
              colored_branches.append(CYAN+BRIGHT+b+RESET)
              current = None
            elif b in all_branches:
              colored_branches.append(GREEN+BRIGHT+b+RESET)
              all_branches.remove(b)
            elif b in all_tags:
              colored_branches.append(MAGENTA+BRIGHT+b+RESET)
              all_tags.remove(b)
            else:
              colored_branches.append(RED+b)
          line = "%s%s%s" % (line[:start],
                              (GREEN+", ").join(colored_branches)+GREEN,
                              line[end:])
      sys.stdout.write(line)

  except KeyboardInterrupt:
    pass
  except IOError:
    pass
  return 0


if __name__ == '__main__':
  sys.exit(main())
