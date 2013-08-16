#!/usr/bin/env python

import sys

from common import git_hash, parents, run_git

NUM_CACHE = {}

def get_num(ref):
  ret = NUM_CACHE.get(ref)
  if ret is None:
    try:
      ret = int(run_git('notes', '--ref', 'number', 'show', ref))
      NUM_CACHE[ref] = ret
    except:  # pylint: disable=W0702
      return None
  return ret

def set_num(ref, val):
  NUM_CACHE[ref] = val
  return run_git('notes', '--ref', 'number', 'add',
                 '-f', '-m', str(int(val)), ref)


def get_gen_num(ref, pars=None):
  num = get_num(ref)
  if num is not None:
    return num
  if pars is None:
    pars = parents(ref)

  m_num = -1
  for par in pars:
    val = get_num(par)
    if val is None:
      return None
    if val > m_num:
      m_num = val
  new_num = m_num + 1
  set_num(ref, new_num)
  return new_num


def main():
  target = git_hash(sys.argv[1] if len(sys.argv) > 1 else 'HEAD')
  to_resolve = [target]

  while to_resolve:
    cur = to_resolve.pop()
    pars = parents(cur)
    gen_num = get_gen_num(cur, pars)
    if gen_num is None:
      to_resolve.append(cur)
      to_resolve.extend(pars)

  print gen_num

if __name__ == '__main__':
  main()
