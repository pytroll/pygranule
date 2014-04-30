
from .file_access_layer import FileAccessLayer

class LocalFileAccessLayer(FileAccessLayer):

    __implements__ = (FileAccessLayer,)

    def __init__(self):
        FileAccessLayer.__init__(self)

    def list_source_directory(self, directory):
        """
        Lists directory on the source file system
        Returns a list of filename paths.
        E.g. from .list_directory("/home/ftp/data/avhrr/") -->
        ["/home/ftp/data/avhrr/avh_noaa19_20140225_1400.hrp.bz2",
         "/home/ftp/data/avhrr/avh_noaa19_20140225_1401.hrp.bz2",
         "/home/ftp/data/avhrr/avh_noaa19_20140225_1403.hrp.bz2"]
        """
        return self.list_local_directory(directory)

    def _copy_file(self, source, destination):
        """
        Copes a single file from source path to destination.
        Destination must be a path within the local file system.
        """
        self.shutil.copyfile(source, destination)

    def remove_source_file(self, filename):
        """
        Deletes a single file at source.
        """
        self.remove_local_file(filename)

    def check_for_source_file(self, filename):
        """
        Checks if file at path filename exists.
        Returns True or False.
        """
        return self.check_for_local_file(filename)


