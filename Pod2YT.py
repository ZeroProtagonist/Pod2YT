import requests
import os
from xml.etree import ElementTree

RSS_URL = '' #Put your podcast rss.xml feed here.
response = requests.get(RSS_URL)
tree = ElementTree.fromstring(response.content)

# Get the URL of the latest podcast episode
latest_episode = tree.find('channel/item/enclosure').attrib['url']

# Download the episode
audio_response = requests.get(latest_episode)
filename = os.path.join(os.getcwd(), 'latest_episode.mp3')
with open(filename, 'wb') as audio_file:
    audio_file.write(audio_response.content)

print(f"Latest episode downloaded to {filename}")

from moviepy.editor import *

# Path to your static image
image_path = 'background.jpg'
audio_path = 'latest_episode.mp3'
output_video_path = 'output_video.mp4'

audio = AudioFileClip(audio_path)
video = ImageClip(image_path).set_duration(audio.duration)
final_clip = video.set_audio(audio)
final_clip.write_videofile(output_video_path, fps=24)

print(f"Video created at {output_video_path}")









