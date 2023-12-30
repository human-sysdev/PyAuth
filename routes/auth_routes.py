import flask
import providers.github
import providers.discord
import providers.universal
import utils.session

auth_blueprint = flask.Blueprint("auth_blueprint", __name__)

SIGNIN_URL_GENERATORS = {
    "github": providers.github.get_signin_url,
    "discord": providers.discord.get_signin_url,
}

TOKEN_HANDLER_GENERATORS = {
    "github": providers.github.retrieve_github_token,
    "discord": providers.discord.retrieve_discord_token,
}

USER_RETRIEVER_GENERATORS = {
    "github": providers.github.get_github_user,
    "discord": providers.discord.get_discord_user,
}


@auth_blueprint.get("/signin/<string:provider>")
def signin_with_provider(provider: str):
    origin_url = flask.session.get("origin_url")
    callback_url = flask.session.get("callback_url")
    state_value = flask.session.get("state_value")
    if None in [origin_url, callback_url, state_value]:
        return "Error, missing arguments", 400
    signin_url_generator = SIGNIN_URL_GENERATORS.get(provider)
    if not signin_url_generator:
        return "unsupported provider", 401
    url = signin_url_generator()
    return flask.redirect(url)


@auth_blueprint.get("/callback/<string:provider>")
def signin_callback(provider: str):
    origin_url = flask.session.get("origin_url")
    callback_url = flask.session.get("callback_url")
    state_value = flask.session.get("state_value")
    if None in [origin_url, callback_url, state_value]:
        return "Error, missing arguments", 400
    
    login_request = providers.universal.append_signin_code(flask.request)
    if not login_request:
        return "could not verify OAuth CODE"

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

    server_session = utils.session.create_user_session(user, state_value)
    if not server_session:
        return "could not assign session"
    
    flask.session["server_session_value"] = server_session.value
    
    valid_post = providers.universal.post_user_data(server_session.value, state_value, callback_url)
    if not valid_post:
        return "invalid post"
    return flask.redirect(origin_url)