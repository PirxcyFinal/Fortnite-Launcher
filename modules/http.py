import requests

class Endpoints:

    ACCOUNT_PUBLIC_SERVICE = "https://account-public-service-prod03.ol.epicgames.com"
    OAUTH_TOKEN = f"{ACCOUNT_PUBLIC_SERVICE}/account/api/oauth/token"
    EXCHANGE_CODE = f"{ACCOUNT_PUBLIC_SERVICE}/account/api/oauth/exchange"
    KILL_TOKEN = f"{ACCOUNT_PUBLIC_SERVICE}/api/oauth/sessions/kill/" + "{accessToken}"

    CREATE_DEVICE_AUTH = f"{ACCOUNT_PUBLIC_SERVICE}/account/api/public/account/" + "{accountId}" + "/deviceAuth"
    DELETE_DEVICE_AUTH = f"{ACCOUNT_PUBLIC_SERVICE}/api/public/account/" + "{accountId}/deviceAuth/{deviceId}"
    GET_DEVICE_AUTH = f"{ACCOUNT_PUBLIC_SERVICE}/api/public/account/" + "{accountId}/deviceAuth/{deviceId}"


class Clients:

    launcherAppClient2 = "MzRhMDJjZjhmNDQxNGUyOWIxNTkyMTg3NmRhMzZmOWE6ZGFhZmJjY2M3Mzc3NDUwMzlkZmZlNTNkOTRmYzc2Y2Y="
    fortniteIOSGameClient = "MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE="


class EpicAPI:

    async def authorization_code_auth(self, code: str, client = Clients.launcherAppClient2):

        headers = {
            'Authorization': f'basic {client}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'authorization_code',
            'code': code
        }

        response = requests.post(
            Endpoints.OAUTH_TOKEN,
            headers = headers,
            data = data
        )

        return response

    async def device_auths_auth(self, device_auths: dict):

        headers = {
            'Authorization': f'basic {Clients.fortniteIOSGameClient}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'device_auth',
            'account_id': device_auths['account_id'],
            'device_id': device_auths['device_id'],
            'secret': device_auths['secret']
        }

        response = requests.post(
            Endpoints.OAUTH_TOKEN,
            headers = headers,
            data = data
        )

        return response

    async def refresh_token_auth(self, refresh_token: str):

        headers = {
            'Authorization': f'basic {Clients.launcherAppClient2}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        response = requests.post(
            Endpoints.OAUTH_TOKEN,
            headers = headers,
            data = data
        )

        return response

    async def exchange_code_auth(self, exchange_code: str, client=Clients.launcherAppClient2):

        headers = {
            'Authorization': f'basic {client}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'exchange_code',
            'exchange_code': exchange_code
        }

        response = requests.post(
            Endpoints.OAUTH_TOKEN,
            headers = headers,
            data = data
        )

        return response
    
    async def get_exchange_code(self, access_token: str):

        headers = {
            'Authorization': f'bearer {access_token}',
        }

        response = requests.get(
            Endpoints.EXCHANGE_CODE,
            headers = headers
        )

        return response

    async def get_device_auth(self, access_token: str, account_id: str, device_id: str):

        headers = {
            'Authorization': f'bearer {access_token}'
        }

        response = requests.get(
            Endpoints.GET_DEVICE_AUTH.format(accountId=account_id, deviceId=device_id),
            headers = headers
        )

        return response


    async def create_device_auth(self, access_token: str, account_id: str):

        headers = {
            'Authorization': f'bearer {access_token}',
            'User-Agent': 'Fortnite-Launcher v2.1'
        }

        response = requests.post(
            Endpoints.CREATE_DEVICE_AUTH.format(accountId = account_id),
            headers = headers
        )

        return response

    async def delete_device_auth(self, access_token: str, account_id: str, device_id: str):

        headers = {
            'Authorization': f'bearer {access_token}',
        }

        response = requests.delete(
            Endpoints.DELETE_DEVICE_AUTH.format(accountId=account_id, deviceId=device_id),
            headers = headers
        )

        return response

    async def kill_oauth_session(self, access_token: str):

        headers = {
            'Authorization': f'bearer {access_token}',
        }

        response = requests.delete(
            Endpoints.KILL_TOKEN.format(accessToken = access_token),
            headers = headers
        )

        return response.status_code

    async def get_launch_info(self):

        response = requests.get(
            'https://baydev.online/api/v1/launchinfo'
        )

        return response