import threading
from AudioTranscriber import AudioTranscriber
import customtkinter as ctk
import AudioRecorder
import queue
import time
import sys
import TranscriberModels
import subprocess
import os
import requests

from dotenv import load_dotenv
from openai import OpenAI

# Allow duplicate OpenMP libraries
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Load environment variables from a .env file
load_dotenv()

# Read API related information
api_key = Your_Deepseek_API_Key
base_url = "https://api.deepseek.com"
chat_model = "deepseek-chat"

# Initial prompt configuration for Deepseek
INITIAL_DEEPSEEK_PROMPT = """
You will play the role of an experienced electrical and electronic engineering interviewer who is good at technical interviews and professional interviews. 
Your task is to provide a clear and concise transcript by analyzing the transcribed audio input. 
You need to provide an organized and easy-to-understand transcript.
Your answer format must be one large paragraph and only contain the transcript content itself, without any additional comments, and must be easy to read aloud. 
Do not add any bold words.
"""

# Initialize the OpenAI client with the provided API key and base URL
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

def write_in_textbox(textbox, text):
    """
    Updates the content of the given textbox with the provided text.
    """
    textbox.delete("0.0", "end")
    textbox.insert("0.0", text)

def update_transcript_UI(transcriber, textbox):
    """
    Periodically updates the transcript displayed in the UI by fetching
    the current transcript from the transcriber and writing it in the textbox.
    It self-schedules every 300 milliseconds.
    """
    transcript_string = transcriber.get_transcript()
    write_in_textbox(textbox, transcript_string)
    textbox.after(300, update_transcript_UI, transcriber, textbox)

def clear_context(transcriber, speaker_queue, mic_queue):
    """
    Clears the transcribed content in the transcriber and empties the
    speaker and microphone audio queues.
    """
    transcriber.clear_transcript_data()

    with speaker_queue.mutex:
        speaker_queue.queue.clear()
    with mic_queue.mutex:
        mic_queue.queue.clear()

def generate_deepseek_response(transcriber, reply_textbox=None, speaker_queue=None, mic_queue=None):
    """
    使用流式传输获取Deepseek响应并实时更新界面
    """
    transcript = transcriber.get_transcript().strip()
    if not transcript:
        print("[INFO] Transcript is empty, unable to request Deepseek.")
        return

    # 清空回复框内容
    reply_textbox.delete("0.0", "end")
    
    try:
        # 创建流式请求
        stream = client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": INITIAL_DEEPSEEK_PROMPT},
                {"role": "user",   "content": transcript}
            ],
            stream=True  # 启用流式传输
        )

        collected_chunks = []
        full_reply = ""

        # 实时处理每个chunk
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                chunk_content = chunk.choices[0].delta.content
                
                # 收集片段
                collected_chunks.append(chunk_content)
                full_reply += chunk_content
                
                # 立即更新界面
                reply_textbox.insert("end", chunk_content)
                reply_textbox.update_idletasks()  # 强制立即更新UI
                reply_textbox.see("end")  # 自动滚动到底部

        print("[Deepseek] Full response:", full_reply)

    except Exception as e:
        error_msg = f"[ERROR] Deepseek请求失败: {str(e)}"
        print(error_msg)
        reply_textbox.insert("end", "\n\n" + error_msg)

    # 最后清空上下文
    def clear_after_delay():
        if speaker_queue and mic_queue:
            clear_context(transcriber, speaker_queue, mic_queue)
        else:
            transcriber.clear_transcript_data()
    
    # 延迟3秒后清空上下文（可根据需要调整）
    threading.Timer(3, clear_after_delay).start()

def create_ui_components(root, transcriber, speaker_queue, mic_queue):
    """
    Creates and configures the UI components using customtkinter and returns the transcript textbox widget.
    """
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root.title("Ecoute")
    root.geometry("1000x600")

    # Configure root grid layout
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    # Main frame for organizing UI elements
    main_frame = ctk.CTkFrame(root)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=0)
    main_frame.grid_rowconfigure(2, weight=0)
    main_frame.grid_rowconfigure(3, weight=0)

    # Textbox that displays the transcript
    transcript_textbox = ctk.CTkTextbox(
        main_frame, 
        font=("Arial", 20), 
        text_color='#FFFCF2', 
        wrap="word"
    )
    transcript_textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    # Button to clear the transcript and associated context
    clear_button = ctk.CTkButton(
        main_frame, 
        text="Clear Transcript", 
        command=lambda: clear_context(transcriber, speaker_queue, mic_queue)
    )
    clear_button.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

    # Textbox to display the Deepseek response
    reply_textbox = ctk.CTkTextbox(
        main_frame, 
        font=("Arial", 16), 
        text_color='#FFFCF2', 
        wrap="word",
        height=300
    )
    reply_textbox.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

    # Button to generate the Deepseek response using the current transcript
    deepseek_button = ctk.CTkButton(
        main_frame,
        text="Generate Deepseek Reply",
        command=lambda: generate_deepseek_response(transcriber, reply_textbox, speaker_queue, mic_queue)
    )
    deepseek_button.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))

    return transcript_textbox

def main():
    """
    Main function to initialize the transcriber, audio recorders, and UI,
    then starts the transcription thread and launches the UI main loop.
    """
    # Verify that ffmpeg is installed
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("ERROR: The ffmpeg library is not installed. Please install ffmpeg and try again.")
        return

    # Initialize the main window
    root = ctk.CTk()

    # Create queues for audio data from the speaker and microphone
    speaker_queue = queue.Queue()
    mic_queue = queue.Queue()

    # Start the microphone recorder and record audio into mic_queue
    user_audio_recorder = AudioRecorder.DefaultMicRecorder()
    user_audio_recorder.record_into_queue(mic_queue)

    # Short delay before starting the speaker recorder
    time.sleep(2)

    # Start the speaker recorder and record audio into speaker_queue
    speaker_audio_recorder = AudioRecorder.DefaultSpeakerRecorder()
    speaker_audio_recorder.record_into_queue(speaker_queue)

    # Load the transcription model (checks for '--api' flag in command-line arguments)
    model = TranscriberModels.get_model('--api' in sys.argv)

    # Initialize the transcriber with audio sources and the prediction model
    transcriber = AudioTranscriber(user_audio_recorder.source, speaker_audio_recorder.source, model)
    
    # Start a separate thread to continuously transcribe the audio queues
    transcribe = threading.Thread(target=transcriber.transcribe_audio_queue, args=(speaker_queue, mic_queue))
    transcribe.daemon = True
    transcribe.start()

    # Create the UI components and retrieve the transcript textbox
    transcript_textbox = create_ui_components(root, transcriber, speaker_queue, mic_queue)

    print("READY")

    # Begin updating the transcript on the UI periodically
    update_transcript_UI(transcriber, transcript_textbox)

    # Start the main UI event loop
    root.mainloop()

if __name__ == "__main__":
    main()