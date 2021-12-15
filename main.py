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
except ModuleNotFoundError:
  print('It seems that some modules are missing. Run "INSTALL.bat" and try again.')
  input('Press ENTER to exit')
  exit()
except Exception as e:
  print(f"An Unknown Error Importing Had Occured" + e)

from modules import http

v = '2.0'
AUTHORIZATION_URL = 'https://www.epicgames.com/id/api/redirect?clientId=34a02cf8f4414e29b15921876da36f9a&responseType=code'
AUTHORIZATION_URL_LOGIN = 'https://www.epicgames.com/id/logout?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253D34a02cf8f4414e29b15921876da36f9a%2526responseType%253Dcode'
log = logging.getLogger('FortniteLauncher')

configuration = json.load(
  open(
    'config.json', 
    'r', 
    encoding = 'utf-8'
  )
)
auths = json.load(
  open(
    'auths.json', 
    'r', 
    encoding = 'utf-8'
  )
)
``
def get_colored_box(color, text):
  return f'{color("[")}{text}{color("]")}'

async def get_other_clients():
  log.debug('Looking for other running clients...')
  clients = []
  for p in psutil.process_iter(
    [
      'name', 
      'pid'
    ]
  ):
    if p.info['name'] == 'FortniteClient-Win64-Shipping.exe':
      clients.append(p.info['pid'])
    log.debug(f'Found {len(clients)} clients.')
    return clients

async def wait_for_game_spawn(process: psutil.Process, ignore: list):
  log.debug(f'Waiting for game to spawn...')
  while True:
    if process.is_running() == False:
      return False
    for p in psutil.process_iter(
      [
        'name', 
        'pid'
      ]
    ):
      if p.info['name'] == 'FortniteClient-Win64-Shipping.exe':
        if p.info['pid'] in ignore:
          continue
        return True


async def add_account():
  log.debug('add_account flow started.')
  print()
  print(
    crayons.green(
      'Add Account', 
      bold=True
    )
  )
  while True:
    user_selection = await aioconsole.ainput(f'Are you logged in to the required account in your web browser?\nType {crayons.green("1")} if yes.\nType {crayons.red("2")} if no.\n')
    user_logged = user_selection.strip(' ')
    if user_logged == '1':
      choosen_url = AUTHORIZATION_URL
    elif user_logged == '2':
      choosen_url = AUTHORIZATION_URL_LOGIN
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

  if code in [
    'cancel', 
    'c'
  ]:
    log.debug('add_account flow stopped. User cancelled')
    print('Account add cancelled')
    return False

  if len(code) != 32:
    log.debug('add_account flow stopped. The code from the user was invalid.')
    print(f'Failed account add. The code\'s lenght is invalid. A valid authorization code is 32 characters long.')
    return False

  Auth = http.EpicAPI()

  auth_request = await Auth.authorization_code_auth(code)

  if 'errorCode' not in auth_request.text:
    oauth_json = auth_request.json()
    credentials = {}
    credentials['refresh_token'] = str(oauth_json['refresh_token'])
    credentials['refresh_expires'] = int(time.time()) + oauth_json['refresh_expires']
    auths[oauth_json['displayName']] = credentials
    with open(
      'auths.json', 
      'w', 
      encoding='utf-8'
    ) as f:
      json.dump(auths, f, indent=2, ensure_ascii=False)
      log.debug('add_account flow completed without errors.')
      return f'Account "{oauth_json["displayName"]}" added successfully! (Note: this login will expire after 23 days of inactivity)'
    return

  else:
    print(f'Authentication failed. {auth_request.json()["errorMessage"]}')
    log.debug('add_account flow stopped. The authentication failed.')
    return False

async def remove_account():
  log.debug('remove_account flow started.')
  print()
  print(
    crayons.red(
      'Remove Account',
      bold=True
      )
    )
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
      if user_selection.lower() in [
        'c', 
        'cancel'
      ]:
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
  if int(time.time()) > credentials['refresh_expires']:
    del auths[account_list[int(user_selection) - 1]]
    with open(
      'auths.json', 
      'w', 
      encoding='utf-8'
      ) as f:
      json.dump(
        auths, 
        f, 
        indent=2, 
        ensure_ascii=False
      )
      log.debug('remove_account flow completed. The saved refresh wasn\'t valid and removed from auths.json file')
      print('Account removed successfully.')
      return True
    
  else:
    Auth = http.EpicAPI()
    auth_request = await Auth.refresh_token_auth(refresh_token = credentials['refresh_token'])
    if 'errorCode' not in auth_request.text:
      oauth_json = auth_request.json()
      kill_request = await Auth.kill_oauth_session(oauth_json['access_token'])
      if kill_request != 403:
        del auths[account_list[int(user_selection) - 1]]
        with open(
          'auths.json', 
          'w', 
          encoding='utf-8'
          ) as f:
          json.dump(
            auths, 
            f, 
            indent=2, 
            ensure_ascii=False
          )
          log.debug('remove_account flow completed without errors')
          print('Account removed successfully.')
          return True

      else:
        print(f'Authentication failed. {auth_request.json()["errorMessage"]}')
        print('Removing account from auths.json file anyway.')
        del auths[account_list[int(user_selection) - 1]]
        with open(
          'auths.json', 
          'w',
          encoding='utf-8'
        ) as f:
          json.dump(
            auths, 
            f, 
            indent=2, 
            ensure_ascii=False
          )
          log.debug('remove_account flow failed successfully. Authentication failed but removed from auths.json anyways')
          print('Account removed.') # task failed successfully
          return True

    
async def launch_game(exchange_code: str, launch_command: str):
  log.debug('Launching game...')
  fortnite_path = configuration['fortnite_path']
  executable_args = launch_command
  additional_args = configuration["commandline_arguments"]
  log.debug('Manifest downloaded and processed correctly, preparing command line arguments')
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

  FortniteLauncher = subprocess.Popen(
    [f'{fortnite_path}/FortniteGame/Binaries/Win64/FortniteLauncher.exe'] + args, 
    cwd=f'{fortnite_path}/FortniteGame/Binaries/Win64/', 
    stdout=subprocess.DEVNULL
  )
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
        configuration = json.load(
          open(
            'config.json', 
            'r', 
            encoding = 'utf-8'
            )
          )
      except Exception as e:
        print(f'An error ocurred loading config.json file. {e}')
        await aioconsole.ainput('Press ENTER to exit')
        exit()

      try:
        auths = json.load(
          open(
            'auths.json',
            'r', 
            encoding = 'utf-8'
            )
          )
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
        #i vomited when i saw this 
        user_selection = await aioconsole.ainput(f'Select an option: ')
        try:
          user_selection.strip(' ')
          if user_selection.lower() == 'x':
            exit()
          
          if user_selection.lower() == 'a':
            await add_account()
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
          exit()

        else:
          credentials = auths[account_list[selected_account]]
          if int(time.time()) > credentials['refresh_expires']:
            print('The credentials of this account have expired. Re-add the account and try again')
          Auth = http.EpicAPI()
          auth_request = await Auth.refresh_token_auth(refresh_token = credentials['refresh_token'])
          if 'errorCode' not in auth_request.text:
            oauth_json = auth_request.json()
            credentials['refresh_token'] = str(oauth_json['refresh_token'])
            credentials['refresh_expires'] = int(time.time()) + oauth_json['refresh_expires']
            auths[account_list[selected_account]] = credentials
            with open(
              'auths.json', 
              'w', 
              encoding='utf-8'
            ) as f:
              json.dump(
                auths, 
                f, 
                indent=2, 
                ensure_ascii=False
              )
              exchange_request = await Auth.get_exchange_code(oauth_json['access_token'])
              if 'errorCode' not in exchange_request.text:
                exchange_json = exchange_request.json()
                launch_command = ''
                launch_info = await Auth.get_launch_info()
                if launch_info.status_code == 200:
                  log.debug('Using baydev.online launch args.')
                  launch_command = launch_info.json()['data']['launch_args']
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


asyncio.run(start())
