import imdb_parser
from imdb import Cinemagoer


def movieNamesCleaner():
    movieNames = imdb_parser.top10NamesParser()
    for i, movie in enumerate(movieNames[:10]):
        movieNames[i] = movie.replace(f'{i+1}.', '')
    return movieNames


def movieMapListParse():
    movieNames = movieNamesCleaner()
    movieLinks = imdb_parser.top10LinkParser()
    movieDescriptions = imdb_parser.top10MoviesDescriptionParser()
    #movieStorylines = imdb_parser.getMovieStoryline(movieNames)

    movieMapList = []

    for i in range(10):
        movieMapList.append({
            "title": movieNames[i],
            "url": movieLinks[i],
            "description": movieDescriptions[i],
            #"storyline": movieStorylines[i]
        })
    
    return movieMapList
