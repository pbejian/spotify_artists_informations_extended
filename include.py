#-------------------------------------------------------------------------------

import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import streamlit as st
from bs4 import BeautifulSoup

#-------------------------------------------------------------------------------

def get_authorization_headers():

    # Identifiants pour les API de Spotify
    client_id = st.secrets["CLIENT_ID"]
    client_secret = st.secrets["CLIENT_SECRET"]

    # Créez l'authentification client pour accéder à l'API Spotify
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token_url = 'https://accounts.spotify.com/api/token'

    # Obtenez un ACCESS_TOKEN
    token = oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)
    access_token = token['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    return headers


def artist_id_from_name(artist_name, headers):
    """
    Renvoie l'id d'un artiste à partir de son nom.
    """
    url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist"
    response = requests.get(url, headers=headers)
    artist_id = response.json()['artists']['items'][0]['id']
    return artist_id


def artist_name_from_id(artist_id, headers):
    """
    Renvoie le nom d'un artiste à partir de son identifiant.
    """
    # Interrogez l'API Spotify pour obtenir le nom de l'artiste
    artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
    artist_response = requests.get(artist_url, headers=headers)
    artist_data = artist_response.json()
    return artist_data["name"]


def artist_data_from_id(artist_id, headers):
    """
    Renvoie les infos d'un artiste à partir de son identifiant.
    Il s'agit d'un dictionnaire avec un "name" et un "id".
    """
    # Interrogez l'API Spotify pour obtenir le nom de l'artiste
    artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
    artist_response = requests.get(artist_url, headers=headers)
    artist_data = artist_response.json()
    return artist_data


def artist_styles_from_id(artist_id, headers):
    """
    Renvoie les infos d'un artiste à partir de son identifiant.
    """
    # Interrogez l'API Spotify pour obtenir le nom de l'artiste
    artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
    artist_response = requests.get(artist_url, headers=headers)
    artist_data = artist_response.json()
    return artist_data["genres"]


def artist_page_soup(artist_id, headers):
    base_url = "https://open.spotify.com/artist/"
    artist_url = f"{base_url}{artist_id}"
    response = requests.get(artist_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


def related_artists(artist_id, headers):
    """
    À partir d'un identifiant d'artiste, cette fonction renvoie une liste de
    dictionnaire, un dictionnaire pour chaque artistes proches du premier
    artiste. Chaque dictionnaire contient le nom (champs "name") et
    l'identifiant (champ "id") de l'artiste.
    """
    # Interrogez l'API Spotify pour obtenir les artistes connexes
    related_artists_url = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
    related_artists_response = requests.get(related_artists_url, headers=headers)
    related_artists_data = related_artists_response.json()
    related_artists_dicts = []
    # Ajouter les artistes connexes dans la liste related_artists_dicts
    for artist in related_artists_data["artists"]:
        artist_dict = {"name": artist["name"], "id": artist["id"]}
        related_artists_dicts.append(artist_dict)
    return related_artists_dicts


def myprint(mylist):
    for item in mylist:
        print(item)


def myprint_only_the_name(mylist):
    for item in mylist:
        print(item["name"])


def delete_double(mylist):
    result = []
    for x in mylist:
        if x not in result:
            result.append(x)
    return result


def deep_related_artists(artist_list, headers):
    final_list = []
    for artist in artist_list:
        final_list.append(artist)
        artist_list = related_artists(artist["id"], headers)
        final_list = final_list + artist_list
    return delete_double(final_list)


def espace(n):
    """
    Cette fonction ne renvoie rien mais affiche n lignes vides
    dans une application streamlit.
    """
    for _ in range(n):
        st.write("")
    return None


def this_is_playlist(artist_name, headers):

    headers = get_authorization_headers()
    artist_id = artist_id_from_name(artist_name, headers=headers)
    artist_name = artist_name_from_id(artist_id, headers=headers)
    soup = artist_page_soup(artist_id, headers)

    soup = str(soup)
    soup_tab = soup.split("Featuring " + artist_name)
    soup = soup_tab[1]
    soup_tab = soup.split("This Is " + artist_name)
    soup = soup_tab[0]

    soup_tab = soup.split("playlist/")
    playlist = soup_tab[1]
    playlist_tab =playlist.split("\"")
    playlist_ID = playlist_tab[0]
    # st.title(artist_name)

    html_title = "<h1 style='text-align:center;color:#1ED760'>« This is ... » playlist</h1>"
    # st.markdown(html_title, unsafe_allow_html=True)

    html_frame = f"<iframe style=\"border-radius:12px\" src=\"https://open.spotify.com/embed/playlist/{playlist_ID}?utm_source=generator\" \
    width=\"700px\" height=\"1000\" frameBorder=\"0\" allowfullscreen=\"\" allow=\"autoplay; clipboard-write; encrypted-media; fullscreen; \
    picture-in-picture\" loading=\"lazy\"></iframe>"

    return html_frame
