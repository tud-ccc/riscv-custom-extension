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