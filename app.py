import pickle
import streamlit as st
import requests
import json

def fetch_poster(movie_id):
    # Handle errors in API requests
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=9e4101bba5150ab6a37eba241f58f24c&language=en-US"
        data = requests.get(url)
        data.raise_for_status()  # This will raise an exception for HTTP errors
        data = data.json()
        
        # Check if poster_path exists
        if 'poster_path' in data:
            poster_path = data['poster_path']
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            return full_path
        else:
            return "https://via.placeholder.com/500x750.png?text=No+Poster"  # Placeholder for no poster
    except requests.exceptions.RequestException as e:
        return "https://via.placeholder.com/500x750.png?text=Error+Fetching+Poster"  # Placeholder for error

def recommend(movie):
    try:
        # Get the index of the selected movie
        index = movies[movies['title'] == movie].index[0]
        
        # Get similarity scores for the movie
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        
        recommended_movie_names = []
        recommended_movie_posters = []
        
        # Loop through the top 5 recommended movies
        for i in distances[1:6]:  # Skip the first one as it's the same movie
            movie_index = i[0]  # Index of the recommended movie
            movie_id = movies.iloc[movie_index].movie_id  # Get the movie ID
            
            # Fetch poster for the movie
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movies.iloc[movie_index].title)
        
        return recommended_movie_names, recommended_movie_posters
    except IndexError:
        return [], []  # In case the movie is not found or any index error occurs

# Streamlit UI setup
st.header('Movie Recommendation System')

# Load the movies dataset and similarity matrix
movies = pickle.load(open('movie.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

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


def get_movie_dialogues(movie_name):
    try:
        with open('movie_dialogues.json', 'r') as f:
            dialogues = json.load(f)
        return dialogues.get(movie_name, ["No famous dialogues found for this movie."])
    except FileNotFoundError:
        return ["Dialogues database not found."]

# In your Streamlit app, after recommendation section:
if st.button('Show Famous Lines'):
    dialogues = get_movie_dialogues(selected_movie)
    st.subheader("Famous Lines")
    for dialogue in dialogues:
        st.write(f"• {dialogue}")