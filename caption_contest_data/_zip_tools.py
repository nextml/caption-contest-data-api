"""
Usage:
    python zip_util.py zip
    python zip_util.py unzip

    Assumes the following directories exist with the following arguments:

    - responses (zip)
        Write the compressed CSV files as ZIP files to this directory
    - responses-unzipped (unzip)
        Write the uncompressed ZIP files as CSV files to this directory

"""
import os
import sys
from subprocess import DEVNULL, call

USAGE = 'USAGE: python zip_util.py [zip | unzip]'

def cli(operation):
    if call('git lfs env', shell=True,
                       stdout=DEVNULL, stderr=DEVNULL) != 0:
        print('''Git LFS is not installed.
Install Git LFS and run `git lfs pull` in this repository to pull the contents of the data files.''')
        return

    if operation == 'zip':
        in_dir = 'responses-unzipped'
        out_dir = 'responses'
        for file in os.listdir(in_dir):
            if 'DS_Store' in file:
                continue
            os.system(f'cd {in_dir}; zip {file}.zip {file}; mv {file}.zip ../{out_dir}')

    elif operation == 'unzip':
        in_dir = 'responses'
        out_dir = 'responses-unzipped'
        for file in os.listdir(in_dir):
            if 'DS_Store' in file:
                continue
            assert file[-4:] == '.zip'
            filename = file[:-4]
            os.system(f'cd {in_dir}; unzip {file}; mv {filename} ../{out_dir}')

    else:
        print(USAGE)
        sys.exit(2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(USAGE)
        sys.exit(2)

    cli(sys.argv[1])
