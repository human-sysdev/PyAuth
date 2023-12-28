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


@identity_blueprint.get("/user/<int:id>")
def get_foreign_user(id: int):
    if not flask.session.get("server_session_value"):
        return "not logged in"
    foreign_user_data = utils.session.get_foreign_user_data(id)
    return flask.jsonify(foreign_user_data)
    