from flask import Flask, request, render_template_string, url_for, session
from imdb import IMDb
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed to keep session variables
ia = IMDb()

def fetch_movies(title, start, end):
    search_results = ia.search_movie(title)
    total_results = len(search_results)
    search_results = search_results[start:end]  # Ensure slicing is within bounds
    movies = []
    for result in search_results:
        movie_id = result.movieID
        movie = ia.get_movie(movie_id)
        if 'plot' in movie:
            plot = movie['plot'][0] if movie['plot'] else 'No description available.'
        else:
            plot = 'No description available.'
        poster_url = movie.get('cover url', 'https://via.placeholder.com/150')  # Default placeholder if no cover url
        movies.append({
            'title': movie['title'],
            'description': plot,
            'id': movie_id,
            'poster_url': poster_url  # Store the poster URL
        })
    return movies, total_results

@app.route('/', methods=['GET', 'POST'])
@app.route('/<int:page>', methods=['GET', 'POST'])
def home(page=1):
    per_page = 5
    results = []
    query = session.get('query', '')
    if request.method == 'POST':
        query = request.form['query']
        session['query'] = query  # Save query in session to reuse on pagination

    start = (page - 1) * per_page
    end = start + per_page
    movies, total_results = fetch_movies(query, start, end)
    if end > total_results:
        movies = []  # No more results to display

    inverted_index = create_inverted_index(movies)
    results = search_inverted_index(inverted_index, query)
    total_pages = (total_results // per_page) + (1 if total_results % per_page else 0)
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movie Search</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="mb-4">Movie Search</h1>
        <form method="post">
            <div class="input-group mb-3">
                <input type="text" name="query" class="form-control" placeholder="Search movies..." required value="{{ query }}">
                <button type="submit" class="btn btn-primary">Search</button>
            </div>
        </form>
        {% if results %}
            <h2>Results for '{{ query }}':</h2>
            {% for movie in results %}
            <div class="card mb-3">
                <div class="row g-0">
                    <div class="col-md-4">
                        <img src="{{ movie['poster_url'] }}" class="img-fluid rounded-start" alt="Poster for {{ movie['title'] }}">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">{{ movie['title'] }}</h5>
                            <p class="card-text">{{ movie['description'] }}</p>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
            <nav aria-label="Search results pages">
                <ul class="pagination">
                    {% if page > 1 %}
                    <li class="page-item"><a class="page-link" href="{{ url_for('home', page=page-1) }}">Previous</a></li>
                    {% endif %}
                    {% if page < total_pages %}
                    <li class="page-item"><a class="page-link" href="{{ url_for('home', page=page+1) }}">Next</a></li>
                    {% endif %}
                </ul>
            </nav>
        {% endif %}
    </div>
</body>
</html>
''', query=query, results=results, page=page, total_pages=total_pages)

def create_inverted_index(movies):
    inverted_index = {}
    for movie in movies:
        content = movie['title'] + ' ' + movie['description']
        words = re.findall(r'\w+', content.lower())
        for word in words:
            if word not in inverted_index:
                inverted_index[word] = []
            inverted_index[word].append(movie)
    return inverted_index

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
