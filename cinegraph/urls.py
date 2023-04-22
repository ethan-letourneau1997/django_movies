from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('movies/', views.movies, name='movies'),
    path('movies/<int:movie_id>/', views.movie, name='movie'),
    path('movies/<int:movie_id>/cast_and_crew',
         views.movie_credits, name='movie_credits'),
    path('tv/', views.shows, name='shows'),
    path('tv/<int:show_id>/', views.show, name='show'),
    path('tv/<int:show_id>/cast_and_crew',
         views.show_credits, name='show_credits'),
    path('tv/<int:show_id>/seasons/', views.seasons, name='seasons'),
    path('<int:show_id>/season/<int:season_number>/',
         views.season_detail, name='season_detail'),
    path('<int:show_id>/season/<int:season_number>/episode/<int:episode_number>',
         views.episode_detail, name='episode_detail'),
    path('people/', views.people, name='people'),
    path('people/<int:person_id>/', views.person, name='person'),
    path('search/', views.search, name='search'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
]
