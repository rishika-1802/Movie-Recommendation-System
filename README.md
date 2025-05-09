# Movie-Recommendation-System
It is a personalized movie recommendation web app that suggests films based on user mood and preferences using an AI-powered matchmaking engine.

**Features**
1.User Sign Up and Sign In
2.Mood-based movie recommendations
3.Similarity search using Annoy index
4.Responsive and clean UI with custom branding
5.MySQL/SQLite database integration for user and movie data

**Tech Stack**
Frontend: HTML, CSS, JavaScript
Backend: Python, Flask
Database: SQLite (or MySQL)
Machine Learning: Annoy for similarity search
Libraries: Flask-CORS, Flask-Login, sqlite3, Annoy

**Getting Started**
**1. Clone the Repository**
git clone https://github.com/your-username/movie-recommendation-system.git
cd movie-recommendation-system

**2. Set Up Virtual Environment**
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

**3. Install Requirements**
pip install -r requirements.txt

**4. Initialize the Database**
If using SQLite:
sqlite3 moodflix.db < schema.sql
For MySQL, create the tables manually or run a migration script.

**5. Run the App**
python app.py
Open your browser and go to: http://127.0.0.1:5000

**Screenshots**
Index:![image](https://github.com/user-attachments/assets/9f8ea588-5795-4072-bf42-1dffc10c8965)
Signin:![image](https://github.com/user-attachments/assets/2e6e7cf1-a8a0-4ba9-be77-0b3fac610242)
Signup:![image](https://github.com/user-attachments/assets/0dc43bec-462f-4f2b-9de5-53a75a6d1b6c)
Reset Password:![image](https://github.com/user-attachments/assets/d1951551-3b2b-415e-baea-f06b3f61a301)
Forget password:![image](https://github.com/user-attachments/assets/06130310-ecf6-459c-aa88-108f3282e42b)

**Future Improvements**
1.Add support for user ratings and reviews
2.Integrate with external APIs (TMDB, IMDb)
3.Improve recommendation algorithm with deep learning
4.Add dark mode toggle
