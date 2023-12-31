import dotenv
import flask
import os
import requests
import urllib.parse

import utils.database

dotenv.load_dotenv()


def get_signin_url() -> str:
    login_request = utils.database.Database().create_new_login_request()
    url = "https://github.com/login/oauth/authorize"
    params = {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "state": login_request.state,
        "scope": "user:email",
        "redirect_uri": f"{os.getenv('SERVER_URL')}/callback/github"
    }
    url = f"{url}?{urllib.parse.urlencode(params)}"
    return url


def retrieve_github_token(login_request: utils.database.Database.LoginRequest) -> utils.database.Database.LoginRequest | None:
    post_url = "https://github.com/login/oauth/access_token"
    post_data = {
        "client_id": os.getenv('GITHUB_CLIENT_ID'),
        "client_secret": os.getenv('GITHUB_CLIENT_SECRET'),
        "code": login_request.code,
    }
    post_headers = {
        "Accept": "application/json"
    }
    token = requests.post(post_url, data=post_data, headers=post_headers)
    token = dict(token.json())
    token = token.get("access_token")
    if not token:
        return None
    
    login_request.token = token
    login_request = utils.database.Database().update_login_request(login_request)
    return login_request


def get_github_user(login_request: utils.database.Database.LoginRequest):
    if not login_request.token:
        return None
    
    url = "https://api.github.com/user"
    email_url = "https://api.github.com/user/emails"
    headers = {
        "Authorization": f"Bearer {login_request.token}"
    }
    user_info = requests.get(url, headers=headers)
    user_emails = requests.get(email_url, headers=headers)
    user_info = dict(user_info.json())
    user_emails = list([dict(entry) for entry in list(user_emails.json())])

    email: str = next(
        (entry.get("email") for entry in user_emails if entry.get("primary") == True), 
        user_emails[0].get("email")
        )
    
    if not email:
        return None
    
    pfp = user_info.get("avatar_url")
    username = user_info.get("login")
    provider = "github"
    provider_id = user_info.get("id")
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