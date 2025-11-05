import time
from PySide6.QtCore import QObject, Signal
import sounddevice as sd
import numpy as np
from myMFCC import extract_features
import json
from scipy.spatial.distance import cosine


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
            #print("Worker: Ekstrakcja cech...")
            #time.sleep(1)  # Symulacja działania

            signal = audio_data.flatten()
            # wywołanie funkcji MFCC
            features = extract_features(signal, self.sample_rate)
            print("Worker: Wektor cech obliczony:")
            print(features)

            #TODO algorytm porównywania cech z bazą json
            print("Worker: Porównuję z bazą...")
            #time.sleep(0.5) # Symulacja działania

            with open("voice_users.json", "r") as f:
                db = json.load(f)

            best_user = None
            best_score = 999

            for username, stored_vec in db.items():
                dist = cosine(features, stored_vec)
                if dist < best_score:
                    best_score = dist
                    best_user = username

            # próg podobieństwa > 0.8
            similarity = 1 - best_score
            if similarity > 0.8:
                print(f"Zidentyfikowano: {best_user}, similarity={similarity:.2f}")
                login_success_py = True
            else:
                print(f"Brak dopasowania (max similarity={similarity:.2f})")
                login_success_py = False


            #login_success_np = np.random.choice([True, False]) # Losowe powodzenie logowania, symulacja działania
            #login_success_py = bool(login_success_np)

            print(f"Worker: Zakończono. Wynik: {login_success_py}")
            self.resultReady.emit(login_success_py)

        except Exception as e:
            print(f"Worker: Wystąpił błąd! {e}")
            self.error.emit(str(e))