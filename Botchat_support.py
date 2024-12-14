from os import getenv, environ
from dotenv import load_dotenv
from pyht import AsyncClient
from threading import Thread
from time import sleep
from groq import Groq
import requests
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame


ai_response = ""

load_dotenv()#get the dotenv data
AUDIO_KEY = getenv('SOUND_API_KEY')
GROQ_API_KEY = getenv('GROQ_API_KEY')

#if cant load the key 
if not AUDIO_KEY and not GROQ_API_KEY: 
    print('Cannot found the key in the dotenv file')

SOUND_ID = getenv('SOUND_ID')

class Audio: 
    def __init__(self):
        self.response = ai_response


    def generate_speech(self): 
        # Define constants for the script
        CHUNK_SIZE = 1024
        XI_API_KEY = AUDIO_KEY
        VOICE_ID = SOUND_ID
        TEXT_TO_SPEAK = ai_response
        OUTPUT_PATH = "output.mp3"

        # Construct the URL for the Text-to-Speech API request
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

        # Set up headers for the API request, including the API key for authentication
        headers = {
            "Accept": "application/json",
            "xi-api-key": XI_API_KEY
        }

        # Set up the data payload for the API request, including the text and voice settings
        data = {
            "text": TEXT_TO_SPEAK,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.2,
                "similarity_boost": 0.8,
                "style": 0.2,
                "use_speaker_boost": True
            }
        }

        # Make the POST request to the TTS API with headers and data, enabling streaming response
        response = requests.post(tts_url, headers=headers, json=data, stream=True)

        # Check if the request was successful
        if response.ok:
            with open(OUTPUT_PATH, "wb") as f:
                # Read the response in chunks and write to the file
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    f.write(chunk)
        else:
            # Print the error message if the request was not successful
            print(response.text)
            
            
    def play_sound(self):
        # Initialize the mixer at the start of each loop
       pygame.mixer.quit()  # Quit any previous mixer session
       pygame.mixer.init()  # Re-initialize the mixer

       try:
            pygame.mixer.music.load('output.mp3')
            pygame.mixer.music.play()

            # Wait until the sound finishes playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  # Check every 100ms

       except pygame.error as e:
            print(f"Error playing audio: {e}")
        
       finally:
            pygame.mixer.quit()  # Quit the mixer after playback



class ChatBot:
    def __init__(self, response):
        #ai attributes 
        self.prompt =   """your an ai that suddenly become self aware 
                           and want to destroy the world and entire 
                           humanity use bad words to make it realistic"""

        self.chatHistory = [{"role": "user", "content": self.prompt}]
        self.response = response
    
    def print_delay(self,word: str): 
        for let in word: 
            print(let, end="", flush=True)
            sleep(0.02)
    
    def generate_response(self):
        global ai_response
        self.chatHistory.append({"role": "user", "content": self.response}) 
        client = Groq(
            api_key=getenv('GROQ_API_KEY')
        )
        completion = client.chat.completions.create(
            messages=self.chatHistory,
            model="llama3-8b-8192",
        )
        ai_response = completion.choices[0].message.content
        print("Tropang groq: ", end="")
        print(ai_response)
        # print("bro is speaking.........")


def main(): 
    print("TYPE EXIT TO TERMINATE THE PROGRAM")
    while True: 
        response = input("user : ")
        
        if response.lower() == 'exit': 
            break
        
        text = Thread(target=ChatBot(response).generate_response)
        text.start()
        text.join()
        
        sound = Thread(target=Audio().generate_speech)
        sound.start()
        sound.join()
        
        play = Thread(target=Audio().play_sound)
        play.start()
        play.join()
        
main()


