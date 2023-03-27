from datetime import datetime
import math
from django.shortcuts import render
from django.http import HttpResponse
import requests
from .utils.imageUtils import get_image_overlay


# Create your views here.
API_KEY = '0fd7a8764e6522629a3b7e78c452c348'


def index(request):
    trending_response = requests.get(
        f'https://api.themoviedb.org/3/trending/all/week?api_key={API_KEY}&page=1'
    )
    hero_response = requests.get(
        f'https://api.themoviedb.org/3/tv/76331?api_key={API_KEY}&language=en-US&append_to_response=seasons,episodes,watch/providers')

    trending = trending_response.json()['results']
    hero = hero_response.json()['backdrop_path']

    context = {
        'trending': trending,
        'hero': hero,
    }

    return render(request, 'index.html', context)


def movies(request):

    # Pull data from third party rest api
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page=1')

    # Convert response data into json
    movies = response.json()['results']

    context = {
        'movies': movies,
    }

    return render(request, 'movies/movies.html', context)


def movie(request, movie_id):

    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US&append_to_response=credits,videos,release_dates,watch/providers,similar')

    movie = response.json()

    # > Get URL of image
    image_url = movie['poster_path']

    # > Get backdrop filter gradient
    backdrop_filter = get_image_overlay(
        f'http://image.tmdb.org/t/p/w92{image_url}')

    # h_ Get movie details

    # < Array to store released similar movies
    released_similar_movies = []

    # < Remove unreleased movies from similar.
    for similar in movie['similar']['results']:
        if similar['release_date']:
            release_date = datetime.strptime(
                similar['release_date'], '%Y-%m-%d')
            if release_date < datetime.now():
                released_similar_movies.append(similar)

    # < Create variable to store MPAA rating
    rating = None

    # < Find the rating it he us release information
    us_release = next((r for r in response.json()[
        'release_dates']['results'] if r['iso_3166_1'] == 'US'), None)

    # < If there is a us rating, save it
    if us_release:

        rating = us_release['release_dates'][0]['certification']

    # < Get any streaming services the movie is available on
    if 'US' in movie['watch/providers']['results'] and \
            movie['watch/providers']['results']['US'].get('flatrate'):
        streaming_services = movie['watch/providers']['results']['US']['flatrate']
    else:
        streaming_services = None

    # < Get review score.
    review = round(float(movie['vote_average']), 1)

    # < Get movie budget and format in USD.
    if movie['budget']:
        budget = '$' + '{:,}'.format(movie['budget'])
    else:
        budget = None

    # < Get movie revenue and format in USD.
    if movie['revenue']:
        revenue = '$' + '{:,}'.format(movie['revenue'])
    else:
        revenue = None

    # < Get movie release date and format.
    if movie['release_date']:
        release_date = movie['release_date']
        release_date = release_date.replace('-', '/')
    else:
        release_date = None

    # < Get movie runtime in minutes and format for hours
    if movie['runtime']:
        runtime = movie['runtime']
        hours = math.floor(runtime / 60)
        minutes = runtime % 60
        runtime = str(hours) + 'hr ' + str(minutes) + 'm'
    else:
        runtime = None

    for person in movie['credits']['crew']:
        if person['job'] == 'Director':
            pass

    # * Create context for template.
    context = {
        'movie': movie,
        'backdrop_filter': backdrop_filter,
        'streaming_services': streaming_services,
        'review': review,
        'revenue': revenue,
        'budget': budget,
        'release_date': release_date,
        'runtime': runtime,
        'rating': rating,
        'similar': released_similar_movies,
    }
    return render(request, 'movies/movie.html', context)


def shows(request):
    # Pull data from third party rest api
    response = requests.get(
        f'https://api.themoviedb.org/3/trending/tv/week?api_key={API_KEY}'
    )

    # Convert response data into json
    shows = response.json()['results']

    context = {
        'shows': shows,
    }

    return render(request, 'tv/shows.html', context)


def show(request, show_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}?api_key={API_KEY}&language=en-US&append_to_response=seasons,episodes,watch/providers')

    show = response.json()

    # > Get any streaming services the movie is available on
    if 'US' in show['watch/providers']['results'] and \
            show['watch/providers']['results']['US'].get('flatrate'):
        streaming_services = show['watch/providers']['results']['US']['flatrate']
    else:
        streaming_services = None

    # > Get URL of image
    image_url = show['poster_path']
    image_url = f'http://image.tmdb.org/t/p/w500{image_url}'

    # > Get backdrop filter gradient
    backdrop_filter = get_image_overlay(
        f'http://image.tmdb.org/t/p/w92{image_url}')

    # * Create context for template.
    context = {
        'show': show,
        'backdrop_filter': backdrop_filter,
        'streaming_services': streaming_services,
    }
    return render(request, 'tv/show.html', context)
