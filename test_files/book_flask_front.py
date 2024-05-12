from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
import urllib3

app = Flask(__name__)

# Disable SSL verification warnings
urllib3.disable_warnings()

@app.route('/', methods=['GET', 'POST'])
def search_goodreads():
    books = []
    if request.method == 'POST':
        book_name = request.form['book_name']
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
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Search Goodreads</title>
    </head>
    <body>
        <h1>Book Search on Goodreads</h1>
        <form action="/" method="post">
            <input type="text" name="book_name" placeholder="Enter book name" required>
            <button type="submit">Search</button>
        </form>
        {% if books %}
            <h2>Search Results</h2>
            <ul>
            {% for book in books %}
                <li><a href="{{ book.link }}">{{ book.title }}</a></li>
            {% endfor %}
            </ul>
        {% else %}
            {% if request.method == 'POST' %}
                <p>No results found.</p>
            {% endif %}
        {% endif %}
    </body>
    </html>
    '''
    return render_template_string(html, books=books)

if __name__ == "__main__":
    app.run(debug=True)
