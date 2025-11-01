import time
from PySide6.QtCore import QObject, Signal
import sounddevice as sd
import numpy as np


class RegisterWorker(QObject):

    recordingReady = Signal(object, bool)
    error = Signal(str)

    def __init__(self, duration=5, sample_rate=44100): #można później zmienić częstotliwość próbkowania w zalezności od wyników projektu
        super().__init__()
        self.duration = duration
        self.sample_rate = sample_rate

    def run(self):
        try:
            print("Worker: Rozpoczynam nagrywanie...")


            #audio_data = sd.rec(int(self.duration * self.sample_rate),
            #                    samplerate=self.sample_rate, channels=1, dtype='float32')
            #sd.wait()


            print("Worker: Nagrywanie...")
            time.sleep(2)  # Krótsza symulacja na potrzeby testów
            audio_data = np.random.rand(self.duration * self.sample_rate)
            print("Worker: Nagrywanie zakończone.")

            recording_success = True # Losowe powodzenie logowania, symulacja działania

            print(f"Worker: Zakończono. {recording_success}")
            self.recordingReady.emit(audio_data, recording_success)

        except Exception as e:
            print(f"Worker: Wystąpił błąd! {e}")
            self.error.emit(str(e))