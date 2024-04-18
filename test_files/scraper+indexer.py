import requests 
from bs4 import BeautifulSoup

def download_text_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract text from paragraphs
        paragraphs = soup.find_all("p")
        # Join the text from paragraphs into a single string
        text = "\n".join(paragraph.get_text() for paragraph in paragraphs)
        return text
    else:
        print("Failed to download page.")
        return None

def create_inverted_index(text):
    if text:
        inverted_index = {}
        # Split the text into words
        words = text.split()
        for word in words:
            inverted_index.setdefault(word, 0)
            inverted_index[word] += 1
        return inverted_index
    else:
        print("Text is empty. Cannot create inverted index.")
        return None

def search_inverted_index(inverted_index, word):
    if inverted_index and word in inverted_index:
        return inverted_index[word]
    else:
        return "Word not found in the inverted index"

if __name__ == "__main__":
    # Wikipedia page URL
    wikipedia_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    wikipedia_text = download_text_from_url(wikipedia_url)
    wikipedia_inverted_index = create_inverted_index(wikipedia_text)
    
    if wikipedia_inverted_index:
        print("Inverted Index for Wikipedia Page:")
        for word, count in wikipedia_inverted_index.items():
            print(f"{word}: {count}")
        
        search_word = "Python"
        search_result = search_inverted_index(wikipedia_inverted_index, search_word)
        print(f"Occurrences of the word '{search_word}': {search_result}")
    else:
        print("Error occurred. Inverted index not created.")
