import sys
from pynsett.install import CustomFileDownloader

_commands = {'download': CustomFileDownloader()}

if __name__ == '__main__':
    try:
        argument = sys.argv[1]
        command = _commands[argument]
        command.run()
    except KeyError:
        raise ValueError('Could not find the right action to execute: ' + argument)

