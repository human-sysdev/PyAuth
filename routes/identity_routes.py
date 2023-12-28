import flask
import utils.session

identity_blueprint = flask.Blueprint("identity_blueprint", __name__)

@identity_blueprint.get("/me")
def get_identity():
    server_session_value = flask.session.get("server_session_value")
    if not server_session_value:
        return "not logged in"
    user_data = utils.session.get_user_session(server_session_value)
    if not user_data:
        return "could not construct user data"
    return flask.jsonify(user_data)


@identity_blueprint.post("/me/server")
def get_server_identity():
    args = dict(flask.request.json)
    session_hash = args.get("session_hash")
    user_id = args.get("user_id")
    if None in [session_hash, user_id]:
        return "missing arguments", 400    
    
    user_data = utils.session.get_server_session(session_hash)
    if not user_data:
        return "could not construct user data"
    
    if user_data.get("user_id") != user_id:
        return "invalid arguments", 401
    
    return flask.jsonify(user_data)


@identity_blueprint.get("/user/<int:id>")
def get_foreign_user(id: int):
    if not flask.session.get("server_session_value"):
        return "not logged in"
    foreign_user_data = utils.session.get_foreign_user_data(id)
    return flask.jsonify(foreign_user_data)
    