import dotenv
import flask
import os
import requests

import utils.database

dotenv.load_dotenv()

git_auth_blueprint = flask.Blueprint("git_auth_blueprint", __name__)

@git_auth_blueprint.get("/auth/github")
def github_request_identity():
    request_state = utils.database.Database().create_new_request_state()
    print("\n\n----------")
    print(request_state.value)
    print("\n\n----------")
    url = "https://github.com/login/oauth/authorize"
    url += f"?client_id={os.getenv('GITHUB_CLIENT_ID')}"
    url += f"&state={request_state.value}"
    url += f"&redirect_uri={os.getenv('WORKING_URL')}/auth/github/callback"
    return flask.redirect(url)

@git_auth_blueprint.get("/auth/github/callback")
def github_request_identity_callback():
    args = dict(flask.request.args)
    code = args.get("code")
    state = args.get("state")
    if None in [code, state]:
        return "invalid args", 400
    
    request_state = utils.database.Database().get_request_state_by_value(state)
    if request_state.code:
        return "state expired", 400
    
    request_state.code = code
    request_state = utils.database.Database().update_request_state(request_state)
    
    post_url = "https://github.com/login/oauth/access_token"
    post_data = {
        "client_id": os.getenv('GITHUB_CLIENT_ID'),
        "client_secret": os.getenv('GITHUB_CLIENT_SECRET'),
        "code": request_state.code,
    }
    post_headers = {
        "Accept": "application/json"
    }
    token = requests.post(post_url, data=post_data, headers=post_headers)
    token = dict(token.json())
    token = token.get("access_token")
    if not token:
        return "something went wrong, could not get token", 400
    
    request_state.token = token
    request_state = utils.database.Database().update_request_state(request_state)

    # TODO we now have a token, next up is creating a user from the token
    # and we should also set a session value to identify the user i thinks

    return f"code: {code}\nstate: {state}"