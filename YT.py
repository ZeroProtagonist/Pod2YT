import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import xml.etree.ElementTree as ET
import requests
from google.auth.transport.requests import Request

CLIENT_SECRET_FILE = 'client_secret.json' #save your client secret as this filename, or change the filename to the name of your .json file.
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube']

TOKEN_PICKLE_FILE = "token.pickle"
PLAYLIST_ID = "" #put the plalist ID of the playlist you'd like to upload your podcast to. 

def get_authenticated_service():
    creds = None
    # Check if there's a token.pickle file
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)

    # If there are no valid credentials available, prompt the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(TOKEN_PICKLE_FILE, 'wb') as token:
                pickle.dump(creds, token)

    return build(API_NAME, API_VERSION, credentials=creds)

def get_latest_episode_info_from_rss(rss_url):
    response = requests.get(rss_url)
    root = ET.fromstring(response.content)
    latest_item = root.find("channel/item")
    title = latest_item.findtext("title")
    description = latest_item.findtext("description")
    return title, description

def add_video_to_playlist(youtube, video_id):
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": PLAYLIST_ID,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    response = request.execute()
    print(f'Added video to playlist with ID {response["id"]}')

def upload_video():
    youtube = get_authenticated_service()

    video_title, video_description = get_latest_episode_info_from_rss("https://www.klcc.org/podcast/oregon-on-the-record/rss.xml")

    body = {
        'snippet': {
            'title': video_title,
            'description': video_description,
            'tags': ['podcast', 'your tag', 'another tag'],
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': 'public',
            'madeForKids': False
        }
    }
    request = youtube.videos().insert(
    part='snippet,status',
    body=body,
    media_body="output_video.mp4"
)

    response = request.execute()

    print(response)  # <-- This line will print the entire API response

    print(f'Video uploaded with ID {response["id"]}')

    # Add the video to the playlist
    add_video_to_playlist(youtube, response["id"])

if __name__ == "__main__":
    upload_video()



