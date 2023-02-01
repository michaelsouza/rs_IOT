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
    ''' main function
    '''
    print(
        f'\n{FMT.OKBLUE}{FMT.BOLD}\u26A1{FMT.UNDERLINE}PROJECT UPLOADER:\n{FMT.ENDC}')

    wd_project = sys.argv[1]  # project folder
    port = '/dev/ttyUSB0'

    for k, argv in enumerate(sys.argv):
        if argv == '-p':
            port = sys.argv[k+1]
    fname = os.path.join(wd_project, 'configs.json')
    if os.path.exists(fname):
        with open(fname, 'r', encoding='utf-8') as fp:
            config = json.load(fp)

        print(f'{FMT.OKBLUE}{FMT.BOLD}Configurations:{FMT.ENDC}')
        for row in json.dumps(config, indent=2).split('\n'):
            print(f'\t{row}')
    else:
        print(f'{FMT.FAIL}{FMT.BOLD}WARNING: There is no config.json file.\n{FMT.ENDC}')

    fnames = []
    print(f'{FMT.OKBLUE}{FMT.BOLD}File(s) to upload:\n{FMT.ENDC}')
    for k, fname in enumerate(sorted(os.listdir(wd_project))):
        if fname == 'configs.json':
            continue
        fname = os.path.join(wd_project, fname)
        print(f'\t{k+1}. {fname}')
        fnames.append(fname)

    ans = ''
    while ans not in ['y', 'n']:
        print(f'{FMT.WARNING}{FMT.BOLD}\nContinue [y]/n?{FMT.ENDC}  ', end='')
        ans = input()
        if ans == '':
            ans = 'y'

    if ans == 'n':
        print(f'{FMT.FAIL}{FMT.BOLD}\n\u26D4 Aborting\n\n{FMT.ENDC}')
        return

    print(f'{FMT.OKGREEN}{FMT.BOLD}\n\u261D Uploading files\n{FMT.ENDC}')
    for fname in tqdm(fnames):        
        os.system(f'ampy --port {port} put {fname}')

    print(f'{FMT.WARNING}{FMT.BOLD}\nDone (Remember to reset your device.)\n\n{FMT.ENDC}')


if __name__ == "__main__":
    main()
