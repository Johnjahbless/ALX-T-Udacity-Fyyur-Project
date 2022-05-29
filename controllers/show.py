from sqlalchemy import or_
from flask import render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import * 

# Import models
from models.models import Venue, Artist, Show

db = SQLAlchemy()


#  Shows
#  ----------------------------------------------------------------

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

def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


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
