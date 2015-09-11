# Copyright (c) 2015, National Documentation Centre (EKT, www.ekt.gr)
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

#     Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.

#     Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.

#     Neither the name of the National Documentation Centre nor the
#     names of its contributors may be used to endorse or promote
#     products derived from this software without specific prior written
#     permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""The classes and functions in this module convert the ``lxml.etree``
representation of the server response to native objects similar to a
JSON representation. The functions in this module implement a
recursive descent parser based on the tags of the XML representation.

The parser is driven by parsing tables that actually describe the
grammar the parser accepts. In this sense this library resembles tools
like yacc and bison.

"""

__author__ = "Panagiotis Koutsourakis <kutsurak@ekt.gr>"


class ParseError(Exception):
    def __init__(self, *args, **kwargs):
        "This class represents a parse error."
        super(ParseError, self).__init__(*args, **kwargs)


class ParserEngine(object):
    """This is class converts the ``lxml.etree`` representation to native
    Python objects.

    The user does not need to interact with it.

    Every parse table is a dictonary containing at least one two keys: The name
    of the tag that we are trying to parse, specified as the string value of
    the ``'tag'`` key and the type of the tag. This is specified as the value
    of the ``'type'`` key inside the dict.

    Currently the :py:class:`pyrundeck.xml2native.ParserEngine` recognizes the
    following types of tags.

    ``'text'``
       A tag that contains only text::

          <text_tag>Text</text_tag>

    ``'attribute'``
       A tag that contains only attributes::

          <attribute_tag attrib1="foo" attrib2="bar"/>

    ``'attribute text'``
       A tag that contains attributes and text::

          <tag attrib="value">Text</attrib>

       A special parse table dict key named ``'text tag'`` should be
       specified. It's value should be a string and it is used as the
       key to the returned dictionary for the text. See
       :py:meth:`RundeckParser.attribute_text_tag`

    ``'list'``
       A tag that is a homogeneous list of tags::

          <tag>
            <child>Child 1</child>
            <child>Child 2</child>
            <child>Child 3</child>
            <child>Child 4</child>
          </tag>

       The value of the key ``'element parse table'''`` should be a parse table
       that specifies how each element of the list will be parsed.

       A special parse table dict key named ``'skip count'`` can be set
       to ``True``, to prevent the check for a count attribute in this
       tag.

    ``'composite'``
       A tag that is composed of other tags and attributes.

       The value of the key ``'all''`` should be a list that contains the parse
       tables for the mandatory child tags. The optional child tags should be
       specified as a list value of the ``'any'`` tag.

    ``'alternatives'``
      A tag that can be parsed in multiple ways.

      The value of the key ``'parse tables'`` should be the different parse
      tables that can be used to parse this tag.

    """
    def __init__(self):
        self.callbacks = {
            'text':           self.text_tag,
            'attribute':      self.attribute_tag,
            'attribute text': self.attribute_text_tag,
            'list':           self.list_tag,
            'composite':      self.composite_tag,
            'alternatives':   self.alternatives_tag
        }

    def text_tag(self, root, parse_table):
        """Parse a tag containing only text.

        **Example**

        Parse table::

           {'tag': 'name', 'type': 'text'}

        Input::

           <name>Random text</name>

        Output::

           "Random text"

        :return: The text of the tag.
        """
        self.check_root_tag(root.tag, parse_table['tag'])

        if len(root) != 0:
            msg = ('tag <{}> is not a text tag '
                   '(number of children = {})'.format(root.tag, len(root)))
            raise ParseError(msg)

        if len(root.keys()) != 0:
            msg = ('tag <{}> is not a text tag '
                   '(number of attributes = {})'.format(root.tag,
                                                        len(root.keys())))
            raise ParseError(msg)

        return root.text

    def attribute_tag(self, root, parse_table):
        """Parse a tag with attributes.

        **Example**

        Parse table::

           {'tag': 'name', 'type': 'attribute'}

        Input::

           <option name="arg1" value="faf"/>

        Output::

           {'name': 'arg1', 'value': 'faf'}

        :return: A dictionary containing key value pairs for all the attributes
        """
        self.check_root_tag(root.tag, parse_table['tag'])

        if len(root) != 0:
            msg = ('tag <{}> is not an attribute tag '
                   '(number of children = {})'.format(root.tag, len(root)))
            raise ParseError(msg)

        if root.text is not None:
            msg = ('tag <{}> is not an attribute tag '
                   '({}.text = "{}")'.format(root.tag, root.tag, root.text))
            raise ParseError(msg)

        return root.attrib

    def attribute_text_tag(self, root, parse_table):
        """Parse a tag with attributes and text.

        **Example**

        Parse table::

           {
             'date-started': {
                'type': 'attribute text',
                'text tag': 'time'
             }
           }

        Input::

           <date-started unixtime="1437474661504">
             2015-07-21T10:31:01Z
           </date-started>

        Output::

           {
             'unixtime': '1437474661504',
             'text tag': '2015-07-21T10:31:01Z'
           }

        :return: A dictionary containing all the attributes of the
                 tag. The text of the tag is entered in the dictionary
                 as a value with key a string provided by the parse
                 table for this tag.

        """
        self.check_root_tag(root.tag, parse_table['tag'])

        if len(root) != 0:
            msg = ('tag <{}> is not a text attribute tag '
                   '(number of children = {})'.format(root.tag, len(root)))
            raise ParseError(msg)

        ret = root.attrib

        text_tag = parse_table['text tag']
        ret.update({text_tag: root.text})

        return ret

    def list_tag(self, root, parse_table):
        """Parse a tag that is a list of elements.

        **Example**

        Parse table::

           {
             'type': 'list',
             'element_parse_table': self.option_parse_table,
             'skip len': True
           }

        Input::

           <options>
             <option name="arg1" value="foo"/>
             <option name="arg2" value="bar"/>
           </options>

        Output::

           [
             {'name': 'arg1', 'value': 'foo'},
             {'name': 'arg2', 'value': 'bar'}
           ]

        :param root: The actual XML object that we need to parse.
        :param expected_tags: A list containing the tags this element can
                              start with.
        :param parse_table: The parse table for this element.
        :return: A list of elements specified by the parse table.
        """
        self.check_root_tag(root.tag, parse_table['tag'])

        element_pt = parse_table['element parse table']
        callback_type = element_pt['type']
        callback = self.callbacks[callback_type]

        lst = [callback(c, element_pt) for c in root]
        # TODO maybe remove this to make the parser more general.
        cnt_str = root.get('count')

        skip_len = parse_table.get('skip count', False)
        if skip_len:
            return {'list': lst}

        if cnt_str is None:
            raise ParseError('attribute @count missing from <{}>'
                             .format(root.tag))

        cnt = int(cnt_str)
        ln = len(lst)
        if cnt != ln:
            raise ParseError('list len(={}) and count(={})'
                             .format(ln, cnt) + ' are different')
        return {'count': cnt, 'list': lst}

    def composite_tag(self, root, parse_table):
        """Parse a tag consisting of other tags.

        **Example**

        Parse table::

           {
             'type': 'composite',
             'components': {
               'tags': {
                 'user': {
                   'type': 'text',
                 },
                 'date-started': {
                   'type': 'attribute text',
                   'parse table': self.date_parse_table
                 },
                 'job': {
                   'type': 'composite',
                   'parse table': self.job_parse_table
                 },
                 'description': {
                   'type': 'text'
                 },
                 'argstring': {
                   'type': 'text'
                 },
                 'serverUUID': {
                   'type': 'text'
                 },
                 'date-ended': {
                   'type': 'attribute text',
                    'parse table': self.date_parse_table
                 },
                 'abortedby': {
                   'type': 'text'
                 },
                 'successfulNodes': {
                   'type': 'list',
                   'parse table': self.nodes_parse_table
                 },
                 'failedNodes': {
                   'type': 'list',
                   'parse table': self.nodes_parse_table
                 }
               },
               'mandatory_attributes': [
                 'user', 'date-started',
                 'description'
               ]
             }
           }

        Input::

           <execution id="117"
              href="http://192.168.50.2:4440/execution/follow/117"
              status="succeeded" project="API_client_development">
             <user>admin</user>
             <date-started unixtime="1437474661504">
               2015-07-21T10:31:01Z
             </date-started>
             <date-ended unixtime="1437474662344">
               2015-07-21T10:31:02Z
             </date-ended>
             <job id="78f491e7-714f-44c6-bddb-8b3b3a961ace"
                  averageDuration="2716">
               <name>test_job_1</name>
               <group/>
               <project>API_client_development</project>
               <description/>
             </job>
             <description>echo "Hello"</description>
             <argstring/>
             <successfulNodes>
             <node name="localhost"/>
             </successfulNodes>
           </execution>

        Output::

           {
               'id': '117',
               'href': 'http://192.168.50.2:4440/execution/follow/117',
               'status': 'succeeded',
               'project': 'API_client_development',
               'user': 'admin',
               'date-started': {
                   'unixtime': '1437474661504',
                   'time': '2015-07-21T10:31:01Z'
               },
               'date-ended': {
                   'unixtime': '1437474662344',
                   'time': '2015-07-21T10:31:02Z'
               },
               'job': {
                   'id': '78f491e7-714f-44c6-bddb-8b3b3a961ace',
                   'averageDuration': '2716',
                   'name': 'test_job_1',
                   'group': None,
                   'project': 'API_client_development',
                   'description': None,
               },
               'description': 'echo "Hello"',
               'argstring': None,
               'successfulNodes': [
                   {'name': 'localhost'}
               ]
           }

        :return: A dictionary representing the XML object.
        """
        self.check_root_tag(root.tag, parse_table['tag'])

        # pt = parse_table[root.tag]['components']

        mandatory_tags = [t['tag'] for t in parse_table.get('all', {})]
        allowed_tags = list(mandatory_tags)
        allowed_tags.extend(
            [t['tag'] for t in parse_table.get('any', {})]
        )
        pt_index = {t.get('tag'): t for t in parse_table.get('all', {})}
        pt_index.update({t.get('tag'): t for t in parse_table.get('any', {})})

        # allowed_tags = set(pt['tags'].keys())
        # callbacks = pt['tags']

        ret = {}
        for c in root:
            c_tag = c.tag
            if c_tag not in allowed_tags:
                msg = 'Unknown tag <{}> inside <{}>'.format(c_tag, root.tag)
                raise ParseError(msg)
            callback_type = pt_index[c_tag]['type']
            callback = self.callbacks[callback_type]
            ret[c_tag] = callback(c, pt_index[c_tag])

        for atk, atv in root.attrib.items():
            if atk in ret:
                ret[atk + '_attribute'] = atv
            else:
                ret[atk] = atv

        for elem in mandatory_tags:
            if ret.get(elem) is None:
                msg = ('expected tag <{}> not found in tag <{}>'
                       .format(elem, root.tag))
                raise ParseError(msg)

        return ret

    def alternatives_tag(self, root, parse_table):
        """Parse a tag that can have multiple different forms.

        **Example**

        Parse table::

           {
             'tag': 'text_or_attribute',
             'type': 'alternatives',
             'parse tables': [
               {'type': 'text'},
               {'type': 'attribute'}
             ]
           }

        Input::

           <text_or_attribute>Example text</text_or_attribute>

        Output::

           "Example text"

        Input::

           <text_or_attribute attribute="value"/>

        Output::

           {'attribute': 'value'}
        """
        possible_pts = parse_table.get('parse tables', [])
        ret = None
        for pt in possible_pts:
            try:
                pt['tag'] = parse_table['tag']
                callback = self.callbacks.get(pt.get('type'))
                ret = callback(root, pt)
            except ParseError:
                ret = None

        if ret is None:
            msg = ("None of the alternatives could be parsed for tag "
                   "{}".format(root.tag))
            raise ParseError(msg)

        return ret

    def check_root_tag(self, actual, expected):
        """Check that the ``actual`` tag is in the ``expected`` list or raise
        an error.

        """
        if actual != expected:
            msg = "expected one of {}, but got: '{}'".format(expected, actual)
            msg += ""
            raise ParseError(msg)
