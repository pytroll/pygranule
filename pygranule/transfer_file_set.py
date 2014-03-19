from .file_set import FileSet
import os

class TransferFileSet(FileSet):
    """
    An extension to the FileSet container, handling
    easy execution of file transfers. Accepts an additional
    list of paths, and a file access layer object to handle file 
    transfer from source to destination.
    """
    def __init__(self, source_paths=None, destination_paths=None, file_access_layer=None):
        FileSet.__init__(self,source_paths)
        # Now ammend dictionary to contain
        # source destination pairs
        for i, f in enumerate(source_paths):
            filename = os.path.basename(f)
            self.filedict[filename] = (self.filedict[filename], destination_paths[i])
        # set the file_access_layer
        self.file_access_layer = file_access_layer

    def add(self, source_path, destination_path):
        self.filedict[os.path.basename(source_path)] = (source_path, destination_path)
     
    def transfer(self):
        """
        If file access layer exists, execute transfers of
        files from source path to destination path, according
        to path pairs from the paths() method.
        """
        if self.file_access_layer is not None:
            for (spath, dpath) in self.paths():
                self.file_access_layer.copy_file(spath, dpath)
                
    def source_paths(self):
        return [ x[0] for x in self.paths() ]

    def destination_paths(self):
        return [ x[1] for x in self.paths() ]

    
