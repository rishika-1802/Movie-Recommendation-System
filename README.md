# 🎬 Next Up - Movie Recommendation System 🍿

## 🌟 Overview  
**Next Up** is a movie recommendation system that offers **generalized** suggestions based on popularity, genre, and year, and also provides **personalized** recommendations using the user's selected genres and casts. Additionally, it recommends similar movies based on user-selected titles using **content-based filtering** and **Annoy (Approximate Nearest Neighbors)**.

🔗 GitHub Repository: [Movie-Recommendation-System](https://github.com/rishika-1802/Movie-Recommendation-System-.git)

---

## 🚀 Features  
- ✅ **User Authentication:** Sign-up, Sign-in, Forgot Password, OTP Verification  
- ✅ **User Validation:** Proper validations on every input page  
- ✅ **Database Integration:** User credentials and preferences are stored securely  
- ✅ **Responsive Design:** Seamless user experience across devices  
- ✅ **Recommendation Types:**
  - Based on preferred genres and casts  
  - Based on genre popularity  
  - Based on yearly popularity  
  - Based on similarity to selected movie  
- ✅ **Movie Details:** Shows movie info and trailer  
- ✅ **Watch Option:** Movie watching interface  
- ✅ **Like/Dislike System:** Collects preferences (for future enhancement)  
- ✅ **Client-side Sessions**  
- ✅ **Local Development Friendly (VS Code)**

---

## 🧭 Project Structure  

```
📁 Movie-Recommendation-System
├── model\data\
│   ├── choice.sqlite
│   ├── movies.sqlite
│   ├── popular.sqlite
│   └── users.sqlite
├── static\
│   ├── css\
│   │   └── style.css
│   ├── js\
│   │   └── script.js
│   └── images\
├── templates\
│   ├── choices.html
│   ├── forgotPass.html
│   ├── index.html
│   ├── movie.html
│   ├── recommendations.html
│   ├── reset.html
│   ├── signin.html
│   ├── signup.html
│   └── watch.html
├── annoySearch.py
├── app.py
├── db.py
├── movie-recommender-system.ipynb
├── pkl-to-db.ipynb
├── SqlQuery.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env
├── source_code.py
```

---
## Interfaces

### Landing Page
* Seamless landing page with `Sign-in` and `Sign-up` (Get Started) button.
![home page](https://github.com/user-attachments/assets/9f8ea588-5795-4072-bf42-1dffc10c8965)

### Sign-up Page
![sign-up page](https://github.com/user-attachments/assets/0dc43bec-462f-4f2b-9de5-53a75a6d1b6c)

### Sign-in Page
![5 - sign-in](https://github.com/user-attachments/assets/2e6e7cf1-a8a0-4ba9-be77-0b3fac610242)
### OTP Validation Page
![11 - otp validation](https://user-images.githubusercontent.com/55057608/170730305-cbccfd03-cf80-45aa-b893-734503d01a30.png)

### Reset password Page
![14 - reset](https://user-images.githubusercontent.com/55057608/170730899-809feb1c-eb6a-4a06-b6e8-c4ba3ea1085d.png)

### Restrictions and validations on the sign-up page, sign-in page, forgot password functionality, OTP validation page, and reset password page
* All fields not filled
* Email account already registered (sign-up), Email account not registered (sign-in)
* Incorrect password, OTP incorrect
* Email address not entered, OTP not entered, new password not entered

![6 - validations](https://user-images.githubusercontent.com/55057608/170794709-7b6623b8-6fe8-4248-ae0e-c02f49a42034.PNG)

### Choices Page
* Page for choosing preferred genres and casts used for recommending movies

![choices](https://user-images.githubusercontent.com/55057608/170731172-7ac6e050-93ab-433f-9d38-2466972cc5d6.png)

### Recommendations page
* This page shows recommended movies based on genres and casts chosen by the user.
* It also displays the most popular movies based on different genres and years.

![16 - recommendations](https://user-images.githubusercontent.com/55057608/170731099-138356e1-2113-4ae1-bebb-6740431432b1.png)

### Movie Page
* This page shows details and a trailer of the movie selected by the user.
* It also recommends similar movies to the user based on the selected movie.

![18 - movie](https://user-images.githubusercontent.com/55057608/170731745-71dcabad-78ca-489e-92cd-402900a14845.png)

### Watch Movie Page
* This page is to watch the movie selected.

![19 - watch](https://user-images.githubusercontent.com/55057608/170731856-2595f39a-4ea1-41e3-9160-d699d82bf578.png)


## 💻 Tech Stack  
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap, jQuery  
- **Backend**: Python (Flask)  
- **Databases**: SQLite3  
- **Machine Learning**: Jupyter Notebook, scikit-learn, Annoy  
- **IDE**: Visual Studio Code 💙  
- **Version Control**: Git & GitHub  

---

## 🧠 Recommendation Algorithm  
This is a **Content-Based Recommendation System**. It uses:
- Movie Title
- Genres
- Cast
- Director
- Keywords
- Overview

After vectorization, **Cosine Similarity** is computed using the **Annoy algorithm** for fast approximate nearest neighbor search.

📚 Learn more about Annoy: https://github.com/spotify/annoy

---

## 🛠️ Installation & Environment Setup (💻 Local via VS Code)

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/rishika-1802/Movie-Recommendation-System-.git
   cd Movie-Recommendation-System-
   ```

2. **Install Python Dependencies**  
   Make sure Python 3 is installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the App Locally**  
   Use the terminal inside VS Code:
   ```bash
   python app.py
   ```

4. **Access the Web App**  
   Open your browser and navigate to:  
   👉 http://127.0.0.1:5000

---

## 📈 Future Scope  
- 👍 **Like/Dislike-based Suggestions:** Train on preference data for improved recommendations  
- 🎞️ **Dynamic Movie Playback:** Customize the Watch Page for each movie  
- 🤝 **Hybrid System:** Combine collaborative filtering with the current content-based approach  

---

## 📄 Documentation    
- 📚 A complete project report for the system with a use case diagram, web flow, ER diagram, etc can be found here:[Documentation](Documentation.docx)  
