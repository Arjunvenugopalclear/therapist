import pyaudio
import wave
import io
import speech_recognition as sr
from gtts import gTTS

def process_audio(recorder):
    # Wait for the recorder to finish and get the audio data
    audio_data = recorder.get_audio_data()
    return audio_data

def transcribe_audio(audio_data):
    # Transcribe the audio data using speech recognition
    recognizer = sr.Recognizer()
    audio_file = io.BytesIO(audio_data)

    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)

    try:
        transcription = recognizer.recognize_google(audio)
        return transcription
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."
    except sr.RequestError:
        return "Sorry, there was an error processing your speech."

def text_to_speech(text):
    # Convert text to speech and save it
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")

    # Return the path to the saved audio file
    return "response.mp3"

def play_audio(file_path):
    # Play the audio file
    chunk = 1024
    wf = wave.open(file_path, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(chunk)

    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    stream.stop_stream()
    stream.close()
    p.terminate()
