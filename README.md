# RealTimeTranscribeAI

RealTimeTranscribeAI is an enhanced version of the original [Ecoute](https://github.com/SevaSk/ecoute) project with an added AI reply feature. This tool simultaneously captures audio from your microphone (user input) and speakers (system output), transcribes it in real time, and uses the Deepseek API to generate professional AI responses.

## Features

- **Dual Audio Capture**  
  Record audio concurrently from both the microphone and the speakers.

- **Real-Time Transcription**  
  Choose between two transcription modes:
  - **Local Transcription:** Powered by the Faster Whisper model.
  - **API Transcription:** Uses OpenAI’s transcription API.

- **AI-Powered Reply Generation**  
  Generate concise, interview-style responses based on the transcribed text using the Deepseek API.

- **User-Friendly Graphical Interface**  
  The CustomTkinter-based GUI displays live transcriptions, allows you to clear the transcript, and shows AI-generated replies.

- **Automatic Ambient Noise Adjustment**  
  Automatically calibrates for ambient noise to enhance transcription accuracy.

## Table of Contents

- [Installation](#installation)
- [Deepseek API Configuration](#deepseek-api-configuration)
- [Usage](#usage)

## Installation

### System Requirements

- **Python Version:** Python 3.8 or higher.
- **Operating System:** Primarily designed for Windows (speaker capture utilizes WASAPI loopback devices; other platforms may require additional configuration).
- **External Tools:**  
  [FFmpeg](https://ffmpeg.org) — Ensure the `ffmpeg` command is available in your system PATH for proper audio processing.

### Python Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

### Deepseek API Configuration

Before running RealTimeTranscribeAI, edit the following lines in the `main.py` file to set up your Deepseek API details:

```python
api_key = "Your_Deepseek_API_Key"
base_url = "https://api.deepseek.com"
chat_model = "deepseek-chat"
```

Replace `"Your_Deepseek_API_Key"` with your actual Deepseek API key. You can also modify the `INITIAL_DEEPSEEK_PROMPT` variable to customize the initial prompt for AI-generated replies.

## Usage

1. Complete the installation and API configuration steps.
2. Launch the application with the following command:
   ```bash
   python main.py
   ```
3. Once started, the graphical interface will display the live transcription and AI responses. Use the interface buttons to clear the transcript or adjust settings as needed.