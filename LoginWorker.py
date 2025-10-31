import time
from PySide6.QtCore import QObject, Signal
import sounddevice as sd
import numpy as np


class LoginWorker(QObject):

    resultReady = Signal(bool)
    error = Signal(str)

    def __init__(self, duration=5, sample_rate=44100): #można później zmienić częstotliwość próbkowania w zalezności od wyników projektu
        super().__init__()
        self.duration = duration
        self.sample_rate = sample_rate

    def run(self):
        try:
            print("Worker: Rozpoczynam nagrywanie...")
            audio_data = sd.rec(int(self.duration * self.sample_rate),
                                samplerate=self.sample_rate, channels=1, dtype='float32')
            sd.wait()
            print("Worker: Nagrywanie zakończone.")

            #TODO napisac algorytm ekstrakcji cech - ręczny algorytm od zera
            print("Worker: Ekstrakcja cech...")
            time.sleep(1)  # Symulacja działania

            #TODO algorytm porównywania cech z bazą json
            print("Worker: Porównuję z bazą...")
            time.sleep(0.5) # Symulacja działania

            login_success = np.random.choice([True, False]) # Losowe powodzenie logowania, symulacja działania

            print(f"Worker: Zakończono. Wynik: {login_success}")
            self.resultReady.emit(login_success)

        except Exception as e:
            print(f"Worker: Wystąpił błąd! {e}")
            self.error.emit(str(e))