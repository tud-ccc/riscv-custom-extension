<%
	num_models = len(models)
	names = [model.name for model in models]
%>\
% for i in range(0, num_models):
${names[i]} rd rs1 rs2 31..25=${i} 14..12=${i} 6..2=0x02 1..0=3
% endfor
