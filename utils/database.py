import datetime
import sqlalchemy as sql
import sqlalchemy.orm as orm
import os
import dotenv
import utils.crypt

dotenv.load_dotenv()


DATABASE_PATH = os.getenv("DB_PATH")

class Database:
    db_uri = f"sqlite:///{DATABASE_PATH}"
    engine = sql.create_engine(db_uri)
    Base = orm.declarative_base()
    SessionMaker = orm.sessionmaker(engine, expire_on_commit=False)
    
    class LoginRequest(Base):
        __tablename__ = "login_request"
        id = sql.Column(sql.Integer, unique=True, primary_key=True)
        state = sql.Column(sql.String, unique=True)
        code = sql.Column(sql.String)
        token = sql.Column(sql.String)
        created_at = sql.Column(sql.DateTime, default=datetime.datetime.utcnow)
        expires_at = sql.Column(sql.DateTime, default=lambda: datetime.datetime.utcnow() + datetime.timedelta(hours=1))
    
    class User(Base):
        """
        snowflake → f"{provider}{provider_id}"
        """
        __tablename__ = "user"
        id = sql.Column(sql.Integer, unique=True, primary_key=True)
        snowflake = sql.Column(sql.String, unique=True)
        email = sql.Column(sql.String)
        pfp = sql.Column(sql.String)
        username = sql.Column(sql.String)
        provider = sql.Column(sql.String)
        created_at = sql.Column(sql.DateTime, default=datetime.datetime.utcnow)
    
    class Session(Base):
        __tablename__ = "session"
        id = sql.Column(sql.Integer, unique=True, primary_key=True)
        user_id = sql.Column(sql.Integer)
        value = sql.Column(sql.String)
        hash = sql.Column(sql.String)
        created_at = sql.Column(sql.DateTime, default=datetime.datetime.utcnow)
        expires_at = sql.Column(sql.DateTime, default=lambda: datetime.datetime.utcnow() + datetime.timedelta(hours=1))
    
    def create_new_login_request(self) -> LoginRequest:
        rs = self.LoginRequest()
        rs.created_at = datetime.datetime.utcnow()
        rs.state = utils.crypt.random_string()
        with self.SessionMaker() as session:
            session.add(rs)
            session.commit()
        return rs
    
    def get_login_request_by_state(self, state: str) -> LoginRequest:
        with self.SessionMaker() as session:
            rs = session.query(self.LoginRequest).where(self.LoginRequest.state == state).first()
        return rs
    
    def get_login_request_by_id(self, id: int) -> LoginRequest:
        with self.SessionMaker() as session:
            rs = session.query(self.LoginRequest).where(self.LoginRequest.id == id).first()
        return rs

    def update_login_request(self, login_request: LoginRequest) -> LoginRequest | None:
        if not login_request.id:
            RuntimeError("DB: Tried Updating LoginRequest with non-existent ID")
        with self.SessionMaker() as session:
            session.add(login_request)
            session.commit()
        return login_request
    
    def get_user_by_snowflake(self, snowflake: str) -> User | None:
        with self.SessionMaker() as session:
            user = session.query(self.User).where(self.User.snowflake == snowflake).first()
        return user
    
    def get_user_by_id(self, id: int) -> User | None:
        with self.SessionMaker() as session:
            user = session.query(self.User).where(self.User.id == id).first()
        return user
    
    def update_user(self, user: User):
        if not user.id:
            RuntimeError("DB: Tried Updating User with non-existent ID")
        with self.SessionMaker() as session:
            session.add(user)
            session.commit()
        return user
    
    def create_new_user(self, email: str, pfp: str, provider: str, username: str, snowflake: str) -> User | None:
        if self.get_user_by_snowflake(snowflake):
            return None
        user = self.User()
        user.email = email
        user.pfp = pfp
        user.provider = provider
        user.username = username
        user.snowflake = snowflake
        with self.SessionMaker() as session:
            session.add(user)
            session.commit()
        return user

    def get_session_from_value(self, session_value: str) -> Session | None:
        with self.SessionMaker() as session:
            s = session.query(self.Session).where(self.Session.value == session_value).first()
        if not s:
            return None
        if s.expires_at < datetime.datetime.utcnow():
            with self.SessionMaker() as session:
                session.delete(s)
                session.commit()
            return None
        return s
    
    def get_session_from_hash(self, session_hash: str) -> Session | None:
        with self.SessionMaker() as session:
            s = session.query(self.Session).where(self.Session.hash == session_hash).first()
        if not s:
            return None
        if s.expires_at < datetime.datetime.utcnow():
            with self.SessionMaker() as session:
                session.delete(s)
                session.commit()
            return None
        return s
    
    def update_session(self, server_session: Session) -> Session | None:
        if not server_session.id:
            RuntimeError("DB: Tried Updating Session with non-existent ID")
        with self.SessionMaker() as session:
            session.add(server_session)
            session.commit()
        return server_session

    def create_new_session(self, user_id: int, value: str) -> Session:
        server_session = self.Session()
        server_session.user_id = user_id
        server_session.value = value
        random_seed = utils.crypt.random_string()
        server_session.hash = utils.crypt.hash_string(random_seed)
        with self.SessionMaker() as session:
            session.add(server_session)
            session.commit()
        return server_session
