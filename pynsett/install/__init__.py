import os
import sys


class CustomFileDownloader():
    _path = os.path.dirname(__file__)

    def run(self):
        sys.stderr.write('Installing the necessary files for Pynsett.\n')
        self.__download_glove()

    # Private

    def __download_glove(self):
        import urllib.request
        sys.stderr.write('Downloading the Glove dataset. This might take a few minutes.\n')
        urllib.request.urlretrieve('http://nlulite.com/download/glove',
                                   os.path.join(self._path, '../data/glove.6B.50d.txt'))
