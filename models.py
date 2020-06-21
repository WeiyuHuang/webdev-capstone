import os
from sqlalchemy import Column, String, Integer, Date, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

db_path = "postgres://ghysxaicsnfpru:12e663bdab7d54b349f96eb72e2f4b989ce93c3296812d93e16b42bf8aaa319e@ec2-54-86-170-8.compute-1.amazonaws.com:5432/dfd1o53eo8m4gp"
# if not db_path:
#     db_name = "movies_test_2"
#     db_path = "postgres://{}/{}".format("localhost:5432", db_name)

db = SQLAlchemy()


def setup_db(app, db_path=db_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = db_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


class Movie(db.Model):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    release_date = Column(Date)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def deletes(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date
        }


class Actor(db.Model):
    __tablename__ = 'actors'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def deletes(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.name,
            'title': self.age,
            'release_date': self.gender
        }
