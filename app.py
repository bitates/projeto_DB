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
        select id_show, title, releaseDate, duration, tagline
        from shows
        order by title
        '''
    ).fetchall()
    return render_template('movie-list.html', movies=movies)

@APP.route('/movies/<int:id>')
def get_movie(id):
    movie = db.execute(
        '''
        select id_show, title, releaseDate, description, duration, tagline, num_seasons, metascore, metascore_count, userscore, userscore_cout
        from shows
        where id_show = ? 
        ''', [id]).fetchone()

    if movie is None:
            abort(404, 'Movie id {} does not exist.'.format(id))

    sentiment_u = db.execute(
        '''
        select s_id, sentiment
        from shows natural join userscore
                   natural join sentiments
        where id_show = ?
        ''',[id]
    ).fetchone()

    sentiment_m = db.execute(
        '''
        select s_id, sentiment
        from shows natural join metascore
                   natural join sentiments
        where id_show = ?
        ''',[id]
    ).fetchone()
    
    genres = db.execute(
        '''
        select id_genre, genre
        from shows natural join genre_of 
                   natural join GENRE
        where id_show = ?
        order by genre
        ''',[id]
        ).fetchall()
    
    writer = db.execute(
        '''
        select id_name, name
        from shows natural join writen_by 
                   natural join people
        where id_show = ?
        order by name 
        ''',[id] 
        ).fetchall()

    director = db.execute(
        '''
        select id_name, name
        from shows natural join  directed_by 
                   natural join people
        where id_show = ?
        order by name 
        ''',[id] 
        ).fetchall()
    
    created_by = db.execute(
        '''
        select id_name, name
        from shows natural join  created_by 
                   natural join people
        where id_show = ?
        order by name 
        ''',[id] 
        ).fetchall()

    cast = db.execute(
        '''
        select id_name, name
        from shows natural join cast_by 
                   natural join people
        where id_show = ?
        order by name 
        ''',[id] 
        ).fetchall()

    rating = db.execute(
        '''
        select r_id, rating
        from shows natural join rating
                   natural join ratings
        where id_show = ?
        order by rating 
        ''',[id]
        ).fetchone()

    return render_template('movie.html',
                movie=movie, sentiment_u=sentiment_u, sentiment_m =sentiment_m, genres=genres, writer=writer, director=director, created_by=created_by, cast=cast, rating=rating )   
    
    
