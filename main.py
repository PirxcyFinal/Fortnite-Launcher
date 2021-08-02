import subprocess
import crayons
import time

import psutil
import util
import json

import auth

log = util.logger('Main')

class Main:

    def __init__(self):
        self.configuration = None
        self.device_auths = None

    def _load_files(self):

        log.debug('Loading files...')

        self.configuration = util.load_config()
        self.device_auths = util.load_device_auths()

    def add_account(self):

        print()

        print(crayons.green('Add Account', bold=True))

        Auth = auth.AuthorizationCode()

        log.info(f'- Open this link {crayons.magenta(auth.AUTHORIZATION_CODE_URL)}\nAnd login with the account to add, then paste {crayons.yellow("ALL", bold=True)} the content of the page:\n')
        content = input('')
        print()
        log.info('Adding account...')
        try:
            data = json.loads(content)
            code = data['redirectUrl'].replace('com.epicgames.fortnite://fnauth/?code=', '')
        except Exception as e:
            log.error('An error ocurred processing the pasted data. Make sure you did it correctly')
            util.log_debug_traceback(e, log)
            return

        auth_session = Auth.authenticate(authorization_code=code)
        if auth_session[0] == False:
            log.error(f'An error ocurred while authenticating: {auth_session[1]["errorMessage"]}')
            return
        else:
            new_device_auth = Auth.generate_device_auths()

            if new_device_auth == False:
                log.error(f'An error ocurred while creating device auth: {new_device_auth[1]["errorMessage"]}')
                return
            else:
                account_info = Auth.get_account_info()
                if account_info[0] == False:
                    log.error(f'An error ocurred while requesting account info: {account_info[1]["errorMessage"]}')
                else:

                    new_data = {
                        "display_name": account_info[1]['displayName'],
                        "device_id": new_device_auth[1]['deviceId'],
                        "account_id": new_device_auth[1]['accountId'],
                        "secret": new_device_auth[1]['secret']
                    }

                    self.device_auths[account_info[1]['email']] = new_data
                    update = util.update_device_auths(self.device_auths)
                    if update == False:
                        util.log_debug_traceback(update[1], log)

                    Auth.kill_auth_session()

                    log.info(f'Account "{account_info[1]["displayName"]}" added successfully!')
                    time.sleep(3)
                    return

    def remove_account(self):

        print()

        print(crayons.red('Remove Account', bold=True))

        accounts = self.device_auths
        accountslist = [i for i in accounts]
        countlist = []
        count = 0
        
        for account in accounts.keys():
            count += 1
            countlist.append(count)
            print(f'{log.get_colored_box(crayons.green, str(count))} {accounts[account]["display_name"]} - {account}')
        
        print()

        while True:
            selected_acc = input(f'Select an account to remove: ')

            try:
                selected_acc.strip(' ')
                if int(selected_acc) not in countlist:
                    print(crayons.red('Invalid selection\n'))
                    continue

            except:
                print(crayons.red('Please enter a valid number\n'))
                continue

            int_selection = int(selected_acc) - 1
            break

        print()
        log.info('Removing account...')

        to_remove = accounts[accountslist[int_selection]]
        log.debug(f'Removing account: {to_remove}')

        Auth = auth.DeviceAuths()

        auth_session = Auth.authenticate(to_remove)

        if auth_session[0] == False:
            log.error(f'An error ocurred while authenticating: {auth_session[1]["errorMessage"]}')
            return
        else:
            delete = Auth.delete_device_auths(to_remove)

            if delete[0] == False:
                log.error(f'An error ocurred deleting device auths: {delete[1]["errorMessage"]}')
            else:
                kill = Auth.kill_auth_session()

                if kill[0] == False:
                    log.error(f'An error ocurred killing generated auth session: {kill[1]["errorMessage"]}')

                else:
                    newdata = self.device_auths.pop(accountslist[int_selection])
                    util.update_device_auths(newdata)
                    log.info(f'Account "{auth_session["display_name"]}" removed successfully!')
                    time.sleep(3)
                    return


    def start(self):

        print(f'\n{crayons.cyan("Fortnite Launcher", bold=True)} | {crayons.white("By Bay#1111", bold=True)}\n')

        while True:

            self._load_files()

            accounts = self.device_auths
            accountslist = [i for i in accounts]
            countlist = []
            count = 0

            for account in accounts.keys():
                count += 1
                countlist.append(count)
                print(f'{log.get_colored_box(crayons.green, str(count))} {accounts[account]["display_name"]} - {account}')

            print(f'\n{log.get_colored_box(crayons.blue, "A")} Add an account')
            print(f'{log.get_colored_box(crayons.blue, "R")} Remove an account\n')
            selected_acc = input(f'Select an option: ')

            try:
                selected_acc.strip(' ')

                if selected_acc.lower() == 'a':
                    self.add_account()
                    print()
                    continue

                if selected_acc.lower() == 'r':
                    if len(accountslist) == 0:
                        print('There is no accounts to remove!\n')
                    self.remove_account()
                    print()
                    continue

                if int(selected_acc) not in countlist:
                    print(crayons.red('Invalid selection\n'))
                    continue

            except:
                print(crayons.red('Select a valid option\n'))
                continue

            int_selection = int(selected_acc) - 1
            print()
        
            Auth = auth.DeviceAuths()
            auth_session = Auth.authenticate(accounts[accountslist[int_selection]])
            if auth_session[0] == False:
                log.error(f'An error ocurred while authenticating: {auth_session[1]["errorMessage"]}')
                continue
            exchange_code = Auth.get_exchange_code()
            if exchange_code[0] == False:
                log.error(f'An error ocurred while generating exchange_code: {exchange_code[1]["errorMessage"]}')
                Auth.kill_auth_session()
                continue

            exchangecode = exchange_code[1]['code']
            epicusername = auth_session[1]['displayName']
            epicuserid = auth_session[1]['account_id']
            game_executable = f'{self.configuration["fortnite_path"]}/FortniteGame/Binaries/Win64/FortniteLauncher.exe'
            additional_arguments = self.configuration['commandline_arguments']

            log.info('Launching...')
            l = subprocess.Popen([game_executable, '-EpicPortal', '-AUTH_LOGIN=unused', f'-AUTH_PASSWORD={exchangecode}', '-AUTH_TYPE=exchangecode', additional_arguments, f'-epicusername={epicusername}', f'-epicuserid={epicuserid}'])
            process = psutil.Process(pid=l.pid)
            log.debug(f'Launched "FortniteLauncher.exe" with additional commandline "{additional_arguments}"')
            log.debug('Waiting for "FortniteClient-Win64-Shipping.exe" to spawn...')

            wait = util.wait_for_game_launch(process)

            if wait[0] == True:
                log.info('Launched!')
                Auth.kill_auth_session()
                time.sleep(2)
                exit()
            else:
                log.error(f'Failed game launch.')
                Auth.kill_auth_session()
                print('\n')
                time.sleep(3)
                continue


Launcher = Main()
Launcher.start()
