import datetime, json, logging, time

from dataclasses import asdict
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func

from db import DB

logger = logging.getLogger("file")


class SchemaEncoder(json.JSONEncoder):
    """Encoder for converting Model objects into JSON."""

    def default(self, obj):
        if isinstance(obj, datetime.date):
            return time.strftime("%Y-%m-%dT%H:%M:%SZ", obj.utctimetuple())
        return json.JSONEncoder.default(self, obj)


class SessionHandler:
    __instance = None

    def __init__(self, session, model):
        """Virtually private constructor."""

        SessionHandler.__instance = self
        self.model = model
        self.session = session

    @staticmethod
    def create(session, model):
        SessionHandler.__instance = SessionHandler(session, model)
        return SessionHandler.__instance

    def add(self, record_dict):
        record_model = self.model(**record_dict)
        self.session.add(record_model)

    def insert_many(self, record_list):
        statements = [
            pg_insert(self.model).values(record_dict).on_conflict_do_nothing()
            for record_dict in record_list
        ]
        return [self.session.execute(statement) for statement in statements]

    def add_many(self, record_list):
        return self.session.add_all(
            [self.model(**record_dict) for record_dict in record_list]
        )

    def update(self, query_dict, update_dict):
        return (
            self.session.query(self.model).filter_by(**query_dict).update(update_dict)
        )

    def upsert(self, record_dict, set_dict, constraint):
        statement = (
            pg_insert(self.model)
            .values(record_dict)
            .on_conflict_do_update(constraint=constraint, set_=set_dict)
        )
        return self.session.execute(statement)

    def get(self, id, to_json=None):
        result = self.session.query(self.model).get(id)
        return asdict(result) if to_json is None else self.to_json(result)

    def get_one(self, query_dict, to_json=None):
        result = self.session.query(self.model).filter_by(**query_dict).first()
        return asdict(result) if to_json is None else self.to_json(result)

    def get_latest(self, query_dict, to_json=None):
        result = (
            self.session.query(self.model)
            .filter_by(**query_dict)
            .order_by(self.model.updated_at.desc())
            .first()
        )
        return (
            None
            if result is None
            else (asdict(result) if to_json is None else self.to_json(result))
        )

    def get_count(self, query_dict, to_json=None):
        return self.session.query(self.model).filter_by(**query_dict).count()

    def get_total_count(self):
        return self.session.query(self.model).count()

    def get_all(self, query_dict, to_json=None):
        results = self.session.query(self.model).filter_by(**query_dict).all()
        return [
            asdict(result) if to_json is None else self.to_json(result)
            for result in results
        ]

    def delete(self, query_dict):
        return self.session.query(self.model).filter_by(**query_dict).delete()

    def to_json(self, record_obj):
        return json.dumps(asdict(record_obj), cls=SchemaEncoder, ensure_ascii=False)

    def get_latest_row(self, to_json=None):
        result = (
            self.session.query(self.model).order_by(self.model.played_at.desc()).first()
        )
        return (
            None
            if result is None
            else (asdict(result) if to_json is None else self.to_json(result))
        )

    def get_top_songs(self, to_json=None):
        return (
            self.session.query(func.count(self.model.song_id), self.model.song_id)
            .group_by(self.model.song_id)
            .order_by(func.count(self.model.song_id).desc())
            .limit(100)
            .all()
        )
