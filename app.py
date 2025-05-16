from utilityFunctions import *
from SqlQuery import *
from flask import Flask, redirect, render_template, request, jsonify, url_for, session
import operator
from annoy import AnnoyIndex
from flask_mail import Mail, Message
from random import randint
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app, support_credentials=True)

# Flask mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.secret_key = os.getenv("SECRET_KEY")
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# fetch movies data
conn = db_connection("movies")
cursor = conn.cursor()
cursor.execute(FETCH_ALL_MOVIES)
movies_result = cursor.fetchall()
conn.close()

# Home page
@app.route('/')
def index():
    return render_template("index.html")

# Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        signup_email = request.form["email"]
        signup_mobile = request.form["mobile"]
        signup_password = request.form["password"]

        conn = db_connection("users")
        cursor = conn.cursor()

        cursor.execute("SELECT email FROM users WHERE email = ?", (signup_email,))
        results = cursor.fetchall()

        if len(results) != 0:
            conn.close()
            return "This email is already registered. <br> Please sign-in."
        else:
            session["user"] = signup_email
            session["choices"] = 0
            # Store signup info in session to use later
            session["signup_password"] = signup_password
            session["signup_mobile"] = signup_mobile
            conn.close()
            return "choices"
    return render_template("signup.html")

# Signin page
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        signin_email = request.form["email"]
        password = request.form["password"]

        conn = db_connection("users")
        cursor = conn.cursor()

        cursor.execute("SELECT email, password FROM users WHERE email = ?", (signin_email,))
        results = cursor.fetchall()
        conn.close()

        if len(results) == 0:
            return "This email is not registered. <br> Please sign-up first."
        elif password != results[0][1]:
            return "Incorrect Password."
        else:
            session["user"] = signin_email
            session["choices"] = 1
            return "recommendations"
    return render_template("signin.html")

# Choices page
@app.route('/choices', methods=['GET', 'POST'])
def choices():
    if "user" in session:
        if "choices" in session and session["choices"] == 1:
            return redirect(url_for("recommendations"))
        else:
            genre_names = []
            cast_dict = {}
            for row in movies_result:
                mov_gen = list(row[5].split("$"))
                for gen in mov_gen:
                    if gen not in genre_names and gen != '':
                        genre_names.append(gen)

                mov_cast = list(row[7].split("$"))
                for cast in mov_cast:
                    if cast in cast_dict and cast != '':
                        cast_dict[cast] = cast_dict[cast] + 1
                    elif cast != '':
                        cast_dict[cast] = 1

            cast_dict = dict(sorted(cast_dict.items(), key=operator.itemgetter(1), reverse=True))
            cast_names = []
            counter = 0
            for key in cast_dict:
                if counter < 25:
                    cast_names.append(key)
                    counter += 1
                else:
                    break

            return render_template("choices.html", genre_names=genre_names, cast_names=cast_names)
    else:
        print("Session not found")
        return redirect(url_for("signup"))

movie_names = [row[2] for row in movies_result]

@app.route('/getByGenre', methods=['GET', 'POST'])
def getByGenre():
    genre = request.form["genre"]
    genre_movies, genre_posters = byGenre(genre, movies_result)
    response = jsonify({"genre_movies": genre_movies, "genre_posters": genre_posters})
    return response

@app.route('/getByYear', methods=['GET', 'POST'])
def getByYear():
    year = request.form["year"]
    year_movies, year_posters = byYear(year, movies_result)
    response = jsonify({"year_movies": year_movies, "year_posters": year_posters})
    return response

# Recommendations page
@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    if "user" not in session:
        print("Session not found")
        return redirect(url_for("signin"))

    conn = db_connection("users")
    cursor = conn.cursor()

    cursor.execute("SELECT selected_genres, selected_cast FROM users WHERE email = ?", (session["user"],))
    results = cursor.fetchall()

    selected_genres = []
    selected_cast = []

    if len(results) != 0:
        selected_genres = results[0][0].split("$") if results[0][0] else []
        selected_cast = results[0][1].split("$") if results[0][1] else []
    else:
        genreList = request.form.getlist('genre-checkbox')
        castList = request.form.getlist('cast-checkbox')

        selected_genres = [i.replace("-", " ") for i in genreList]
        selected_cast = [i.replace("-", " ") for i in castList]

        sg = "$".join(selected_genres)
        sc = "$".join(selected_cast)

        # Use signup info stored in session
        signup_email = session.get("user")
        signup_password = session.get("signup_password")
        signup_mobile = session.get("signup_mobile")

        cursor.execute(INSERT_USER, (signup_email, signup_password, signup_mobile, sg, sc))
        conn.commit()
        session["choices"] = 1

    conn.close()

    choice_movies = byChoice(selected_genres, selected_cast)
    choice_idx = []
    choice_posters = []
    for mov in choice_movies:
        movie_idx = None
        movie_id = None
        for row in movies_result:
            if row[2] == mov:
                movie_idx = row[0]
                movie_id = row[1]
                break
        if movie_idx is not None:
            choice_idx.append(movie_idx)
            choice_posters.append(fetchBackdrop(movie_id))

    genre_movies, genre_posters = byGenre("Action", movies_result)
    year_movies, year_posters = byYear("2016", movies_result)

    return render_template(
        "recommendations.html",
        movie_names=movie_names,
        genre_movies=genre_movies,
        year_movies=year_movies,
        genre_posters=genre_posters,
        year_posters=year_posters,
        choice_idx=choice_idx,
        movies_result=movies_result,
        choice_posters=choice_posters,
    )

# Movie page
@app.route('/movie/<movie_name>')
def movie(movie_name):
    if "user" not in session:
        print("Session not found")
        return redirect(url_for("signin"))

    def recommend(movie):
        import os
        from annoy import AnnoyIndex

        file_path = './model/data/vectors.ann'
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found.")
            return [], []

        movie_index = None
        for row in movies_result:
            if row[2] == movie:
                movie_index = row[0]
                break
        if movie_index is None:
            print(f"Movie {movie} not found.")
            return [], []

        u = AnnoyIndex(5000, 'angular')
        try:
            u.load(file_path)
        except OSError as e:
            print(f"Error loading AnnoyIndex file: {e}")
            return [], []

        movies_list = u.get_nns_by_item(movie_index, 7)[1:7]

        recommended_movies = []
        movie_posters = []
        for i in movies_list:
            rec_movie_id = movies_result[i][1]
            recommended_movies.append(movies_result[i][2])
            movie_posters.append(fetchPoster(rec_movie_id, movies_result))
        return recommended_movies, movie_posters

    selected_movie = movie_name
    movie_idx = None
    movie_id = None
    for row in movies_result:
        if row[2] == selected_movie:
            movie_idx = row[0]
            movie_id = row[1]
            break

    if movie_idx is None or movie_id is None:
        return "Movie not found", 404

    recommendations, posters = recommend(selected_movie)
    trailer_key = fetchTrailer(movie_id, movies_result)
    movie_poster = fetchPoster(movie_id, movies_result)

    mov_genre = []
    mov_cast = []
    for row in movies_result:
        mg = list(row[5].split("$"))
        mov_genre.append(mg)
        mc = list(row[7].split("$"))
        mov_cast.append(mc)

    return render_template(
        "movie.html",
        movie_names=movie_names,
        movies_result=movies_result,
        movie_idx=movie_idx,
        recommendations=recommendations,
        posters=posters,
        trailer_key=trailer_key,
        movie_poster=movie_poster,
        mov_genre=mov_genre,
        mov_cast=mov_cast,
    )

# Watch page
@app.route('/watch/<movie_name>')
def watch(movie_name):
    if "user" in session:
        return render_template("watch.html", movie_name=movie_name, movie_names=movie_names)
    else:
        print("Session not found")
        return redirect(url_for("signin"))

otp = ""

# Forgot page
@app.route('/forgot', methods=['POST', 'GET'])
def forgot():
    global otp

    if request.method == 'POST':
        signin_email = request.form["email"]

        conn = db_connection("users")
        cursor = conn.cursor()

        cursor.execute("SELECT email, password FROM users WHERE email = ?", (signin_email,))
        results = cursor.fetchall()
        conn.close()

        if len(results) == 0:
            return "This email is not registered. <br> Please sign-up first."
        else:
            otp = randint(10**5, 10**6 - 1)
            message = Message("Next Up | OTP for password reset", sender=app.config['MAIL_USERNAME'], recipients=[signin_email])
            message.body = "OTP: " + str(otp)
            mail.send(message)
            session["forgot_email"] = signin_email
            return "forgot"
    return render_template("forgotPass.html")

# Reset page
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    global otp
    if request.method == 'POST':
        num = request.form["otp"]
        if str(num) == str(otp):
            return "valid"
        else:
            return "OTP entered is incorrect"
    return render_template("reset.html")

# Change password in database
@app.route('/change', methods=['GET', 'POST'])
def change():
    if request.method == 'POST':
        newPass = request.form["newPass"]
