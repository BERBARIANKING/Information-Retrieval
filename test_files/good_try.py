from flask import Flask, request, render_template_string
from imdb import IMDb
import re

app = Flask(__name__)
ia = IMDb()

# Function to fetch movies from IMDb
def fetch_movies(title):
    search_results = ia.search_movie(title)
    movies = []
    for result in search_results:
        movie_id = result.movieID
        movie = ia.get_movie(movie_id)
        # Ensure we have a plot description before appending
        if 'plot' in movie:
            movies.append({'title': movie['title'], 'description': movie['plot'][0], 'id': movie_id})
    return movies

# Function to create an inverted index from the movie list
def create_inverted_index(movies):
    inverted_index = {}
    for movie in movies:
        # Combine title and description for indexing
        content = movie['title'] + ' ' + movie['description']
        words = re.findall(r'\w+', content.lower())
        for word in words:
            if word not in inverted_index:
                inverted_index[word] = []
            inverted_index[word].append(movie)
    return inverted_index

@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    query = ''
    if request.method == 'POST':
        query = request.form['query']
        movies = fetch_movies(query)
        inverted_index = create_inverted_index(movies)
        results = search_inverted_index(inverted_index, query)
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movie Search</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="mb-4">Movie Search</h1>
        <form method="post" class="mb-4">
            <div class="input-group mb-3">
                <input type="text" name="query" class="form-control" placeholder="Search movies..." required>
                <button type="submit" class="btn btn-primary">Search</button>
            </div>
        </form>
        {% if results %}
            <h2>Results for '{{ query }}':</h2>
            {% for movie in results %}
            <div class="card mb-3" style="width: 100%;">
                <div class="card-body">
                    <h5 class="card-title">{{ movie['title'] }}</h5>
                    <p class="card-text">{{ movie['description'] }}</p>
                </div>
            </div>
            {% endfor %}
        {% endif %}
    </div>
</body>
</html>
''', query=query, results=results)

# Function to search within the inverted index
def search_inverted_index(inverted_index, query):
    query = query.lower()
    results = []
    words = re.findall(r'\w+', query)
    for word in words:
        if word in inverted_index:
            results.extend(inverted_index[word])
    return list({v['id']: v for v in results}.values())  # Remove duplicates based on IMDb ID

if __name__ == '__main__':
    app.run(debug=True)
