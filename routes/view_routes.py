import flask
import utils.crypt

view_blueprint = flask.Blueprint("view_blueprint", __name__)

@view_blueprint.get("/")
def index():
    return flask.render_template("index.jinja", public_key=utils.crypt.get_public_key())


@view_blueprint.get("/login")
def login():
    origin_url = flask.request.args.get("redirect_url")
    behalf_of = flask.request.args.get("behalf_of")
    # if not redirect_url:
    #    return "No valid redirect URL"
    flask.session["origin_url"] = origin_url
    return flask.render_template("login.jinja", behalf_of=behalf_of)
    