import flask
import utils.session

identity_blueprint = flask.Blueprint("identity_blueprint", __name__)

@identity_blueprint.get("/me")
def get_identity():
    server_session_value = flask.session.get("server_session_value")
    if not server_session_value:
        return "not logged in"
    user_data = utils.session.create_user_session_dict(server_session_value)
    if not user_data:
        return "could not construct user data"
    return flask.jsonify(user_data)