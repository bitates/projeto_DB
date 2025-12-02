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
        select id_show, title, releaseDate, description, duration, tagline, num_seasons, metascore, metascore_count, userscore, userscore_count
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
                   natural join genres
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
        from shows natural join directed_by 
                   natural join people
        where id_show = ?
        order by name 
        ''',[id] 
        ).fetchall()
    
    created_by = db.execute(
        '''
        select id_name, name
        from shows natural join created_by 
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
    
    
@APP.route('/movies/search/<expr>/')
def search_movie(expr):
    search = { 'expr': expr}
    expr = '%' + expr + '%'
    movies = db.execute(
         '''
        select id_show, title
        from shows
        where title like ?
        ''', [expr]
    ).fetchall()
    return render_template('movie-search.html', search=search, movies=movies)

# writer

@APP.route('/writers/')
def list_writers():
    writers = db.execute(
        '''
        select id_name, name
        from shows natural join writen_by 
                   natural join people
        order by name
        ''').fetchall()
    return render_template('writer-list.html', writers=writers)    
    
@APP.route('/writers/<int:id>/')
def view_movies_by_writer(id):
    writer = db.execute(
        '''
        select id_name, name
        from people
        where id_name = ?
        ''',[id]
    ).fetchone()

    if writer is None:
        abort(404, 'Actor id {} does not exist.'.format(id))

    movies = db.execute(
        '''
        select id_show, title
        from shows natural join writen_by
                   natural join people
        where id_name = ?
        order by title
        ''',[id]
    ).fetchall()

    return render_template('writer.html', writer=writer, movies=movies)

@APP.route('/writers/search/<expr>/')
def search_writer(expr):
    search = { 'expr': expr}
    expr = '%' + expr + '%'
    writers = db.execute(
        '''
        select id_name, name
        from people
        where name like ?
        ''',[expr]
    ).fetchall()

    return render_template('writer-search.html', search=search, writers=writers)
    
#--- disrectors

@APP.route('/directors/')
def list_directors():
    directors = db.execute(
        '''
        select id_name, name
        from shows natural join directed_by 
                   natural join people
        order by name
        ''').fetchall()
    return render_template('director-list.html', directors=directors)    
    
@APP.route('/directors/<int:id>/')
def view_movies_by_director(id):
    director = db.execute(
        '''
        select id_name, name
        from people
        where id_name = ?
        ''',[id]
    ).fetchone()

    if director is None:
        abort(404, 'Director id {} does not exist.'.format(id))

    movies = db.execute(
        '''
        select id_show, title
        from shows natural join directed_by
                   natural join people
        where id_name = ?
        order by title
        ''',[id]
    ).fetchall()

    return render_template('director.html', director=director, movies=movies)

@APP.route('/directors/search/<expr>/')
def search_director(expr):
    search = { 'expr': expr}
    expr = '%' + expr + '%'
    directors = db.execute(
        '''
        select id_name, name
        from people
        where name like ?
        ''',[expr]
    ).fetchall()

    return render_template('director-search.html', search=search, directors=directors)

#--- creators

@APP.route('/creators/')
def list_creators():
    creators = db.execute(
        '''
        select id_name, name
        from shows natural join created_by 
                   natural join people
        order by name
        ''').fetchall()
    return render_template('creator-list.html', creators=creators)    
    
@APP.route('/creators/<int:id>/')
def view_movies_by_creator(id):
    creator = db.execute(
        '''
        select id_name, name
        from people
        where id_name = ?
        ''',[id]
    ).fetchone()

    if creator is None:
        abort(404, 'Creator id {} does not exist.'.format(id))

    movies = db.execute(
        '''
        select id_show, title
        from shows natural join created_by
                   natural join people
        where id_name = ?
        order by title
        ''',[id]
    ).fetchall()

    return render_template('creator.html', creator=creator, movies=movies)

@APP.route('/creators/search/<expr>/')
def search_creator(expr):
    search = { 'expr': expr}
    expr = '%' + expr + '%'
    creators = db.execute(
        '''
        select id_name, name
        from people
        where name like ?
        ''',[expr]
    ).fetchall()

    return render_template('creator-search.html', search=search, creators=creators)


# cast

@APP.route('/cast/')
def list_cast():
    cast = db.execute(
        '''
        select id_name, name
        from shows natural join cast_by 
                   natural join people
        order by name
        ''').fetchall()
    return render_template('cast-list.html', cast=cast)    
    
@APP.route('/cast/<int:id>/')
def view_movies_by_cast(id):
    cast = db.execute(
        '''
        select id_name, name
        from people
        where id_name = ?
        ''',[id]
    ).fetchone()

    if cast is None:
        abort(404, 'Cast id {} does not exist.'.format(id))

    movies = db.execute(
        '''
        select id_show, title
        from shows natural join cast_by
                   natural join people
        where id_name = ?
        order by title
        ''',[id]
    ).fetchall()

    return render_template('cast.html', cast=cast, movies=movies)

@APP.route('/cast/search/<expr>/')
def search_cast(expr):
    search = { 'expr': expr}
    expr = '%' + expr + '%'
    cast = db.execute(
        '''
        select id_name, name
        from people
        where name like ?
        ''',[expr]
    ).fetchall()

    return render_template('cast-search.html', search=search, cast=cast)




@APP.route('/genres/')
def list_genres():
    genres = db.execute(
        '''
        select id_genre, genre
        from genres
        order by genre  
        ''').fetchall()

    return render_template('genre-list.html', genres=genres)    

@APP.route('/genres/<int:id>')
def view_movies_by_genre(id):
    genre = db.execute(
        '''
        select id_genre, genre
        from genres
        where id_genre = ?
        ''',[id]).fetchone()

    if genre is None:
        abort(404, 'Genre id {} does not exit.'.format(id))
    
    movies = db.execute(
        '''
        select id_show, title
        from shows natural join genre_of
                   natural join genres
        where id_genre = ?
        order title
        ''',[id]
    ).fetchall()

    return render_template('genre.html', genre=genre, movies=movies)

