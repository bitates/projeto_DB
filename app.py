import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
    stats = {}
    stats = db.execute('''
    select * from 
        (select count(*) n_movies from shows)
    join
        (select count(*) n_genres from genres)
    join
        (select count(*) n_people from people)
    join
        (select count(*) n_companies from companies)
    join 
        (select count(*) n_rating from ratings)
    ''').fetchone()
    logging.info(stats)
    return render_template('index.html', stats = stats)

@APP.route('/movies/')
def list_movies():
    movies = db.execute(
        '''
        select id_shows, title, releaseDate, duration, tagline
        from shows
        order by title
        '''
    ).fetchall()
    return render_template('movie-list.html', movies=movies)

@APP.route('/movies/<int:id>')
def get_movie(id):
    movie = db.execute(
        '''
        select id_show, title, releaseDate, description, duration, tagline, num_seasons
        from shows
        where id_shows = ? 
        ''', [id]).fetchone()

    if movie is None:
            abort(404, 'Movie id {} does not exist.'.format(id))

    genres = db.execute(
        '''
        select id_genre, genre
        from shows natural join genre_of 
                   natural join GENRE
        where show_id = ?
        order by genre
        ''',[id]).fetchall()
    
