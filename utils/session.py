import datetime

import utils.crypt
import utils.database


def create_user_session(user: utils.database.Database.User, state:str) -> utils.database.Database.Session | None:
    user_session_user_id = user.id
    user_session_value = utils.crypt.random_string()
    user_session_hash = f"{user.id}{user.email}{user.pfp}{user.provider}{user.username}{state}"
    user_session_hash = utils.crypt.hash_string(user_session_hash)
    user_session = utils.database.Database().create_new_session(
        user_id=user_session_user_id, 
        value=user_session_value,
        hash=user_session_hash,
        )
    return user_session


def get_user_session(session_value: str) -> dict | None:
    user_session = utils.database.Database().get_session_from_value(session_value)
    if not user_session:
        return None
    user_session.expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    user_session = utils.database.Database().update_session(user_session)
    user = utils.database.Database().get_user_by_id(user_session.user_id)
    if not user:
        return None
    return {
        "user_id": user.id,
        "user_pfp": user.pfp,
        "user_username": user.username,
        "user_created_at": str(user.created_at),
        "user_email": user.email,
        "user_provider": user.provider,
        "session_hash": user_session.hash,
        "session_signature": utils.crypt.sign_string(user_session.hash),
        "session_expires_at": str(user_session.expires_at),
        "session_created_at": str(user_session.created_at),
    }

def get_foreign_user_data(id: int) -> dict | None:
    user = utils.database.Database().get_user_by_id(id)
    return {
        "user_id": user.id,
        "user_pfp": user.pfp,
        "user_username": user.username,
    }