# Copyright 2020 Lane Shaw
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

''' Helper classes/functions used during testing. '''

from xml.sax.saxutils import XMLGenerator, quoteattr

__all__ = [
    'IndentedXMLGenerator',
]


class IndentedXMLGenerator(XMLGenerator):

    def __init__(self, out=None, encoding="iso-8859-1", short_empty_elements=False, indentation='', xml_declaration=True):
        super().__init__(out=out, encoding=encoding, short_empty_elements=short_empty_elements)
        self._indent_str = indentation
        self._indent_stack = []
        self._xml_declaration = xml_declaration

    def startDocument(self):
        if self._xml_declaration:
            self._write(
                '<?xml version="1.0" encoding="%s"?>\n' %
                self._encoding,
            )

    def startElement(self, name, attrs):
        self._finish_pending_start_element()

        if self._indent_str and self._indent_stack:
            self._write('\n' + self._indent_str * len(self._indent_stack))
            self._indent_stack[-1] = True

        self._indent_stack.append(False)
        self._write('<' + name)

        for (name, value) in attrs.items():
            self._write(' %s=%s' % (name, quoteattr(value)))

        if self._short_empty_elements:
            self._pending_start_element = True
        else:
            self._write(">")

    def startElementNS(self, name, qname, attrs):
        self._finish_pending_start_element()

        if self._indent_str and self._indent_stack:
            self._write('\n' + self._indent_str * len(self._indent_stack))
            self._indent_stack[-1] = True

        self._indent_stack.append(False)
        self._write('<' + self._qname(name))

        for prefix, uri in self._undeclared_ns_maps:
            if prefix:
                self._write(' xmlns:%s="%s"' % (prefix, uri))
            else:
                self._write(' xmlns="%s"' % uri)
        self._undeclared_ns_maps = []

        for (name, value) in attrs.items():
            self._write(' %s=%s' % (self._qname(name), quoteattr(value)))
        if self._short_empty_elements:
            self._pending_start_element = True
        else:
            self._write(">")

    def endElement(self, name):
        has_child = self._indent_stack.pop()

        if self._pending_start_element:
            self._write('/>')
            self._pending_start_element = False
        else:
            if self._indent_str and has_child:
                self._write('\n' + self._indent_str * len(self._indent_stack))
            self._write('</%s>' % name)

        if self._indent_str and not self._indent_stack:
            self._write('\n')

    def endElementNS(self, name, qname):
        has_child = self._indent_stack.pop()

        if self._pending_start_element:
            self._write('/>')
            self._pending_start_element = False
        else:
            if self._indent_str and has_child:
                self._write('\n' + self._indent_str * len(self._indent_stack))
            self._write('</%s>' % self._qname(name))

        if self._indent_str and not self._indent_stack:
            self._write('\n')
