import utils.database
import flask

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