## Copyright (c) 2018 TU Dresden
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met: redistributions of source code must retain the above copyright
## notice, this list of conditions and the following disclaimer;
## redistributions in binary form must reproduce the above copyright
## notice, this list of conditions and the following disclaimer in the
## documentation and/or other materials provided with the distribution;
## neither the name of the copyright holders nor the names of its
## contributors may be used to endorse or promote products derived from
## this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##
## Authors: Robert Scheffel
<%
%>\
#include <cstdint>

% if model.cycles:
uint8_t cycles = ${model.cycles}; // cycle count
% endif
% if model.ftype == 'R':
uint8_t opc    = ${model.opc};  // opc, 5 bits
uint8_t funct3 = ${model.funct3};  // funct3, 3 bits
uint8_t funct7 = ${model.funct7};  // funct7, 7 bits
% elif model.ftype == 'I':
uint8_t opc    = ${model.opc};  // opc, 5 bits
uint8_t funct3 = ${model.funct3};  // funct3, 3 bits
% endif

${model.rettype} ${model.name}(${opperands()})
${model.dfn}

<%def name="opperands()">
	% if model.rd and model.op1 and model.op2:
		${model.inttype} ${model.rd},
        ${model.inttype} ${model.op1},
        ${model.inttype} ${model.op2}
	% endif
	% if model.rd and not model.op1 and model.op2:
        ${model.inttype} ${model.rd},
        ${model.inttype} ${model.op2}   
	% endif
	% if model.rd and model.op1 and not model.op2:
        ${model.inttype} ${model.rd},
        ${model.inttype} ${model.op1}
	% endif
    % if not model.rd and model.op1 and model.op2:
        ${model.inttype} ${model.op1},
        ${model.inttype} ${model.op2}
    % endif
    % if model.rd and not model.op1 and not model.op2:
        ${model.inttype} ${model.rd}
    % endif
    % if not model.rd and model.op1 and not model.op2:
        ${model.inttype} ${model.op1}
    % endif
    % if not model.rd and not model.op1 and model.op2:
        ${model.inttype} ${model.op2}
    % endif
    % if not model.rd and not model.op1 and not model.op2:
    % endif
</%def>