from sqlalchemy import or_
from time import time
from flask import render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import * 
import time

# Import models
from models.models import Venue, Artist, Show

db = SQLAlchemy()


#  Artists
#  ----------------------------------------------------------------
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.order_by('id').all()

  return render_template('pages/artists.html', artists=artists)


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
    my_dic2['num_upcoming_shows'] = Show.query.filter_by(artist_id=a.id).count()
    my_list.append(my_dic2)
  
  my_dic['data'] = my_list

  return render_template('pages/search_artists.html', results=my_dic, search_term=request.form.get('search_term', ''))


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

def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id == artist_id).first()
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)


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
    artist = db.session.query(Artist).filter_by(id=artist_id).first()

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

  return redirect(url_for('artist_bp.show_artist', artist_id=artist_id))


def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    db.session.query(Show).filter_by(artist_id=artist_id).delete()
    db.session.query(Artist).filter_by(id=artist_id).delete()

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


def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


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