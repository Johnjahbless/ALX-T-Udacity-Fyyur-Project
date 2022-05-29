from sqlalchemy import or_
from time import time
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import * 
import time

# Import models
from models.models import Venue, Artist, Show

db = SQLAlchemy()



#  Venues
#  ----------------------------------------------------------------

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
      'num_upcoming_shows': 0
    })
    my_dic['venues'] = my_arr2
    
    venues.append(my_dic)
  
 
  return render_template('pages/venues.html', areas=venues);

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
    my_dic2['num_upcoming_shows'] = 0
    my_list.append(my_dic2)
    
  my_dic['data'] = my_list

  return render_template('pages/search_venues.html', results=my_dic, search_term=request.form.get('search_term', ''))


def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.filter(Venue.id == venue_id).first()
  shows = Show.query.filter(Show.venue_id == venue_id).all()

  venue = {
    "id": data.id,
    "name": data.name,
    "genres": data.genres,
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

def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

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


def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    db.session.query(Show).filter_by(venue_id=venue_id).delete()
    db.session.query(Venue).filter_by(id=venue_id).delete()

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


  
def edit_venue(venue_id):
  form = VenueForm()
  
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.filter(Venue.id == venue_id).first()

  return render_template('forms/edit_venue.html', form=form, venue=venue)


def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False

    # Check if value is available in the list to avoid server error
  if 'seeking_talent' in request.form:
    seeking_talent = request.form['seeking_talent']
  else:
    seeking_talent = ''

  try:
    venue = db.session.query(Venue).filter_by(id=venue_id).first()

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

  return redirect(url_for('venue_bp.show_venue', venue_id=venue_id))