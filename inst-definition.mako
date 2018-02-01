<%
	names = extensions.funcnames
	matches = extensions.matchnames
	masks = extensions.masknames

	# remove items from lists, that are already in
	with open(opcc, 'r') as fh:
		content = fh.readlines()
		for i in range(0, len(names)):
			if names[i] in content:
				# can we assume, that in every list the corresponding elements
				# have the same index?
				# we must!
				names.remove(names[i])
				matches.remove(matches[i])
				masks.remove(masks[i])
%>\
% for i in range(0, len(names)):
{"${names[i]}",       "U",   "d,s,t",  ${matches[i]}, ${masks[i]}, match_opcode, 0 }
% endfor
