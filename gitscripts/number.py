#!/usr/bin/env python

import sys
import os
import shutil
import itertools

from common import git_hash, parents, run_git
from common import CalledProcessError

NUM_CACHE = {}
NEW_NUMS = {}

REF = 'refs/notes/number'

def get_num(ref):
  ret = NUM_CACHE.get(ref)
  if ret is None:
    try:
      ret = int(run_git('notes', '--ref', REF, 'show', ref))
      NUM_CACHE[ref] = ret
    except CalledProcessError:
      return None
  return ret


def set_num(ref, val):
  NUM_CACHE[ref] = val
  NEW_NUMS[ref] = val


def finalize():
  if not NEW_NUMS:
    return

  git_dir = run_git('rev-parse', '--git-dir')
  HEAD_FILE = os.path.join(git_dir, 'HEAD')

  with open(HEAD_FILE, 'rb') as f:
    HEAD = f.read()

  worktree = os.path.abspath(os.path.join(git_dir, 'NUMBER_WORKTREE'))
  index = os.path.abspath(os.path.join(git_dir, 'NUMBER_INDEX'))
  if os.path.exists(worktree):
    shutil.rmtree(worktree)
  if os.path.exists(index):
    os.unlink(index)
  os.mkdir(worktree)

  env = {
    'GIT_WORK_TREE': worktree,
    'GIT_INDEX_FILE': index
  }

  try:
    try:
      run_git('checkout', '-f', REF, env=env, cwd=worktree)
    except CalledProcessError:
      pass
    with open(HEAD_FILE, 'wb') as f:
      f.write('ref: %s\n' % REF)

    for ref, val in NEW_NUMS.iteritems():
      d = os.path.join(worktree, ref[:2])
      if not os.path.exists(d):
        os.makedirs(d)
      with open(os.path.join(d, ref[2:]), 'wb') as f:
        f.write('%s\n' % val)
    run_git('add', '--all', env=env, cwd=worktree)
    run_git('commit', '-m', 'git-number Added %s numbers' % len(NEW_NUMS),
            env=env, cwd=worktree)
    shutil.rmtree(worktree)
    os.unlink(index)
  finally:
    with open(HEAD_FILE, 'wb') as f:
      f.write(HEAD)


def gen_next_num(ref, pars=None):
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


def get_gen_num(ref, pars=None):
  num = get_num(ref)
  if num is not None:
    return num
  if pars is None:
    pars = parents(ref)

  return gen_next_num(ref, pars)


def dumb_resolve(target, limit=1000):
  to_resolve = [target]

  while to_resolve:
    cur = to_resolve.pop()
    pars = parents(cur)
    gen_num = get_gen_num(cur, pars)
    if gen_num is None:
      to_resolve.append(cur)
      to_resolve.extend(reversed(pars))
    if len(to_resolve) > limit:
      return

  return gen_num


def bisect_resolve(target):
  # rev_list[0]: target
  # rev_list[-1]: root commit
  rev_list = run_git('rev-list', '--topo-order', '--parents',
                     target).splitlines()

  hi = len(rev_list)
  lo = 0
  best = hi
  while hi >= lo:
    idx = ((hi - lo) / 2) + lo
    candidate = rev_list[idx]
    toks = candidate.split()
    num = get_gen_num(toks[0], toks[1:])
    if num is None:
      lo = idx + 1
    else:
      best = idx
      hi = idx - 1

  if best == 0:
    return get_gen_num(target)

  best_to_target = itertools.islice(reversed(rev_list), len(rev_list)-best,
                                    len(rev_list))
  for h in best_to_target:
    toks = h.split()
    num = gen_next_num(toks[0], toks[1:])
    assert num is not None

  return num


def main():
  target = git_hash(sys.argv[1] if len(sys.argv) > 1 else 'HEAD')

  gen_num = dumb_resolve(target)
  if gen_num is None:
    gen_num = bisect_resolve(target)

  finalize()

  print gen_num

if __name__ == '__main__':
  main()
