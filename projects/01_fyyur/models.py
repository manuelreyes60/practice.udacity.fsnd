from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from datetime import datetime

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String(50)))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(300))
    shows = db.relationship('Show', backref=db.backref('Venue'), lazy="joined")
    past_shows = []
    upcoming_shows = []

    def GetPastShows(self):
      pastShows = db.session.query(Show).join(Artist).filter(Show.venue_id==self.id).filter(Show.start_time < datetime.now()).all()
      return self.GetShowsArtistInfo(pastShows)

    def GetUpComingShows(self):
      upComingShows = db.session.query(Show).join(Artist).filter(Show.venue_id==self.id).filter(Show.start_time >= datetime.now()).all()
      return self.GetShowsArtistInfo(upComingShows)

    def GetBasicInfo(self):
      return {
        'venue_id': self.id,
        'venue_name': self.name,
        'venue_image_link': self.image_link
      }

    def GetShowsArtistInfo(self, shows):
        shows_info = []
        if len(shows) > 0:
            for show in shows:
                shows_info.append(show.GetArtistInfo())
        return shows_info

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String(50)))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(300))
    shows = db.relationship('Show', backref=db.backref('Artist'), lazy="joined")

    def GetPastShows(self):
      pastShows = db.session.query(Show).join(Venue).filter(Show.artist_id==self.id).filter(Show.start_time < datetime.now()).all()
      return self.GetShowsVenueInfo(pastShows)

    def GetUpComingShows(self):
      upComingShows = db.session.query(Show).join(Venue).filter(Show.artist_id==self.id).filter(Show.start_time >= datetime.now()).all()
      return self.GetShowsVenueInfo(upComingShows)

    def GetBasicInfo(self):
      return {
        'artist_id': self.id,
        'artist_name': self.name,
        'artist_image_link': self.image_link
      }

    def GetShowsVenueInfo(self, shows):
        shows_info = []
        if len(shows) > 0:
            for show in shows:
                shows_info.append(show.GetVenueInfo())
        return shows_info

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def GetArtistInfo(self):
      artist = Artist.query.get(self.artist_id)
      return self.GetBasicInfoFrom(artist)

    def GetVenueInfo(self):
      venue = Venue.query.get(self.venue_id)
      return self.GetBasicInfoFrom(venue)

    def GetBasicInfoFrom(self, model):
      basicInfo = model.GetBasicInfo()
      basicInfo['start_time'] = str(self.start_time)
      return basicInfo