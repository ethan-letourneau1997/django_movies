import requests


def get_episode_ratings(show_id, api_key):
    # Make an API call to retrieve the TV show details from TMDB
    response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}?api_key={api_key}&language=en-US&append_to_response=seasons,episodes,watch/providers')

    show_data = response.json()

    # Retrieve the number of seasons for the TV show
    num_seasons = show_data['number_of_seasons']

    # Loop through each season and retrieve the episode data
    all_episodes_data = []
    for season_num in range(1, num_seasons+1):
        response = requests.get(
            f'https://api.themoviedb.org/3/tv/{show_id}/season/{season_num}?api_key={api_key}')
        season_data = response.json()

        # Loop through each episode in the season and retrieve the episode data
        for episode in season_data['episodes']:
            episode_data = {
                'season_number': season_num,
                'episode_number': episode['episode_number'],
                'name': episode['name'],
                'air_date': episode['air_date'],
                'rating': episode['vote_average']
            }
            all_episodes_data.append(episode_data)

    return all_episodes_data
