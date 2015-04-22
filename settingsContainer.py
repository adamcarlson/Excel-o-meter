__author__ = 'Adam Carlson'

import pickle
import glob

class Settings(object):
    def __init__(self, root, **kwargs):
        self.filename = kwargs.pop('filename', '')
        self.root = root
        if self.filename is not '':
            file = open(self.filename, 'rb')
            self.filePaths, self.lastFolderPath = pickle.Unpickler(file).load()
            file.close()
        else:
            self.filePaths = []
            self.lastFolderPath = ''

    def add_recent(self, filename):
        if filename in self.filePaths:
            self.filePaths.pop(self.filePaths.index(filename))
        self.filePaths.insert(0, filename)

        if len(self.filePaths) > 10:
            self.filePaths.pop()

    def get_quick_files(self):
        x = glob.glob(self.lastFolderPath + '/' + '*.sac')
        print(x)
        return x


    def save_settings(self):
        if self.filename is '':
            file = open('settings.dat', 'wb')
        else:
            file = open(self.filename, 'wb')
        pickle.Pickler(file).dump((self.filePaths, self.lastFolderPath))
        file.close()