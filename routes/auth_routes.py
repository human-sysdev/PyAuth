import flask
import providers.github
import utils.session

auth_blueprint = flask.Blueprint("auth_blueprint", __name__)

SIGNIN_URL_GENERATORS = {
    "github": providers.github.get_signin_url,
}

CODE_HANDLER_GENERATORS = {
    "github": providers.github.append_signin_code,
}

TOKEN_HANDLER_GENERATORS = {
    "github": providers.github.retrieve_github_token,
}

USER_RETRIEVER_GENERATORS = {
    "github": providers.github.get_github_user,
}


@auth_blueprint.get("/signout")
def sign_out():
    flask.session.clear()
    return "signed out"


@auth_blueprint.get("/signin/<string:provider>")
def signin_with_provider(provider: str):
    signin_url_generator = SIGNIN_URL_GENERATORS.get(provider)
    if not signin_url_generator:
        return "unsupported provider", 401
    url = signin_url_generator()
    return flask.redirect(url)


@auth_blueprint.get("/callback/<string:provider>")
def signin_callback(provider: str):
    code_handler = CODE_HANDLER_GENERATORS.get(provider)
    if not code_handler:
        return "unsupported provider", 401
    
    login_request = code_handler(flask.request)
    if not login_request:
        return "something went wrong"

    token_handler = TOKEN_HANDLER_GENERATORS.get(provider)
    if not token_handler:
        return "unsupported provider", 401
    
    login_request = token_handler(login_request)
    if not login_request:
        return "something went wrong"

    user_handler = USER_RETRIEVER_GENERATORS.get(provider)
    if not user_handler:
        return "unsupported provider", 401
    
    user = user_handler(login_request)
    if not user:
        return "something went wrong"

    server_session = utils.session.create_new_session(user)
    if not server_session:
        return "could not assign session"
    
    flask.session["server_session_value"] = server_session.value
    session_data = utils.session.create_user_session_dict(server_session.value)
    if not session_data:
        return "could not construct session data"
    return flask.jsonify(session_data)