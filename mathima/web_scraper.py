import requests 
from bs4 import BeautifulSoup
from urllib.parse import urljoin


#synarthsh gia katebasma keimenou apo url
def download_text_from_url(url):
    #katebase thn istoselida
    response = requests.get(url)
    #elegxos epityxias ths aithshs
    if response.status_code == 200:
         #analush tou html kwdika
         soup = BeautifulSoup(response.text, "html.parser")
         #euresh stoixeiwn pou periexoun keimeno
         text_elements = soup.find_all("p")
         #sygxwneush tou keimenou me ta stoixeia
         text = "\n".join(element.get_text() for element in text_elements)
         return text
    else:
         print("Failed to download page.")
         return None 
    

#synarthsh gia thn euresh links se mia istoselida
def get_links_from_url(url):
    #katebase thn istoselida
    response = requests.get(url)
    #elegxos epityxias ths aithshs
    if response.status_code == 200:
        #analush tou html kwdika
        soup = BeautifulSoup(response.text, "html.parser")
        #euresh stoixeiwn pou periexoun links
        links = soup.find_all("a", href=True)
        #sygxwneush twn links
        internal_links = [urljoin(response.url, link["href"]) for link in links if link["href"].startswith("/wiki/")]
        return internal_links
    else:
        print("Failed to download page.")
        return None

def save_text_to_file(text, filename):
#apothkeush tou keimenou se arxeio
    with open(filename , "w" , encoding="utf-8") as f:
        f.write(text)
        print(f"Text saved to {filename}")

if __name__ == "__main__":
    # orismos ths url istoselidas wikipedia gia thn glossa python
    url = "https://icsd.aegean.gr"
    #katebasma keimenou apo url
    text = download_text_from_url(url)
    if text:
        #apothkeush tou keimenou se arxeio
        save_text_to_file(text, "python_icsd_text.txt")
