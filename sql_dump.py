#!/usr/bin/env python
'''
Order of columns in tabular dumps is provided as namedtuples below
'''

import re
import os
import os.path
import sys
from collections import namedtuple
from optparse import OptionParser

Page = namedtuple('Page', [
  'id',
  'namespace',
  'title',
  'restrictions',
  'counter',
  'is_redirect',
  'is_new',
  'random',
  'touched',
  'latest',
  'len'
])

Revision = namedtuple('Revision', [
  'id',
  'page',
  'text_id',
  'comment',
  'user',
  'user_text',
  'timestamp',
  'minor_edit',
  'deleted',
  'len',
  'parent_id'
])

Text = namedtuple('Text', [
  'id',
  'text',
  'flags'
])

class TabularWriter(object):
  '''
  Article writer will produce tabular dumps of page, revision, comment in the CSV style.
  '''
  def __init__(self, basedir=None, delimiter="\t"):
    self.delimiter = delimiter
    self.base = basedir
    if not self.base:
      self.base = "text_sqldata"
    if not os.path.exists(self.base):
      os.makedirs(self.base)

    self.write_loader()

  def write_loader(self):
    '''
    A short .mysql script will efficiently load records from tabular
    files into a mediawiki database.
    '''
    loader = open(os.path.join(self.base, "import.sql"), "w+")
    tables = { 'text': 'old', 'revision': 'rev', 'page': 'page' }
    for table, mapping in tables.items():
      container_class = globals()[table.capitalize()]
      source = os.path.abspath(os.path.join(self.base, table+".dmp"))
      columns = [mapping+"_"+field for field in container_class._fields]

      loader.write("""
          LOAD DATA INFILE "%s"
            REPLACE
              INTO TABLE %s
              FIELDS TERMINATED BY '%s'
            (%s);\n
      """ % (source, self.delimiter, table, ', '.join(columns)))

      dumpfile = open(source, 'w+')
      setattr(self, table+"s", dumpfile) 

  def escape(self, text):
    def tr(match):
      if match.group(0) == "\t":
        return "\\t"
      if match.group(0) == "\n":
        return "\\n"

    if isinstance(text, str) or isinstance(text, unicode):
      return re.sub("(\t|\n)", tr, text).encode("utf_8")
    elif isinstance(text, list) or isinstance(text, tuple):
      return [self.escape(e) for e in text]
    else:
      return repr(text)

  def format_line(self, seq):
    return self.delimiter.join(self.escape(seq))+"\n"
    
  def write_article(self, article):
    self.texts.write(self.format_line(article.text))
    self.revisions.write(self.format_line(article.revision))
    self.pages.write(self.format_line(article.page))


if __name__ == "__main__":
  op = OptionParser()
  op.add_option("-d", "--dir", dest="base_dir",
    help="base directory for output files")
  op.add_option("-f", "--force", dest="force", action="store_true",
    help="ignore processing errors")
  op.add_option("-s", "--skip", dest="skip", type="int",
    help="skip over this many articles before begining import")
  #op.add_option("--import", dest="do_sql", action="store_true",
  #  help="run sql import script when finished with dump")
  #op.add_option("--no-import", dest="do_sql", action="store_false",
  #  help="stop after dump, do not import sql")
  #op.add_option("--ignore-existing", dest="replace", action="store_false",
  #  help="no not overwrite existing data")
  #op.add_option("--replace-existing", dest="replace", action="store_true",
  #  help="generated sql statements will overwrite existing data")
  options, args = op.parse_args()

  if len(args) > 1:
    print "too many input file arguments provided: "+" ".join(args)
    sys.exit(-1)
  elif len(args) == 0 or args[0] == '-':
    f = sys.stdin
  else:
    f = open(args[0])

  output = TabularWriter(basedir=options.base_dir)
  p = DumpParser(input=f, force=options.force, skip=options.skip)

  p.parse()
