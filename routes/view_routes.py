import flask
import utils.crypt
import os
import dotenv

dotenv.load_dotenv()

view_blueprint = flask.Blueprint("view_blueprint", __name__)

@view_blueprint.get("/")
def index():
    return flask.render_template("index.jinja", public_key=utils.crypt.get_public_key())


@view_blueprint.get("/login")
def login():
    origin_url = flask.request.args.get("redirect")
    callback_url = flask.request.args.get("callback")
    state_value = flask.request.args.get("state")
    if None in [origin_url, callback_url, state_value]:
        return "Missing arguments"
    behalf_of = flask.request.args.get("from")
    # if not redirect_url:
    #    return "No valid redirect URL"
    flask.session["origin_url"] = origin_url
    flask.session["callback_url"] = callback_url
    flask.session["state_value"] = state_value
    return flask.render_template("login.jinja", behalf_of=behalf_of, server_url=os.getenv("SERVER_URL"))
    