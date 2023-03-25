from django.shortcuts import render
from django.http import HttpResponse
import requests


# Create your views here.
API_KEY = '0fd7a8764e6522629a3b7e78c452c348'


def index(request):
    response = requests.get(
        f'https://api.themoviedb.org/3/trending/all/week?api_key={API_KEY}&page=1'
    )

    trending = response.json()['results']
    print(trending)

    context = {
        'trending': trending,
    }

    return render(request, 'index.html', context)
