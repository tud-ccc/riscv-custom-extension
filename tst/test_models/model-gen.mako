<%
%>\
#include <cstdint>

% if model.ftype == 'R':
uint8_t opc    = ${model.opc};  // opc, 5 bits
uint8_t funct3 = ${model.funct3};  // funct3, 3 bits
uint8_t funct7 = ${model.funct7};  // funct7, 7 bits
% elif model.ftype == 'I':
uint8_t opc    = ${model.opc};  // opc, 5 bits
uint8_t funct3 = ${model.funct3};  // funct3, 3 bits
% endif

void ${model.name}(${opperands()})
${model.dfn}

<%def name="opperands()">
	% if model.rd is not '':
		${model.inttype} ${model.rd},
	% endif
	% if model.op1 is not '':
		${model.inttype} ${model.op1},
	% endif
	% if model.op2:
		${model.inttype} ${model.op2},
	% endif
</%def>