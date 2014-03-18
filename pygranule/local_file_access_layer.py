
from .file_access_layer import FileAccessLayer
from .file_set import FileSet
import os
import shutil

class LocalFileAccessLayer(FileAccessLayer):
    def __init__(self):
        pass

    def list_source_directory(self, directory):
        """
        Lists directory on the source file system
        Returns a FileSet of filenames including their full
        paths within the source file system.
        E.g. from .list_directory("/home/ftp/data/avhrr/") -->
        FileSet(["/home/ftp/data/avhrr/avh_noaa19_20140225_1400.hrp.bz2",
         "/home/ftp/data/avhrr/avh_noaa19_20140225_1401.hrp.bz2",
         "/home/ftp/data/avhrr/avh_noaa19_20140225_1403.hrp.bz2"])
        """
        return FileSet([ directory + '/' + x for x in os.listdir(directory) if os.path.isfile(directory+'/'+x) ])

    def list_local_directory(self, directory):
        """
        Lists directory on the local file system
        Returns a list of filenames including their full
        paths within the source file system.
        E.g. from .list_directory("/home/ftp/data/avhrr/") -->
        FileSet(["/home/ftp/data/avhrr/avh_noaa19_20140225_1400.hrp.bz2",
         "/home/ftp/data/avhrr/avh_noaa19_20140225_1401.hrp.bz2",
         "/home/ftp/data/avhrr/avh_noaa19_20140225_1403.hrp.bz2"])
        """
        return self.list_source_directory(directory)

    def copy_file(self, source, destination):
        """
        Copes a single file from source path to destination.
        Destination must be a path within the local file system.
        """
        shutil.copyfile(source, destination)

    def remove_source_file(self, filename):
        """
        Deletes a single file at source.
        """
        os.remove(filename)

    def remove_local_file(self, filename):
        """
        Deletes a single file at source.
        """
        self.remove_source_file(filename)

    def check_local_file(self, filename):
        """
        Checks if file at path filename exists.
        Returns True or False.
        """
        return os.path.isfile(filename)

