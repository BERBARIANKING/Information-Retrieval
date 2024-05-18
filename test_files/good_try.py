from flask import Flask, request, redirect, url_for, render_template_string, session, render_template
from imdb import IMDb
import re
import requests
from bs4 import BeautifulSoup
import urllib3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Modify with your actual secret key for production
ia = IMDb()
urllib3.disable_warnings()

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
            'poster_url': poster_url
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
    <title>Movie & Book Search</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="mb-4">Movie & Book Search</h1>
        <form method="post" action="{{ url_for('home') }}">
            <div class="input-group mb-3">
                <input type="text" name="query" class="form-control" placeholder="Search movies..." required value="{{ query }}">
                <button type="submit" class="btn btn-primary">Search Movies</button>
            </div>
        </form>
        <form method="post" action="{{ url_for('search_books') }}">
            <div class="input-group mb-3">
                <input type="text" name="book_name" class="form-control" placeholder="Search books..." required>
                <button type="submit" class="btn btn-secondary">Search Books</button>
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

@app.route('/search_books', methods=['POST'])
def search_books():
    book_name = request.form['book_name']
    return redirect(url_for('book_home', book_name=book_name))

@app.route('/book_home', methods=['GET', 'POST'])
def book_home():
    books = []
    book_name = request.args.get('book_name', '')  # Get from query string for GET method
    if request.method == 'POST':
        book_name = request.form['book_name']  # Post method override

    if book_name:
        books = fetch_books(book_name)

    return render_template('book.html', books=books)

def fetch_books(book_name):
    books = []
    formatted_book_name = '+'.join(book_name.split())
    search_url = f"https://www.goodreads.com/search?q={formatted_book_name}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }
    response = requests.get(search_url, headers=headers, verify=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        book_results = soup.find_all('tr', itemtype='http://schema.org/Book')
        for book in book_results:
            title = book.find('a', class_='bookTitle').get_text(strip=True)
            link = "https://www.goodreads.com" + book.find('a', class_='bookTitle')['href']
            books.append({'title': title, 'link': link})
    return books

if __name__ == '__main__':
    app.run(debug=True)
