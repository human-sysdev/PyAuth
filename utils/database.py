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
    
    class RequestState(Base):
        __tablename__ = "request_state"
        id = sql.Column(sql.Integer, unique=True, primary_key=True)
        value = sql.Column(sql.String)
        code = sql.Column(sql.String)
        token = sql.Column(sql.String)
        created_at = sql.Column(sql.DateTime)
    
    def create_new_request_state(self) -> RequestState:
        rs = self.RequestState()
        rs.created_at = datetime.datetime.utcnow()
        rs.value = utils.crypt.random_string()
        with self.SessionMaker() as session:
            session.add(rs)
            session.commit()
        return rs
    
    def get_request_state_by_value(self, value: str) -> RequestState:
        with self.SessionMaker() as session:
            rs = session.query(self.RequestState).where(self.RequestState.value == value).first()
        return rs
    
    def get_request_state_by_id(self, id: int) -> RequestState:
        with self.SessionMaker() as session:
            rs = session.query(self.RequestState).where(self.RequestState.id == id).first()
        return rs

    def update_request_state(self, request_state: RequestState) -> RequestState | None:
        if not request_state.id:
            RuntimeError("DB: Tried Updating request state of non-existent ID")
        with self.SessionMaker() as session:
            session.add(request_state)
            session.commit()
        return request_state