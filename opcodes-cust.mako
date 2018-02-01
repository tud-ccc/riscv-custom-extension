<%
%>\
% for operation in operations:
% if operation.form == 'regreg':
${operation.name} rd rs1 rs2 31..25=${operation.funct7} 14..12=${operation.funct3} 6..2=${operation.opc} 1..0=3
% elif operation.form == 'regimm':
${operation.name} rd rs1 imm12 14..12=${operation.funct3} 6..2=${operation.opc} 1..0=3
% else:
Format not supported.
<% return STOP_RENDERING %>
%endif
% endfor
