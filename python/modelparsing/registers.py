# Copyright (c) 2018 TU Dresden
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Robert Scheffel

import logging
import re

logger = logging.getLogger(__name__)


class Registers:
    '''
    Defined custom registers.
    '''

    def __init__(self, regfile):
        '''
        Init method, that takes the location of
        the register file as an argument.
        '''

        logger.info("Parsing register file @ %s" % regfile)

        self.parse_file(regfile)

    def parse_file(self, file):
        '''
        Parse the file and search for all necessary information.
        '''

        with open(file, 'r') as fh:
            content = fh.readlines()

        regs = []
        prog = re.compile(r"^[#]define\s([\w_-]+)\s+(0x[0-9a-fA-F]{8})$")

        for line in content:
            match = prog.match(line)
            if match:
                logger.debug("Defined register: {}".format(match.group()))
                regs.append(match)

        self._regmap = {}

        for match in regs:
            self._regmap[match.group(1)] = int(match.group(2), 16)

    @property
    def regmap(self):
        return self._regmap
