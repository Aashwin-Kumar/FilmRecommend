import streamlit as st
import pickle as pkl
import requests

# Loading the pickle files for movies and similarity matrix
movie_list = pkl.load(open('movie_pikle.pkl', 'rb'))
similarity = pkl.load(open('similarity.pkl', 'rb'))

# Define constants for API usage
API_KEY = "e4806f2807cfbd3fce9193634e75531b"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500/"

# Function to fetch movie poster using TMDb API
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US/"
        )
        response.raise_for_status()  # Check for successful API response
        data = response.json()
        return POSTER_BASE_URL + data['poster_path']
    except (requests.exceptions.RequestException, KeyError) as e:
        st.write(f"Error fetching poster: {e}")
        return ""  # Return empty string if any error occurs

# Function to recommend top 5 similar movies based on the selected movie name
def recommend_movies(movie_name):
    movie_name = movie_name.lower()
    matching_movies = movie_list[movie_list['title'].str.contains(movie_name, na=False)]

    if matching_movies.empty:
        st.write("No matching movie name found. Please check your input or try a different keyword.")
        return []  # Return empty lists if no match is found

    movie_index = matching_movies.index[0] #by this ill fetch index for fetch similarity's index
    similar_movies = sorted(
        list(enumerate(similarity[movie_index])), # i sorted the distance from movie index, means most similar movies will come first
        reverse=True, key=lambda x: x[1]
    )[1:6]  # Exclude the first movie as it's the same as input

    recommended_titles, movie_posters = [], []
    for i in similar_movies:
        movie_id = movie_list.iloc[i[0]].movie_id
        recommended_titles.append(movie_list.iloc[i[0]].title)
        movie_posters.append(fetch_poster(movie_id))

    return recommended_titles, movie_posters

# Streamlit user interface
st.markdown("# :rainbow[Movie Recommendation System]")

# Dropdown menu to select movie titles
selected_movie = st.selectbox('Choose a Movie', movie_list['title'].values)

# Button to suggest similar movies based on selected title
if st.button('Suggest Movie'):
    titles, posters = recommend_movies(selected_movie)

    if titles:  # Only display if recommendations are available
        cols = st.columns(5)  # Create 5 columns for displaying movies
        for idx, col in enumerate(cols):
            if idx < len(titles):
                with col:
                    st.text(titles[idx])
                    st.image(posters[idx], use_column_width=True)
