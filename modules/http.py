import requests

class Endpoints:

    ACCOUNT_PUBLIC_SERVICE = "https://account-public-service-prod03.ol.epicgames.com"
    OAUTH_TOKEN = f"{ACCOUNT_PUBLIC_SERVICE}/account/api/oauth/token"
    EXCHANGE_CODE = f"{ACCOUNT_PUBLIC_SERVICE}/account/api/oauth/exchange"
    KILL_TOKEN = f"{ACCOUNT_PUBLIC_SERVICE}/api/oauth/sessions/kill/" + "{accessToken}"

    
class EpicAPI:

    async def authorization_code_auth(self, code: str):

        headers = {
            'Authorization': f'basic MzRhMDJjZjhmNDQxNGUyOWIxNTkyMTg3NmRhMzZmOWE6ZGFhZmJjY2M3Mzc3NDUwMzlkZmZlNTNkOTRmYzc2Y2Y=',
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

    async def refresh_token_auth(self, refresh_token: str):

        headers = {
            'Authorization': f'basic MzRhMDJjZjhmNDQxNGUyOWIxNTkyMTg3NmRhMzZmOWE6ZGFhZmJjY2M3Mzc3NDUwMzlkZmZlNTNkOTRmYzc2Y2Y=',
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
    
    async def get_exchange_code(self, access_token: str):

        headers = {
            'Authorization': f'bearer {access_token}',
        }

        response = requests.get(
            Endpoints.EXCHANGE_CODE,
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
            'https://baydev.online/api/v1/fortnite/launchinfo'
        )

        return response