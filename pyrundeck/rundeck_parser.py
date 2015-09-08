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

    Each parse table describes a specific tag. See
    :py:class:`pyrundeck.xml2native.ParserEngine` for more details.

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

        self.engine = ParserEngine()

    def parse(self, xml_tree, cb_type, parse_table):
        """This method is the external interface to the ParserEngine class.

        The parse table for each element must contain a key named
        ``'function'`` that should contain the type of the parse function
        that should be called to parse this tag. This is the
        ``cb_type`` argument of the parse method.

        """
        # Create a parser engine.

        # Find which call back we need to call...
        cb = self.engine.callbacks[cb_type]
        # ... and call it
        return cb(xml_tree, parse_table)

# The entry point for this module
_parser = RundeckParser()


def parse(xml_tree, cb_type='composite',
          parse_table=_parser.result_parse_table):
    """Main entry point to the parser"""
    return _parser.parse(xml_tree, cb_type, parse_table)
