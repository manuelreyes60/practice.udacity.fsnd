#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from flask_wtf.csrf import CSRFProtect
from models import Venue, Artist, Show, db

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

csrf = CSRFProtect(app)
csrf.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  try:
    date = dateutil.parser.parse(value)
  except:
    date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Helpers.
#----------------------------------------------------------------------------#
def GetCompleteInfoFrom(model):
  model.past_shows = model.GetPastShows()
  model.upcoming_shows = model.GetUpComingShows()
  model.past_shows_count = len(model.past_shows)
  model.upcoming_shows_count = len(model.upcoming_shows)
  return model

def GetVenuesFrom(city, state):
  venuesFound = Venue.query.filter_by(state=state).filter_by(city=city).all()
  return GetInfoFrom(venuesFound)

def GetInfoFrom(models):
  info = []
  for model in models:
    info.append({
        'id': model.id,
        'name': model.name,
        'num_upcoming_shows': len(model.GetUpComingShows())
    })
  return info

def DBActionSuccessful(action=None, *args):
  successful = True
  try:
      if(action):
        if args: action(args[0])
        else: action()
      db.session.commit()
  except Exception as e:
      successful = False
      db.session.rollback()
      return render_template('errors/500.html', error=str(e))
  finally:
      db.session.close()
  return successful

def FlashMessage(condition, successMsg, erroMsg):
  if not condition:
    abort(400)
    flash(f"An error occurred. {erroMsg}", 'danger')
  if condition:
      flash(f"{successMsg}", 'success')

def SearchFor(model, searchTerm):
  models = model.query.filter(func.lower(model.name).contains(searchTerm)).all()
  modelsInfo = GetInfoFrom(models)

  results = {
      'data': modelsInfo,
      'count': len(modelsInfo)
  }

  return results

def IsFormValid(form):
  if not form.validate():
      for fieldName, errorMessages in form.errors.items():
        flash(f"Some errors on {fieldName.replace('_', ' ')}: " + ''.join([str(message) for message in errorMessages]), 'warning')
      return False
  return True

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#----------------------------------------------------------------------------#
#  Venues
#----------------------------------------------------------------------------#

@app.route('/venues')
def venues():
  areas = []
  availableAreas = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

  for availableArea in availableAreas:
    areas.append({
        'city': availableArea.city,
        'state': availableArea.state,
        'venues': GetVenuesFrom(availableArea.city, availableArea.state)
    })

  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  return render_template('pages/search_venues.html', results=SearchFor(Venue, search_term), search_term=search_term )

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  return render_template('pages/show_venue.html', venue=GetCompleteInfoFrom(Venue.query.get(venue_id)))

#----------------------------------------------------------------------------#
#  Create Venue
#----------------------------------------------------------------------------#

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  return render_template('forms/new_venue.html', form=VenueForm())

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()

  if not IsFormValid(form):
    return redirect('/venues/create')

  venue = Venue(
    name=request.form['name'],
    city=request.form['city'],
    state=request.form['state'],
    address=request.form['address'],
    phone=request.form['phone'],
    genres=request.form.getlist('genres'),
    image_link=request.form['image_link'],
    facebook_link=request.form['facebook_link'],
    website=request.form['website'],
    seeking_talent=True if 'seeking_talent' in request.form else False,
    seeking_description=request.form['seeking_description'],
  )

  success = DBActionSuccessful(db.session.add, venue)
  FlashMessage(success, f"Venue {request.form['name']} was successfully listed!", f"Venue {request.form['name']} could not be listed.")

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  success = DBActionSuccessful(Venue.query.filter_by(id=venue_id).delete)
  FlashMessage(success, 'Venue was successfully deleted!', 'Venue could not be deleted.')

  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Artists
#----------------------------------------------------------------------------#

@app.route('/artists')
def artists():
  artists = Artist.query.with_entities(Artist.id, Artist.name).order_by('id').all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  return render_template('pages/search_artists.html', results=SearchFor(Artist, search_term), search_term=search_term )

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  return render_template('pages/show_artist.html', artist=GetCompleteInfoFrom(Artist.query.get(artist_id)))

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter(Artist.id == artist_id).first()

  form = ArtistForm()
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.website.data = artist.website
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()

  if not IsFormValid(form):
    return redirect(f'/artists/{artist_id}/edit')

  artist = Artist.query.get(artist_id)
  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.genres = request.form.getlist('genres')
  artist.image_link = request.form['image_link']
  artist.facebook_link = request.form['facebook_link']
  artist.website = request.form['website']
  artist.seeking_talent = True if 'seeking_talent' in request.form else False
  artist.seeking_description = request.form['seeking_description']

  success = DBActionSuccessful()
  FlashMessage(success, f"Artist {request.form['name']} was successfully Updated!", f"Artist {request.form['name']} could not be updated.")

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter(Venue.id == venue_id).first()

  form = VenueForm()
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.website.data = venue.website
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm()

  if not IsFormValid(form):
    return redirect(f'/venues/{venue_id}/edit')

  venue = Venue.query.get(venue_id)
  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.address = request.form['address']
  venue.phone = request.form['phone']
  venue.genres = request.form.getlist('genres')
  venue.image_link = request.form['image_link']
  venue.facebook_link = request.form['facebook_link']
  venue.website = request.form['website']
  venue.seeking_talent = True if 'seeking_talent' in request.form else False
  venue.seeking_description = request.form['seeking_description']

  success = DBActionSuccessful()
  FlashMessage(success, f"Venue {request.form['name']} was successfully Updated!", f"Venue {request.form['name']} could not be updated.")

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()

  if not IsFormValid(form):
    return redirect('/artists/create')

  artist = Artist(
    name=request.form['name'],
    city=request.form['city'],
    state=request.form['state'],
    phone=request.form['phone'],
    genres=request.form.getlist('genres'),
    image_link=request.form['image_link'],
    facebook_link=request.form['facebook_link'],
    website=request.form['website'],
    seeking_venue=True if 'seeking_venue' in request.form else False,
    seeking_description=request.form['seeking_description'],
  )

  success = DBActionSuccessful(db.session.add, artist)
  FlashMessage(success, f"Artist {request.form['name']} was successfully listed!", f"Artist {request.form['name']} could not be listed.")

  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []

  shows = db.session.query(Venue.name, Artist.name, Artist.image_link, Show.venue_id, Show.artist_id, Show.start_time) \
    .filter(Venue.id == Show.venue_id, Artist.id == Show.artist_id)

  for show in shows:
      data.append({
        'venue_name': show[0],
        'artist_name': show[1],
        'artist_image_link': show[2],
        'venue_id': show[3],
        'artist_id': show[4],
        'start_time': str(show[5])
      })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()

  show = Show(
    artist_id=request.form['artist_id'],
    venue_id=request.form['venue_id'],
    start_time=request.form['start_time'],
  )

  success = DBActionSuccessful(db.session.add, show)
  FlashMessage(success, f"Show was successfully listed!", f"Show could not be listed.")
  return render_template('pages/home.html')

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
