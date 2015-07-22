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

import logging
from lxml import etree


__author__ = "Panagiotis Koutsourakis <kutsurak@ekt.gr>"


class RundeckParseError(Exception):
    def __init__(self, *args, **kwargs):
        "docstring"
        super(RundeckParseError, self).__init__(*args, **kwargs)


def parse_single_job(xml_tree):
    if xml_tree.tag != 'job':
        raise RundeckParseError('expected tag <job>, got: <{}>'
                                .format(xml_tree.tag))

    #  Creates a dictionary having as keys the tag names and as values
    #  the
    ret = {child.tag: child.text for child in xml_tree}
    ret.update(xml_tree.items())  # add any attributes of the root tag

    mandatory_tags = ['id', 'name', 'project']
    for tag in mandatory_tags:
        if ret.get(tag) is None:
            raise RundeckParseError('tag <{}> missing from job'.format(tag))

    return ret


def parse_multiple_jobs(xml_tree):
    if xml_tree.tag != 'jobs':
        raise RundeckParseError('expected tag <job>, got: <{}>'
                                .format(xml_tree.tag))

    if xml_tree.get('count') is None:
        raise RundeckParseError('attribute @count missing from jobs')

    jobs = [parse_single_job(child) for child in xml_tree]
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
