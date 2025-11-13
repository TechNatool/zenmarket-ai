# Dummy sgmllib module for testing
import re

# Regular expressions from original sgmllib
charref = re.compile('&#(?:[0-9]+|[xX][0-9a-fA-F]+)[;]?')
tagfind = re.compile('[a-zA-Z][-_.a-zA-Z0-9]*')
attrfind = re.compile(r'\s*([a-zA-Z_][-:.a-zA-Z_0-9]*)(\s*=\s*'
                      r'(\'[^\']*\'|"[^"]*"|[-a-zA-Z0-9./,:;+*%?!&$\(\)_#=~@]*))?')
entityref = re.compile('&([a-zA-Z][-.a-zA-Z0-9]*)[;]?')

class SGMLParser:
    pass
