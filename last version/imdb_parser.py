from bs4 import BeautifulSoup
import requests
from imdb import Cinemagoer


def top10LinkParser():
    url = "https://www.imdb.com/list/ls003992425/"
    headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        if link['href'].startswith('/title/') and link['href'][-3] == 't' or link['href'][-4] == 't':
            links.append(link['href'])
    links.pop(10)
    baseUrl = "https://www.imdb.com"
    
    for i in range(0,10):
        links[i] = baseUrl + links[i]
    return links

def top10NamesParser():
    url = "https://www.imdb.com/list/ls003992425/"
    headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')

    top10Movies = []
    for data in soup.find_all('h3'):
        top10Movies.append(data.text)

    top10Movies.pop(10)
    top10Movies.pop(10)
    return top10Movies


def getMovieStoryline(movieNames):
    ia = Cinemagoer()
    movieStorylines = []

    for m in movieNames:
        movies = ia.search_movie(m)
        if movies:
            movie = ia.get_movie(movies[0].movieID)
            storyline = movie.get('plot outline') or movie.get('storyline') or 'No storyline available.'
        else:
            storyline = 'No movie found.'
        movieStorylines.append(storyline)

    return movieStorylines

def getMovieStorylineForMovie(title):
    ia = Cinemagoer()

    movies = ia.search_movie(title)
    if movies:
        movie = ia.get_movie(movies[0].movieID)
        storyline = movie.get('plot outline') or movie.get('storyline') or 'No storyline available.'
        return storyline
    else:
        return 'No movie found.'


def top10MoviesDescriptionParser():
    top10Links = top10LinkParser()
    headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0"
    }
    responses = []
    descriptions = []
    for i,l in enumerate(top10Links[:10]):
        responses.append(requests.get(l, headers=headers))
        soup = BeautifulSoup(responses[i].text, 'html.parser')
        description_tag = soup.find('span', {'data-testid': 'plot-xl'})
        if description_tag:
            descriptions.append(description_tag.text.strip())
        else:
            descriptions.append("No description found.")
    return descriptions


