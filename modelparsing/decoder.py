import logging
import os

from mako.template import Template

logger = logging.getLogger(__name__)


class Decoder:
    '''
    This class builds the code snippets, that are later integrated in the gem5
    decoder. It builds a custom decoder depending on the previously parsed
    models.
    '''

    def __init__(self, models):
        self._models = models
        self._decoder = ''

        self._dec_templ = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'decoder.mako')

    def gen_decoder(self):
        # iterate of all custom extensions and generate a custom decoder
        # first sort models:
        # opcode > funct3 (> funct7)
        logger.info('Generate custom decoder from models.')

        # sort models
        self._models.sort(key=lambda x: (x.opc, x.funct3, x.funct7))

        dec_templ = Template(r"""<%
dfn = {}
for model in models:
    if model.opc in dfn:
        dfn[model.opc].append(model)
    else:
        dfn[model.opc] = [model]
for opc, mdls in dfn.items():
    funct3 = {}
    for mdl in mdls:
        if mdl.form == 'I':
            funct3[mdl.funct3] = mdl
        else:
            if mdl.funct3 in funct3:
                funct3[mdl.funct3].append(mdl)
            else:
                funct3[mdl.funct3] = [mdl]
    dfn[opc] = funct3
%>\
% for opc,funct3_dict in dfn.items():
${hex(opc)}: decode FUNCT3 {
% for funct3, val in funct3_dict.items():
% if type(val) != list:
${hex(funct3)}: I32Op::${mdl.name}({${mdl.definition}}, uint32_t);
% else:
${hex(funct3)}: decode FUNCT7 {
% for mdl in val:
${hex(mdl.funct7)}: R32Op::${mdl.name}({${mdl.definition}});
% endfor
}
% endif
% endfor
}
% endfor""")

        self._decoder = dec_templ.render(models=self._models)

    @property
    def models(self):
        return self._models

    @property
    def decoder(self):
        return self._decoder
