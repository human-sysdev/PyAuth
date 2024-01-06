import os
import urllib.parse
import dotenv
import requests
import utils.database

_REDIRECT_URI = f"{os.getenv('SERVER_URL')}/callback/discord"

dotenv.load_dotenv()

def get_signin_url() -> str:
    login_request = utils.database.Database().create_new_login_request()
    url = "https://discord.com/oauth2/authorize"
    params = {
        "response_type": "code",
        "client_id": os.getenv("DISCORD_CLIENT_ID"),
        "state": login_request.state,
        "scope": "email identify",
        "redirect_uri": _REDIRECT_URI,
        "prompt": "none"
    }
    url = f"{url}?{urllib.parse.urlencode(params)}"
    return url


def retrieve_discord_token(login_request: utils.database.Database.LoginRequest) -> utils.database.Database.LoginRequest | None:
    post_url = "https://discord.com/api/oauth2/token"
    post_data = {
        "grant_type": "authorization_code",
        "code": login_request.code,
        "redirect_uri": _REDIRECT_URI,
    }
    post_headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    client_id = os.getenv("DISCORD_CLIENT_ID")
    client_secret = os.getenv("DISCORD_CLIENT_SECRET")
    token = requests.post(post_url, data=post_data, headers=post_headers, auth=(client_id, client_secret))
    token = dict(token.json())
    token = token.get("access_token")
    if not token:
        return None
    
    login_request.token = token
    login_request = utils.database.Database().update_login_request(login_request)
    return login_request


def get_discord_user(login_request: utils.database.Database.LoginRequest):
    if not login_request.token:
        return None
    
    url = "https://discord.com/api/users/@me"
    headers = {
        "Authorization": f"Bearer {login_request.token}"
    }
    user_info = requests.get(url, headers=headers)
    user_info = dict(user_info.json())

    email = user_info.get("email")    
    username = user_info.get("username")
    provider = "discord"
    provider_id = user_info.get("id")
    pfp = user_info.get("avatar")
    pfp = f"https://cdn.discordapp.com/avatars/{provider_id}/{pfp}.png"
    snowflake = f"{provider}{provider_id}"

    user = utils.database.Database().get_user_by_snowflake(snowflake)
    if not user:
        user = utils.database.Database().create_new_user(
            email=email, 
            pfp=pfp, 
            provider=provider, 
            username=username, 
            snowflake=snowflake)
    else:
        user.email = email
        user.pfp = pfp
        user.username = username
        user = utils.database.Database().update_user(user)
    return user