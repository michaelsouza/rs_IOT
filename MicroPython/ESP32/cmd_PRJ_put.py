#!venv/bin/python

import os
import sys
import json
from tqdm import tqdm


class FMT:
    '''Formatter class'''
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'             # close tag


def main() -> None:
    ''' main function'''

    print(f'\n{FMT.OKBLUE}{FMT.BOLD}{FMT.UNDERLINE}PROJECT UPLOADER:{FMT.ENDC}\u26A1\n')

    wd_project = sys.argv[1]  # project folder
    port = '/dev/ttyUSB0'

    for k, argv in enumerate(sys.argv):
        if argv == '-p':
            port = sys.argv[k+1]
    
    # read configs.json
    fname = os.path.join(wd_project, 'configs.json')
    configs = {}
    if os.path.exists(fname):
        with open(fname, 'r') as fp:            
            configs = json.load(fp)
        print(f'{FMT.OKBLUE}{FMT.BOLD}Configurations:{FMT.ENDC}')
        for row in json.dumps(configs, indent=2).split('\n'):
            print(f'\t{row}')
    else:
        print(f'{FMT.FAIL}{FMT.BOLD}WARNING: There is no configs.json file.\n{FMT.ENDC}')

    # get files to be uploaded
    fnames, max_len = [], 0
    print(f'\n{FMT.OKBLUE}{FMT.BOLD}File(s) to upload:{FMT.ENDC}')
    for fname in sorted(os.listdir(wd_project)):
        if fname == 'configs.json' or fname in configs['ignore']:
            continue
        fname = os.path.join(wd_project, fname)
        max_len = max([len(fname), max_len])
        fnames.append(fname)

    # print fnames with sizes in KB
    total_size = 0
    for k, fname in enumerate(fnames):
        fstat = os.stat(fname)
        total_size += fstat.st_size
        print(f'%2d. %-{max_len + 3}s %5.2f KB' % (k+1, fname, round(fstat.st_size / 1024,2)))
    print(((2+2+max_len + 3 + 9) * '-'))
    print(f'    %-{max_len + 3}s %5.2f KB' % ('Total', round(total_size / 1024,2)))

    ans = ''
    while ans not in ['y', 'n']:
        print(f'{FMT.WARNING}{FMT.BOLD}\nContinue [y]/n?{FMT.ENDC}  ', end='')
        ans = input()
        if ans == '':
            ans = 'y'

    if ans == 'n':
        print(f'{FMT.FAIL}{FMT.BOLD}\n\u26D4 Aborting\n\n{FMT.ENDC}')
        return

    print(f'{FMT.OKGREEN}{FMT.BOLD}\nUploading files\u261D\n{FMT.ENDC}')
    for fname in tqdm(fnames):        
        os.system(f'ampy --port {port} put {fname}')

    print(f'{FMT.WARNING}{FMT.BOLD}\nReseting device{FMT.ENDC}')
    os.system(f'ampy --port {port} run -n ./TOOLS/machine_reset.py')


    print(f'{FMT.OKGREEN}{FMT.BOLD}\nDone{FMT.ENDC}')


if __name__ == "__main__":
    main()
