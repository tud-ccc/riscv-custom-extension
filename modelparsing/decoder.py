import logging

logger = logging.getLogger(__name__)


class Decoder:
    '''
    This class builds the code snippets, that are later integrated in the gem5
    decoder. It builds a custom decoder depending on the previously parsed
    models.
    '''
    def __init__(self, models):
        self._models = models
        self._defn = ''

    @property
    def models(self):
        return self._models

    @property
    def defn(self):
        return self._defn
