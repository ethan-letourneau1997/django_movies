from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('search/', views.search, name='search'),
    path('movies/', views.movies, name='movies'),
    path('movies/<str:movie_id>', views.movie, name='movie'),
    # path('shows/', views.shows, name='shows'),
    # path('shows/<str:show_id>', views.show, name="show"),
    # path('shows/<str:show_id>/season/<str:season_number>/',
    #      views.season, name="season"),
    # path('shows/<str:show_id>/season/<str:season_number>/episodes/<str:episode_number>/',
    #      views.episode, name="episode"),
    # path('actors', views.actors, name="actors"),
    # path('actors/<str:actor_id>', views.actor, name="actor"),
]
