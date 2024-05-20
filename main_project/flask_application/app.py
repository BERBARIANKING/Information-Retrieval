from flask import Flask, request, redirect, url_for, render_template_string, session, render_template
from imdb import IMDb
import re
import requests
from bs4 import BeautifulSoup
import urllib3
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Modify with your actual secret key for production
ia = IMDb()
urllib3.disable_warnings()

def summarize_text(input_text, sentences_count=3):
    """ Summarize the input text to a specified number of sentences. """
    parser = PlaintextParser.from_string(input_text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences_count=sentences_count)
    return " ".join(str(sentence) for sentence in summary)

def fetch_movies(title, start, end):
    """ Fetch movies from IMDb and summarize their plots, including genres and main characters. """
    search_results = ia.search_movie(title)
    total_results = len(search_results)
    search_results = search_results[start:end]  # Slice results for pagination
    movies = []
    for result in search_results:
        movie_id = result.movieID
        movie = ia.get_movie(movie_id)
        plot = movie.get('plot', ['No description available.'])[0].split('::')[0]
        summary = summarize_text(plot, 3)  # Summarize the plot
        genres = movie.get('genres', ['Unknown Genre'])
        cast = movie.get('cast', [])
        characters = [person.currentRole for person in cast[:5]]  # List the characters of the first 5 cast members
        character_names = [str(character) for character in characters]  # Convert characters to string
        poster_url = movie.get('cover url', 'https://via.placeholder.com/150')
        movies.append({
            'title': movie['title'],
            'description': plot,
            'summary': summary,
            'genres': genres,
            'characters': character_names,
            'id': movie_id,
            'poster_url': poster_url
        })
    return movies, total_results


@app.route('/', methods=['GET', 'POST'])
@app.route('/<int:page>', methods=['GET', 'POST'])
def home(page=1):
    per_page = 5
    results = []
    if request.method == 'POST':
        # When a new search is submitted, update the session.
        query = request.form['query']
        session['query'] = query
    else:
        # For GET requests, use the existing session data.
        query = session.get('query', '')

    if query:
        start = (page - 1) * per_page
        end = start + per_page
        movies, total_results = fetch_movies(query, start, end)
        if end > total_results:
            movies = []

        inverted_index = create_inverted_index(movies)
        results = search_inverted_index(inverted_index, query)
        total_pages = (total_results // per_page) + (1 if total_results % per_page else 0)
    else:
        total_pages = 0
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movie & Book Search</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="icon" type="image/x-icon" href="static/assets/favicon.ico" />
    <link href="{{ url_for('static', filename='assets/css/styles.css') }}" rel="stylesheet" />
    <style>
        body, html {
            height: 100%;
            margin: 0;
            overflow-x: hidden;
        }
        .bg-video {
            position: fixed; /* Make video background fixed */
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1; /* Place video behind the content */
        }
        .container {
            position: relative;
            z-index: 1; /* Ensure container is above background */
            padding-top: 100px; /* Adjust padding to avoid overlapping with the masthead */
        }
        .results-container {
            max-height: 600px;
            overflow-y: auto;
        }
        .masthead, .social-icons {
            z-index: 2; /* Higher z-index to ensure visibility and interaction */
        }
    </style>
</head>
<body>
    <!-- Background Video -->
    <video class="bg-video" playsinline="playsinline" autoplay="autoplay" muted="muted" loop="loop">
        <source src="static/assets/mp4/edu.mp4" type="video/mp4" />
    </video>

    <!-- Masthead -->
    <div class="masthead">
        <div class="masthead-content text-white">
            <div class="container-fluid px-4 px-lg-0">
                <a href="/">
                    <img src="{{ url_for('static', filename='searchblack.png') }}" alt="Home Logo" class="mb-4">
                </a>
            </div>
        </div>
    </div>
    
    <!-- Search Form and Results -->
    <div class="container mt-5">
       <!-------<h1 class="mb-4 text-center">Movie & Book Search!</h1>----->
        <form method="post" action="{{ url_for('home') }}" class="mb-4">
            <div class="input-group">
                <input type="text" name="query" class="form-control" placeholder="Search movies..." required value="{{ query }}">
                <button type="submit" class="btn btn-primary">Search</button>
            </div>
        </form>

        <!-- Scrollable Results Container -->
        <div class="results-container">
            {% if results %}
                <h2 class="text-center">Results for '{{ query }}':</h2>
                {% for movie in results %}
                <div class="card mb-3">
                    <div class="row g-0">
                        <div class="col-md-4">
                            <img src="{{ movie['poster_url'] }}" class="img-fluid rounded-start" alt="Poster for {{ movie['title'] }}">
                        </div>
                        <div class="col-md-8">
                            <div class="card-body">
                                <h5 class="card-title">{{ movie['title'] }}</h5>
                                <p class="card-text"><strong>Summary:</strong> {{ movie['summary'] }}</p>
                                <p class="card-text"><strong>Genres:</strong> {{ ', '.join(movie['genres']) }}</p>
                                <p class="card-text"><strong>Main Characters:</strong> {{ ', '.join(movie['characters']) }}</p>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% endif %}
        </div>

        <!-- Pagination -->
        {% if results %}
        <nav aria-label="Search results pages" class="mb-5">
            <ul class="pagination justify-content-center">
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

    <!-- Social Icons Footer -->
    <div class="social-icons">
        <div class="d-flex flex-row flex-lg-column justify-content-center align-items-center h-100 mt-3 mt-lg-0">
            <a class="btn btn-dark m-3" href="#!"><i class="fab fa-twitter"></i></a>
            <a class="btn btn-dark m-3" href="#!"><i class="fab fa-facebook-f"></i></a>
            <a class="btn btn-dark m-3" href="#!"><i the class="fab fa-instagram"></i></a>
        </div>
    </div>

    <!-- Bootstrap and Theme Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="static/assets/js/scripts.js"></script>
    <script src="https://cdn.startbootstrap.com/sb-forms-latest.js"></script>
</body>
</html>


''', query=query, results=results, page=page, total_pages=total_pages)

def create_inverted_index(movies):
    inverted_index = {}
    for movie in movies:
        content = movie['title'] + ' ' + movie['description']
        words = re.findall(r'\b\w+(?:-\w+)*\b', content.lower())
        for word in words:
            if word not in inverted_index:
                inverted_index[word] = []
            inverted_index[word].append(movie)
    return inverted_index

def search_inverted_index(inverted_index, query):
    query = query.lower()
    results = []
    words = re.findall(r'\b\w+(?:-\w+)*\b', query)
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
