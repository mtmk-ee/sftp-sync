import argparse
from pathlib import Path
import pysftp
import time

from syncer import FileSync


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str, help='host name')
    parser.add_argument('-u', type=str, default=None, help='remote username', required=True)
    parser.add_argument('-p', type=str, default=None, help='remote password', required=True)
    args = parser.parse_args()

    host = args.host
    username = args.u
    password = args.p

    remote_dir = f'/home/{username}/synced'
    local_dir = str(Path.home() / 'synced')

    print(f'Remote host: {host}')
    print(f'Remote user: {username}')
    print(f'Local sync directory:  {local_dir}')
    print(f'Remote sync directory: {remote_dir}')

    try:
        with pysftp.Connection(host=host, username=username, password=password) as sftp:
            fs = FileSync(sftp, local_dir, remote_dir)

            try:
                while True:
                    fs.put_root()
                    time.sleep(1)
            except KeyboardInterrupt:
                print('Closing connection')
    except:
        raise


if __name__ == '__main__':
    main()

