from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('movies/', views.movies, name='movies'),
    path('movies/<int:movie_id>/', views.movie, name='movie'),
    path('shows/', views.shows, name='shows'),
    path('shows/<int:show_id>/', views.show, name="show"),
    path('people/', views.people, name='people'),
    path('people/<int:person_id>/', views.person, name='person'),
    path('search/', views.search, name='search'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
]
