import os
import sys


class CustomFileDownloader():
    _path = os.path.dirname(__file__)

    def run(self):
        sys.stderr.write('Installing the necessary files for Pynsett.\n')
        self.__download_coref()

    # Private

    def __download_coref(self):
        import urllib.request
        sys.stderr.write('Downloading the AllenNLP coref model. This might take a few minutes.\n')
        urllib.request.urlretrieve('https://allennlp.s3.amazonaws.com/models/coref-model-2018.02.05.tar.gz',
                                   os.path.join(self._path, '../data/coref-model-2018.02.05.tar.gz'))
