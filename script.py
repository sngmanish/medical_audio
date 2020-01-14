from threading import Thread
from queue import Queue
import speech_recognition as sr

r = sr.Recognizer()
audio_queue = Queue()

def recognize_worker():
    while True:
        audio = audio_queue.get()
        try:
            if audio is None: return
            
            text = r.recognize_google(audio)
            print(text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        except AssertionError:
            return
        finally:
            audio_queue.task_done()

recognize_thread = Thread(target=recognize_worker,daemon=True)
recognize_thread.start()

with sr.Microphone() as source:
    try:
        while True:
            audio_queue.put(r.listen(source))
    except KeyboardInterrupt:
        print("this worked")
        pass

audio_queue.join()
audio_queue.put(None)
recognize_thread.join()
