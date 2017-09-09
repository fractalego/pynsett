import os
from setuptools.command.install import install


class CustomInstaller(install):
    _path = os.path.dirname(__file__)

    def run(self):
        install.run(self)
        self.__download_glove()
        self.__download_spacy_datasets()

    # Private

    def __download_glove(self):
        import urllib.request
        urllib.request.urlretrieve('http://nlulite.com/download/glove',
                                   os.path.join(self._path, '../../data/glove.6B.50d.txt'))

    def __spacy_datasets(self):
        import os
        os.system('python -m spacy download m')