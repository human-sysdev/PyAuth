import dotenv
import flask
import os
import waitress
import flask_cors

import routes.auth_routes
import routes.identity_routes
import routes.view_routes

dotenv.load_dotenv()

server = flask.Flask(__name__)
server.secret_key = os.getenv("SERVER_SECRET")
server.config["SESSION_COOKIE_SECURE"] = True
cors = flask_cors.CORS(server, supports_credentials=True, )

server.register_blueprint(routes.auth_routes.auth_blueprint)
server.register_blueprint(routes.identity_routes.identity_blueprint)
server.register_blueprint(routes.view_routes.view_blueprint)

if __name__ == "__main__":
    if os.getenv("ENVIRONMENT") == "DEV":
        server.debug = True
        server.run(port=3000, host="0.0.0.0")
    else:
        waitress.serve(server, port=3000, host="0.0.0.0")