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

import logging  # TODO: use the logger

__author__ = "Panagiotis Koutsourakis <kutsurak@ekt.gr>"


class RundeckParseError(Exception):
    # TODO refactor the name to ParseError.
    def __init__(self, *args, **kwargs):
        "This class represents a parse error."
        super(RundeckParseError, self).__init__(*args, **kwargs)


class RundeckParser(object):
    """This class contains the parsing tables for various rundeck elements.

    Each parse table describes a tag, or a set of alternative tags and
    their components.

    Every parse table is a dictonary containing at least one key. The
    key is the tag that we are trying to parse. If the dict contains
    more than one key then these are the alterantives for the tag. For
    instance if the parse table is ``{'foo': {...}, 'bar': {...}}``
    the parser will accept either the tag ``foo`` or the tag ``bar``.

    Every parse table needs to specify what type of tag we are
    parsing. This is done using the ``'function'`` key inside the dict
    that describes the tag. Currently the
    :py:class:`pyrundeck.xml2native.ParserEngine` recognizes the
    following functions.

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
       A tag that is a list of other similar tags.

       A special parse table dict key named ``'skip len'`` can be set
       to ``True``, to prevent the check for a count attribute in this
       tag.

    ``'composite'``
       A tag that is composed of other tags and attributes.

    """

    def __init__(self):
        # An option is just a tag with attributes. Use the attribute
        # function to parse it.
        # Example:
        # <option name="arg1" value="foo"/>
        self.option_parse_table = {
            'option': {
                'function': 'attribute'
            }
        }

        # The options are parsed as a list that contain many single
        # option objects.
        # Example:
        # <options>
        #   <option name="arg1" value="foo"/>
        # </options>
        self.options_parse_table = {
            'options': {
                'function': 'list',
                'element_parse_table': self.option_parse_table,
                'skip len': True
            }
        }

        # A node is an attribute tag.
        # Example:
        # <node name="localhost"/>
        self.node_parse_table = {
            'node': {
                'function': 'attribute',
            }
        }

        # A job is a composite tag that MUST have id, name and
        # project, and CAN also have group, description, id and
        # options.
        self.job_parse_table = {
            'job': {
                'function': 'composite',
                'components': {
                    'tags': {
                        'name': {
                            'function': 'text'
                        },
                        'project': {
                            'function': 'text'
                        },
                        'group': {
                            'function': 'text'
                        },
                        'description': {
                            'function': 'text'
                        },
                        'id': {
                            'function': 'text'
                        },
                        'options': {
                            'function': 'list',
                            'parse table': self.options_parse_table
                        },
                    },
                    'mandatory_attributes': ['id', 'name', 'project']
                }
            }
        }

        self.jobs_parse_table = {
            'jobs': {
                'function': 'list',
                'element_parse_table': self.job_parse_table
            }
        }

        self.nodes_parse_table = {
            'successfulNodes': {
                'function': 'list',
                'element_parse_table': self.node_parse_table,
                'skip len': True
            },
            'failedNodes': {
                'function': 'list',
                'element_parse_table': self.node_parse_table,
                'skip len': True
            }
        }

        self.date_parse_table = {
            'date-started': {
                'function': 'attribute text',
                'text tag': 'time'
            },
            'date-ended': {
                'function': 'attribute text',
                'text tag': 'time'
            }
        }

        self.execution_parse_table = {
            'execution': {
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
        }

        self.executions_parse_table = {
            'executions': {
                'function': 'list',
                'element_parse_table': self.execution_parse_table
            }
        }

        self.error_parse_table = {
            'error': {
                'function': 'composite',
                'components': {
                    'tags': {
                        'message': {
                            'function': 'text',
                        }
                    },
                    'mandatory_attributes': []
                }
            }
        }

        self.result_parse_table = {
            'result': {
                'function': 'composite',
                'components': {
                    'tags': {
                        'jobs': {
                            'function': 'list',
                            'parse table': self.jobs_parse_table
                        },
                        'executions': {
                            'function': 'list',
                            'parse table': self.executions_parse_table
                        },
                        'error': {
                            'function': 'composite',
                            'parse table': self.error_parse_table
                        },
                    },
                    'mandatory_attributes': []
                }
            }
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
        expected_tags = list(parse_table.keys())  # What tags are we parsing?
        return cb(xml_tree, expected_tags, parse_table)  # Call the callback


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

    def text_tag(self, root, expected_tags, parse_table=None):
        # TODO: Refactor this method, renaming it to text_tag
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
        self.check_root_tag(root.tag, expected_tags)
        return root.text

    def attribute_tag(self, root, expected_tags, parse_table=None):
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
        self.check_root_tag(root.tag, expected_tags)
        return root.attrib

    def attribute_text_tag(self, root, expected_tags, parse_table):
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
        self.check_root_tag(root.tag, expected_tags)
        ret = root.attrib

        text_tag = parse_table[root.tag]['text tag']
        ret.update({text_tag: root.text})

        return ret

    def list_tag(self, root, expected_tags, parse_table):
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
        self.check_root_tag(root.tag, expected_tags)

        element_pt = parse_table[root.tag]['element_parse_table']
        exp_tag = list(element_pt.keys())[0]
        callback_type = element_pt[exp_tag]['function']
        callback = self.callbacks[callback_type]

        lst = [callback(c, exp_tag, element_pt) for c in root]
        # TODO maybe remove this to make the parser more general.
        cnt_str = root.get('count')

        skip_len = (parse_table[root.tag].get('skip len') is not None and
                    parse_table[root.tag].get('skip len'))
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

    def composite_tag(self, root, expected_tags, parse_table):
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
        self.check_root_tag(root.tag, expected_tags)

        pt = parse_table[root.tag]['components']

        allowed_tags = set(pt['tags'].keys())
        callbacks = pt['tags']

        ret = {}
        for c in root:
            c_tag = c.tag
            if c_tag not in allowed_tags:
                msg = 'Unknown tag <{}> inside <{}>'.format(c_tag, root.tag)
                raise RundeckParseError(msg)
            callback_type = callbacks[c_tag]['function']
            callback = self.callbacks[callback_type]
            if (callback_type == 'list' or callback_type == 'composite' or
                    callback_type == 'attribute text'):
                args = callbacks[c_tag]['parse table']
                ret[c_tag] = callback(c, c_tag, args)
            elif callback_type == 'text' or callback_type == 'attribute':
                ret[c_tag] = callback(c, c_tag)

        for atk, atv in root.attrib.items():
            if atk in ret:
                ret[atk + '_attribute'] = atv
            else:
                ret[atk] = atv

        for elem in pt['mandatory_attributes']:
            if ret.get(elem) is None:
                msg = ('expected tag <{}> not found in tag <{}>'
                       .format(elem, root.tag))
                raise RundeckParseError(msg)

        return ret

    def check_root_tag(self, actual, expected):
        """Check that the ``actual`` tag is in the ``expected`` list or raise
        an error.

        """
        if actual not in expected:
            msg = "expected one of {}, but got: '{}'".format(expected, actual)
            msg += ""
            raise RundeckParseError(msg)

# The entry point for this module
parser = RundeckParser()


def parse(xml_tree, cb_type='composite',
          parse_table=parser.result_parse_table):
    """Main entry point to the parser"""
    return parser.parse(xml_tree, cb_type, parse_table)
