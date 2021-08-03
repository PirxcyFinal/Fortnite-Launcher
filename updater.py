import requests
import json

from util import logger, check_for_updates
from main import v

url = 'https://raw.githubusercontent.com/BayGamerYT/Fortnite-Launcher/main/'

log = logger('Updater')

def update():

    check = check_for_updates(v)

    if check == False:
        log.info('There is no updates. Exiting...')
        exit()
    else:
        log.info('Updating...')

    normal_files = ['updater.py', 'main.py', 'util.py', 'auth.py', 'INSTALL.bat', 'RUN.bat', 'UPDATE.bat', 'README.md', 'requirements.txt', 'LICENSE']
    json_files = ['config.json']
    updated_files = []

    for file in normal_files:
        log.info(f'\nChecking "{file}"...')

        not_found_flag = False

        response = requests.get(f'{url}{file}')

        if response.status_code == 200:
            
            try:
                old_file = open(file, 'r', encoding='utf-8')
            except FileNotFoundError:
                not_found_flag = True

            new_file = response.text

            if not_found_flag == False:
                if old_file.read() != new_file:
                    with open(file, 'w', encoding='utf-8') as f:
                        f.write(new_file)
                    if file == 'updater.py':
                        log.warn('"updater.py" got updated. Run UPDATE.bat again.')
                        exit()
                    updated_files.append(file)
                    log.info(f'Updated "{file}"\n')
                else:
                    log.info(f'Skipped "{file}". No changes found\n')
            else:
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(new_file)
                log.info(f'Created file "{file}"\n')

        elif response.status_code == 404:
            log.info(f'File {file} was not found.\n')
            continue

    for file in json_files:
        log.info(f'\nChecking json file "{file}"...')

        not_found_flag = False

        response = requests.get(f'{url}{file}')

        if response.status_code == 200:
            
            try:
                old_file = json.load(open(file, 'r', encoding='utf-8'))
            except FileNotFoundError:
                not_found_flag = True

            new_file = response.json()

            if not_found_flag == False:

                old_file_keys = old_file.keys()
                new_file_keys = new_file.keys()

                keys_to_add = []

                for i in new_file_keys:
                    if i not in old_file_keys:
                        keys_to_add.append(i)

                if len(keys_to_add) == 0:
                    log.info(f'Skipping {file}. No changes found.\n')
                else:
                    for i in keys_to_add:
                        old_file[i] = new_file[i]
                    with open(file, 'w', encoding='utf-8') as f:
                        json.dump(old_file, f, indent=4, ensure_ascii=False)
                    updated_files.append(file)
                    log.info(f'Updated {file}\n')

            else:
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(new_file)
                log.info(f'Created file "{file}"\n')

        elif response.status_code == 404:
            log.info(f'File {file} was not found.\n')
            continue

    if 'requirements.txt' in updated_files:
        log.info('\nUpdate finished. Run INSTALL.bat to install new requirements.')
    else:
        log.info('\nUpdate finished.')

update()