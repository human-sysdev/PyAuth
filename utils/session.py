import datetime

import utils.crypt
import utils.database


def create_new_session(user: utils.database.Database.User) -> utils.database.Database.Session | None:
    server_session_user_id = user.id
    server_session_value = utils.crypt.random_string()
    server_session = utils.database.Database().create_new_session(
        user_id=server_session_user_id, 
        value=server_session_value
        )
    return server_session


def create_user_session_dict(session_value: str) -> dict | None:
    server_session = utils.database.Database().get_session_from_value(session_value)
    if not server_session:
        return None
    server_session.expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    server_session = utils.database.Database().update_session(server_session)
    user = utils.database.Database().get_user_by_id(server_session.user_id)
    if not user:
        return None
    return {
        "user_id": user.id,
        "user_pfp": user.pfp,
        "user_username": user.username,
        "user_created_at": user.created_at,
        "user_email": user.email,
        "session_expires_at": server_session.expires_at,
        "session_created_at": server_session.created_at,
    }

def get_foreign_user_data(id: int) -> dict | None:
    user = utils.database.Database().get_user_by_id(id)
    if not user:
        return None
    return {
        "user_id": user.id,
        "user_pfp": user.pfp,
        "user_username": user.username,
        "user_created_at": user.created_at,
    }