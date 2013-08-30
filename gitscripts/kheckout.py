#!/usr/bin/env python

import multiprocessing
import os
import shutil
import sys

from common import parse_one_committish, dehexlify, git_tree, ScopedPool
from common import run_git, CalledProcessError, StatusPrinter, cat_blob


FMT = "Checked out %%d/%d files"
PROC_COUNT = multiprocessing.cpu_count()*2

def nuke_extras(all_files):
  for dirpath, dirnames, filenames in os.walk('.'):
    if dirpath.endswith('.git'):
      dirnames[:] = []
      continue
    elif dirpath != '' and '.git' in dirnames:
      dirnames[:] = []
      continue

    for path in (os.path.join(dirpath, f) for f in filenames):
      if path not in all_files:
        os.unlink(path)


def place_file(path, mode, ref):
  try:
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    if sys.platform.startswith('win'):
      flags |= os.O_BINARY
    fd = os.open(path, flags, mode)
    try:
      cat_blob(ref, fd)
    finally:
      os.close(fd)
  except CalledProcessError as e:
    print e, e.out_err
  except Exception as e:
    print e


def place_link(path, ref):
  if os.path.exists(path):
    os.unlink(path)
  os.symlink(run_git('cat-file', 'blob', ref), path)


def make_dir(path):
  if not os.path.exists(path):
    os.makedirs(path)


def fix_head(target):
  try:
    git_dir = run_git('rev-parse', '--git-dir')
    with open(os.path.join(git_dir, 'HEAD'), 'wb') as f:
      f.write(target)
  except CalledProcessError as e:
    print e, e.out_err


def handle_file(made_dirs, pool, inc, path, tup):
  mode, typ, ref = tup

  d = os.path.dirname(path)
  if d and d not in made_dirs:
    make_dir(d)
    made_dirs.add(d)

  if typ == 'blob' and mode[:3] == '100':
    pool.apply_async(place_file, (path, int(mode[-3:], 8), ref), callback=inc)
  elif typ == 'blob' and mode[:3] == '120':
    pool.apply_async(place_link, (path, ref), callback=inc)
  elif typ == 'commit':
    pool.apply_async(make_dir, (path,), callback=inc)
  else:
    print 'I do not understand "%s": %s, %s, %s' % (path, mode, typ, ref)


def kill_it(path):
  if os.path.exists(path):
    if os.path.isdir(path):
      shutil.rmtree(path)
    else:
      os.unlink(path)


def diff_checkout(tree):
  made_dirs = set()
  opts = ['--porcelain', '-z', '--ignore-submodules=dirty']
  f_diff = run_git('status', *opts).split('\0')
  total = (len(f_diff) - 1)
  fmt = FMT % total
  if not total:
    return

  with StatusPrinter(fmt) as inc:
    ign_inc = lambda *_: inc()
    with ScopedPool(PROC_COUNT) as pool:
      for mode, pathish in (x.split(None, 1) for x in f_diff if x):
        if mode[0] in 'DM':
          handle_file(made_dirs, pool, ign_inc, pathish, tree[pathish])
        elif mode[0] in 'A?':
          pool.apply_async(kill_it, (pathish,), callback=ign_inc)
        elif mode[0] in 'RC':
          frm, to = pathish.split('\0')
          pool.apply_async(kill_it, (frm,))
          pool.apply_async(handle_file, (to,), callback=ign_inc)
        else:
          print (
            "I do not understand WAT IS HAPPEN TO ME!? %s %s"
            % (mode, pathish)
          )


def force_checkout(tree):
  made_dirs = set()
  fmt = FMT % len(tree)
  with StatusPrinter(fmt) as inc:
    ign_inc = lambda *_: inc()
    with ScopedPool(PROC_COUNT) as pool:
      pool.apply_async(nuke_extras, (tree,), callback=ign_inc)

      for path, tup in tree.iteritems():
        handle_file(made_dirs, pool, ign_inc, path, tup)


def main():
  force = '-f' in sys.argv
  if force:
    sys.argv.remove('-f')

  StatusPrinter.ENABLED = True

  target = dehexlify(parse_one_committish())
  print 'Got Target: %s' % target
  fix_head(target)
  run_git('reset', '-q', target)
  tree = git_tree(target, recurse=True)

  if force:
    force_checkout(tree)
  else:
    diff_checkout(tree)


if __name__ == '__main__':
  sys.exit(main())
