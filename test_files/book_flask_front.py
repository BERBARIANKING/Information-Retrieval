from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
import urllib3

app = Flask(__name__)

# Disable SSL verification warnings
urllib3.disable_warnings()

@app.route('/', methods=['GET', 'POST'])
def home():
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

    return render_template('book.html', books=books)

if __name__ == "__main__":
    app.run(debug=True)
