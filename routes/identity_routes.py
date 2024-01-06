import flask
import base64

identity_blueprint = flask.Blueprint("identity_blueprint", __name__)

@identity_blueprint.get("/key")
def get_public_key():
    with open("pub.pem", "rb") as file:
        public_key = file.read()
    public_key = base64.b64encode(public_key).decode("ascii")
    return public_key