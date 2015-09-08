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

from pyrundeck.xml2native import ParserEngine

__author__ = "Panagiotis Koutsourakis <kutsurak@ekt.gr>"


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

# The entry point for this module
parser = RundeckParser()


def parse(xml_tree, cb_type='composite',
          parse_table=parser.result_parse_table):
    """Main entry point to the parser"""
    return parser.parse(xml_tree, cb_type, parse_table)
