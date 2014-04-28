from pygranule.file_access_layer import FileAccessLayer, FileAccessLayerError
import paramiko
import stat

class SSHFileAccessLayer(FileAccessLayer):
    
    __implements__ = (FileAccessLayer,)

    def __init__(self, hostname, username, password=None, port=22):
        FileAccessLayer.__init__(self)
        # host info
        self.hostname = hostname
        self.username = username
        self.port = port
        self.password = password
        # for holding connection open
        self.client = None
        self.sftp = None

    def __del__(self):
        # close any open connection.
        self._close_connection()

    def _close_connection(self):
        try:
            self.sftp.close()
            self.client.close()
        except (NameError, AttributeError):
            pass

    def _get_cur_connection(self):
        return self.sftp, self.client

    def _get_new_connection(self):
        # close for good measure
        self._close_connection()
        # establish new connection
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.connect(self.hostname, self.port, username=self.username, password=self.password, timeout=10.0)
        self.sftp = self.client.open_sftp()
        return self.sftp, self.client
        
    def list_source_directory(self, directory):
        directory = directory.rstrip("/")
        files = []

        sftp = self._get_cur_connection()[0]

        try:
            for x in sftp.listdir_attr(directory):
                if stat.S_IFMT(x.st_mode) != stat.S_IFDIR:
                    files.append(directory + "/" + x.filename)
        except AttributeError:
            sftp = self._get_new_connection()[0]
            for x in sftp.listdir_attr(directory):
                if stat.S_IFMT(x.st_mode) != stat.S_IFDIR:
                    files.append(directory + "/" + x.filename)
        return files

    def copy_file(self, source, destination):
        try:
            sftp = self._get_cur_connection()[0]
            sftp.get(source, destination)
        except AttributeError:
            sftp = self._get_new_connection()[0]
            sftp.get(source, destination)

    def remove_source_file(self, filepath):
        try:
            sftp = self._get_cur_connection()[0]
            sftp.remove(filepath)
        except AttributeError:
            sftp = self._get_new_connection()[0]
            sftp.remove(filepath)

    def check_for_source_file(self, filepath):
        try:
            sftp = self._get_cur_connection()[0]
            try:
                sftp.lstat(filepath)
                status = True
            except IOError:
                status = False
        except AttributeError:
            sftp = self._get_new_connection()[0]
            try:
                sftp.lstat(filepath)
                status = True
            except IOError:
                status = False
        return status



