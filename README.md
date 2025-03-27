# RealTimeTranscribeAI

RealTimeTranscribeAI is an enhanced version of the original Ecoute project with an added AI reply feature. This tool records audio simultaneously from your microphone and speakers, transcribes it in real time, and generates professional AI responses using the Deepseek API.

## Features

- **Enhanced Dual Audio Capture**  
  Record audio simultaneously from both the microphone (user input) and speakers (system output).

- **Real-Time Transcription**  
  Transcribe audio on the fly using two approaches:
  - **Local Transcription:** Powered by the Faster Whisper model.
  - **API Transcription:** Leveraging OpenAI's transcription API.

- **AI-Powered Reply**  
  Generate concise, interview-style AI responses from the transcribed text using the Deepseek API.

- **User-Friendly Graphical Interface**  
  Built with CustomTkinter, the GUI displays live transcriptions, allows you to clear the transcript, and view AI-generated replies.

- **Automatic Ambient Noise Adjustment**  
  Automatically calibrates for ambient noise to improve transcription accuracy.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Code Structure](#code-structure)
- [Important Notes](#important-notes)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Installation

### System Requirements

- **Python Version:** Python 3.8 or higher.
- **Operating System:** Primarily designed for Windows (speaker capture uses WASAPI loopback devices; additional setup may be required for other platforms).
- **External Tools:**  
  [FFmpeg](https://ffmpeg.org) — Ensure that the `ffmpeg` command is available in your system PATH for proper audio processing.

### Python Dependencies

Install the required Python packages via pip. Note that some libraries may be custom or require platform-specific adjustments:

```bash
pip install customtkinter faster-whisper torch openai python-dotenv