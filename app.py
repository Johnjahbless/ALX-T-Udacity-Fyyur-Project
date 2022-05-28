#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from distutils.log import error
import json
from sqlalchemy import or_, desc
from os import abort
from site import venv
from time import time
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import * 
from flask_migrate import Migrate
import datetime
import time

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:56560000@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    num_upcoming_shows = db.Column(db.Integer, default=0)
    website_link = db.Column(db.String(50), nullable=True)
    seeking_talent = db.Column(db.String(), nullable=True)
    seeking_description = db.Column(db.String(), nullable=True)
    genres = db.Column(db.String(), nullable=True)
    created_date = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    shows = db.relationship('Show', backref='Venue', lazy=True);

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    num_upcoming_shows = db.Column(db.Integer, default=0)
    website_link = db.Column(db.String(50), nullable=True)
    seeking_venue = db.Column(db.String(), nullable=True)
    seeking_description = db.Column(db.String(), nullable=True)
    genres = db.Column(db.String(), nullable=True)
    created_date = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    available = db.Column(db.String(), nullable=True)
    shows = db.relationship('Show', backref='Artist', lazy=True);


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  date_time = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  value = value.isoformat()
  #datetime.strftime(value)
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  venues = Venue.query.order_by(desc('id')).limit(5).all()
  artists = Artist.query.order_by(desc('id')).limit(5).all()


  return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  areas = Venue.query.order_by('id').all()

  #declare an empty list to hold venues data
  venues = []

  for v in areas:
    #declare an empty dictionary to hold each venue data and their values
    my_dic = {}

    #declare an empty list to hold upcoming shows for each venue
    my_arr2 = []

    my_dic['city'] = v.city
    my_dic['state'] = v.state
    my_arr2.append({
      'id': v.id,
      "name": v.name,
      'num_upcoming_shows': v.num_upcoming_shows
    })
    my_dic['venues'] = my_arr2
    
    venues.append(my_dic)
  
 
  return render_template('pages/venues.html', areas=venues);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_text = request.form.get('search_term')

  # get all data from the table based on the search text using the 
  # LIKE keyword for either the name
  # of the venue, city or state  
  response = db.session.query(Venue).filter(or_ (Venue.name.ilike(f'%{search_text}%'), Venue.city.ilike(f'%{search_text}%'), Venue.state.ilike(f'%{search_text}%'))).all()

  # A dictionary that will hold all the data returned from the DB
  my_dic = {}

  # A list that will hold each venue data and thier values
  my_list = []

  # An int of the count increases based on the total num of results returned from the DB
  i = 0

  # A loop to loop through each returned data
  for a in response:
    # A dictionary that holds each venue and thier values
    my_dic2 = {}
    i = i + 1
    my_dic['count'] = i 
    my_dic2['id'] = a.id
    my_dic2['name'] = a.name
    my_dic2['num_upcoming_shows'] = a.num_upcoming_shows
    my_list.append(my_dic2)
    
  my_dic['data'] = my_list

  return render_template('pages/search_venues.html', results=my_dic, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.filter(Venue.id == venue_id).first()
  shows = Show.query.filter(Show.venue_id == venue_id).all()

  venue = {
    "id": data.id,
    "name": data.name,
    "genres": data.genres.split(','),
    "address": data.address,
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website": data.website_link,
    "facebook_link": data.facebook_link,
    "seeking_talent": data.seeking_talent,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link
  }

  # Current datetime in seconds
  t = time.time()

  # A list to hold all past shows
  my_list = []

  # A list to hold all upcoming shows
  my_list2 = []

  for s in shows:
    my_dic = {}
    if s.start_time.timestamp() < t :
      my_dic['artist_id'] = s.artist_id
      my_dic['artist_name'] = Artist.query.filter(Artist.id == s.artist_id).first().name
      my_dic['artist_image_link'] = Artist.query.filter(Artist.id == s.artist_id).first().image_link
      my_dic['start_time'] = s.start_time
      my_list.append(my_dic)

    else:
      my_dic['artist_id'] = s.artist_id
      my_dic['artist_name'] = Artist.query.filter(Artist.id == s.artist_id).first().name
      my_dic['artist_image_link'] = Artist.query.filter(Artist.id == s.artist_id).first().image_link
      my_dic['start_time'] = s.start_time
      my_list2.append(my_dic)

  venue['past_shows']= my_list
  venue['upcoming_shows'] = my_list2
  
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  error = False

  # Check if a values are available in the list to avoid server error
  if 'seeking_talent' in request.form:
    seeking_talent = request.form['seeking_talent']
  else:
    seeking_talent = ''

  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = ',' .join(request.form.getlist('genres'))
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    seeking_talent = seeking_talent
    seeking_description = request.form['seeking_description']

    venue = Venue(
      name = name, 
      city = city, 
      state = state, 
      address = address, 
      phone = phone, 
      genres = genres,
      facebook_link = facebook_link, 
      image_link = image_link, 
      website_link = website_link, 
      seeking_talent = seeking_talent,
      seeking_description = seeking_description
    )

    db.session.add(venue)
    db.session.commit()
  
  except Exception as e: 
    print(e)
    error = True
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    Show.query.filter(Show.venue_id==venue_id).delete()
    Venue.query.filter_by(id=venue_id).delete()

    db.session.commit()

  except Exception as e:
    error = True
    print(e)
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue could not be deleted.')

    
  else:
    flash('Venue was successfully deleted!')

  return redirect(url_for('index'))
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.order_by('id').all()

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_text = request.form.get('search_term')

  # get all data from the table based on the search text using the 
  # LIKE keyword for either the name
  # of the artist, city or state
  artists = db.session.query(Artist).filter(or_ (Artist.name.ilike(f'%{search_text}%'), Artist.city.ilike(f'%{search_text}%'), Artist.state.ilike(f'%{search_text}%'))).all()

  # A dictionary that will hold all the data returned from the DB
  my_dic = {}

  # A list that will hold each artist data and thier values
  my_list = []

  # An int of the count increases based on the total num of results returned from the DB
  i = 0

  # A loop to loop through each returned data
  for a in artists:
    # A dictionary that holds each venue and thier values
    my_dic2 = {}
    i = i + 1
    my_dic['count'] = i 
    my_dic2['id'] = a.id
    my_dic2['name'] = a.name
    my_dic2['num_upcoming_shows'] = a.num_upcoming_shows
    my_list.append(my_dic2)
  
  my_dic['data'] = my_list

  return render_template('pages/search_artists.html', results=my_dic, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = Artist.query.filter(Artist.id == artist_id).first()
  shows = Show.query.filter(Show.artist_id == artist_id).all()

  artist = {
    "id": data.id,
    "name": data.name,
    "genres": data.genres.split(','),
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website": data.website_link,
    "facebook_link": data.facebook_link,
    "seeking_venue": data.seeking_venue,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link,
    "available": data.available
  }

  # Current datetime in seconds
  t = time.time()

  my_list = []
  my_list2 = []

  for s in shows:
    my_dic = {}
    if s.start_time.timestamp() < t :
      my_dic['venue_id'] = s.venue_id
      my_dic['venue_name'] = Venue.query.filter(Venue.id == s.venue_id).first().name
      my_dic['venue_image_link'] = Venue.query.filter(Venue.id == s.venue_id).first().image_link
      my_dic['start_time'] = s.start_time
      my_list.append(my_dic)

    else:
      my_dic['venue_id'] = s.venue_id
      my_dic['venue_name'] = Venue.query.filter(Venue.id == s.venue_id).first().name
      my_dic['venue_image_link'] = Venue.query.filter(Venue.id == s.venue_id).first().image_link
      my_dic['start_time'] = s.start_time
      my_list2.append(my_dic)

  artist['past_shows']= my_list
  artist['upcoming_shows'] = my_list2

  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id == artist_id).first()
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False

  # Check if some values are available in the list to avoid server error
  if 'seeking_venue' in request.form:
    seeking_venue = request.form['seeking_venue']
  else:
    seeking_venue = ''

  if 'available' in request.form:
    available = request.form['available']
  else:
    available = ''

  try:
    artist = Artist.query.get(artist_id)

    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = ',' .join(request.form.getlist('genres'))
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    seeking_venue = seeking_venue
    seeking_description = request.form['seeking_description']
    available = available

    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.genres = genres
    artist.facebook_link = facebook_link
    artist.image_link = image_link
    artist.website_link = website_link
    artist.seeking_venue = seeking_venue
    artist.seeking_description = seeking_description
    artist.available = available

    db.session.commit()
  
  except Exception as e: 
    print(e)
    error = True
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
    
  else:
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully edited!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    Show.query.filter(Show.artist_id==artist_id).delete()
    Artist.query.filter_by(id=artist_id).delete()

    db.session.commit()

  except Exception as e:
    error = True
    print(e)
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist could not be deleted.')
    
  else:
    flash('Artist was successfully deleted!')

  return redirect(url_for('index'))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.filter(Venue.id == venue_id).first()

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False

    # Check if value is available in the list to avoid server error
  if 'seeking_talent' in request.form:
    seeking_talent = request.form['seeking_venue']
  else:
    seeking_talent = ''

  try:
    venue = Venue.query.get(venue_id)
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = ',' .join(request.form.getlist('genres'))
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    seeking_talent = seeking_talent
    seeking_description = request.form['seeking_description']

    venue.name = name
    venue.city = city
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.genres = genres
    venue.facebook_link = facebook_link
    venue.image_link = image_link
    venue.website_link = website_link
    venue.seeking_talent = seeking_talent
    venue.seeking_description = seeking_description

    db.session.commit()
  
  except Exception as e: 
    print(e)
    error = True
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')

    
  else:
    flash('Venue ' + request.form['name'] + ' was successfully edited!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False

  # Check if some values are available in the list to avoid server error
  if 'seeking_venue' in request.form:
    seeking_venue = request.form['seeking_venue']
  else:
    seeking_venue = ''

  if 'available' in request.form:
    available = request.form['available']
  else:
    available = ''

  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = ',' .join(request.form.getlist('genres'))
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    seeking_venue = seeking_venue
    available = available
    seeking_description = request.form['seeking_description']

    artist = Artist( name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, seeking_venue=seeking_venue, available=available, seeking_description=seeking_description )

    db.session.add(artist)
    db.session.commit()
  
  except Exception as e: 
    print(e)
    error = True
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

    
  else:
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.order_by('id').all()

  my_list = []

  for s in shows:
    my_dic = {}
    my_dic['venue_id'] = s.venue_id
    my_dic['venue_name'] = Venue.query.filter(Venue.id == s.venue_id).first().name
    my_dic['artist_id'] = s.artist_id
    my_dic['artist_name'] = Artist.query.filter(Artist.id == s.artist_id).first().name
    my_dic['artist_image_link'] = Artist.query.filter(Artist.id == s.artist_id).first().image_link
    my_dic['start_time'] = s.start_time

    my_list.append(my_dic)

  data = my_list

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False

  # Get the artist data by id to check availability
  artist = Artist.query.filter(Artist.id == request.form['artist_id']).first()

  # Check if artist is available
  if artist.available == 'y':
    artist_is_available = True
  else:
    artist_is_available = False  

  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    show = Show(artist_id = artist_id, venue_id = venue_id, start_time = start_time)
    
    if artist_is_available:
      db.session.add(show)
      db.session.commit()


  except Exception as e: 
    print(e)
    error = True
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    flash('An error occurred. show could not be listed.')

  elif artist_is_available == False:
    flash('Artist ' + artist.name + ' is not Currently Available. show could not be listed.')

  else: 

  # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
