import pickle
import streamlit as st
import requests
import json
import ast
import itertools

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=9e4101bba5150ab6a37eba241f58f24c&language=en-US"
        data = requests.get(url)
        data.raise_for_status()
        data = data.json()
        if 'poster_path' in data:
            poster_path = data['poster_path']
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            return full_path
        else:
            return "https://via.placeholder.com/500x750.png?text=No+Poster"
    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750.png?text=Error+Fetching+Poster"

def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_movie_names = []
        recommended_movie_posters = []
        for i in distances[1:6]:
            movie_index = i[0]
            movie_id = movies.iloc[movie_index].movie_id
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movies.iloc[movie_index].title)
        return recommended_movie_names, recommended_movie_posters
    except IndexError:
        return [], []

def get_movie_dialogues(movie_name):
    try:
        with open('movie_dialogues.json', 'r') as f:
            dialogues = json.load(f)
        return dialogues.get(movie_name, ["No famous dialogues found for this movie."])
    except FileNotFoundError:
        return ["Dialogues database not found."]

def display_movies_by_genre(genres):
    filtered_movies = movies[movies['genres'].apply(lambda x: any(genre in x for genre in genres))]
    if filtered_movies.empty:
        st.error("No movies found for the selected genre(s).")
        return
    max_display = 20
    if len(filtered_movies) > max_display:
        st.info(f"Displaying top {max_display} movies out of {len(filtered_movies)} found.")
        filtered_movies = filtered_movies.head(max_display)
    posters = []
    titles = []
    for _, row in filtered_movies.iterrows():
        poster_url = fetch_poster(row['movie_id'])
        posters.append(poster_url)
        titles.append(row['title'])
    num_columns = 5
    rows = len(posters) // num_columns + 1
    for row_idx in range(rows):
        cols = st.columns(num_columns)
        for col_idx in range(num_columns):
            movie_idx = row_idx * num_columns + col_idx
            if movie_idx < len(posters):
                with cols[col_idx]:
                    st.image(posters[movie_idx], use_column_width=True)
                    st.caption(titles[movie_idx])

# Streamlit UI setup
st.header('Movie Recommendation System')

# Load the movies dataset and similarity matrix
movies = pickle.load(open('movie.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Extract unique genres
unique_genres = sorted(list(set(itertools.chain.from_iterable(movies['genres']))))

# List of movie titles for dropdown
movie_list = movies['title'].values

# Dropdown for movie selection
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

# Recommendation button
if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    if recommended_movie_names:
        # Display recommended movies
        col1, col2, col3, col4, col5 = st.columns(5)
        for idx, col in enumerate([col1, col2, col3, col4, col5]):
            if idx < len(recommended_movie_names):
                with col:
                    st.text(recommended_movie_names[idx])
                    st.image(recommended_movie_posters[idx])
    else:
        st.error("Sorry, we couldn't find any recommendations for that movie.")

# Famous Lines Section
if st.button('Show Famous Lines'):
    dialogues = get_movie_dialogues(selected_movie)
    st.subheader("Famous Lines")
    for dialogue in dialogues:
        st.write(f"• {dialogue}")

# Category Selection Section
st.subheader("Explore Movies by Category")

selected_genres = st.multiselect(
    "Select Genre(s):",
    unique_genres
)

if st.button('Show Movies by Category'):
    if selected_genres:
        display_movies_by_genre(selected_genres)
    else:
        st.warning("Please select at least one genre.")
