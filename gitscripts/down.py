#!/usr/bin/env python
import sys

from common import current_branch, branches, upstream, run_git


def main(argv):
  assert len(argv) == 1, "No arguments expected"
  cur = current_branch()
  downstreams = [b for b in branches() if upstream(b) == cur]
  if not downstreams:
    return "No downstream branches"
  elif len(downstreams) == 1:
    run_git('checkout', downstreams[0])
  else:
    high = len(downstreams) - 1
    while True:
      print "Please select a downstream branch"
      for i, b in enumerate(downstreams):
        print "  %d. %s" % (i, b)
      r = raw_input("Selection (0-%d)[0]: " % high).strip() or '0'
      if not r.isdigit() or (0 > int(r) > high):
        print "Invalid choice."
      else:
        run_git('checkout', downstreams[int(r)])
        break


if __name__ == '__main__':
  sys.exit(main(sys.argv))