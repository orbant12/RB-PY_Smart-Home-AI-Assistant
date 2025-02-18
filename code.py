import os
import time
import openai
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv

# Load environment variables (make sure you have a .env file with OPENAI_API_KEY defined)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Instantiate the OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def listen_for_audio():
    """Listen to the microphone until a pause is detected and save audio to a WAV file."""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300  # Minimum audio energy to trigger recording
    recognizer.pause_threshold = 0.8   # Seconds of silence to consider the phrase complete

    print("DEBUG: Energy threshold set to:", recognizer.energy_threshold)
    print("DEBUG: Pause threshold set to:", recognizer.pause_threshold)

    with sr.Microphone() as source:
        print("DEBUG: Using microphone:", source)
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
    """Use OpenAI Whisper model to transcribe the audio file."""
    with open(file_path, "rb") as audio_file:
        print("DEBUG: Opened audio file for transcription.")
        start_time = time.time()
        print("DEBUG: Calling transcription endpoint using client.audio.transcriptions.create")
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        elapsed_time = time.time() - start_time
        print(f"DEBUG: Transcription API call took {elapsed_time:.2f} seconds")
    text = transcript.text  # Access text attribute directly
    print("Transcription:", text)
    return text

def get_chatgpt_response(user_text, conversation_history):
    """Send the conversation history (including the new user text) to ChatGPT and retrieve the response."""
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
    """Use pyttsx3 to read the provided text aloud."""
    print("DEBUG: Initiating text-to-speech for the following text:")
    print(text)
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    print("DEBUG: Text-to-speech completed.")

def main():
    # Initialize conversation history with a system prompt
    conversation_history = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    while True:
        try:
            print("\nDEBUG: Starting new iteration of the main loop.")
            # Capture audio from the microphone
            audio_file = listen_for_audio()
            
            # Transcribe the recorded audio using OpenAI Whisper
            user_input = transcribe_audio(audio_file)
            
            # If transcription is empty, skip processing
            if not user_input.strip():
                print("DEBUG: No speech detected. Restarting iteration...")
                continue

            # Query ChatGPT with the full conversation history
            chat_reply = get_chatgpt_response(user_input, conversation_history)
            
            # Read ChatGPT's reply using text-to-speech
            speak_text(chat_reply)
            
            # Optional pause between iterations
            time.sleep(1)
        
        except KeyboardInterrupt:
            print("\nDEBUG: KeyboardInterrupt detected. Exiting...")
            break
        except Exception as e:
            print("DEBUG: An error occurred:", e)
            time.sleep(1)

if __name__ == "__main__":
    main()
