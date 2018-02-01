<%
	# remove items from lists, that are already in
	with open(opcc, 'r') as fh:
		content = fh.readlines()
		for inst in insts:
			if inst.name in content:
				# can we assume, that in every list the corresponding elements
				# have the same index?
				# we must!
				logger.info('Instruction {} already defined. Skip instertion'.format(inst.name))
				insts.remove(inst)
%>\
% for inst in insts:
{"${inst.name}",       "U",   "${inst.operands}",  ${inst.matchname}, ${inst.maskname}, match_opcode, 0 }
% endfor