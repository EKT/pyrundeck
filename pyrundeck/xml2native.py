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

"""The functions in this module convert the ``lxml.etree``
representation of the server response to native objects similar to a
JSON representation. The functions in this module implement a
recursive descent parser based on thetags of the XML representation.

"""

import logging  # TODO: use the logger

__author__ = "Panagiotis Koutsourakis <kutsurak@ekt.gr>"


class RundeckParseError(Exception):
    def __init__(self, *args, **kwargs):
        "This class represents a parse error."
        super(RundeckParseError, self).__init__(*args, **kwargs)


def job(xml_tree):
    "Parse a single job. Return a dict represeting a job."

    check_root_tag(xml_tree.tag, ['job'])

    ret = {}
    for child in xml_tree:
        current_tag = child.tag
        if current_tag == 'options':
            ret[current_tag] = options(child)
        else:
            ret[current_tag] = child.text
    ret.update(xml_tree.items())  # add any attributes of the root tag

    mandatory_tags = ['id', 'name', 'project']
    for tag in mandatory_tags:
        if ret.get(tag) is None:
            raise RundeckParseError('tag <{}> missing from job'.format(tag))

    return ret


def jobs(xml_tree):
    "Parse multiple jobs. Return a list containing the jobs."

    check_root_tag(xml_tree.tag, ['jobs'])

    if xml_tree.get('count') is None:
        raise RundeckParseError('attribute @count missing from jobs')

    jobs = [job(child) for child in xml_tree]
    ret = {
        'count': int(xml_tree.get('count')),
        'jobs': jobs
    }

    cnt = ret.get('count')
    ln = len(ret.get('jobs'))
    if cnt != ln:
        raise RundeckParseError('number of jobs(={}) and count(={})'
                                .format(ln, cnt) + ' are different')

    return ret


def date(xml_tree):
    "Parse a date-started or a date-ended. Return a dict."

    check_root_tag(xml_tree.tag, ['date-started', 'date-ended'])

    return {
        'time': xml_tree.text.strip(),
        'unixtime': xml_tree.get('unixtime').strip()
    }


def node(xml_tree):
    "Parse a node. Return a dict."
    if xml_tree.tag != 'node':
        raise RundeckParseError('expected tag <node>, got: <{}>'
                                .format(xml_tree.tag))
    return xml_tree.attrib


def nodes(xml_tree):
    "Parse multiple nodes. Return a list of nodes."

    check_root_tag(xml_tree.tag, ['successfulNodes', 'failedNodes'])

    return [node(child) for child in xml_tree]


def execution(xml_tree):
    "Parse a single execution. Return a dict."

    check_root_tag(xml_tree.tag, ['execution'])

    ret = {}
    for child in xml_tree:
        current_tag = child.tag
        if current_tag == 'job':
            ret[current_tag] = job(child)
        elif current_tag.startswith('date-'):
            ret[current_tag] = date(child)
        elif current_tag.endswith('Nodes'):
            ret[current_tag] = nodes(child)
        else:
            ret[current_tag] = child.text

    ret.update(xml_tree.items())
    return ret


def executions(xml_tree):
    "Parse multiple executions. Return a list."
    check_root_tag(xml_tree.tag, ['executions'])
    ret = {}
    if xml_tree.get('count') is None:
        raise RundeckParseError('attribute @count missing from executions')

    cnt = int(xml_tree.get('count'))
    ret['count'] = cnt
    ret['executions'] = [execution(c) for c in xml_tree]

    ln = len(ret['executions'])
    if cnt != ln:
        raise RundeckParseError('number of jobs(={}) and count(={})'
                                .format(ln, cnt) + ' are different')

    return ret


def option(xml_tree):
    "Parse a single option. Return a dict."

    check_root_tag(xml_tree.tag, ['option'])

    return xml_tree.attrib


def options(xml_tree):
    "Parse multiple options. Return a list."

    check_root_tag(xml_tree.tag, ['options'])
    return [option(c) for c in xml_tree]


def check_root_tag(actual, expected):
    if actual not in expected:
        msg = "expected tag one of: " + str(expected)
        msg += ", but got: '{}'".format(actual)
        raise RundeckParseError(msg)
