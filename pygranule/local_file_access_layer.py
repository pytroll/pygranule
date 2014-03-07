
from .file_access_layer import FileAccessLayer
import os
import shutil

class LocalFileAccessLayer(FileAccessLayer):
    def __init__(self):
        pass

    def list_directory(self, directory):
        """
        Lists directory on the source file system
        Returns a list of filenames including their full
        paths within the source file system.
        E.g. from .list_directory("/home/ftp/data/avhrr/") -->
        ["/home/ftp/data/avhrr/avh_noaa19_20140225_1400.hrp.bz2",
         "/home/ftp/data/avhrr/avh_noaa19_20140225_1401.hrp.bz2",
         "/home/ftp/data/avhrr/avh_noaa19_20140225_1403.hrp.bz2"]
        """
        return [ x for x in os.listdir(directory) if os.path.isfile(directory+'/'+x) ]

    def file_copy(self, source, destination):
        """
        Copes a single file from source path to destination.
        Destination must be a path within the local file system.
        """
        shutil.copyfile(source, destination)

