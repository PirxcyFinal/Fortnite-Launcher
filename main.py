v = '2.1'

try:
    import UEManifestReader
    import coloredlogs
    import aioconsole
    import webbrowser
    import subprocess
    import crayons
    import logging
    import asyncio
    import psutil
    import json
    import time
    import sys
    import os
except:
    print('It seems that some modules are missing. Run "INSTALL.bat" and try again.')
    input('Press ENTER to exit')

from os import kill
from modules import http

log = logging.getLogger('FortniteLauncher')

configuration = json.load(open('config.json', 'r', encoding = 'utf-8'))
auths = json.load(open('auths.json', 'r', encoding = 'utf-8'))

def get_colored_box(color, text):

    return f'{color("[")}{text}{color("]")}'

async def get_other_clients():

    log.debug('Looking for other running clients...')

    clients = []

    for p in psutil.process_iter(['name', 'pid']):
        if p.info['name'] == 'FortniteClient-Win64-Shipping.exe':
            clients.append(p.info['pid'])

    log.debug(f'Found {len(clients)} clients.')

    return clients

async def wait_for_game_spawn(process: psutil.Process, ignore: list):

    log.debug(f'Waiting for game to spawn...')

    while True:
        if process.is_running() == False:
            return False
        for p in psutil.process_iter(['name', 'pid']):
            if p.info['name'] == 'FortniteClient-Win64-Shipping.exe':
                if p.info['pid'] in ignore:
                    continue
                return True


async def add_account():

    log.debug('add_account flow started.')

    print()
    print(crayons.green('Add Account', bold=True))

    auth_type = configuration['auth_type']

    LAUNCHER_AUTHORIZATION_URL = 'https://www.epicgames.com/id/api/redirect?clientId=34a02cf8f4414e29b15921876da36f9a&responseType=code'
    LAUNCHER_AUTHORIZATION_URL_LOGIN = 'https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253D34a02cf8f4414e29b15921876da36f9a%2526responseType%253Dcode'

    IOS_AUTHORIZATION_URL = 'https://www.epicgames.com/id/api/redirect?clientId=3446cd72694c4a4485d81b77adbb2141&responseType=code'
    IOS_AUTHORIZATION_URL_LOGIN = 'https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253D3446cd72694c4a4485d81b77adbb2141%2526responseType%253Dcode'

    while True:
        user_selection = await aioconsole.ainput(f'Are you logged in to the required account in your web browser?\nType {crayons.white("1", bold=True)} if yes.\nType {crayons.white("2", bold=True)} if no.\n')

        user_logged = user_selection.strip(' ')

        if user_logged == '1':

            if auth_type == 'refresh':

                choosen_url = LAUNCHER_AUTHORIZATION_URL
            else:
                choosen_url = IOS_AUTHORIZATION_URL

        elif user_logged == '2':

            if auth_type == 'refresh':
                choosen_url = LAUNCHER_AUTHORIZATION_URL_LOGIN
            else:
                choosen_url = IOS_AUTHORIZATION_URL_LOGIN

        else:

            print('Select a valid option! Try again\n')

            continue
        break

    webbrowser.open_new_tab(choosen_url)

    print(choosen_url)
    if user_logged == '1':
        print('An epic games page should be opened in your web brower. Paste the authorizationCode here:')
    else:
        print('An epic games page should be opened in your web brower. Login on the required account and then paste the authorizationCode here:')
    
    user_code = await aioconsole.ainput('> ')

    code = user_code.strip(' ')

    if code in ['cancel', 'c']:
        log.debug('add_account flow stopped. User cancelled')
        print('Account add cancelled')
        return False

    if len(code) != 32:
        log.debug('add_account flow stopped. The code from the user was invalid.')
        print(f'Failed account add. The code\'s lenght is invalid. A valid authorization code is 32 characters long.')
        return False

    Auth = http.EpicAPI()

    if auth_type == 'refresh':

        auth_request = await Auth.authorization_code_auth(code)

        if 'errorCode' not in auth_request.text:

            oauth_json = auth_request.json()

            credentials = {}

            credentials['auth_type'] = 'refresh'
            credentials['refresh_token'] = str(oauth_json['refresh_token'])
            credentials['refresh_expires'] = int(time.time()) + oauth_json['refresh_expires']

            auths[oauth_json['displayName']] = credentials

            with open('auths.json', 'w', encoding='utf-8') as f:
                json.dump(auths, f, indent=4, ensure_ascii=False)

            log.debug('add_account flow completed without errors.')

            return f'Account "{oauth_json["displayName"]}" added successfully! (Note: this login will expire after 23 days of inactivity)'

        else:
            print(f'Authentication failed. {auth_request.json()["errorMessage"]}')
            log.debug('add_account flow stopped. The authentication failed.')
            return False
    
    elif auth_type == 'device':

        auth_request = await Auth.authorization_code_auth(code, client = http.Clients.fortniteIOSGameClient)

        if 'errorCode' not in auth_request.text:

            oauth_json = auth_request.json()

            device_create = await Auth.create_device_auth(oauth_json['access_token'], oauth_json['account_id'])

            if 'errorCode' not in device_create.text:

                device_json = device_create.json()

                credentials = {}
                
                credentials['auth_type'] = 'device'
                credentials['account_id'] = device_json['accountId']
                credentials['device_id'] = device_json['deviceId']
                credentials['secret'] = device_json['secret']


                auths[oauth_json['displayName']] = credentials

                with open('auths.json', 'w', encoding='utf-8') as f:
                    json.dump(auths, f, indent=4, ensure_ascii=False)

                await Auth.kill_oauth_session(oauth_json['access_token'])

                return f'Account "{oauth_json["displayName"]}" added successfully!'

            else:
                print(f'Device auth creation failed. {auth_request.json()["errorMessage"]}')
                log.debug('add_account flow stopped. The authentication failed.')
                return False

        else:
            print(f'Authentication failed. {auth_request.json()["errorMessage"]}')
            log.debug('add_account flow stopped. The authentication failed.')
            return False


async def remove_account():

    log.debug('remove_account flow started.')

    print()
    print(crayons.red('Remove Account', bold=True))

    while True:

        account_list = list(auths.keys())
        countlist = []
        count = 0

        for account in account_list:
            count += 1
            countlist.append(count)
            print(f'{get_colored_box(crayons.red, str(count))} {account}')

        print(f'{get_colored_box(crayons.green, "C")} Cancel\n')


        user_selection = await aioconsole.ainput(f'Select an account: ')

        try:
            user_selection.strip(' ')

            if user_selection.lower() in ['c', 'cancel']:
                print(crayons.red('Account remove cancelled.'))
                log.debug('remove_account flow cancelled by user.')
                return False

            if int(user_selection) not in countlist:
                print(crayons.red('Invalid selection\n'))
                continue

            else:
                break
        except:
            print(crayons.red('Select a valid option\n'))
            continue

    credentials = auths[account_list[int(user_selection) - 1]]

    if credentials['auth_type'] == 'refresh':

        if int(time.time()) > credentials['refresh_expires']:

            del auths[account_list[int(user_selection) - 1]]

            with open('auths.json', 'w', encoding='utf-8') as f:
                json.dump(auths, f, indent=4, ensure_ascii=False)

            log.debug('remove_account flow completed. The saved refresh wasn\'t valid and removed from auths.json file')
            print('Account removed successfully.')
            return True
        
        else:

            Auth = http.EpicAPI()
            auth_request = await Auth.refresh_token_auth(refresh_token = credentials['refresh_token'])

            if 'errorCode' not in auth_request.text:

                oauth_json = auth_request.json()
                
                kill_request = await Auth.kill_oauth_session(oauth_json['access_token'])

                if kill_request not in [401, 403]:

                    del auths[account_list[int(user_selection) - 1]]

                    with open('auths.json', 'w', encoding='utf-8') as f:
                        json.dump(auths, f, indent=4, ensure_ascii=False)

                    log.debug('remove_account flow completed without errors')
                    print('Account removed successfully.')
                    return True

            else:

                print(f'Authentication failed. {auth_request.json()["errorMessage"]}')
                print('Removing account from auths.json file anyway.')

                del auths[account_list[int(user_selection) - 1]]

                with open('auths.json', 'w', encoding='utf-8') as f:
                    json.dump(auths, f, indent=4, ensure_ascii=False)

                log.debug('remove_account flow failed successfully. Authentication failed but removed from auths.json anyways')

                print('Account removed.') # task failed successfully
                return True

    elif credentials['auth_type'] == 'device':

        Auth = http.EpicAPI()

        auth_request = await Auth.device_auths_auth(credentials)

        if 'errorCode' not in auth_request.text:

            oauth_json = auth_request.json()

            kill_device = await Auth.delete_device_auth(oauth_json['access_token'], account_id=credentials['account_id'], device_id=credentials['device_id'])

            if kill_device.status_code not in [401, 403]:

                del auths[account_list[int(user_selection) - 1]]

                with open('auths.json', 'w', encoding='utf-8') as f:
                    json.dump(auths, f, indent=4, ensure_ascii=False)

                await Auth.kill_oauth_session(oauth_json['access_token'])

                log.debug('remove_account flow completed without errors')
                print('Account removed successfully.')
                return True

            else:

                print(f'Device auth delete failed. {kill_device.json()["errorMessage"]}')
                print('Removing account from auths.json anyway. Change the account password to make sure you kill the device auth.')

                del auths[account_list[int(user_selection) - 1]]

                with open('auths.json', 'w', encoding='utf-8') as f:
                    json.dump(auths, f, indent=4, ensure_ascii=False)

                log.debug('remove_account flow failed successfully. Device delete failed but removed from auths.json anyways')

                await Auth.kill_oauth_session(oauth_json['access_token'])

                print('Account removed.') # task failed successfully
                return True

        else:

                print(f'Authentication failed. {auth_request.json()["errorMessage"]}')
                print('Removing account from auths.json anyway.')

                del auths[account_list[int(user_selection) - 1]]

                with open('auths.json', 'w', encoding='utf-8') as f:
                    json.dump(auths, f, indent=4, ensure_ascii=False)

                log.debug('remove_account flow failed successfully. Authentication failed but removed from auths.json anyways')

                print('Account removed.') # task failed successfully
                return True

    
async def launch_game(exchange_code: str, launch_command: str):

    log.debug('Launching game...')

    fortnite_path = configuration['fortnite_path']
    executable_args = launch_command
    additional_args = configuration["commandline_arguments"]

    log.debug('Preparing command line arguments.')

    args = [
        executable_args,
        '-AUTH_LOGIN=unused',
        f'-AUTH_PASSWORD={exchange_code}',
        '-AUTH_TYPE=exchangecode',
        '-epicapp=Fortnite',
        '-epicenv=Prod',
        '-EpicPortal',
    ]

    for i in additional_args:
        if i.startswith('-'):
            args.append(i)

    ignore_list = await get_other_clients()

    log.debug(f'Starting FortniteLauncher.exe with args {args}...')

    FortniteLauncher = subprocess.Popen([f'{fortnite_path}/FortniteGame/Binaries/Win64/FortniteLauncher.exe'] + args, cwd=f'{fortnite_path}/FortniteGame/Binaries/Win64/', stdout=subprocess.DEVNULL)
    process = psutil.Process(pid = FortniteLauncher.pid)

    wait_spawn = await wait_for_game_spawn(process, ignore_list)

    if wait_spawn == True:

        log.debug('Game launched correctly.')
        return True

    else:

        log.debug('Game did\'nt launch.')
        return False


async def start():

    if '--debug' in sys.argv:
        coloredlogs.install(
            level='DEBUG'
        )

    while True:

        print()

        print(f'\n{crayons.cyan("Fortnite Launcher", bold=True)} | {crayons.white(f"Beta v{v}", bold=True)}\n')

        try:
            configuration = json.load(open('config.json', 'r', encoding = 'utf-8'))

            if configuration['auth_type'] not in ['refresh', 'device']:
                print('Error, the choosen auth type in configuration file isn\'t valid. Auth type must be "refresh" or "device".')
                await aioconsole.ainput('Press ENTER to exit')
                exit()

        except Exception as e:
            print(f'An error ocurred loading config.json file. {e}')
            await aioconsole.ainput('Press ENTER to exit')
            exit()

        try:
            auths = json.load(open('auths.json', 'r', encoding = 'utf-8'))
        except Exception as e:
            print(f'An error ocurred loading auths.json file. {e}')
            await aioconsole.ainput('Press ENTER to exit')
            exit()

        account_list = list(auths.keys())
        countlist = []
        count = 0

        for account in account_list:
            count += 1
            countlist.append(count)
            print(f'{get_colored_box(crayons.green, str(count))} {account}')

        print(f'\n{get_colored_box(crayons.blue, "A")} Add an account')
        print(f'{get_colored_box(crayons.blue, "R")} Remove an account\n')
        print(f'{get_colored_box(crayons.red, "X")} Exit\n')

        user_selection = await aioconsole.ainput(f'Select an option: ')

        try:
            user_selection.strip(' ')

            if user_selection.lower() == 'x':
                exit()

            if user_selection.lower() == 'a':
                add = await add_account()
                if isinstance(add, str):
                    print(add)
                continue

            if user_selection.lower() == 'r':
                if len(account_list) == 0:
                    print('There is no accounts to remove!\n')
                    continue
                
                else:
                    await remove_account()
                    continue

            if int(user_selection) not in countlist:
                print(crayons.red('Invalid selection\n'))
                continue

        except:
            print(crayons.red('Select a valid option\n'))
            continue

        selected_account = int(user_selection) - 1

        game_folder = configuration['fortnite_path']

        if os.path.isdir(game_folder) == False:
            print('Seems like the fortnite path in configuration is not valid. Check it and try again')
            await aioconsole.ainput('Press ENTER to exit')

        else:

            credentials = auths[account_list[selected_account]]

            auth_type = credentials['auth_type']

            if auth_type == 'refresh':

                if int(time.time()) > credentials['refresh_expires']:
                    print('The credentials of this account have expired. Re-add the account and try again')

                Auth = http.EpicAPI()
                auth_request = await Auth.refresh_token_auth(refresh_token = credentials['refresh_token'])

                if 'errorCode' not in auth_request.text:

                    oauth_json = auth_request.json()

                    credentials['refresh_token'] = str(oauth_json['refresh_token'])
                    credentials['refresh_expires'] = int(time.time()) + oauth_json['refresh_expires']

                    auths[account_list[selected_account]] = credentials

                    with open('auths.json', 'w', encoding='utf-8') as f:
                        json.dump(auths, f, indent=4, ensure_ascii=False)

                    exchange_request = await Auth.get_exchange_code(oauth_json['access_token'])

                    if 'errorCode' not in exchange_request.text:

                        exchange_json = exchange_request.json()
                        launch_command = ''

                        launch_info = await Auth.get_launch_info()
                        if launch_info.status_code == 200:
                            log.debug('Using baydev api launch args.')
                            launch_command = launch_info.json()['data']['launch_args']
                            log.debug(f'Launch args for build {launch_info.json()["data"]["build"]}')

                        else:
                            log.debug('Using epicgames manifest launch args.')
                            Reader = UEManifestReader.UEManifestReader()
                            manifest = await Reader.download_manifest()
                            launch_command = manifest['LaunchCommand']

                        print('Launching...')

                        launch_try = await launch_game(exchange_json['code'], launch_command)

                        if launch_try == False:
                            print('Failed game launch.')
                            await asyncio.sleep(2)
                            continue

                        else:

                            print('Launched.')
                            await asyncio.sleep(3)
                            exit()

                    else:
                        print(f'Exchange code request failed. {exchange_request.json()["errorMessage"]}')
                        continue

                else:
                    print(f'Authentication failed. {auth_request.json()["errorMessage"]}')
                    continue

            else:

                Auth = http.EpicAPI()
                auth_request = await Auth.device_auths_auth(credentials)

                if 'errorCode' not in auth_request.text:

                    oauth_json = auth_request.json()

                    exchange_request = await Auth.get_exchange_code(oauth_json['access_token'])

                    if 'errorCode' not in exchange_request.text:

                        exchange_auth = exchange_request.json()

                        launcher_auth_request = await Auth.exchange_code_auth(exchange_auth['code'])

                        if 'errorCode' not in launcher_auth_request.text:

                            launcher_auth = launcher_auth_request.json()

                            launcher_exchange_request = await Auth.get_exchange_code(launcher_auth['access_token'])

                            if 'errorCode' not in launcher_exchange_request.text:

                                final_exchange_json = launcher_exchange_request.json()

                                launch_command = ''

                                launch_info = await Auth.get_launch_info()
                                if launch_info.status_code == 200:
                                    log.debug('Using baydev api launch args.')
                                    launch_command = launch_info.json()['data']['launch_args']

                                else:
                                    log.debug('Using epicgames manifest launch args. (This may take a while)')
                                    Reader = UEManifestReader.UEManifestReader()
                                    manifest = await Reader.download_manifest()
                                    launch_command = manifest['LaunchCommand']

                                print('Launching...')

                                launch_try = await launch_game(final_exchange_json['code'], launch_command)

                                if launch_try == False:
                                    print('Failed game launch.')
                                    await Auth.kill_oauth_session(oauth_json['access_token'])
                                    await asyncio.sleep(2)
                                    continue

                                else:

                                    print('Launched.')
                                    await asyncio.sleep(3)
                                    exit()
                            
                            else:
                                print(f'Launcher exchange code generate failed. {launcher_exchange_request.json()["errorMessage"]}')
                                await Auth.kill_oauth_session(oauth_json['access_token'])
                                continue

                        else:
                            print(f'Launcher exchange auth failed. {launcher_auth_request.json()["errorMessage"]}')
                            await Auth.kill_oauth_session(oauth_json['access_token'])
                            continue

                    else:
                        print(f'Exchange code request failed. {exchange_request.json()["errorMessage"]}')
                        await Auth.kill_oauth_session(oauth_json['access_token'])
                        continue
                
                else:
                    print(f'Authentication failed. {auth_request.json()["errorMessage"]}')
                    continue



if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())