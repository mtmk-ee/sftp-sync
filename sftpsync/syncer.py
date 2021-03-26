from threading import local
import pysftp
from pathlib import Path
import os
import datetime
import enum

class Comparison(enum.Enum):
    RemoteNewer = 0,
    LocalNewer = 0,
    Equal = 0,


class FileSync:

    def __init__(self, sftp: pysftp.Connection, local_dir: str, remote_dir: str):
        self.sftp = sftp
        self.local_dir = local_dir
        self.remote_dir = remote_dir
        self.verbose = True

        self.sftp.chdir(self.remote_dir)

    def put_dir(self, local_dir: str, remote_dir: str, preserve_mtime=True):
        for entry in os.listdir(local_dir):
            remotepath = remote_dir + "/" + entry
            localpath = os.path.join(local_dir, entry)
            if not os.path.isfile(localpath):
                try:
                    self.sftp.mkdir(remotepath)
                except OSError:
                    pass
                self.put_dir(localpath, remotepath, preserve_mtime)
            else:
                #self.sftp.put(localpath, remotepath, preserve_mtime=preserve_mtime)
                self.put_if_local_is_newer(localpath, remotepath, preserve_mtime)

    def put_root(self):
        self.put_dir(self.local_dir, self.remote_dir)

    def get_remote_modified_time(self, remote_dir) -> int:
        stat = self.sftp.stat(remote_dir)
        return int(stat.st_mtime)

    def get_local_modified_time(self, local_dir) -> int:
        return int(os.stat(local_dir).st_mtime)

    def put_file(self, localpath, remotepath, preserve_mtime=True):
        self.sftp.put(localpath, remotepath, preserve_mtime=preserve_mtime)

    def put_if_local_is_newer(self, localpath: str, remotepath: str, preserve_mtime=True):
        local_exists = os.path.exists(localpath)
        remote_exists = self.sftp.exists(remotepath)

        if local_exists and not remote_exists:
            if self.verbose:
                print(f'Sending new file to remote: {localpath}')
            self.put_file(localpath, remotepath, preserve_mtime)
        elif not local_exists and remote_exists:
            if self.verbose:
                print(f'Removing file from remote: {remotepath}')
            self.sftp.remove(remotepath)
        else:
            local_time = self.get_local_modified_time(localpath)
            remote_time = self.get_remote_modified_time(remotepath)
            if local_time > remote_time:
                if self.verbose:
                    print(f'Sending updated file to remote: {localpath}')

                self.put_file(localpath, remotepath, preserve_mtime)
                self.sftp.sftp_client.utime(remotepath, (local_time, local_time))

