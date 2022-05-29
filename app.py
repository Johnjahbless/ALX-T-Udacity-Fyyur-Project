#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from sqlalchemy import desc
import dateutil.parser
import babel
from flask import Flask, render_template
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import * 
from flask_migrate import Migrate

from models.models import db, Venue, Artist

# Imports routes blueprints
from routes.venue_bp import venue_bp
from routes.artist_bp import artist_bp
from routes.show_bp import show_bp

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# Register routes blueprint
app.register_blueprint(venue_bp, url_prefix='/venues')
app.register_blueprint(artist_bp, url_prefix='/artists')
app.register_blueprint(show_bp, url_prefix='/shows')




# TODO: connect to a local postgresql database



@app.route('/')
def index():
  venues = Venue.query.order_by(desc('id')).limit(5).all()
  artists = Artist.query.order_by(desc('id')).limit(5).all()


  return render_template('pages/home.html', venues=venues, artists=artists)


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


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
