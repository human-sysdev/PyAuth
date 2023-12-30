import utils.database
import utils.session
import requests
import flask
import json


def append_signin_code(request: flask.Request) -> utils.database.Database.LoginRequest | None:
    args = dict(request.args)
    code = args.get("code")
    state = args.get("state")
    if None in [code, state]:
        return None
    
    login_request = utils.database.Database().get_login_request_by_state(state)
    if not login_request:
        return None
    
    login_request.code = code
    login_request = utils.database.Database().update_login_request(login_request)
    return login_request

def post_user_data(session_value: str, state_value: str, url: str) -> bool:
    session = utils.session.get_user_session(session_value)
    if not session:
        return False
    session["state"] = state_value
    resp = requests.post(url, json=session)
    print(resp.status_code)
    return True