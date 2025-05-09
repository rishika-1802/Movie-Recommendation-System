from SqlQuery import *
import requests
import sqlite3
import psycopg2


# Database connections
def db_connection(db_name):
    conn = None
    try:
        # SQLite connection with timeout and WAL mode
        conn = sqlite3.connect("./model/data/" + db_name + ".sqlite", timeout=10)  # Wait up to 10 seconds if locked
        conn.execute("PRAGMA journal_mode=WAL;")  # Enable Write-Ahead Logging for better concurrency
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
    return conn


# Get trailer key
def fetchTrailer(movie_id, movies_result):
    for row in movies_result:
        if row[1] == movie_id:
            movie_index = row[0]
            break
    key = movies_result[movie_index][12]
    return key


# Get Backdrop image path
def fetchBackdrop(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=65669b357e1045d543ba072f7f533bce&language=en-US',
            timeout=10  # Set a timeout of 10 seconds
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        return "https://image.tmdb.org/t/p/original" + str(data.get('backdrop_path', ''))
    except requests.exceptions.Timeout:
        print(f"Request to fetch backdrop for movie_id {movie_id} timed out.")
        return "https://via.placeholder.com/500x281?text=No+Image+Available"
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return "https://via.placeholder.com/500x281?text=No+Image+Available"


# Get poster image path
def fetchPoster(movie_id, movies_result):
    for row in movies_result:
        if row[1] == movie_id:
            movie_index = row[0]
            break
    poster = movies_result[movie_index][11]
    return poster


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
            for c in castList:
                if cast == c:
                    cf += 1
        if cf != 0:
            sql_query = f"Update choice set castFre = {cf} where movie_id = {row[1]}"
            cursor.execute(sql_query)

    for row in results:
        gf = 0
        mov_gen = list(row[3].split("$"))
        for gen in mov_gen:
            for g in genreList:
                if gen == g:
                    gf += 1
        if gf != 0:
            sql_query = f"Update choice set genFre = {gf} where movie_id = {row[1]}"
            cursor.execute(sql_query)

    cursor.execute(SORT_BY_CAST)
    results = cursor.fetchall()
    conn.close()  # Close the connection

    choice_movies = []
    counter = 0
    for row in results:
        if counter != 3:
            choice_movies.append(row[0])
            counter += 1
        else:
            break
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
        if counter != 6:
            mov_gen = list(row[1].split("$"))
            for gen in mov_gen:
                if gen == genre:
                    cursor.execute(f"Select title from popular where movie_id = '{row[0]}'")
                    title = cursor.fetchall()
                    genre_movies.append(title[0][0])
                    genre_posters.append(fetchPoster(row[0], movies_result))
                    counter += 1
                    break
        else:
            break

    conn.close()  # Close the connection
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
        if counter != 6:
            if year == row[1]:
                cursor.execute(f"Select title from popular where movie_id = '{row[0]}'")
                title = cursor.fetchall()
                year_movies.append(title[0][0])
                year_posters.append(fetchPoster(row[0], movies_result))
                counter += 1
        else:
            break

    conn.close()  # Close the connection
    return year_movies, year_posters
