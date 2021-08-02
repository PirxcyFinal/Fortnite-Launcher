import requests
import crayons
import util

log = util.logger('Auth')

IOS_TOKEN = "MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE="

ACCOUNT_PUBLIC_SERVICE = "https://account-public-service-prod03.ol.epicgames.com"
OAUTH_TOKEN = f"{ACCOUNT_PUBLIC_SERVICE}/account/api/oauth/token"
EXCHANGE = f"{ACCOUNT_PUBLIC_SERVICE}/account/api/oauth/exchange"
ACCOUNT_BY_USER_ID = f"{ACCOUNT_PUBLIC_SERVICE}/account/api/public/account/" + "{user_id}"
DEVICE_AUTH_GENERATE = f"{ACCOUNT_PUBLIC_SERVICE}/account/api/public/account/" + "{account_id}/deviceAuth"
DEVICE_AUTH_DELETE = f"{ACCOUNT_PUBLIC_SERVICE}/api/public/account/" + "{account_id}/deviceAuth/{device_id}"
KILL_AUTH_SESSION = f"{ACCOUNT_PUBLIC_SERVICE}/api/oauth/sessions/kill/" + "{access_token}"

AUTHORIZATION_CODE_URL = "https://www.epicgames.com/id/login?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Fapi%2Fredirect%3FclientId%3D3446cd72694c4a4485d81b77adbb2141%26responseType%3Dcode"

class AuthorizationCode:

    def __init__(self):
        self.authenticated = False
        self.auth_session = None

    def HTTPRequest(self, url: str, headers = None, data = None, method = None):

        if method == 'GET':
            response = requests.get(url, headers=headers, data=data)
            log.debug(f'[GET] {crayons.magenta(url)} > {response.text} | {response.headers}')
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=data)
            log.debug(f'[POST] {crayons.magenta(url)} > {response.text} | {response.headers}')
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, data=data)
            log.debug(f'[DELETE] {crayons.magenta(url)} > {response.text} | {response.headers}')

        return response

    def get(self, url, headers=None, data=None):
        return self.HTTPRequest(url, headers, data, 'GET')

    def post(self, url, headers=None, data=None):
        return self.HTTPRequest(url, headers, data, 'POST')

    def delete(self, url, headers=None, data=None):
        return self.HTTPRequest(url, headers, data, 'DELETE')

    def authenticate(self, authorization_code: str):

        headers = {
            "Authorization": f"basic {IOS_TOKEN}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code
        }
        response = self.post(OAUTH_TOKEN, headers, data)

        if 'errorCode' in response.text:
            self.authenticated = False
            self.auth_session = None
            return False, response.json()

        else:

            self.authenticated = True
            self.auth_session = response.json()

            return True, response.json()


    def generate_device_auths(self, **kwargs):

        auth_session = kwargs.get('auth_session', self.auth_session)

        headers = {
            "Authorization": f"bearer {auth_session['access_token']}"
        }
        response = self.post(DEVICE_AUTH_GENERATE.format(account_id=auth_session['account_id']), headers)

        if 'errorCode' in response.text:
            return False, response.json()

        else:
            return True, response.json()

    def get_account_info(self, **kwargs):

        auth_session = kwargs.get('auth_session', self.auth_session)

        headers = {
            "Authorization": f"bearer {auth_session['access_token']}"
        }
        response = self.get(ACCOUNT_BY_USER_ID.format(user_id=auth_session['account_id']), headers)

        if 'errorCode' in response.text:
            return False, response.json()

        else:
            return True, response.json()

    def delete_device_auths(self, device_auths: dict, **kwargs):

        auth_session = kwargs.get('auth_session', self.auth_session)

        headers = {
            "Authorization" f"bearer {auth_session['access_token']}"
        }
        response = self.delete(DEVICE_AUTH_DELETE.format(account_id=device_auths['account_id'], device_id=device_auths['device_id']), headers)

        if 'errorCode' in response.text:
            return False, response.json()

        else:
            return True, response.ok

    def kill_auth_session(self, **kwargs):

        auth_session = kwargs.get('auth_session', self.auth_session)

        headers = {
            "Authorization": f"bearer {auth_session['access_token']}"
        }
        response = self.delete(KILL_AUTH_SESSION.format(access_token=auth_session['access_token']), headers)

        if 'errorCode' in response.text:
            return False, response.json()

        else:
            return True, response.ok


class DeviceAuths:

    def __init__(self):
        self.authenticated = False
        self.auth_session = None

    def HTTPRequest(self, url: str, headers = None, data = None, method = None):

        if method == 'GET':
            response = requests.get(url, headers=headers, data=data)
            log.debug(f'[GET] {crayons.magenta(url)} > {response.text} | {response.headers}')
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=data)
            log.debug(f'[POST] {crayons.magenta(url)} > {response.text} | {response.headers}')
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, data=data)
            log.debug(f'[DELETE] {crayons.magenta(url)} > {response.text} | {response.headers}')

        return response

    def get(self, url, headers=None, data=None):
        return self.HTTPRequest(url, headers, data, 'GET')

    def post(self, url, headers=None, data=None):
        return self.HTTPRequest(url, headers, data, 'POST')

    def delete(self, url, headers=None, data=None):
        return self.HTTPRequest(url, headers, data, 'DELETE')

    def authenticate(self, device_auths):

        headers = {
            "Authorization": f"basic {IOS_TOKEN}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "device_auth",
            "device_id": device_auths['device_id'],
            "account_id": device_auths['account_id'],
            "secret": device_auths['secret']
        }

        response = self.post(OAUTH_TOKEN, headers=headers, data=data)

        if 'errorCode' in response.text:
            return False, response.json()
        else:
            self.authenticated = True
            self.auth_session = response.json()
            return True, response.json()

    def get_exchange_code(self):

        headers = {
            "Authorization": f"bearer {self.auth_session['access_token']}"
        }

        response = self.get(EXCHANGE, headers=headers)

        if 'errorCode' in response.text:
            return False, response.json()
        else:
            return True, response.json(), response.cookies

    def generate_device_auths(self):

        headers = {
            "Authorization": f"bearer {self.auth_session['access_token']}"
        }
        response = self.post(DEVICE_AUTH_GENERATE.format(account_id=self.auth_session['account_id']), headers)

        if 'errorCode' in response.text:
            return False, response.json()
        else:
            return True, response.json()

    def delete_device_auths(self, device_auths: dict):

        headers = {
            "Authorization": f"bearer {self.auth_session['access_token']}"
        }
        response = self.delete(DEVICE_AUTH_DELETE.format(account_id=device_auths['account_id'], device_id=device_auths['device_id']), headers)

        if 'errorCode' in response.text:
            return False, response.json()
        else:
            return True, None

    def kill_auth_session(self):

        headers = {
            "Authorization": f"bearer {self.auth_session['access_token']}"
        }
        response = self.delete(KILL_AUTH_SESSION.format(access_token=self.auth_session['access_token']), headers)

        if 'errorCode' in response.text:
            return False, response.json()
        else:
            self.authenticated = False
            self.auth_session = None
            return True, None