from django.shortcuts import render
from django.http import HttpResponse
import requests


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
    print('reload')

    context = {
        'trending': trending,
        'hero': hero,
    }

    return render(request, 'index.html', context)
