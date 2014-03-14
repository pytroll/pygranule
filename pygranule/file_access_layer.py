
class FileAccessLayerError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class FileAccessLayer(object):
    """
    A model layer for abstracting various file
    access routines, such as file listing and file transfer.
    This class provides the basic interface for particular
    implementations based on particular access protocols,
    such as the local file systems, ftp and ssh.
    """
    def __init__(self):
        pass

    def list_source_directory(self, directory):
        """
        Lists directory on the source file system
        Returns a list of filenames including their full
        paths within the source file system.
        E.g. from .list_directory("/home/ftp/data/avhrr/") -->
        ["/home/ftp/data/avhrr/avh_noaa19_20140225_1400.hrp.bz2",
         "/home/ftp/data/avhrr/avh_noaa19_20140225_1401.hrp.bz2",
         "/home/ftp/data/avhrr/avh_noaa19_20140225_1403.hrp.bz2"]
        """
        pass

    def list_local_directory(self, directory):
        """
        Lists directory on the local file system
        Returns a list of filenames including their full
        paths within the source file system.
        E.g. from .list_directory("/home/ftp/data/avhrr/") -->
        ["/home/ftp/data/avhrr/avh_noaa19_20140225_1400.hrp.bz2",
         "/home/ftp/data/avhrr/avh_noaa19_20140225_1401.hrp.bz2",
         "/home/ftp/data/avhrr/avh_noaa19_20140225_1403.hrp.bz2"]
        """
        pass

    def copy_file(self, source, destination):
        """
        Copes a single file from source path to destination.
        Destination must be a path within the local file system.
        """
        pass

    def remove_source_file(self, filename):
        """
        Deletes a single file at source.
        """
        pass

    def remove_local_file(self, filename):
        """
        Deletes a single file at source.
        """
        pass

    def check_for_local_file(self, filename):
        """
        Checks if file at path filename exists.
        Returns True or False.
        """

    

    
