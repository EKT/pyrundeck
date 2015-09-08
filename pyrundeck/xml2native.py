# Copyright (c) 2007-2015, National Documentation Centre (EKT, www.ekt.gr)
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


class RundeckParseError(Exception):
    # TODO refactor the name to ParseError.
    def __init__(self, *args, **kwargs):
        "This class represents a parse error."
        super(RundeckParseError, self).__init__(*args, **kwargs)


class RundeckParser(object):
    """This class contains the parsing tables for various rundeck elements.

    Each parse table describes a specific tag.

    Every parse table is a dictonary containing at least one two keys: The name
    of the tag that we are trying to parse, specified as the string value of the
    ``'tag'`` key and the type of the tag. This is specified as the value of the
    ``'type'`` key inside the dict.

    Currently the :py:class:`pyrundeck.xml2native.ParserEngine` recognizes the
    following types of tags.

    ``'text'``
       A tag that contains only text.

    ``'attribute'``
       A tag that contains only attributes.

    ``'attribute text'``
       A tag that contains attributes and text.

       A special parse table dict key named ``'text tag'`` should be
       specified. It's value should be a string and it is used as the
       key to the returned dictionary for the text. See
       :py:meth:`RundeckParser.attribute_text_tag`

    ``'list'``
       A tag that is a homogeneous list of tags.

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

    """
    def __init__(self):
        self.error_parse_table = {
            'tag': 'error',
            'type': 'composite',
            'all': [{'tag': 'message', 'type': 'text'}]
        }

        self.start_date_parse_table = {
            'tag': 'date-started',
            'type': 'attribute text',
            'text tag': 'time'
        }

        self.date_ended_parse_table = {
            'tag': 'date-ended',
            'type': 'attribute text',
            'text tag': 'time'
        }

        self.node_parse_table = {
            'tag': 'node',
            'type': 'attribute'
        }

        self.successful_nodes_parse_table = {
            'tag': 'successfulNodes',
            'type': 'list',
            'element parse table': self.node_parse_table,
            'skip count': True,
        }

        self.failed_nodes_parse_table = {
            'tag': 'failedNodes',
            'type': 'list',
            'element parse table': self.node_parse_table,
            'skip count': True,
        }

        self.option_parse_table = {'tag': 'option', 'type': 'attribute'}

        self.options_parse_table = {
            'tag': 'options',
            'type': 'list',
            'element parse table': self.option_parse_table,
            'skip count': True
        }

        self.job_parse_table = {
            'tag': 'job',
            'type': 'composite',
            'all': [
                {'tag': 'id', 'type': 'text'},
                {'tag': 'name', 'type': 'text'},
                {'tag': 'project', 'type': 'text'},
            ],
            'any': [
                {'tag': 'group', 'type': 'text'},
                {'tag': 'description', 'type': 'text'},
                {'tag': 'url', 'type': 'text'},
                self.options_parse_table
            ]
        }

        self.jobs_parse_table = {
            'tag': 'jobs',
            'type': 'list',
            'element parse table': self.job_parse_table
        }

        self.execution_parse_table = {
            'tag': 'execution',
            'type': 'composite',
            'all': [
                {'tag': 'user', 'type': 'text'},
                self.start_date_parse_table,
                {'tag': 'description', 'type': 'text'}
            ],
            'any': [
                self.job_parse_table,
                {'tag': 'argstring', 'type': 'text'},
                {'tag': 'serverUUID', 'type': 'text'},
                {'tag': 'abortedby', 'type': 'text'},
                self.date_ended_parse_table,
                self.successful_nodes_parse_table,
                self.failed_nodes_parse_table
            ]
        }

        self.executions_parse_table = {
            'tag': 'executions',
            'type': 'list',
            'element parse table': self.execution_parse_table
        }

        self.result_parse_table = {
            'tag': 'result',
            'type': 'composite',
            'any': [
                self.jobs_parse_table,
                self.executions_parse_table,
                self.error_parse_table,
            ],
        }

    @staticmethod
    def parse(xml_tree, cb_type, parse_table):
        """This method is the external interface to the ParserEngine class.

        The parse table for each element must contain a key named
        ``'function'`` that should contain the type of the parse function
        that should be called to parse this tag. This is the
        ``cb_type`` argument of the parse method.

        """
        # Create a parser engine.

        # TODO: It is probably a mistake to create a new engine every
        # time this function is called. OPTIMIZE.
        engine = ParserEngine()
        cb = engine.callbacks[cb_type]  # Find which call back we need to call
        return cb(xml_tree, parse_table)  # Call the callback


class ParserEngine(object):
    """This is class converts the ``lxml.etree`` representation to native
    Python objects.

    The user does not need to interact with it.

    """
    def __init__(self):
        self.callbacks = {
            'text':           self.text_tag,
            'attribute':      self.attribute_tag,
            'attribute text': self.attribute_text_tag,
            'list':           self.list_tag,
            'composite':      self.composite_tag
        }

    def text_tag(self, root, parse_table=None):
        """Parse a tag containing only text.

        **Example**

        Input::

           <name>Random text</name>

        Parse table::

           None (This is a terminal symbol in the grammar)

        Output::

           "Random text"

        :return: The text of the tag.
        """
        self.check_root_tag(root.tag, parse_table)
        return root.text

    def attribute_tag(self, root, parse_table=None):
        """Parse a tag with attributes.

        **Example**

        Input::

           <option name="arg1" value="faf"/>

        Parse table::

           None (This is a terminal symbol in the grammar)

        Output::

           {'name': 'arg1', 'value': 'faf'}

        :return: A dictionary containing key value pairs for all the attributes
        """
        self.check_root_tag(root.tag, parse_table['tag'])
        return root.attrib

    def attribute_text_tag(self, root, parse_table):
        """Parse a tag with attributes and text.

        **Example**

        Input::

           <date-started unixtime="1437474661504">
             2015-07-21T10:31:01Z
           </date-started>

        Parse table::

           {
             'date-started': {
                'function': 'attribute text',
                'text tag': 'time'
             }
           }

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
        ret = root.attrib

        text_tag = parse_table['text tag']
        ret.update({text_tag: root.text})

        return ret

    def list_tag(self, root, parse_table):
        """Parse a tag that is a list of elements.

        **Example**

        Input::

           <options>
             <option name="arg1" value="foo"/>
             <option name="arg2" value="bar"/>
           </options>

        Parse table::

           {
             'function': 'list',
             'element_parse_table': self.option_parse_table,
             'skip len': True
           }

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

        skip_len = (parse_table.get('skip count') is not None and
                    parse_table.get('skip count'))
        if skip_len:
            return lst

        if cnt_str is None:
            raise RundeckParseError('attribute @count missing from <{}>'
                                    .format(root.tag))

        cnt = int(cnt_str)
        ln = len(lst)
        if cnt != ln:
            raise RundeckParseError('list len(={}) and count(={})'
                                    .format(ln, cnt) + ' are different')
        return {'count': cnt, 'list': lst}

    def composite_tag(self, root, parse_table):
        """Parse a tag consisting of other tags.

        **Example**

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

        Parse table::

           {
             'function': 'composite',
             'components': {
               'tags': {
                 'user': {
                   'function': 'text',
                 },
                 'date-started': {
                   'function': 'attribute text',
                   'parse table': self.date_parse_table
                 },
                 'job': {
                   'function': 'composite',
                   'parse table': self.job_parse_table
                 },
                 'description': {
                   'function': 'text'
                 },
                 'argstring': {
                   'function': 'text'
                 },
                 'serverUUID': {
                   'function': 'text'
                 },
                 'date-ended': {
                   'function': 'attribute text',
                    'parse table': self.date_parse_table
                 },
                 'abortedby': {
                   'function': 'text'
                 },
                 'successfulNodes': {
                   'function': 'list',
                   'parse table': self.nodes_parse_table
                 },
                 'failedNodes': {
                   'function': 'list',
                   'parse table': self.nodes_parse_table
                 }
               },
               'mandatory_attributes': [
                 'user', 'date-started',
                 'description'
               ]
             }
           }

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
        allowed_tags = mandatory_tags.copy()
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
                raise RundeckParseError(msg)
            callback_type = pt_index[c_tag]['type']
            callback = self.callbacks[callback_type]
            if (callback_type == 'list' or callback_type == 'composite' or
                    callback_type == 'attribute text'):
                args = pt_index[c_tag]
                ret[c_tag] = callback(c, args)
            elif callback_type == 'text' or callback_type == 'attribute':
                ret[c_tag] = callback(c, c_tag)

        for atk, atv in root.attrib.items():
            if atk in ret:
                ret[atk + '_attribute'] = atv
            else:
                ret[atk] = atv

        for elem in mandatory_tags:
            if ret.get(elem) is None:
                msg = ('expected tag <{}> not found in tag <{}>'
                       .format(elem, root.tag))
                raise RundeckParseError(msg)

        return ret

    def check_root_tag(self, actual, expected):
        """Check that the ``actual`` tag is in the ``expected`` list or raise
        an error.

        """
        if actual != expected:
            msg = "expected one of {}, but got: '{}'".format(expected, actual)
            msg += ""
            raise RundeckParseError(msg)

# The entry point for this module
parser = RundeckParser()


def parse(xml_tree, cb_type='composite',
          parse_table=parser.result_parse_table):
    """Main entry point to the parser"""
    return parser.parse(xml_tree, cb_type, parse_table)
