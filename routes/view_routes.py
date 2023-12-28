import flask
import utils.session

view_blueprint = flask.Blueprint("view_blueprint", __name__)

@view_blueprint.get("/")
def index():
    return flask.render_template("index.jinja")


@view_blueprint.get("/login")
def login():
    origin_url = flask.request.args.get("redirect_url")
    # if not redirect_url:
    #    return "No valid redirect URL"
    flask.session["origin_url"] = origin_url
    return flask.render_template("login.jinja")
    