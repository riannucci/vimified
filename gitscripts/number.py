#!/usr/bin/env python

import collections
import functools
import multiprocessing
import struct
import sys
import tempfile
import threading

from common import git_hash, run_git, git_intern_f, git_tree
from common import git_mktree, run_git_lines, CalledProcessError

VERBOSE = False

class StatusPrinter(threading.Thread):
  def __init__(self, fmt=None, use_lock=False):
    self.fmt = fmt
    self._use_lock = use_lock
    self._lock = threading.Lock()
    self._count = 0
    self._dead = False
    self._dead_cond = threading.Condition()
    super(StatusPrinter, self).__init__()

  @staticmethod
  def _emit(s):
    if VERBOSE:
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
    if self._use_lock:
      with self._lock:
        self._count += amount
    else:
      self._count += amount

  @property
  def count(self):
    if self._use_lock:
      with self._lock:
        return self._count
    else:
      return self._count


DIRTY_TREES = collections.defaultdict(int)
NEW_NUM_COUNT = 0

BLOB_MOD = '100644'
BLOB = 'blob'
TREE_MOD = '040000'
TREE = 'tree'

REF = 'refs/number/commits'

def memoize(f):
  cache = {}

  @functools.wraps(f)
  def inner(arg):
    ret = cache.get(arg)
    if ret is None:
      ret = f(arg)
      if ret is not None:
        cache[arg] = ret
    return ret

  return inner

CHUNK_FMT = '!20sL'
CHUNK_SIZE = struct.calcsize(CHUNK_FMT)


ROOT_TREE = None
def get_root_elms():
  global ROOT_TREE
  if ROOT_TREE is None:
    tree = git_tree(REF)
    if tree is None:
      ref = run_git('commit-tree',
                    '-m', 'Initial commit from git-number', git_mktree({}))
      run_git('update-ref', REF, ref)
      ROOT_TREE = set()
    else:
      ROOT_TREE = set(map(hexlify, tree))
  return ROOT_TREE


@memoize
def get_par_elms(prefix_byte):
  if prefix_byte not in get_root_elms():
    return {}

  return set(map(hexlify, git_tree('%s:%02x' % (REF, ord(prefix_byte))) or {}))


@memoize
def get_num_tree(prefix_bytes):
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
  with tempfile.TemporaryFile() as f:
    for k, v in sorted(tree.iteritems()):
      f.write(struct.pack(CHUNK_FMT, k, v))
    f.seek(0)
    return git_intern_f(f)


def get_num(ref):
  return get_num_tree(ref[:2]).get(ref)


def hexlify(s):
  return s.decode('hex')


def dehexlify(s):
  return s.encode('hex')


def set_num(ref, val):
  prefix = ref[:2]
  get_num_tree(prefix)[ref] = val
  DIRTY_TREES[prefix] += 1


def group_prefix(items):
  group = []
  prefix = None
  for obj in items:
    name, value = obj
    cur_prefix = name[:-2]
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
    prefix, count = prefix_count
    t = get_num_tree(prefix)
    ret = prefix.encode('hex'), pool.apply_async(intern_num_tree, (t,))
    inc(count)
    return ret
  return make_flat_file_inner


def finalize(target):
  if not DIRTY_TREES:
    return

  total = sum(DIRTY_TREES.itervalues())
  msg = 'git-number Added %s numbers' % total

  total += len(DIRTY_TREES)
  total += len(set(x[:1] for x in DIRTY_TREES))
  fmt = 'Finalizing: (%%d/%d)' % total

  status = StatusPrinter(fmt, use_lock=True)
  status.start()

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


def gen_next_num(ref, *pars):
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


def get_gen_num(ref, *pars):
  num = get_num(ref)
  if num is not None:
    return num
  return gen_next_num(ref, *pars)


def resolve(target):
  load_status = StatusPrinter('Loading commits: %d')

  opts = ['rev-list', '--topo-order', '--parents', '--reverse',
          dehexlify(target), '^'+REF]

  rev_list = []
  try:
    load_status.start()
    for line in run_git_lines(*opts):
      rev_list.append(map(hexlify, line.split()))
      load_status.inc()
  finally:
    load_status.join()

  for toks in rev_list:
    num = get_gen_num(*toks)

  return num


def main():
  global VERBOSE
  try:
    sys.argv.remove('-v')
    VERBOSE = True
  except ValueError:
    pass

  target = hexlify(git_hash(sys.argv[1] if len(sys.argv) > 1 else 'HEAD'))

  # try get_num because maybe we can get lucky :)
  gen_num = get_num(target) or resolve(target)

  finalize(dehexlify(target))

  print gen_num

if __name__ == '__main__':
  main()
