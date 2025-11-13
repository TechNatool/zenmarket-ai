# Dummy sgmllib module for testing (Python 3.11 compatibility)
import re

# Regular expressions from original sgmllib
charref = re.compile("&#(?:[0-9]+|[xX][0-9a-fA-F]+)[;]?")
tagfind = re.compile("[a-zA-Z][-_.a-zA-Z0-9]*")
attrfind = re.compile(
    r"\s*([a-zA-Z_][-:.a-zA-Z_0-9]*)(\s*=\s*"
    r'(\'[^\']*\'|"[^"]*"|[-a-zA-Z0-9./,:;+*%?!&$\(\)_#=~@]*))?'
)
entityref = re.compile("&([a-zA-Z][-.a-zA-Z0-9]*)[;]?")
incomplete = re.compile("&[a-zA-Z#]")
interesting = re.compile("[&<]")
shorttag = re.compile("<([a-zA-Z][-.a-zA-Z0-9]*)/([^/]*)/")
shorttagopen = re.compile("<([a-zA-Z][-.a-zA-Z0-9]*)/")
piclose = re.compile(">")
endbracket = re.compile(">")
starttagopen = re.compile("<[a-zA-Z]")
endtagopen = re.compile("</[a-zA-Z]")
commentopen = re.compile("<!--")
commentclose = re.compile(r"--\s*>")
special = re.compile("<![^<>]*>")
declopen = re.compile("<![a-zA-Z]")
cdataopen = re.compile(r"<!\[CDATA\[")
cdataclose = re.compile(r"\]\]>")


class SGMLParser:
    """Minimal SGML parser stub for feedparser compatibility."""

    def __init__(self):
        pass

    def reset(self):
        pass

    def feed(self, data):
        pass

    def close(self):
        pass

    def goahead(self, end):
        """Stub goahead method for feedparser compatibility."""

    def parse_starttag(self, i):
        """Stub parse_starttag for feedparser compatibility."""
        return -1

    def parse_endtag(self, i):
        """Stub parse_endtag for feedparser compatibility."""
        return -1

    def finish_shorttag(self, tag, attrs):
        """Stub finish_shorttag for feedparser compatibility."""
