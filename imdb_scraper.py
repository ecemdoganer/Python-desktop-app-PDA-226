import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
from imdb import Cinemagoer

# Gemini API
# API key
genai.configure(api_key="AIzaSyBsldWs2a7SGRZaYx5fFq9VmaN8yFVrpm4")
model = genai.GenerativeModel("gemini-1.5-flash")

# create prompt
storyline = "A donerman prepares kebab for dinner for a family gathering."
prompt = f"""
Storyline: {storyline}

Create a dialogue between this family of 4 people and the donerman. Make them argue at some point. Don't exceed 120 words.
"""

response = model.generate_content(prompt)

print("=== Dialogue Between The Donerman and The Family ===\n")
print(response.text)

def get_top_10_movies():
    url = "https://www.imdb.com/chart/top/"
    headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    movies = soup.select("ul.ipc-metadata-list li a.ipc-title-link-wrapper")[:10]

    top_movies = []
    for movie in movies:
        title = movie.get_text(strip=True)
        link = "https://www.imdb.com" + movie.get("href")
        top_movies.append((title, link))

    return top_movies

def get_movie_storyline(title):
    imdb = Cinemagoer()
    movies = imdb.search_movie(title)

    if movies:
        movie = imdb.get_movie(movies[0].movieID)
        return movie.get('plot outline', 'No storyline available.')
    else:
        return "Movie not found."

if __name__ == "__main__":
    top10 = get_top_10_movies()
    for i, (title, link) in enumerate(top10, 1):
        print(f"{i}. {title}")
        print(f"   {link}")

    title = input("Enter the movie title: ")
    storyline = get_movie_storyline(title)
    print("\n📜 Storyline:\n", storyline)