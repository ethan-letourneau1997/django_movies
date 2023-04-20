from datetime import datetime
import math
from django import forms
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
import requests
from .utils.imageUtils import get_image_overlay
from .utils.getEpisodeRatings import get_episode_ratings
import json
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from django.utils.safestring import mark_safe

# > FORMS


class SearchForm(forms.Form):
    search = forms.CharField(label=mark_safe('<i class="fa fa-search"></i>'), label_suffix='', widget=forms.TextInput(
        attrs={'placeholder': 'Search...', 'class': 'form-control nav-search-input', 'id': 'search-input', 'autocomplete': 'off'}))


# Create your views here.
API_KEY = '0fd7a8764e6522629a3b7e78c452c348'


def autocomplete(request):
    query = request.GET.get('query')
    url = f'https://api.themoviedb.org/3/search/multi?api_key={API_KEY}&query={query}'
    response = requests.get(url)
    results = response.json()['results']
    suggestions = []
    for result in results:
        if result['media_type'] == 'movie':
            suggestions.append(
                {'id': result['id'], 'title': result['title'], 'media_type': result['media_type']})
        elif result['media_type'] == 'tv':
            suggestions.append(
                {'id': result['id'], 'title': result['name'], 'media_type': result['media_type']})
        elif result['media_type'] == 'person':
            suggestions.append(
                {'id': result['id'], 'name': result['name'], 'media_type': result['media_type']})
    return JsonResponse({'suggestions': suggestions})


def search_template(request):
    context = {
        'form': SearchForm()
    }
    return render(request, 'search_form.html', {'search_form': context})


def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            # print('Query:', search)
            # response = HttpResponse(search)

            response = requests.get(
                f'https://api.themoviedb.org/3/search/multi?api_key={API_KEY}&language=en-US&query={search}&page=1&include_adult=false')

            results = response.json()['results']

            context = {
                'results': results,
                'form': SearchForm(),
            }
            return render(request, 'search.html', context)

        else:
            response = HttpResponse('Form is not valid')
            return response
    else:
        response = HttpResponse('no_luck')
        return response


def index(request):
    movies_response = requests.get(
        f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page=1')

    tv_response = requests.get(
        f'https://api.themoviedb.org/3/trending/tv/week?api_key={API_KEY}'
    )

    person_response = requests.get(
        f'https://api.themoviedb.org/3/trending/person/week?api_key={API_KEY}'
    )

    movies = movies_response.json()['results']
    shows = tv_response.json()['results']
    people = person_response.json()['results']

    for item in movies:
        if 'release_date' in item:
            formatted_date = datetime.strptime(
                item['release_date'], '%Y-%m-%d')
            item['formatted_date'] = formatted_date

    for item in shows:
        if 'first_air_date' in item:
            formatted_date = datetime.strptime(
                item['first_air_date'], '%Y-%m-%d')
            item['formatted_date'] = formatted_date

    context = {
        'movies': movies,
        'shows': shows,
        'people': people,
        'form': SearchForm
    }

    return render(request, 'index.html', context)


def movies(request):

    # Pull data from third party rest api
    trending = requests.get(
        f'https://api.themoviedb.org/3/trending/movie/day?api_key={API_KEY}&language=en-US&page=1')

    popular = requests.get(
        f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page=1')

    # > Trending Movies
    # Convert response data into json
    trending_movies = trending.json()['results']

    for movie in trending_movies:
        if 'release_date' in movie:
            formatted_date = datetime.strptime(
                movie['release_date'], '%Y-%m-%d')
            movie['formatted_date'] = formatted_date

    # > Trending Movies
    # Convert response data into json
    popular_movies = popular.json()['results']

    for movie in popular_movies:
        if 'release_date' in movie:
            formatted_date = datetime.strptime(
                movie['release_date'], '%Y-%m-%d')
            movie['formatted_date'] = formatted_date

    context = {
        'trending_movies': trending_movies,
        'popular_movies': popular_movies,
        'form': SearchForm()
    }

    return render(request, 'movies/movies.html', context)


def movie(request, movie_id):

    # TODO clean up movie view (see show)

    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US&append_to_response=credits,videos,release_dates,watch/providers,similar,recommendations,images&include_image_language=en,null')

    movie = response.json()

    # < set default backdrop filter
    backdrop_filter = 'rgba(0,0,0,0)'

    if movie['poster_path']:
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
        revenue = 'unknown'

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

    # > Get movie trailers
    trailers = []
    for item in movie['videos']['results']:
        if item['type'] == 'Trailer':
            trailers.append(item['key'])
    trailer = None
    if len(trailers) > 0:
        trailer = trailers[0]

    # > Batch posters
    posters = []
    for poster in movie['images']['posters']:
        posters.append(poster)

    poster_batches = [posters[i:i+3] for i in range(0, len(posters), 3)]

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
        'trailer': trailer,
        'poster_batches': poster_batches,
        'form': SearchForm()
    }
    return render(request, 'movies/movie.html', context)


def shows(request):
    # Pull data from third party rest api
    response = requests.get(
        f'https://api.themoviedb.org/3/trending/tv/day?api_key={API_KEY}'
    )

    # Convert response data into json
    shows = response.json()['results']

    for show in shows:
        if 'first_air_date' in show:
            formatted_date = datetime.strptime(
                show['first_air_date'], '%Y-%m-%d')
            show['formatted_date'] = formatted_date

    context = {
        'shows': shows,
        'form': SearchForm()
    }

    return render(request, 'tv/shows.html', context)


def show(request, show_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}?api_key={API_KEY}&language=en-US&append_to_response=seasons,episodes,watch/providers,videos,credits,aggregate_credits,recommendations,images&include_image_language=en,null')

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

    # > Get show trailers
    trailers = []
    for item in show['videos']['results']:
        if item['type'] == 'Trailer':
            trailers.append(item['key'])
    trailer = None
    if len(trailers) > 0:
        trailer = trailers[0]

    # > Batch posters
    posters = []
    for poster in show['images']['posters']:
        posters.append(poster)

    poster_batches = [posters[i:i+3] for i in range(0, len(posters), 3)]

    context = {
        'show': show,
        'backdrop_filter': backdrop_filter,
        'streaming_services': streaming_services,
        'trailer': trailer,
        'poster_batches': poster_batches,
        'form': SearchForm(),


    }
    return render(request, 'tv/show.html', context)


def seasons(request, show_id):

    response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}?api_key={API_KEY}&language=en-US')

    show = response.json()

    context = {
        'show': show,
    }

    return render(request, 'tv/seasons.html', context)


def season_detail(request, show_id, season_number):

    # Make API call to retrieve season details
    response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}/season/{season_number}?api_key={API_KEY}&language=en-US')
    season = response.json()

    show_response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}?api_key={API_KEY}&language=en-US')

    show = show_response.json()

    name = show['name']

    context = {
        'season': season,
        'name': name,
        'show': show,
    }

    return render(request, 'tv/season_detail.html', context)


def episode_detail(request, show_id, season_number, episode_number):

    response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}/season/{season_number}/episode/{episode_number}?api_key={API_KEY}&language=en-US&append_to_response=credits')

    episode = response.json()

    my_json = json.dumps(episode['credits'], indent=4)

    print(my_json)

    context = {
        'episode': episode,
    }

    return render(request, 'tv/episode_detail.html', context)


def episode_credits(request, show_id, season_number, episode_number):
    response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}/season/{season_number}/episode/{episode_number}/credits?api_key={API_KEY}&language=en-US')

    credits = response.json()

    context = {
        'credits': credits,
    }

    return render(request, 'cast_and_crew.html', context)


def people(request):

    # Pull data from third party rest api
    response = requests.get(
        f'https://api.themoviedb.org/3/trending/person/week?api_key={API_KEY}&language=en-US&page=1&append_to_response=movie_credits')

    # Convert response data into json
    people = response.json()['results']

    for person in people:
        titles = []
        for item in person['known_for']:
            if 'title' in item:
                titles.append(item['title'])
            elif 'name' in item:
                titles.append(item['name'])
            else:
                titles.append("Unknown title")
        titles_str = ", ".join(titles)
        titles = titles_str
        person['title_str'] = titles_str

    context = {
        'people': people,
        'form': SearchForm()
    }

    return render(request, 'people/people.html', context)


def person(request, person_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/person/{person_id}?api_key={API_KEY}&language=en-US&append_to_response=combined_credits,tv_credits,movie_credits')

    person = response.json()

    formatted_birthday = None
    if 'birthday' in person == True:
        formatted_birthday = datetime.strptime(
            person['birthday'], '%Y-%m-%d')

    formatted_deathday = None
    if 'deathday' in person and person['deathday']:
        formatted_deathday = datetime.strptime(
            person['deathday'], '%Y-%m-%d')

    # for credit in person['combined_credits']['cast']:
    #     if credit['media_type'] == 'movie':
    #         print(credit['title'])
    #     if credit['media_type'] == 'tv':
    #         print(credit['name'])

    # Sort the credits by date
    sorted_credits = sorted(person['combined_credits']['cast'], key=lambda x: x.get(
        'release_date') or x.get('first_air_date') or '0000-00-00', reverse=True)

    # for credit in sorted_credits:
    #     if credit['media_type'] == 'movie':
    #         print(credit['title'])
    #         print(credit['release_date'])
    #     if credit['media_type'] == 'tv':
    #         print(credit['name'])

    known_for = []

    for credit in person['combined_credits']['cast']:
        if credit['media_type'] == 'movie':
            known_for.append(credit)
        elif credit['media_type'] == 'tv':
            known_for.append(credit)

    # sort the credits by popularity in descending order
    sorted_known_for = sorted(
        known_for, key=lambda x: x['vote_count'], reverse=True)

    # TODO check for lists shorter than 6
    known_for = [credit for credit in sorted_known_for[:10]]

    context = {
        'person': person,
        'form': SearchForm(),
        'birthday': formatted_birthday,
        'deathday': formatted_deathday,
        'credits': sorted_credits,
        'known_for': known_for,
    }

    return render(request, 'people/person.html', context)
