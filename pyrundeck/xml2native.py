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

"""

import logging  # TODO: use the logger

__author__ = "Panagiotis Koutsourakis <kutsurak@ekt.gr>"


class RundeckParseError(Exception):
    def __init__(self, *args, **kwargs):
        "This class represents a parse error."
        super(RundeckParseError, self).__init__(*args, **kwargs)


class RundeckParser(object):
    "This class contains the parsing tables for various rundeck elements."
    def __init__(self):
        self.option_parse_table = {
            'option': {
                'function': 'attribute'
            }
        }

        # The options are parsed as a list that contain many single
        # option objects
        self.options_parse_table = {
            'options': {
                'function': 'list',
                'element_parse_table': self.option_parse_table,
                'skip len': True
            }
        }

        self.node_parse_table = {
            'node': {
                'function': 'attribute',
            }
        }

        self.job_parse_table = {
            'job': {
                'function': 'non terminal',
                'components': {
                    'tags': {
                        'name': {
                            'function': 'terminal'
                        },
                        'project': {
                            'function': 'terminal'
                        },
                        'group': {
                            'function': 'terminal'
                        },
                        'description': {
                            'function': 'terminal'
                        },
                        'id': {
                            'function': 'terminal'
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
                'function': 'non terminal',
                'components': {
                    'tags': {
                        'user': {
                            'function': 'terminal',
                        },
                        'date-started': {
                            'function': 'attribute text',
                            'parse table': self.date_parse_table
                        },
                        'job': {
                            'function': 'non terminal',
                            'parse table': self.job_parse_table
                        },
                        'description': {
                            'function': 'terminal'
                        },
                        'argstring': {
                            'function': 'terminal'
                        },
                        'serverUUID': {
                            'function': 'terminal'
                        },
                        'date-ended': {
                            'function': 'attribute text',
                            'parse table': self.date_parse_table
                        },
                        'abortedby': {
                            'function': 'terminal'
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

        self.result_parse_table = {
            'result': {
                'function': 'non terminal',
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
                    },
                    'mandatory_attributes': []
                }
            }
        }

    @staticmethod
    def parse(xml_tree, cb_type, parse_table):
        """This method is the external interface to the ParserEngine class.

        The parse table for each element must contain a key named
        'function' that should contain the type of the parse function
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
            'terminal':       self.terminal_tag,
            'attribute':      self.attribute_tag,
            'attribute text': self.attribute_text_tag,
            'list':           self.list_tag,
            'non terminal':   self.non_terminal_tag
        }

    def terminal_tag(self, root, expected_tags, parse_table=None):
        # TODO: Refactor this method, renaming it to text_tag
        """Parse a tag containing only text.

        Example:
        Input:
        <name>Random text</name>
        Parse table:
        None (This is a terminal symbol in the grammar)
        Output:
        "Random text"

        :return: The text of the tag.
        """
        self.check_root_tag(root.tag, expected_tags)
        return root.text

    def attribute_tag(self, root, expected_tags, parse_table=None):
        """Parse a tag with attributes.

        Example:
        Input:
        <option name="arg1" value="faf"/>
        Parse table:
        None (This is a terminal symbol in the grammar)
        Output: {'name': 'arg1', 'value': 'faf'}

        :return: A dictionary containing key value pairs for all the attributes
        """
        self.check_root_tag(root.tag, expected_tags)
        return root.attrib

    def attribute_text_tag(self, root, expected_tags, parse_table):
        """Parse a tag with attributes and text.

        Example:

        Input:
        <date-started unixtime="1437474661504">
          2015-07-21T10:31:01Z
        </date-started>
        Parse table:
        {
          'date-started': {
              'function': 'attribute text',
              'text tag': 'time'
          }
        }
        Output:
        {
          'unixtime': '1437474661504',
          'text tag': '2015-07-21T10:31:01Z'
        }

        :return: A dictionary containing all the attributes of the
        tag. The text of the tag is entered in the dictionary as a
        value with key a string provided by the parse table for this
        tag.

        """
        self.check_root_tag(root.tag, expected_tags)
        ret = root.attrib

        text_tag = parse_table[root.tag]['text tag']
        ret.update({text_tag: root.text})

        return ret

    def list_tag(self, root, expected_tags, parse_table):
        """Parse a tag that is a list of elements.

        Example:
        Input:
        <options>
          <option name="arg1" value="foo"/>
          <option name="arg2" value="bar"/>
        </options>
        Parse table:
        {
          'function': 'list',
          'element_parse_table': self.option_parse_table,
          'skip len': True
        }
        Output:
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

    def non_terminal_tag(self, root, expected_tags, parse_table):
        # TODO: Refactor the name of this method to composite_tag
        """Parse a tag consisting of other tags.

        Input:
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
        Parse table:
        {
          'function': 'non terminal',
          'components': {
            'tags': {
              'user': {
                'function': 'terminal',
              },
              'date-started': {
                'function': 'attribute text',
                'parse table': self.date_parse_table
              },
              'job': {
                'function': 'non terminal',
                'parse table': self.job_parse_table
              },
              'description': {
                'function': 'terminal'
              },
              'argstring': {
                'function': 'terminal'
              },
              'serverUUID': {
                'function': 'terminal'
              },
              'date-ended': {
                'function': 'attribute text',
                 'parse table': self.date_parse_table
              },
              'abortedby': {
                'function': 'terminal'
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
        Output:
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
                msg = 'Unknown tag <{}> for <{}>'.format(c_tag, root.tag)
                raise RundeckParseError(msg)
            callback_type = callbacks[c_tag]['function']
            callback = self.callbacks[callback_type]
            if (callback_type == 'list' or callback_type == 'non terminal' or
                    callback_type == 'attribute text'):
                args = callbacks[c_tag]['parse table']
                ret[c_tag] = callback(c, c_tag, args)
            elif callback_type == 'terminal' or callback_type == 'attribute':
                ret[c_tag] = callback(c, c_tag)

        ret.update(root.attrib)

        for elem in pt['mandatory_attributes']:
            if ret.get(elem) is None:
                msg = ('expected tag <{}> not found in tag <{}>'
                       .format(elem, root.tag))
                raise RundeckParseError(msg)

        return ret

    def check_root_tag(self, actual, expected):
        if actual not in expected:
            msg = "expected one of {}, but got: '{}'".format(expected, actual)
            msg += ""
            raise RundeckParseError(msg)


def job(xml_tree):
    "Parse a single job. Return a dict represeting a job."

    return parse(xml_tree, 'non terminal', parser.job_parse_table)

    # check_root_tag(xml_tree.tag, ['job'])

    # ret = {}
    # for child in xml_tree:
    #     current_tag = child.tag
    #     if current_tag == 'options':
    #         ret[current_tag] = options(child)
    #     else:
    #         ret[current_tag] = child.text
    # ret.update(xml_tree.items())  # add any attributes of the root tag

    # mandatory_tags = ['id', 'name', 'project']
    # for tag in mandatory_tags:
    #     if ret.get(tag) is None:
    #         raise RundeckParseError('tag <{}> missing from job'.format(tag))

    # return ret


def jobs(xml_tree):
    "Parse multiple jobs. Return a list containing the jobs."

    return parse(xml_tree, 'list', parser.jobs_parse_table)
    # check_root_tag(xml_tree.tag, ['jobs'])

    # if xml_tree.get('count') is None:
    #     raise RundeckParseError('attribute @count missing from jobs')

    # jobs = [job(child) for child in xml_tree]
    # ret = {
    #     'count': int(xml_tree.get('count')),
    #     'jobs': jobs
    # }

    # cnt = ret.get('count')
    # ln = len(ret.get('jobs'))
    # if cnt != ln:
    #     raise RundeckParseError('number of jobs(={}) and count(={})'
    #                             .format(ln, cnt) + ' are different')

    # return ret


def date(xml_tree):
    "Parse a date-started or a date-ended. Return a dict."

    return parse(xml_tree, 'attribute text', parser.date_parse_table)

    # check_root_tag(xml_tree.tag, ['date-started', 'date-ended'])

    # return {
    #     'time': xml_tree.text.strip(),
    #     'unixtime': xml_tree.get('unixtime').strip()
    # }


def node(xml_tree):
    "Parse a node. Return a dict."

    return parse(xml_tree, 'attribute', parser.node_parse_table)
    # if xml_tree.tag != 'node':
    #     raise RundeckParseError('expected tag <node>, got: <{}>'
    #                             .format(xml_tree.tag))
    # return xml_tree.attrib


def nodes(xml_tree):
    "Parse multiple nodes. Return a list of nodes."

    return parse(xml_tree, 'list', parser.nodes_parse_table)
    # parser = RundeckParser()
    # return parser.parse('list', xml_tree,
    #                     'nodes', parser.nodes_parse_table)
    # check_root_tag(xml_tree.tag, ['successfulNodes', 'failedNodes'])

    # return [node(child) for child in xml_tree]


def execution(xml_tree):
    "Parse a single execution. Return a dict."

    return parse(xml_tree, 'non terminal', parser.execution_parse_table)
    # check_root_tag(xml_tree.tag, ['execution'])

    # ret = {}
    # for child in xml_tree:
    #     current_tag = child.tag
    #     if current_tag == 'job':
    #         ret[current_tag] = job(child)
    #     elif current_tag.startswith('date-'):
    #         ret[current_tag] = date(child)
    #     elif current_tag.endswith('Nodes'):
    #         ret[current_tag] = nodes(child)
    #     else:
    #         ret[current_tag] = child.text

    # ret.update(xml_tree.items())
    # return ret


def executions(xml_tree):
    "Parse multiple executions. Return a list."

    return parse(xml_tree, 'list', parser.executions_parse_table)
    # check_root_tag(xml_tree.tag, ['executions'])
    # ret = {}
    # if xml_tree.get('count') is None:
    #     raise RundeckParseError('attribute @count missing from executions')

    # cnt = int(xml_tree.get('count'))
    # ret['count'] = cnt
    # ret['executions'] = [execution(c) for c in xml_tree]

    # ln = len(ret['executions'])
    # if cnt != ln:
    #     raise RundeckParseError('number of jobs(={}) and count(={})'
    #                             .format(ln, cnt) + ' are different')

    # return ret


def option(xml_tree):
    "Parse a single option. Return a dict."

    return parse(xml_tree, 'attribute', parser.option_parse_table)
    # check_root_tag(xml_tree.tag, ['option'])

    # return xml_tree.attrib


def options(xml_tree):
    "Parse multiple options. Return a list."

    return parse(xml_tree, 'list', parser.options_parse_table)
    # check_root_tag(xml_tree.tag, ['options'])
    # return [option(c) for c in xml_tree]

# The entry point for this module
parser = RundeckParser()


def parse(xml_tree, cb_type='non terminal',
          parse_table=parser.result_parse_table):
    """Main entry point to the parser"""
    return parser.parse(xml_tree, cb_type, parse_table)
