import os
from xml.sax.saxutils import quoteattr as xml_quoteattr
from directory import DirTree
import tkinter

def DirAsXML(path):
    result = '<dir name=%s>\n' % xml_quoteattr(os.path.basename(path))
    for item in os.listdir(path):
        itempath = os.path.join(path, item)
        if os.path.isdir(itempath):
            result += '\n'.join('   ' + line for line in
                DirAsXML(os.path.join(path, item)).split('\n'))
        elif os.path.isfile(itempath):
            result += '    <file name=%s />\n' % xml_quoteattr(item)
    result += '</dir>\n'
    return result


#filename, file_extension = os.path.splitext("classify.py")

