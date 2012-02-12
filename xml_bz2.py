'''
Parse .xml.bz2 dumps
'''

import re
import random
from lxml import etree
from datetime import datetime

class DumpParser(object):
  '''
  parse methods are named after element tag, building up the class instance member self.article
  '''

  xmlns = '{http://www.mediawiki.org/xml/export-0.5/}'

  class ParsedArticle(object):
    '''
    Just an empty object container
    '''
    def __init__(self):
      pass

  class Element(object):
    '''
    Convenience around ElementTree, mostly to hide xml namespace
    '''
    def __init__(self, element):
      self.element = element

    def text(self, tag, default='NULL'):
      return self.element.findtext(xmlns+tag, default)

    def attr(self, tag, default='NULL'):
      return self.element.get(xmlns+tag, default)

    def child(self, tag):
      children = self.element.iterchildren(tag=xmlns+tag)
      try:
        return Element(element=children.next())
      except:
        pass

    def contents(self):
      return self.element.text


  def __init__(self, input, output):
    '''
    If input is blank or "-", use stdin.
    '''
    if not input or input == "-":
      self.input = sys.stdin
    else:
      self.input = input
    self.output = output

  def parse(self):
    '''
    loop over the dump stream and process after every end page tag
    '''

    #TODO we would have to listen to tag start events,
    # but in order to compare file format version
    for _, element in etree.iterparse(source=self.input, events=("start-ns","start")):
      if tag == 'mediawiki':
        assert Element(element).attr('xmlns') != xmlns, "Unrecognized file schema"
      else:
        break

    for _, element in etree.iterparse(source=self.input, tag=xmlns+'page'):
      article = self.page(element=Element(element))
      self.output.write(article)

      element.clear()

  #def parse_element(element):
  #    tag = element.tag.split(xmlns).pop()
  #    method = getattr(DumpParser, tag, None)
  #    if method:
  #      return method(self, element=Element(element))

  def page(self, element):
    self.article = ParsedArticle()

    self.article.page_id=element.text('id')
    self.revision(element.child('revision'))

    title = element.text('title')
    if ':' in title:
      namespace, title = title.split(':', 1)
    else:
      namespace = 'Main'

    #XXX startswith ?
    if re.match("#redirect", self.article.text.text, re.I):
      redirect = 1
    else:
      redirect = 0

    touched = datetime.now().strftime("%Y%m%d%H%M%S") # mysql timestamp

    self.article.page = Page(
      id=self.article.page_id,
      namespace=namespace,
      title=title,
      restrictions=element.text('restrictions', 0),
      counter=0,
      is_redirect=redirect, #XXX
      is_new=0,
      random=random.randint(0, 4000000000),
      touched=touched,
      latest=self.article.revision.id,
      len=self.article.text_len
    )
    return self.article

  def revision(self, element):
    self.article.revision_id = element.text('id')
    self.text(element.child('text'))
    self.contributor(element.child('contributor'))
    self.comment(element.child('comment'))

    parsed_time = datetime.strptime(element.text('timestamp'), "%Y-%m-%dT%H:%M:%SZ")
    timestamp = parsed_time.strftime("%Y%m%d%H%M%S") # mysql timestamp

    self.article.revision = Revision(
      id=self.article.revision_id,
      page=self.article.page_id,
      text_id=self.article.text.id,
      comment=self.article.comment,
      user=self.article.contrib_id,
      user_text=self.article.contrib_user,
      timestamp=timestamp,
      minor_edit=element.text('minor', 0),
      deleted=0,
      len=self.article.text_len,
      parent_id=self.article.page_id
    )

  def text(self, element):
    #XXX deleted, preserve
    self.article.text = Text(
      id=self.article.revision_id,
      text=element.contents(),
      flags='utf-8'
    )
    self.article.text_len = 0
    if self.article.text.text:
      self.article.text_len = len(self.article.text.text)

  def contributor(self, element):
    self.article.contrib_user = element.text('username', element.text('ip'))
    self.article.contrib_id = element.text('id', 0)

  def comment(self, element):
    if element and not element.attr('deleted'):
      self.article.comment = element.contents()
    else:
      self.article.comment = ''


