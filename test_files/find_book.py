import requests
from bs4 import BeautifulSoup
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings()

def search_goodreads(book_name):
    # Replace spaces with plus signs for the URL
    formatted_book_name = '+'.join(book_name.split())

    # Construct the search URL for Goodreads
    search_url = f"https://www.goodreads.com/search?q={formatted_book_name}"

    # Define headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Connection': 'keep-alive'
    }

    # Send a GET request to the search URL on Goodreads, adding headers and disabling SSL verification
    response = requests.get(search_url, headers=headers, verify=False)

    # Check if request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all the book titles and their respective links
        book_results = soup.find_all('tr', itemtype='http://schema.org/Book')

        if book_results:
            for i, book in enumerate(book_results, 1):
                # Extract book title and link
                title = book.find('a', class_='bookTitle').get_text(strip=True)
                link = book.find('a', class_='bookTitle')['href']
                print(f"{i}. Title: {title}")
                print(f"   Link: {link}")

            # Prompt the user to select a book
            selection = input("Enter the number of the book you want to view on Goodreads: ")

            # Validate user input
            try:
                selection = int(selection)
                if 1 <= selection <= len(book_results):
                    selected_book = book_results[selection - 1]
                    goodreads_link = f"https://www.goodreads.com{selected_book.find('a', class_='bookTitle')['href']}"
                    print(f"Redirecting to Goodreads page for '{selected_book.find('a', class_='bookTitle').get_text(strip=True)}'...")
                    print(f"Goodreads Link: {goodreads_link}")
                else:
                    print("Invalid selection. Please enter a number within the range.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
        else:
            print("No results found for the given book name.")
    else:
        print("Failed to retrieve search results from Goodreads.")
        # Print out the HTML content of the response to diagnose the issue
        print(response.content)

if __name__ == "__main__":
    book_name = input("Enter the name of the book: ")
    search_goodreads(book_name)
