import traceback
import datetime
import crayons
import psutil
import json
import sys
import os

class logger():

    def __init__(self, name: str):

        self.name = name

    def get_current_timestamp(self):

        timestamp = datetime.datetime.now().strftime('[%H:%M:%S]')
        return crayons.green(timestamp)

    def get_colored_box(self, color, text):

        return f'{color("[")}{text}{color("]")}'

    def info(self, content: str):

        print(f'{content}')

    def warn(self, content: str):

        print(f'{self.get_colored_box(crayons.yellow, "WARN")} {content}')

    def error(self, content: str):

        print(f'{self.get_colored_box(crayons.red, "ERROR")} {content}')

    def debug(self, content: str):

        if '--debug' in sys.argv:
            print(f'{self.get_current_timestamp()} {self.get_colored_box(crayons.blue, self.name)} {crayons.magenta("[DEBUG]")} {content}')


log = logger('Util')

def log_debug_traceback(exception, logger):

    try:
        if '--debug' in sys.argv:
            tb = traceback.format_tb(exception.__traceback__)
            logger.debug(f'Traceback: {tb}')
    except:
        return None

def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        log.debug('Loaded configuration.')
        return config
    except Exception as e:
        log.critical(f'Failed loading config file: {e}')
        log_debug_traceback(e, log)

def load_device_auths():
    try:
        with open('device_auths.json', 'r', encoding='utf-8') as f:
            device_auths = json.load(f)
        log.debug('Loaded device auths.')
        return device_auths
    except Exception as e:
        log.critical(f'Failed loading device auths file: {e}')
        log_debug_traceback(e, log)

def update_device_auths(new_data):
    try:
        with open('device_auths.json', 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
        return True, None
    except Exception as e:
        return False, e

def wait_for_game_launch(process):

    while True:
        if process.is_running() == False:
            return False, process.pid
        for p in psutil.process_iter(['name', 'pid']):
            if p.info['name'] == 'FortniteClient-Win64-Shipping.exe':
                return True, p.info['pid']