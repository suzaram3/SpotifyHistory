from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func
from db import DB


db = DB("prod")
engine = db.engine
Session = sessionmaker(bind=engine)


class SessionHandler:
    def get_all_records(self, session: object, model: object) -> list:
        return list(session.query(model).all())

    def get_table_count(self, session: object, model: object) -> int:
        return {"model": model, "count": session.query(model).count()}

    def insert_many(self, session: object, payload: dict) -> None:
        """Bulk insert into model"""
        statements = [
            pg_insert(payload["model"]).values(record).on_conflict_do_nothing()
            for record in payload["records"]
        ]
        [session.execute(statement) for statement in statements]
        return self.get_table_count(session, payload["model"])

    @contextmanager
    def session_scope(self) -> None:
        session = Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
