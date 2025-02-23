# Voice-Controlled Home Assistant with Todoist Integration

A smart home assistant that combines voice control, task management, and morning routines using OpenAI's GPT and Whisper APIs, along with Todoist integration.

## Features

- Voice-activated assistant with multiple personality modes
- Bilingual support (English and Hungarian)
- Todoist task integration with upcoming task alerts
- Morning routine with weather updates and daily task summaries
- Background music with smart volume control
- Customizable voice personalities

## Prerequisites

### Required API Keys
- OpenAI API key
- Todoist API token

### Required Python Packages
```bash
openai
speech_recognition
pyttsx3
playsound
python-dotenv
requests
pytz
pygame
```

## Installation

1. Clone the repository
2. Install required packages:
```bash
pip install openai speech_recognition pyttsx3 playsound python-dotenv requests pytz pygame
```

3. Create a `.env` file with your API keys:
```plaintext
OPENAI_API_KEY=your_openai_key_here
TODOIST_API_TOKEN=your_todoist_token_here
```

## Usage

### Voice Commands

#### Activation Phrases
- English mode: `hey english`
- Hungarian mode: `hey hungary`

#### Voice Personalities (English Mode)
- Bad News: `hey english bad news`
- Good News: `hey english good news`
- Whisper: `hey english whisper`
- Goblin: `hey english goblin`
- Superstar: `hey english superstar`
- Fred: `hey english fred`
- Weird: `hey english weird`
- Default (Antal): `hey english`

#### Closing Commands
- English: `close chat`
- Hungarian: `viszont latasra` or `viszontlátásra`

## Features in Detail

### Todoist Integration
The assistant automatically:
- Checks for tasks due within the next 30 minutes
- Provides audio alerts for upcoming tasks
- Triggers morning routine with "Wakey" task

### Morning Routine
Activated by the "Wakey" task in Todoist:
- Plays background music with smart volume control
- Announces weather information
- Lists all tasks for the day

### Voice Recognition
- Utilizes OpenAI's Whisper model for accurate transcription
- Supports both English and Hungarian languages
- Maintains conversation context

## Project Structure
```
project/
├── sounds/
│   ├── trigger_beep.wav
│   ├── alert_hung.wav
│   └── 9.wav
├── .env
└── main.py
```

## Error Handling
- Automatic recovery from connection issues
- Debug logging for troubleshooting
- Continuous operation with error recovery

## Notes
- The assistant checks Todoist every 60 seconds
- Voice personality changes persist until chat is closed
- Background music volume adjusts automatically during interactions

## License
MIT

## Author
Tamas Orban
