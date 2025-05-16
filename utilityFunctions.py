from SqlQuery import *
import requests
import sqlite3
import psycopg2


# Database connection with timeout and WAL mode
def db_connection(db_name):
    conn = None
    try:
        conn = sqlite3.connect(f"./model/data/{db_name}.sqlite", timeout=10)
        conn.execute("PRAGMA journal_mode=WAL;")
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
    return conn


# Get trailer key safely
def fetchTrailer(movie_id, movies_result):
    for row in movies_result:
        if row[1] == movie_id:
            movie_index = row[0]
            return movies_result[movie_index][12]
    return None  # Return None if not found


# Get Backdrop image path with timeout and error handling
def fetchBackdrop(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=65669b357e1045d543ba072f7f533bce&language=en-US',
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        backdrop_path = data.get('backdrop_path')
        if backdrop_path:
            return f"https://image.tmdb.org/t/p/original{backdrop_path}"
        else:
            return "https://via.placeholder.com/500x281?text=No+Image+Available"
    except requests.exceptions.Timeout:
        print(f"Request to fetch backdrop for movie_id {movie_id} timed out.")
        return "https://via.placeholder.com/500x281?text=No+Image+Available"
    except requests.exceptions.RequestException as e:
        print(f"An error occurred fetching backdrop for movie_id {movie_id}: {e}")
        return "https://via.placeholder.com/500x281?text=No+Image+Available"


# Get poster image path safely
def fetchPoster(movie_id, movies_result):
    for row in movies_result:
        if row[1] == movie_id:
            movie_index = row[0]
            return movies_result[movie_index][11]
    return "https://via.placeholder.com/500x281?text=No+Image+Available"


# Get 3 recommended movies based on genres and cast chosen by user
def byChoice(genreList, castList):
    conn = db_connection("choice")
    cursor = conn.cursor()
    cursor.execute(FETCH_ALL_CHOICE)
    results = cursor.fetchall()

    for row in results:
        cf = 0
        mov_cast = list(row[4].split("$"))
        for cast in mov_cast:
            if cast in castList:
                cf += 1
        if cf != 0:
            cursor.execute(f"UPDATE choice SET castFre = {cf} WHERE movie_id = {row[1]}")

    for row in results:
        gf = 0
        mov_gen = list(row[3].split("$"))
        for gen in mov_gen:
            if gen in genreList:
                gf += 1
        if gf != 0:
            cursor.execute(f"UPDATE choice SET genFre = {gf} WHERE movie_id = {row[1]}")

    cursor.execute(SORT_BY_CAST)
    results = cursor.fetchall()
    conn.close()

    choice_movies = [row[0] for row in results[:3]]
    return choice_movies


# Get most popular movies in that genre
def byGenre(genre, movies_result):
    counter = 0
    genre_movies = []
    genre_posters = []

    conn = db_connection("popular")
    cursor = conn.cursor()
    cursor.execute(FETCH_GENRES_POPULAR)
    results = cursor.fetchall()

    for row in results:
        if counter == 6:
            break
        mov_gen = list(row[1].split("$"))
        if genre in mov_gen:
            cursor.execute(f"SELECT title FROM popular WHERE movie_id = '{row[0]}'")
            title = cursor.fetchone()
            if title:
                genre_movies.append(title[0])
                genre_posters.append(fetchPoster(row[0], movies_result))
                counter += 1

    conn.close()
    return genre_movies, genre_posters


# Get most popular movies of that year
def byYear(year, movies_result):
    counter = 0
    year_movies = []
    year_posters = []

    conn = db_connection("popular")
    cursor = conn.cursor()
    cursor.execute(FETCH_DATE_POPULAR)
    results = cursor.fetchall()

    for row in results:
        if counter == 6:
            break
        if year == row[1]:
            cursor.execute(f"SELECT title FROM popular WHERE movie_id = '{row[0]}'")
            title = cursor.fetchone()
            if title:
                year_movies.append(title[0])
                year_posters.append(fetchPoster(row[0], movies_result))
                counter += 1

    conn.close()
    return year_movies, year_posters
