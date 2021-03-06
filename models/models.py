from enum import unique
from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(120), unique=True, nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(50), nullable=True)
    seeking_talent = db.Column(db.String(), nullable=True)
    seeking_description = db.Column(db.String(), nullable=True)
    genres = db.Column(db.String(), nullable=False)
    created_date = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    shows = db.relationship('Show', backref='Venue', lazy=True);


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), unique=True, nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(50), nullable=True)
    seeking_venue = db.Column(db.String(), nullable=True)
    seeking_description = db.Column(db.String(), nullable=True)
    genres = db.Column(db.String(), nullable=False)
    created_date = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    available = db.Column(db.String(), nullable=True)
    shows = db.relationship('Show', backref='Artist', lazy=True);


class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
