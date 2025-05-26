from SqlQuery import *
import requests
import sqlite3

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
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=65669b357e1045d543ba072f7f533bce&language=en-US",
            timeout=5)
        if response.status_code == 200:
            data = response.json()
            return "https://image.tmdb.org/t/p/original" + str(data.get('backdrop_path', ''))
        else:
            return "https://via.placeholder.com/500x281?text=No+Backdrop"
    except Exception as e:
        print("Backdrop fetch failed:", e)
        return "https://via.placeholder.com/500x281?text=Error"

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
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute(FETCH_ALL_CHOICE)
        results = cursor.fetchall()

        # Update cast frequencies
        for row in results:
            cf = sum(1 for cast in row[4].split("$") if cast in castList)
            if cf != 0:
                cursor.execute("UPDATE choice SET castFre = ? WHERE movie_id = ?", (cf, row[1]))

        # Update genre frequencies
        for row in results:
            gf = sum(1 for gen in row[3].split("$") if gen in genreList)
            if gf != 0:
                cursor.execute("UPDATE choice SET genFre = ? WHERE movie_id = ?", (gf, row[1]))

        conn.commit()  # commit after all updates

        # Fetch sorted recommendations
        cursor.execute(SORT_BY_CAST)
        sorted_results = cursor.fetchall()
        choice_movies = [row[0] for row in sorted_results[:3]]

        return choice_movies

    except sqlite3.Error as e:
        print("Database error:", e)
        return []

    finally:
        conn.close()

# Get most popular movies in a genre
def byGenre(genre, movies_result):
    counter = 0
    genre_movies = []
    genre_posters = []

    conn = db_connection("popular")
    if not conn:
        return genre_movies, genre_posters

    try:
        cursor = conn.cursor()
        cursor.execute(FETCH_GENRES_POPULAR)
        results = cursor.fetchall()

        for row in results:
            if counter == 6:
                break
            if genre in row[1].split("$"):
                cursor.execute("SELECT title FROM popular WHERE movie_id = ?", (row[0],))
                title = cursor.fetchone()
                if title:
                    genre_movies.append(title[0])
                    genre_posters.append(fetchPoster(row[0], movies_result))
                    counter += 1

        return genre_movies, genre_posters

    except sqlite3.Error as e:
        print("Genre filter error:", e)
        return genre_movies, genre_posters

    finally:
        conn.close()

# Get most popular movies of a year
def byYear(year, movies_result):
    counter = 0
    year_movies = []
    year_posters = []

    conn = db_connection("popular")
    if not conn:
        return year_movies, year_posters

    try:
        cursor = conn.cursor()
        cursor.execute(FETCH_DATE_POPULAR)
        results = cursor.fetchall()

        for row in results:
            if counter == 6:
                break
            if year == row[1]:
                cursor.execute("SELECT title FROM popular WHERE movie_id = ?", (row[0],))
                title = cursor.fetchone()
                if title:
                    year_movies.append(title[0])
                    year_posters.append(fetchPoster(row[0], movies_result))
                    counter += 1

        return year_movies, year_posters

    except sqlite3.Error as e:
        print("Year filter error:", e)
        return year_movies, year_posters

    finally:
        conn.close()
