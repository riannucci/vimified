#!/usr/bin/env python

# Monkeypatch IMapIterator so that Ctrl-C can kill everything properly.
# Derived from https://gist.github.com/aljungberg/626518
import multiprocessing.pool
from multiprocessing.pool import IMapIterator
def wrapper(func):
  def wrap(self, timeout=None):
    return func(self, timeout=timeout or 1e100)
  return wrap
IMapIterator.next = wrapper(IMapIterator.next)
IMapIterator.__next__ = IMapIterator.next

import collections
import contextlib
import functools
import optparse
import os
import signal
import struct
import subprocess
import sys
import tempfile
import threading

from common import git_hash, run_git, git_intern_f, git_tree
from common import git_mktree, CalledProcessError


CHUNK_FMT = '!20sL'
CHUNK_SIZE = struct.calcsize(CHUNK_FMT)
DIRTY_TREES = collections.defaultdict(int)
REF = 'refs/number/commits'
PREFIX_LEN = 1


hexlify = lambda s: s.decode('hex')
dehexlify = lambda s: s.encode('hex')
pathlify = lambda s: '/'.join('%02x' % ord(b) for b in s)


@contextlib.contextmanager
def ScopedPool(*args, **kwargs):
  kwargs['initializer'] = signal.signal
  kwargs['initargs'] = (signal.SIGINT, signal.SIG_IGN)
  pool = multiprocessing.pool.Pool(*args, **kwargs)
  try:
    yield pool
    pool.close()
  finally:
    pool.terminate()
    pool.join()


class StatusPrinter(object):
  """Threaded single-stat status message printer."""
  ENABLED = False

  def __init__(self, fmt):
    """
    Create a StatusPrinter.

    Call .start() to get it going.

    Args:
      fmt - String format with a single '%d' where the counter value should go.
    """
    self.fmt = fmt
    self._count = 0
    self._dead = False
    self._dead_cond = threading.Condition()
    self._thread = threading.Thread(target=self._run)

  def _emit(self, s):
    if self.ENABLED:
      sys.stderr.write('\r'+s)
      sys.stderr.flush()

  def _run(self):
    with self._dead_cond:
      while not self._dead:
        self._emit(self.fmt % self._count)
        self._dead_cond.wait(.5)
      self._emit((self.fmt+'\n') % self._count)

  def inc(self, amount=1):
    self._count += amount

  def __enter__(self):
    self._thread.start()
    return self.inc

  def __exit__(self, _exc_type, _exc_value, _traceback):
    self._dead = True
    with self._dead_cond:
      self._dead_cond.notifyAll()
    self._thread.join()
    del self._thread


def memoize_deco(default=None):
  def memoize_(f):
    """Decorator to memoize a pure function taking 0 or more positional args."""
    cache = {}

    @functools.wraps(f)
    def inner(*args):
      ret = cache.get(args)
      if ret is None:
        if default and inner.default_enabled:
          ret = default()
          cache[args] = ret
        else:
          ret = f(*args)
          if ret is not None:
            cache[args] = ret
      return ret
    inner.cache = cache
    inner.default_enabled = False

    return inner
  return memoize_


@memoize_deco(dict)
def get_num_tree(prefix_bytes):
  """Return a dictionary of the blob contents specified by |prefix_bytes|.
  This is in the form of {<full ref>: <gen num> ...}

  >>> get_num_tree('\x83\xb4')
  {'\x83\xb4\xe3\xe4W\xf9J*\x8f/c\x16\xecD\xd1\x04\x8b\xa9qz': 169, ...}
  """
  ret = {}
  ref = '%s:%s' % (REF, pathlify(prefix_bytes))

  p = subprocess.Popen(['git', 'cat-file', 'blob', ref],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  p.stderr.close()
  raw = buffer(p.stdout.read())
  for i in xrange(len(raw) / CHUNK_SIZE):
    ref, num = struct.unpack_from(CHUNK_FMT, raw, i * CHUNK_SIZE)
    ret[ref] = num

  return ret


def intern_num_tree(tree):
  """Transform a number tree (in the form returned by |get_num_tree|) into a
  git blob.

  Returns the git blob hash.

  >>> d = {'\x83\xb4\xe3\xe4W\xf9J*\x8f/c\x16\xecD\xd1\x04\x8b\xa9qz': 169}
  >>> intern_num_tree(d)
  'c552317aa95ca8c3f6aae3357a4be299fbcb25ce'
  """
  with tempfile.TemporaryFile() as f:
    for k, v in sorted(tree.iteritems()):
      f.write(struct.pack(CHUNK_FMT, k, v))
    f.seek(0)
    return git_intern_f(f)


@memoize_deco()
def get_num(ref):
  """Takes a hash and returns the generation number for it or None."""
  return get_num_tree(ref[:PREFIX_LEN]).get(ref)


def set_num(ref, val):
  """Updates the global state such that the generation number for |ref|
  is |val|.

  This change will not be saved to the git repo until finalize() is called.
  """
  prefix = ref[:PREFIX_LEN]
  get_num_tree(prefix)[ref] = val
  DIRTY_TREES[prefix] += 1
  get_num.cache[ref,] = val
  return val


UPDATE_IDX_FMT = '100644 blob %s\t%s\0'
def leaf_map_fn(prefix_tree):
  pre, tree = prefix_tree
  return UPDATE_IDX_FMT % (intern_num_tree(tree), pathlify(pre))


def finalize(target):
  """After calculating the generation number for |target|, call finalize to
  save all our work to the git repository.
  """
  if not DIRTY_TREES:
    return

  msg = 'git-number Added %s numbers' % sum(DIRTY_TREES.itervalues())


  idx = os.path.join(run_git('rev-parse', '--git-dir'), 'number.idx')
  env = {'GIT_INDEX_FILE': idx}

  with StatusPrinter('Finalizing: (%%d/%d)' % len(DIRTY_TREES)) as inc:
    run_git('read-tree', REF, env=env)

    prefixes_trees = ((p, get_num_tree(p)) for p in sorted(DIRTY_TREES))
    updater = subprocess.Popen(['git', 'update-index', '-z', '--index-info'],
                               stdin=subprocess.PIPE, env=env)

    with ScopedPool() as leaf_pool:
      for item in leaf_pool.imap(leaf_map_fn, prefixes_trees):
        updater.stdin.write(item)
        inc()

    updater.stdin.close()
    updater.wait()

    run_git('update-ref', REF,
            run_git('commit-tree', '-m', msg,
                    '-p', git_hash(REF), '-p', target,
                    run_git('write-tree', env=env)))


def preload_tree(prefix):
  return prefix, get_num_tree(prefix)


def resolve(target):
  """Return the generation number for target.

  As a side effect, record any new calculated data to the git repository.
  """
  num = get_num(target)
  if num is not None:
    return num

  if git_tree(REF) is None:
    empty = git_mktree({})
    ref = run_git('commit-tree', '-m', 'Initial commit from git-number', empty)
    run_git('update-ref', REF, ref)

  with ScopedPool() as pool:
    available = pool.apply_async(git_tree, args=(REF,), kwds={'recurse': True})
    preload = set()
    rev_list = []

    with StatusPrinter('Loading commits: %d') as inc:
      for line in run_git('rev-list', '--topo-order', '--parents',
                         '--reverse', dehexlify(target), '^'+REF).splitlines():
        toks = map(hexlify, line.split())
        rev_list.append((toks[0], toks[1:]))
        preload.update(t[:PREFIX_LEN] for t in toks)
        inc()

    preload.intersection_update(
      hexlify(k.replace('/', ''))
      for k in available.get().iterkeys()
    )
    preload.difference_update((x,) for x in get_num_tree.cache)

    if preload:
      preload_iter = pool.imap_unordered(preload_tree, preload)
      with StatusPrinter('Preloading nurbs: (%%d/%d)' % len(preload)) as inc:
        for prefix, tree in preload_iter:
          get_num_tree.cache[prefix,] = tree
          inc()

  get_num_tree.default_enabled = True


  for ref, pars in rev_list:
    num = set_num(ref, max(map(get_num, pars)) + 1 if pars else 0)

  finalize(dehexlify(target))

  return num


def parse_options():
  p = optparse.OptionParser(usage='%prog [options] [<committish>]')
  p.add_option('-v', '--verbose', action='store_true')
  opts, args = p.parse_args()

  StatusPrinter.ENABLED = opts.verbose

  if len(args) > 1:
    p.error('May only specify one <committish> at a time.')

  target = args[0] if args else 'HEAD'

  try:
    return hexlify(git_hash(target))
  except CalledProcessError:
    p.error("%r does not seem to be a valid commitish." % target)


def main():
  try:
    print resolve(parse_options())
  except KeyboardInterrupt:
    pass


if __name__ == '__main__':
  main()
