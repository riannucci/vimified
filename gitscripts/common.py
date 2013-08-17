import subprocess
import sys
import tempfile

VERBOSE = '--verbose' in sys.argv
if VERBOSE:
  sys.argv.remove('--verbose')

NO_BRANCH = ('* (no branch)', '* (detached from ')

# Exception classes used by this module.
class CalledProcessError(Exception):
  def __init__(self, returncode, cmd, output=None, out_err=None):
    super(CalledProcessError, self).__init__()
    self.returncode = returncode
    self.cmd = cmd
    self.output = output
    self.out_err = out_err

  def __str__(self):
    return (
        'Command "%s" returned non-zero exit status %d' %
        (self.cmd, self.returncode))


def check_output(*popenargs, **kwargs):
  kwargs.setdefault('stdout', subprocess.PIPE)
  kwargs.setdefault('stderr', subprocess.PIPE)
  indata = kwargs.pop('indata', None)
  if indata is not None:
    kwargs['stdin'] = subprocess.PIPE
  process = subprocess.Popen(*popenargs, **kwargs)
  output, out_err = process.communicate(indata)
  retcode = process.poll()
  if retcode:
    cmd = kwargs.get('args')
    if cmd is None:
      cmd = popenargs[0]
    raise CalledProcessError(retcode, cmd, output=output, out_err=out_err)
  return output


def yield_stdout(*popenargs, **kwargs):
  with tempfile.TemporaryFile() as err_file:
    kwargs['stdout'] = subprocess.PIPE
    kwargs['stderr'] = err_file
    kwargs['stdin'] = subprocess.PIPE

    process = subprocess.Popen(*popenargs, **kwargs)
    process.stdin.close()

    l = ' '
    while l:
      l = process.stdout.readline()
      if not l:
        break
      yield l.strip()

    retcode = process.wait()

    err_file.seek(0)
    out_err = err_file.read()

  if retcode:
    cmd = kwargs.get('args')
    if cmd is None:
      cmd = popenargs[0]
    raise CalledProcessError(retcode, cmd, out_err=out_err)


def run_git_lines(*cmd, **kwargs):
  cmd = ('git',) + cmd
  if VERBOSE:
    print cmd
  return yield_stdout(cmd, **kwargs)


def run_git(*cmd, **kwargs):
  cmd = ('git',) + cmd
  if VERBOSE:
    print cmd
  ret = check_output(cmd, **kwargs)
  ret = (ret or '').strip()
  return ret


def abbrev(ref):
  return run_git('rev-parse', '--abbrev-ref', ref)


def git_hash(reflike):
  return run_git('rev-parse', reflike)


def git_intern_f(f, kind='blob'):
  ret = run_git('hash-object', '-t', kind, '-w', '--stdin', stdin=f)
  f.close()
  return ret


def git_tree(treeish):
  ret = {}
  try:
    for line in run_git('ls-tree', '-z', '--full-tree', treeish).split('\0'):
      if not line:
        continue
      mode, typ, ref, name = line.split()
      ret[name] = (mode, typ, ref)
  except CalledProcessError:
    pass
  return ret


def git_mktree(treedict):
  """
  Args:
    treedict - { name: (mode, type, ref) }
  """
  with tempfile.TemporaryFile() as f:
    for name, (mode, typ, ref) in treedict.iteritems():
      f.write('%s %s %s\t%s\0' % (mode, typ, ref, name))
    f.seek(0)
    return run_git('mktree', '-z', stdin=f)


def parents(ref):
  return run_git('rev-parse', '%s^@' % ref).splitlines()


def upstream(branch):
  try:
    return run_git('rev-parse', '--abbrev-ref', '--symbolic-full-name',
                   branch+'@{upstream}')
  except CalledProcessError:
    return None


def branches(*args):
  for line in run_git('branch', *args).splitlines():
    if line.startswith(NO_BRANCH):
      continue
    yield line.split()[-1]


def tags(*args):
  for line in run_git('tag', *args).splitlines():
    if line.startswith(NO_BRANCH):
      continue
    yield line.split()[-1]


def current_branch():
  return abbrev('HEAD')


def clean_refs():
  run_git('tag', '-d',
          *[t.strip() for t in run_git('tag', '-l', 'gitscripts.*').split()])


MERGE_BASE_TAG_FMT = "gitscripts.merge_base_for_%s"


def manual_merge_base_tag(branch, base):
  tag = "gitscripts.merge_base_for_%s" % git_hash(branch)
  run_git('tag', '-f', '-m', tag, tag, git_hash(base))


def nuke_merge_base_tag(branch):
  tag = "gitscripts.merge_base_for_%s" % git_hash(branch)
  run_git('tag', '-d', tag)


def get_or_create_merge_base_tag(branch, parent):
  tag = MERGE_BASE_TAG_FMT % git_hash(branch)
  tagval = None
  try:
    tagval = git_hash(tag)
    if VERBOSE:
      print 'Found tagged merge-base for %s: %s' % (branch, tagval)
  except CalledProcessError:
    pass
  if not tagval:
    run_git('tag', '-m', tag, tag, run_git('merge-base', parent, branch))
    tagval = git_hash(tag)
  return tagval+'^{}'  # this lets rev-parse know this is actually a tag
