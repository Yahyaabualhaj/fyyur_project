#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify,abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import os
from datetime import datetime
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database from flask_migrate import Migrate
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class ShowArtist(db.Model):
    __tablename__='show_artist'
    venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id', ondelete='CASCADE'),primary_key=True)
    artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id', ondelete='CASCADE'),primary_key=True)
    start_time = db.Column(db.DateTime,nullable=False)
    artists = db.relationship('Artist',backref=db.backref('venues_assoc',lazy=True)) 
    venues = db.relationship('Venue', backref=db.backref('artists_assoc',lazy=True))

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.relationship('VenueGenres',cascade="all, delete-orphan",backref='VenueGenres',lazy=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    artists = db.relationship('Artist',secondary='show_artist')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.relationship('ArtistGenres',cascade="all, delete-orphan",backref='ArtistGenres',lazy=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    artists = db.relationship('Venue',secondary='show_artist')

class ArtistGenres(db.Model):
  __tablename__='ArtistGenres'

  id = db.Column(db.Integer,primary_key=True)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id', ondelete='CASCADE'),nullable=False)
  name = db.Column(db.String(120))

class VenueGenres(db.Model):
  __tablename__='VenueGenres'

  id = db.Column(db.Integer,primary_key=True)
  venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id', ondelete='CASCADE'),nullable=False)
  name = db.Column(db.String(120))


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

 
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/', methods=["GET", "POST"])
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: 
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  today = datetime.now()
  data=[]
  for city, state in db.session.query(Venue.city,Venue.state).distinct():
    venues = []
    for id, name in db.session.query(Venue.id,Venue.name).filter_by(city=city):
      num_upcoming_shows = ShowArtist.query.filter(
        ShowArtist.venue_id==id,
        ShowArtist.start_time > today
        ).count()

      venue = {
        "id":id, "name":name,
        "num_upcoming_shows": num_upcoming_shows
      }

      venues.append(venue)

    _data = {
    "city": city,
    "state": state,
    "venues": venues
    }

    data.append(_data)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term=request.form.get('search_term', '')
  data= Venue.query.filter(Venue.name.ilike('%'+search_term+'%'))
  
  today = datetime.now()
  _date = []
  for d in data:
    venue_id = d.id
    num_upcoming_shows = ShowArtist.query.filter(
    ShowArtist.venue_id==venue_id,
    ShowArtist.start_time > today
    ).count()
    _d ={
      "id": d.id,
      "name": d.name,
      "num_upcoming_shows": num_upcoming_shows,
    }
    _date.append(_d)

  response={
    "count": data.count(),
    "data": _date,
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  today = datetime.now()
  _data = Venue.query.get(venue_id)
  
  upcoming_shows = ShowArtist.query.filter(
    ShowArtist.venue_id==venue_id,
    ShowArtist.start_time > today
    )

  _upcoming_shows = []
  for upcoming_show in upcoming_shows:
    artist = Artist.query.get(upcoming_show.artist_id)
    show = {
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(upcoming_show.start_time)
    }
    _upcoming_shows.append(show)

  past_shows = ShowArtist.query.filter(
    ShowArtist.venue_id==venue_id,
    ShowArtist.start_time < today
    )
  
  _past_shows = []
  for past_show in past_shows:
    artist = Artist.query.get(past_show.artist_id)
    show = {
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(past_show.start_time)
    }
    _past_shows.append(show)

  data={
    "id": _data.id,
    "name": _data.name,
    "genres": [genre.name for genre in _data.genres],
    "address": _data.address,
    "city": _data.city,
    "state": _data.state,
    "phone": _data.phone,
    "website": _data.website,
    "facebook_link": _data.facebook_link,
    "seeking_talent": _data.seeking_talent,
    "seeking_description": _data.seeking_description,
    "image_link": _data.image_link,
    "past_shows": _past_shows,
    "upcoming_shows": _upcoming_shows,
    "past_shows_count": past_shows.count(),
    "upcoming_shows_count": upcoming_shows.count(),
  }
  
  return render_template('pages/show_venue.html', venue=data)

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
  form = VenueForm()
  if form.validate_on_submit():
   
    try:

      new_venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        website=form.website.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        
        )

      db.session.add(new_venue)

      genres = form.genres.data
      for genre in genres:
        new_genre = VenueGenres(name = str(genre))
        new_venue.genres.append(new_genre)
        db.session.add(new_genre)
      
      db.session.commit()
      
      
      # on successful db insert, flash success
      flash('Venue ' + form.name.data + ' was successfully listed!')
    except:
      db.session.rollback()
      # on unsuccessful db insert, flash an error
      flash('An error occurred in data transfer. Venue ' + form.name.data+ ' could not be listed.')
    finally:
      db.session.close()

  else:
    flash('An error occurred. Venue ' + form.name.data+ ' could not be listed.')
   
  return render_template('pages/home.html')

@app.route('/venue/delete/<int:venue_id>',methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue_name=None
  try:
    del_venue = Venue.query.get(venue_id)
    venue_name =del_venue.name
    db.session.delete(del_venue)
    db.session.commit()
    error = False
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  if error:
      abort(500)
  else:
      flash('The Venue ' + venue_name+ ' is deleted.')
      return redirect(url_for('venues'))
     

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  data = db.session.query(Artist.id,Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  data= Artist.query.filter(Artist.name.ilike('%'+search_term+'%'))
  today = datetime.now()
  _date = []
  for d in data:
    artist_id = d.id
    num_upcoming_shows = ShowArtist.query.filter(
    ShowArtist.artist_id==artist_id,
    ShowArtist.start_time > today
    ).count()
    _d ={
      "id": d.id,
      "name": d.name,
      "num_upcoming_shows": num_upcoming_shows,
    }
    _date.append(_d)


  response={
    "count": data.count(),
    "data": _date,
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  today = datetime.now()
  _data = Artist.query.get(artist_id)
  
  upcoming_shows = ShowArtist.query.filter(
    ShowArtist.artist_id==artist_id,
    ShowArtist.start_time > today
    )

  _upcoming_shows = []
  for upcoming_show in upcoming_shows:
    venue = Venue.query.get(upcoming_show.venue_id)
    show = {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": str(upcoming_show.start_time)
    }
    _upcoming_shows.append(show)

  past_shows = ShowArtist.query.filter(
    ShowArtist.artist_id==artist_id,
    ShowArtist.start_time < today
    )
  
  _past_shows = []
  for past_show in past_shows:
    venue = Venue.query.get(past_show.venue_id)
    show = {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": str(past_show.start_time)
    }
    _past_shows.append(show)
  

  artist = Artist.query.get(artist_id)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": [genre.name for genre in artist.genres],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description":artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": _past_shows,
    "upcoming_shows": _upcoming_shows,
    "past_shows_count": past_shows.count(),
    "upcoming_shows_count": upcoming_shows.count(),
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  # TODO: populate form with fields from artist with ID <artist_id>
  
  form = ArtistForm()
  current_artist = Artist.query.get(artist_id)
  form.name.data = current_artist.name 
  form.city.data = current_artist.city 
  form.state.data = current_artist.state 
  form.address.data = current_artist.address 
  form.phone.data = current_artist.phone 
  form.website.data = current_artist.website
  form.image_link.data = current_artist.image_link 
  form.facebook_link.data = current_artist.facebook_link
  return render_template('forms/edit_artist.html', form=form, artist=current_artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm()
  if  form.validate_on_submit():
    

    try:
      current_artist = Artist.query.get(artist_id)
      current_artist.name = form.name.data
      current_artist.city = form.city.data
      current_artist.state = form.state.data
      
      current_artist.phone = form.phone.data
      current_artist.genres = form.genres.data
      current_artist.website = form.website.data
      current_artist.image_link = form.image_link.data
      current_artist.facebook_link = form.facebook_link.data

      genres = form.genres.data # request.form.getlist('genres',None)
      for genre in genres:
        new_genre = ArtistGenres(name = str(genre))
        current_artist.genres.append(new_genre)
        db.session.add(new_genre)

      db.session.commit()
    except:
      db.session.rollback()
    finally:
      db.session.close
      
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
 
  form = VenueForm()
  current_venue = Venue.query.get(venue_id)
  form.name.data = current_venue.name 
  form.city.data = current_venue.city 
  form.state.data = current_venue.state 
  form.address.data = current_venue.address 
  form.phone.data = current_venue.phone 
  form.website.data = current_venue.website
  form.image_link.data = current_venue.image_link 
  form.facebook_link.data = current_venue.facebook_link

  genres = VenueGenres.query.filter(VenueGenres.venue_id==venue_id)
  form.genres .data= genres #[genre for genre in genres]

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=current_venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
 
  form = VenueForm()
  

  if  form.validate_on_submit():
    try:
      current_venue = Venue.query.get(venue_id)
      current_venue.name = form.name.data
      current_venue.city = form.city.data
      current_venue.state = form.state.data
      current_venue.address = form.address.data
      current_venue.phone = form.phone.data
      current_venue.website = form.website.data
      current_venue.image_link = form.image_link.data
      current_venue.facebook_link = form.facebook_link.data


      genres = form.genres.data 
      for genre in genres:
        is_genre_exist = bool(VenueGenres.query.filter(
          VenueGenres.name==str(genre),
          VenueGenres.venue_id==venue_id
          ).first())

        if not is_genre_exist:

          new_genre = VenueGenres(name = str(genre))
          current_venue.genres.append(new_genre)
          db.session.add(new_genre)
      
      db.session.commit()
   
    except:
      db.session.rollback()
    finally:
      db.session.close
    

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
  form = ArtistForm()
  if form.validate_on_submit():
    
    try:

      new_artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        website=form.website.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        )

      db.session.add(new_artist)

      genres = form.genres.data
      for genre in genres:
        new_genre = ArtistGenres(name = str(genre))
        new_artist.genres.append(new_genre)
        db.session.add(new_genre)
      
      db.session.commit()
      
      
      # on successful db insert, flash success
      flash('Artist ' + form.name.data  + ' was successfully listed!')
    except:
      db.session.rollback()
      # on unsuccessful db insert, flash an error
      flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    finally:
      db.session.close()

  else:
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  today = datetime.now()
  data=[]
  for city, state in db.session.query(Venue.city,Venue.state).distinct():
    venues = []
    for id, name in db.session.query(Venue.id,Venue.name).filter_by(city=city):
      num_upcoming_shows = ShowArtist.query.filter(
        ShowArtist.venue_id==id,
        ShowArtist.start_time > today
        ).count()

      venue = {
        "id":id, "name":name,
        "num_upcoming_shows": num_upcoming_shows
      }

      venues.append(venue)
 
  shows = ShowArtist.query.all()
  data=[]
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    num_shows = ShowArtist.query.filter(ShowArtist.venue_id==show.venue_id).count()
    
    _show = {
    "venue_id": venue.id,
    "venue_name": venue.name,
    "artist_id": artist.id,
    "artist_name": artist.name,
    "artist_image_link": artist.image_link,
    "start_time": str(show.start_time)
    }
    data.append(_show)

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
  form = ShowForm()
  if form.validate_on_submit:
    
    try:
        
        new_show = ShowArtist(
        venue_id = form.venue_id.data,
        artist_id=form.artist_id.data,
        start_time=form.start_time.data
        )
       
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
      db.session.rollback()
      flash('Show could not be listed.')
    finally:
      db.session.close()
  
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  print('************************* >>>', form.errors)
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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''