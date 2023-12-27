import flask
import auth.github


auth_blueprint = flask.Blueprint("auth_blueprint", __name__)

SIGNIN_URL_GENERATORS = {
    "github": auth.github.get_signin_url,
}

CODE_HANDLER_GENERATORS = {
    "github": auth.github.append_signin_code,
}

TOKEN_RETRIEVER_GENERATORS = {
    "github": auth.github.retrieve_github_token,
}

USER_RETRIEVER_GENERATORS = {
    "github": auth.github.get_github_user,
}


@auth_blueprint.get("/signin/<string:provider>")
def github_request_identity(provider: str):
    signin_url_generator = SIGNIN_URL_GENERATORS.get(provider)
    if not signin_url_generator:
        return "unsupported provider", 401
    url = signin_url_generator()
    return flask.redirect(url)


@auth_blueprint.get("/callback/<string:provider>")
def github_request_identity_callback(provider: str):
    code_handler = CODE_HANDLER_GENERATORS.get(provider)
    if not code_handler:
        return "unsupported provider", 401
    login_request = code_handler(flask.request)
    if not login_request:
        return "something went wrong"

    token_handler = TOKEN_RETRIEVER_GENERATORS.get(provider)
    if not token_handler:
        return "unsupported provider", 401
    login_request = token_handler(login_request)

    user_handler = USER_RETRIEVER_GENERATORS.get(provider)
    if not user_handler:
        return "unsupported provider", 401
    user = user_handler(login_request)

    # create a session for the user

    return f"""
    <img src='{user.pfp}' />
    <div>{user.username}</div>
    <div>{user.email}</div>
    <div>{user.provider}</div>
    <div>{user.created_at}</div>
    """