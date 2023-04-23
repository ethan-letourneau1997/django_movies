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


def get_department_list(credits):
    crew_credits = credits['crew']
    departments = [credit['department'] for credit in crew_credits]
    unique_departments = set(departments)

    sorted_departments = sorted(set(unique_departments))

    return sorted_departments


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
        f'https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}&language=en-US&page=1')

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
    trending_movies = requests.get(
        f'https://api.themoviedb.org/3/trending/movie/day?api_key={API_KEY}&language=en-US&page=1')

    popular_movies = requests.get(
        f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page=1')

    # > Trending Movies
    # Convert response data into json
    trending = trending_movies.json()['results']

    for movie in trending:
        if 'release_date' in movie:
            formatted_date = datetime.strptime(
                movie['release_date'], '%Y-%m-%d')
            movie['formatted_date'] = formatted_date

    # > Trending Movies
    # Convert response data into json
    popular = popular_movies.json()['results']

    for movie in popular:
        if 'release_date' in movie:
            formatted_date = datetime.strptime(
                movie['release_date'], '%Y-%m-%d')
            movie['formatted_date'] = formatted_date

    context = {
        'trending': trending,
        'popular': popular,
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


def movie_credits(request, movie_id):
    credits_response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}&language=en-US')

    movie_response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US')

    movie = movie_response.json()

    credits = credits_response.json()

    cast_count = len(credits['cast'])
    crew_count = len(credits['crew'])

    # > get all departments for a movie
    crew_credits = credits['crew']
    departments = [credit['department'] for credit in crew_credits]
    unique_departments = set(departments)

    unique_departments.add('Acting')

    context = {
        'form': SearchForm(),
        'credits': credits,
        'cast_count': cast_count,
        'crew_count': crew_count,
        'departments': unique_departments,
        'title': movie,
    }

    return render(request, 'cast_and_crew/cast_and_crew.html', context)


def show_credits(request, show_id):
    credit_response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}/aggregate_credits?api_key={API_KEY}&language=en-US')

    show_response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}?api_key={API_KEY}&language=en-US')

    show = show_response.json()

    credits = credit_response.json()

    cast_count = len(credits['cast'])
    crew_count = len(credits['crew'])

    context = {
        'form': SearchForm(),
        'credits': credits,
        'cast_count': cast_count,
        'crew_count': crew_count,
        'departments': get_department_list(credits),
        'title': show,
    }

    return render(request, 'cast_and_crew/cast_and_crew.html', context)


def shows(request):
    # Pull data from third party rest api
    trending_shows = requests.get(
        f'https://api.themoviedb.org/3/trending/tv/day?api_key={API_KEY}&language=en-US&page=1'
    )

    popular_shows = requests.get(
        f'https://api.themoviedb.org/3/tv/popular?api_key={API_KEY}&with_original_language=en')

    # Convert response data into json
    trending = trending_shows.json()['results']

    for show in trending:
        if 'first_air_date' in show:
            formatted_date = datetime.strptime(
                show['first_air_date'], '%Y-%m-%d')
            show['formatted_date'] = formatted_date

    popular = popular_shows.json()['results']

    for show in popular:
        if 'first_air_date' in show:
            formatted_date = datetime.strptime(
                show['first_air_date'], '%Y-%m-%d')
            show['formatted_date'] = formatted_date

    context = {
        'trending': trending,
        'popular': popular,
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
        f'https://api.themoviedb.org/3/tv/{show_id}?api_key={API_KEY}&language=en-US&append_to_response=credits')

    show = response.json()

    context = {
        'form': SearchForm(),
        'show': show,
    }

    return render(request, 'tv/seasons.html', context)


def season_detail(request, show_id, season_number):

    # Make API call to retrieve season details
    season_response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}/season/{season_number}?api_key={API_KEY}&language=en-US&append_to_response=credits')

    season = season_response.json()

    show_response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}?api_key={API_KEY}&language=en-US')

    show = show_response.json()

    credits = season['credits']

    cast_count = len(credits['cast'])
    crew_count = len(credits['crew'])

    prev_season = None
    next_season = None

    if season['season_number'] > 1:
        prev_season = season['season_number'] - 1

    if season['season_number'] < show['number_of_seasons']:
        next_season = season['season_number'] + 1

    for episode in season['episodes']:
        if 'air_date' in episode:
            formatted_date = datetime.strptime(episode['air_date'], '%Y-%m-%d')
            episode['formatted_date'] = formatted_date.strftime('%b. %d, %Y')
        if 'guest_stars' in episode:
            guest_star_count = len(episode['guest_stars'])
            episode['guest_star_count'] = guest_star_count

    context = {
        'form': SearchForm(),
        'season': season,
        'show': show,
        'cast_count': cast_count,
        'crew_count': crew_count,
        'departments': get_department_list(credits),
        'prev_season': prev_season,
        'next_season': next_season,
    }

    return render(request, 'tv/season_detail.html', context)


def episode_detail(request, show_id, season_number, episode_number):

    episode_response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}/season/{season_number}/episode/{episode_number}?api_key={API_KEY}&language=en-US&append_to_response=credits')

    episode = episode_response.json()

    # Make API call to retrieve season details
    season_response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}/season/{season_number}?api_key={API_KEY}&language=en-US&append_to_response=credits')

    season = season_response.json()

    credits = episode['credits']

    cast_count = len(credits['cast'])
    guest_count = len(credits['guest_stars'])
    crew_count = len(credits['crew'])

    episode_count = len(season['episodes'])

    prev_episode = False
    next_episode = False

    if episode['episode_number'] > 1:
        prev_episode = episode['episode_number'] - 1

    if episode['episode_number'] < episode_count:
        next_episode = episode['episode_number'] + 1

    if prev_episode:
        prev_episode_response = requests.get(
            f'https://api.themoviedb.org/3/tv/{show_id}/season/{season_number}/episode/{prev_episode}?api_key={API_KEY}&language=en-US&append_to_response=credits')

        prev_episode = prev_episode_response.json()

    if next_episode:
        next_episode_response = requests.get(
            f'https://api.themoviedb.org/3/tv/{show_id}/season/{season_number}/episode/{next_episode}?api_key={API_KEY}&language=en-US&append_to_response=credits')

        next_episode = next_episode_response.json()

    context = {
        'form': SearchForm(),
        'episode': episode,
        'departments': get_department_list(credits),
        'cast_count': cast_count,
        'crew_count': crew_count,
        'guest_count': guest_count,
        'season_number': season_number,
        'title': episode,
        'show_id': show_id,
        'prev_episode': prev_episode,
        'next_episode': next_episode,
    }

    return render(request, 'tv/episode_detail.html', context)


def episode_credits(request, show_id, season_number, episode_number):
    response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}/season/{season_number}/episode/{episode_number}/credits?api_key={API_KEY}&language=en-US')

    credits = response.json()

    context = {
        'form': SearchForm(),
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

    combined_credits = person['combined_credits']
    cast_credits = combined_credits['cast']
    crew_credits = combined_credits['crew']

    # Combine the cast and crew lists
    all_credits = cast_credits + crew_credits

    # Sort the combined list by release date or first air date
    sorted_credits = sorted(all_credits, key=lambda x: x.get(
        'release_date') or x.get('first_air_date') or '0000-00-00', reverse=True)

    known_for = []
    known_for_set = set()

    for credit in person['combined_credits']['cast']:
        credit_key = (credit['id'], 'media_type')
        if credit_key not in known_for_set:
            known_for.append(credit)
            known_for_set.add(credit_key)

    for credit in person['combined_credits']['crew']:
        credit_key = (credit['id'], 'media_type')
        if credit_key not in known_for_set:
            known_for.append(credit)
            known_for_set.add(credit_key)

    # sort the credits by popularity in descending order
    sorted_known_for = sorted(
        known_for, key=lambda x: x['vote_count'], reverse=True)

    # TODO check for lists shorter than 9
    known_for = [credit for credit in sorted_known_for[:10]]

    # > get all departments for a person
    crew_credits = person['combined_credits']['crew']
    departments = [credit['department'] for credit in crew_credits]
    unique_departments = set(departments)

    if cast_credits:
        unique_departments.add('Acting')

    context = {
        'person': person,
        'form': SearchForm(),
        'birthday': formatted_birthday,
        'deathday': formatted_deathday,
        'credits': sorted_credits,
        'known_for': known_for,
        'departments': unique_departments,
    }

    return render(request, 'people/person.html', context)
