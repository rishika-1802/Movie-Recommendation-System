import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

df = pd.read_csv("/content/tmdb_5000_movies.csv", on_bad_lines='skip', low_memory=False)

print("Dataset preview:")
print(df.head())
print("\nMissing values per column:")
print(df.isnull().sum())

df.drop_duplicates(inplace=True)

df['homepage'] = df['homepage'].fillna('unknown')
df['overview'] = df['overview'].fillna('missing')
df['release_date'] = df['release_date'].fillna(df['release_date'].mode()[0])
df['runtime'] = df['runtime'].fillna(df['runtime'].median())
df['tagline'] = df['tagline'].fillna('missing')
df['vote_average'] = df['vote_average'].fillna(df['vote_average'].median())
df['vote_count'] = df['vote_count'].fillna(df['vote_count'].median())
df['budget'] = df['budget'].fillna(df['budget'].median())
df['revenue'] = df['revenue'].fillna(df['revenue'].median())
df['popularity'] = df['popularity'].fillna(df['popularity'].median())

def parse_json_column(col):
    try:
        if isinstance(col, str):
            return [item['name'] for item in json.loads(col)]
        else:
            return []
    except (json.JSONDecodeError, TypeError, KeyError):
        return []

df['genres'] = df['genres'].apply(parse_json_column)
df['keywords'] = df['keywords'].apply(parse_json_column)
df['production_companies'] = df['production_companies'].apply(parse_json_column)
df['production_countries'] = df['production_countries'].apply(parse_json_column)
df['spoken_languages'] = df['spoken_languages'].apply(parse_json_column)

df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce')
df['liked'] = (df['vote_average'] > df['vote_average'].median()).astype(int)

all_genres = sum(df['genres'], [])
all_genres = [genre for genre in all_genres if isinstance(genre, str)]

if all_genres:
    top_genres = pd.Series(all_genres).value_counts().head(5).index
    for genre in top_genres:
        df[f'genre_{genre}'] = df['genres'].apply(lambda x: 1 if genre in x else 0)
else:
    top_genres = pd.Index([])
    print("Warning: No valid genres found or parsed.")

features = ['budget', 'popularity', 'revenue', 'runtime', 'vote_count']
if not top_genres.empty:
    features.extend([f'genre_{g}' for g in top_genres])

if 'vote_average' in df.columns:
    features.append('vote_average')

features = [f for f in features if f in df.columns]

X = df[features]
y = df['liked']

X = X.fillna(X.median())

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

param_grid = {
    'C': [0.1, 1, 10],
    'kernel': ['rbf', 'linear'],
    'gamma': ['scale', 'auto']
}

if len(X_train) >= 5:
    model = GridSearchCV(SVC(random_state=42), param_grid, cv=5, scoring='f1', n_jobs=-1)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Precision:", precision_score(y_test, y_pred))
    print("Recall:", recall_score(y_test, y_pred))
    print("F1 Score:", f1_score(y_test, y_pred))

    plt.figure(figsize=(6, 4))
    sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt="d", cmap="Blues")
    plt.title("Confusion Matrix for SVM Classification")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.show()

    if model.best_params_['kernel'] == 'linear':
        try:
            feature_names_out = features
            if len(model.best_estimator_.coef_[0]) == len(feature_names_out):
                feature_importance = pd.Series(abs(model.best_estimator_.coef_[0]), index=feature_names_out)
                plt.figure(figsize=(8, 6))
                feature_importance.sort_values().plot(kind='barh', color='skyblue')
                plt.title("Feature Importance (SVM Linear Kernel)")
                plt.xlabel("Absolute Coefficient Value")
                plt.tight_layout()
                plt.show()
            else:
                print("\nSkipping Feature Importance plot: Number of features doesn't match coefficients.")
        except Exception as e:
            print(f"\nSkipping Feature Importance plot due to error: {e}")

    plt.figure(figsize=(6, 4))
    sns.histplot(df['popularity'], bins=30, kde=True, color='teal')
    plt.title("Distribution of Movie Popularity")
    plt.xlabel("Popularity")
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(8, 6))
    numeric_cols_for_corr = df[features].select_dtypes(include=np.number).columns
    if not numeric_cols_for_corr.empty:
        sns.heatmap(df[numeric_cols_for_corr].corr(), annot=True, fmt=".2f", cmap='coolwarm')
        plt.title("Correlation Heatmap of Numeric Features")
        plt.tight_layout()
        plt.show()
    else:
        print("\nSkipping Correlation Heatmap: No numeric features found for selected features.")
else:
    print("\nNot enough data to perform GridSearchCV. Skipping model training and evaluation.")
