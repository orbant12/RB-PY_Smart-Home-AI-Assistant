import os
import time
import openai
import speech_recognition as sr
import pyttsx3
from playsound import playsound  # Ensure you install this package: pip install playsound
from dotenv import load_dotenv
import requests
import datetime
import pytz
import threading
import pygame

# Load environment variables (make sure you have a .env file with OPENAI_API_KEY defined)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")

#Global vars
current_lang = ""
voice_mode = 14
name = "Assistant"
isListen = False

conversation_history = [
    {"role": "system", "content": "You are a helpful assistant."}
]

# Instantiate the OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def play_sound(sound_file):
    """
    Play a sound effect using the specified sound file.
    """
    try:
        playsound(sound_file)
    except Exception as e:
        print("DEBUG: Error playing sound:", e)

def listen_for_trigger(trigger_phrase="hey english"):
    """
    Listen briefly for the trigger phrase.
    Returns True if the trigger phrase is detected.
    """
    global current_lang
    global voice_mode
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"DEBUG: Listening for trigger phrase '{trigger_phrase}'...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print("DEBUG: Trigger candidate detected:", text)

        trigger_phrase_hun = "hey hungary"

        if trigger_phrase_hun.lower() in text.lower():
            print("DEBUG: Trigger phrase detected!")
            current_lang = "hu"
            play_sound("sounds/trigger_beep.wav")  # Play sound effect when trigger is detected
            user_input = "Szia ma egy segito asszisztens leszel. Neved: Nora. Kezdj ugy hogy azt mondod: Hello Nora vagyok miben segithetek !"
            chat_reply = get_chatgpt_response(user_input, [])
                
            # Read ChatGPT's reply using text-to-speech
            speak_text(chat_reply)

            time.sleep(0.2)
            return True

        if trigger_phrase.lower() in text.lower():
            print("DEBUG: Trigger phrase detected!")
            current_lang = "en"

            # Voice mode
            if "bad news" in text.lower():
                voice_mode = 6
                name = "Bad News"
            elif "good news" in text.lower():
                voice_mode = 39
                name = "Good News"
            elif "whisper" in text.lower():
                voice_mode = 136
                name = "Whisper"
            elif "goblin" in text.lower():
                voice_mode = 7
                name = "Goblin"
            elif "superstar" in text.lower():
                voice_mode = 86
                name = "The Super Star"
            elif "fred" in text.lower():
                voice_mode = 38
                name = "Fred"
            elif "weird" in text.lower():
                voice_mode = 7
                name = "Fred"
            else:
                voice_mode = 14
                name = "Antal"

            play_sound("sounds/trigger_beep.wav")  # Play sound effect when trigger is detected

            user_input = f'Hey today you are going to be a home assistant. Your name : {name}. When they refer to you this is your name. After this prompt start the conversation by saying : Hello Im {name} how can i help you today Sir ! '
            chat_reply = get_chatgpt_response(user_input, conversation_history)

            user_text = {"role": "user", "content": user_input}
            conversation_history.append(user_text)
                
            # Read ChatGPT's reply using text-to-speech
            speak_text(chat_reply)

            time.sleep(0.2)
            return True
    except sr.UnknownValueError:
        print("DEBUG: Could not understand audio while listening for trigger.")
    except sr.RequestError as e:
        print("DEBUG: Could not request results; {0}".format(e))
    return False

def listen_for_audio():
    """
    Listen to the microphone until a pause is detected and save audio to a WAV file.
    """
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300  # Minimum audio energy to trigger recording
    recognizer.pause_threshold = 0.8     # Seconds of silence to consider the phrase complete

    print("DEBUG: Energy threshold set to:", recognizer.energy_threshold)
    print("DEBUG: Pause threshold set to:", recognizer.pause_threshold)

    with sr.Microphone() as source:
        print("Listening... (speak now)")
        start_time = time.time()
        audio_data = recognizer.listen(source)
        duration = time.time() - start_time
        print(f"DEBUG: Audio captured. Duration: {duration:.2f} seconds")
    
    # Save the audio to a file for transcription
    audio_file_path = "input_audio.wav"
    audio_wav = audio_data.get_wav_data()
    with open(audio_file_path, "wb") as f:
        f.write(audio_wav)
        print("DEBUG: Audio file saved as '{}' (Size: {} bytes)".format(audio_file_path, len(audio_wav)))
    
    return audio_file_path

def transcribe_audio(file_path):
    """
    Use OpenAI Whisper model to transcribe the audio file.
    """
    with open(file_path, "rb") as audio_file:
        print("DEBUG: Opened audio file for transcription.")
        start_time = time.time()
        print("DEBUG: Calling transcription endpoint using client.audio.transcriptions.create")
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=current_lang
        )
        elapsed_time = time.time() - start_time
        print(f"DEBUG: Transcription API call took {elapsed_time:.2f} seconds")
    text = transcript.text  # Access text attribute directly
    print("Transcription:", text)
    return text

def get_chatgpt_response(user_text, conversation_history):
    """
    Send the conversation history (including the new user text) to ChatGPT and retrieve the response.
    """
    # Append the latest user input to the conversation history
    conversation_history.append({"role": "user", "content": user_text})
    
    print("DEBUG: Sending the following conversation history to ChatGPT:")
    for msg in conversation_history:
        print(f"{msg['role']}: {msg['content']}")
    
    start_time = time.time()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation_history
    )
    elapsed_time = time.time() - start_time
    print(f"DEBUG: ChatGPT API call took {elapsed_time:.2f} seconds")
    
    # Access the reply using attribute access
    reply = response.choices[0].message.content
    print("ChatGPT response:", reply)
    
    # Append the assistant's reply to the conversation history
    conversation_history.append({"role": "assistant", "content": reply})
    return reply

def speak_text(text):
    """
    Use pyttsx3 to read the provided text aloud using a female voice if available.
    """
    print("DEBUG: Initiating text-to-speech for the following text:")
    print(text)
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    # 14 male
    # 122 robot female
    # 76 magyar female
    if current_lang == "hu":
        engine.setProperty('voice', voices[76].id)
    else:
        engine.setProperty('voice', voices[voice_mode].id)
        

    engine.say(text)
    engine.runAndWait()
    print("DEBUG: Text-to-speech completed.")

def play_sound_with_fade_down_and_up(
    sound_file,
    initial_volume=1.0,
    low_volume=0.2,
    down_delay=5,
    fade_down_duration=2,
    fade_down_steps=20,
    up_delay=5,
    fade_up_duration=2,
    fade_up_steps=20
):
    """
    Play a sound file using Pygame.
    
    Steps:
      1. Start at initial_volume.
      2. Wait for down_delay seconds.
      3. Smoothly fade volume down to low_volume over fade_down_duration.
      4. Wait for up_delay seconds.
      5. Smoothly fade volume back up to initial_volume over fade_up_duration.
    """
    pygame.mixer.init()
    sound = pygame.mixer.Sound(sound_file)
    sound.set_volume(initial_volume)
    channel = sound.play()
    
    # Wait before starting fade-down.
    time.sleep(down_delay)
    
    # Fade down volume.
    step_interval_down = fade_down_duration / fade_down_steps
    volume_decrement = (initial_volume - low_volume) / fade_down_steps
    current_volume = initial_volume
    for _ in range(fade_down_steps):
        current_volume -= volume_decrement
        if current_volume < low_volume:
            current_volume = low_volume
        channel.set_volume(current_volume)
        time.sleep(step_interval_down)
    
    # Wait before fade-up.
    time.sleep(up_delay)
    
    # Fade up volume.
    step_interval_up = fade_up_duration / fade_up_steps
    volume_increment = (initial_volume - low_volume) / fade_up_steps
    current_volume = low_volume
    for _ in range(fade_up_steps):
        current_volume += volume_increment
        if current_volume > initial_volume:
            current_volume = initial_volume
        channel.set_volume(current_volume)
        time.sleep(step_interval_up)
    
    # Optionally, wait until the sound finishes playing.
    while channel.get_busy():
        time.sleep(0.1)
def get_tasks_by_section():
    section_id = "6XG7Fj8c9RP86vP9"
    url = "https://api.todoist.com/rest/v2/tasks"
    headers = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
    params = {
        "section_id": section_id
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        #print(response.json())
        return response.json()
    else:
        return False


def check_todoist_tasks():
    """
    Check Todoist for tasks that are due within the next 30 minutes (in Amsterdam time).
    If such tasks exist, alert the user using text-to-speech.
    """
    print("DEBUG: Running check_todoist_tasks()")
    if not TODOIST_API_TOKEN:
        print("DEBUG: Todoist API token not provided.")
        return
    
    response = get_tasks_by_section()
    if response is False:
        print("DEBUG: Failed to fetch tasks from Todoist.")
        return
    
    # Define Amsterdam timezone
    amsterdam_tz = pytz.timezone("Europe/Amsterdam")
    
    # Get current time in Amsterdam timezone
    now_local = datetime.datetime.now(amsterdam_tz)
    alert_tasks = []
    all_tasks = []

    for task in response:
        task_content = task.get("content")
        if(task_content != "Wakey") and (task_content != "⚠️ RULES 🚨"):
            all_tasks.append(task_content)
    
    for task in response:
        due = task.get("due")
        task_content = task.get("content")

        if task_content == "Wakey":
            weather = 'The weather today in Amsterdam is good'
            today_tasks = "Your tasks for today," + ", ".join([t for t in all_tasks])

            message = f'Good Morning King ! {weather}. {today_tasks}'
            #api_response = ""
            #cels = api_response.cels
            
            
            # Start the sound playback with fade down and fade up in a separate thread.
            fade_value = len(all_tasks) * 4
            sound_thread = threading.Thread(
                target=play_sound_with_fade_down_and_up,
                args=("sounds/9.wav", 1.0, 0.2, 9, 2, 20, fade_value, 2, 20)
            )
            sound_thread.start()
            
            # Wait 18 seconds before speaking the message.
            time.sleep(10)
            speak_text(message)

        if not due:
            print("DEBUG: Task '{}' has no due date.".format(task["content"]))
            continue
        due_datetime_str = due.get("datetime")
        if due_datetime_str:
            try:
                # Parse the ISO 8601 datetime and ensure it's timezone-aware (in UTC)
                due_datetime = datetime.datetime.fromisoformat(due_datetime_str.replace("Z", "+00:00"))
            except Exception as parse_error:
                print("DEBUG: Error parsing due datetime for task '{}': {}".format(task["content"], parse_error))
                continue
            
            # Convert the due datetime to Amsterdam timezone
            due_datetime_local = due_datetime.astimezone(amsterdam_tz)
            delta = (due_datetime_local - now_local).total_seconds()
            if (0 <= delta <= 1800) and (task_content != "Wakey"):  # within 30 minutes
                alert_tasks.append(task)
        else:
            print("DEBUG: Task '{}' has a due date but no specific time.".format(task["content"]))
    
    if alert_tasks:
        message = "Alert: Upcoming tasks within the next 30 minutes: " + ", ".join([t["content"] for t in alert_tasks])
        print("DEBUG:", message)
        
        # Start the sound playback with fade down and fade up in a separate thread.
        sound_thread = threading.Thread(
            target=play_sound_with_fade_down_and_up,
            args=("sounds/alert_hung.wav", 1.0, 0.2, 17, 2, 20, 3, 2, 20)
        )
        sound_thread.start()
        
        # Wait 18 seconds before speaking the message.
        time.sleep(18)
        speak_text(message)
    else:
        print("DEBUG: No tasks due within the next 30 minutes.")

def main():
    global voice_mode, conversation_history, isListen
    last_todoist_check = 0  # timestamp of the last check

    while True:
        try:
            # Check Todoist tasks every 60 seconds
            if time.time() - last_todoist_check > 10:
                check_todoist_tasks()
                last_todoist_check = time.time()

            print("\nDEBUG: Waiting for trigger phrase...")
            if isListen:
                print("DEBUG: Trigger received. Starting command capture.")
                audio_file = listen_for_audio()
                user_input = transcribe_audio(audio_file)
                
                if not user_input.strip():
                    print("DEBUG: No speech detected after trigger. Waiting for next trigger...")
                    continue

                if ("close chat" in user_input.lower() or
                    "viszont latasra" in user_input.lower() or
                    "viszontlátásra" in user_input.lower()):
                    print("DEBUG: 'close chat' detected. Closing current session and returning to trigger listening.")
                    play_sound("sounds/hunger_close.wav")
                    isListen = False
                    voice_mode = 14
                    continue

                chat_reply = get_chatgpt_response(user_input, conversation_history)
                speak_text(chat_reply)
            else:
                if listen_for_trigger():
                    isListen = True
            time.sleep(0.5)
        
        except KeyboardInterrupt:
            print("\nDEBUG: KeyboardInterrupt detected. Exiting...")
            break
        except Exception as e:
            print("DEBUG: An error occurred:", e)
            time.sleep(1)
if __name__ == "__main__":
    main()

"""
    Closing chat
        HUN - "zard be"
        ENG - "close chat"
    --------
    Starting chat
        HUN - "hey english"
        ENG - "hey hungary"
"""