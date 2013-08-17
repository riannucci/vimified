#!/usr/bin/env python

import collections
import functools
import multiprocessing
import optparse
import struct
import sys
import tempfile
import threading

from common import git_hash, run_git, git_intern_f, git_tree
from common import git_mktree, run_git_lines, CalledProcessError


BLOB = 'blob'
BLOB_MOD = '100644'
CHUNK_FMT = '!20sL'
CHUNK_SIZE = struct.calcsize(CHUNK_FMT)
DIRTY_TREES = collections.defaultdict(int)
REF = 'refs/number/commits'
ROOT_TREE = None
TREE = 'tree'
TREE_MOD = '040000'


hexlify = lambda s: s.decode('hex')
dehexlify = lambda s: s.encode('hex')


class StatusPrinter(threading.Thread):
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
    super(StatusPrinter, self).__init__()
    self.start()

  def _emit(self, s):
    if self.ENABLED:
      sys.stderr.write('\r'+s)
      sys.stderr.flush()

  def run(self):
    with self._dead_cond:
      while not self._dead:
        self._emit(self.fmt % self._count)
        self._dead_cond.wait(.5)
      self._emit((self.fmt+'\n') % self._count)

  def join(self, timeout=None):
    self._dead = True
    with self._dead_cond:
      self._dead_cond.notifyAll()
    if self.isAlive():
      super(StatusPrinter, self).join(timeout)

  def inc(self, amount=1):
    self._count += amount


def memoize(f):
  """Decorator to memoize a pure function taking 0 or more positional args."""
  cache = {}

  @functools.wraps(f)
  def inner(*args):
    ret = cache.get(args)
    if ret is None:
      ret = f(*args)
      if ret is not None:
        cache[args] = ret
    return ret
  inner.cache = cache

  return inner


@memoize
def get_root_elms():
  """Return a set() of all the subtree names in the root tree.

  If the root reference doesn't exist, create it with an empty tree.

  >>> get_root_elms()
  set(['\x83', '\x04', '\x87', '\x8b', '\x0c', ...])
  """
  ret = set()
  tree = git_tree(REF)
  if tree is None:
    ref = run_git('commit-tree',
                  '-m', 'Initial commit from git-number', git_mktree({}))
    run_git('update-ref', REF, ref)
  else:
    ret = set(map(hexlify, tree))
  return ret


@memoize
def get_par_elms(prefix_byte):
  """Return a set() of all the blob names in a given subtree of the root.

  >>> get_par_elms('\x83')
  set(['\xb4', '\xf3', ...])
  """
  if prefix_byte not in get_root_elms():
    return {}

  return set(map(hexlify, git_tree('%s:%02x' % (REF, ord(prefix_byte))) or {}))


@memoize
def get_num_tree(prefix_bytes):
  """Return a dictionary of the blob contents specified by |prefix_bytes|.
  This is in the form of {<full ref>: <gen num> ...}

  >>> get_num_tree('\x83\xb4')
  {'\x83\xb4\xe3\xe4W\xf9J*\x8f/c\x16\xecD\xd1\x04\x8b\xa9qz': 169, ...}
  """
  if prefix_bytes[-1:] not in get_par_elms(prefix_bytes[:-1]):
    return {}

  prefix_bytes = map(ord, prefix_bytes)
  ret = {}
  ref = '%s:%02x/%02x' % (REF, prefix_bytes[0], prefix_bytes[1])

  try:
    # TODO(iannucci): Avoid reading the whole file into memory
    raw = buffer(run_git('cat-file', 'blob', ref))

    for chunk_i in range(len(raw) / CHUNK_SIZE):
      ref, num = struct.unpack_from(CHUNK_FMT, raw, chunk_i*CHUNK_SIZE)
      ret[ref] = num
  except CalledProcessError:
    pass

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


def get_num(ref):
  """Takes a hash and returns the generation number for it or None."""
  return get_num_tree(ref[:2]).get(ref)


def set_num(ref, val):
  """Updates the global state such that the generation number for |ref|
  is |val|.

  This change will not be saved to the git repo until finalize() is called.
  """
  prefix = ref[:2]
  get_num_tree(prefix)[ref] = val
  DIRTY_TREES[prefix] += 1


def group_prefix(items):
  """Generator to group entries by prefix.

  Args:
    items - A iterable yielding data in the form of (name, value) sorted by
            |name|.

  |name| is expected to be a string of len >= 2.

  This generator will yield lists of (name, value) pairs such that all of the
  tuples in each emitted list wil share the same first 2 chars of |name|.
  """
  group = []
  prefix = None
  for name, value in items:
    cur_prefix = name[:2]
    if prefix != cur_prefix:
      if group:
        yield group
      group = []
      prefix = cur_prefix

    if prefix == cur_prefix:
      group.append((name, value))

  if group:
    yield group


def make_merged_tree(inc):
  pool = multiprocessing.Pool()
  tree_fmt = REF+':%s'

  def make_merged_tree_inner(group):
    """Takes a group of (name, value) pairs such that the first 2 chars of all
    the |name|s match (the 'prefix'), and value is a promise[blob hash]. The
    function then returns a (subdir, promise[tree hash]).

    The promised tree hash will be the merging of the existing tree at 'prefix',
    plus any new blobs introduced by the current run.
    """
    name, _ = group[0]
    ret_name = name[:2]

    tree = git_tree(tree_fmt % ret_name) or {}
    for name, val in group:
      tree[name[2:]] = (BLOB_MOD, BLOB, val.get())
      inc()

    ret = ret_name, pool.apply_async(git_mktree, (tree,))
    return ret
  return make_merged_tree_inner


def make_flat_file(inc):
  pool = multiprocessing.Pool()
  def make_flat_file_inner(prefix_count):
    """Takes a (prefix, count) where |prefix| is a 2 byte string designating a
    path to the flat-file blob (e.g. '\xab\xcd' -> 'ab/cd'), and |count| is the
    number of new hashes to be merged into said blob.

    Returns (dehexlify(|prefix|), promise[blob hash])
    """
    prefix, count = prefix_count
    t = get_num_tree(prefix)
    ret = dehexlify(prefix), pool.apply_async(intern_num_tree, (t,))
    inc(count)
    return ret
  return make_flat_file_inner


def finalize(target):
  """After calculating the generation number for |target|, call finalize to
  save all our work to the git repository.
  """
  if not DIRTY_TREES:
    return

  total = sum(DIRTY_TREES.itervalues())
  msg = 'git-number Added %s numbers' % total

  total += len(DIRTY_TREES)
  total += len(set(x[:1] for x in DIRTY_TREES))
  fmt = 'Finalizing: (%%d/%d)' % total

  status = StatusPrinter(fmt)

  try:
    files = map(make_flat_file(status.inc), sorted(DIRTY_TREES.iteritems()))
    trees = map(make_merged_tree(status.inc), group_prefix(files))

    tree = git_tree(REF) or {}
    for name, val in trees:
      tree[name] = (TREE_MOD, TREE, val.get())
      status.inc()

    new_head = run_git('commit-tree', '-m', msg, git_mktree(tree),
                       '-p', git_hash(REF), '-p', target)
    run_git('update-ref', REF, new_head)
  finally:
    status.join()


def resolve(target):
  """Return the generation number for target.

  As a side effect, record any new calculated data to the git repository.
  """
  num = get_num(target)
  if num is not None:
    return num

  rev_list = []

  load_status = StatusPrinter('Loading commits: %d')
  try:
    for line in run_git_lines('rev-list', '--topo-order', '--parents',
                              '--reverse', dehexlify(target), '^'+REF):
      rev_list.append(map(hexlify, line.split()))
      load_status.inc()
  finally:
    load_status.join()

  gen_status = StatusPrinter('Reticulating splines: (%%d/%d)' % len(rev_list))
  try:
    for toks in rev_list:
      num = max([-1]+map(get_num, toks[1:])) + 1
      set_num(toks[0], num)
      gen_status.inc()
  finally:
    gen_status.join()

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
  print resolve(parse_options())


if __name__ == '__main__':
  main()
