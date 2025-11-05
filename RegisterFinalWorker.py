import time
import json
import numpy as np
from PySide6.QtCore import QObject, Signal
from myMFCC import extract_features


DB_FILE = 'voice_users.json'
fs = 16000 #można zmienić albo dynamicznie ustawiać

class RegisterFinalWorker(QObject):
    registrationComplete = Signal()
    error = Signal(str)

    def __init__(self, samples):
        super().__init__()
        self.samples = samples

    def run(self):
        try:
            print(f"FinalWorker: Otrzymano {len(self.samples)} próbek. Rozpoczynam przetwarzanie...")

            #TODO logika uśredniania próbek
            print("FinalWorker: Uśrednianie próbek...")
            avg_signal = np.mean(np.stack(self.samples), axis=0)
            print(f"FinalWorker: Średnia długość próbki: {len(avg_signal)}")

            #TODO symulacja ektrakcji cech do wektora
            print("FinalWorker: Ekstrakcja cech...")
            sample_rate = 44100  # TODO przekazanie z konstruktora

            # MFCC
            feature_vector = extract_features(avg_signal, sample_rate)
            print("FinalWorker: Wektor cech obliczony:")
            print(feature_vector)

            print(f"FinalWorker: Zapisywanie wektora cech dla 'user_XYZ' do {DB_FILE}...")

            # Zapis do pliku JSON
            user_data = {
                "mfcc": feature_vector.tolist(),
                "fs": fs
            }

            print(f"FinalWorker: Zapisywanie wektora cech dla 'user_XYZ' do {DB_FILE}...")
            self.save_to_json("user_XYZ", user_data)
            time.sleep(0.5)

            print("FinalWorker: Rejestracja zakończona pomyślnie.")
            self.registrationComplete.emit()

        except Exception as e:
            print(f"FinalWorker: Wystąpił błąd podczas finalnej rejestracji! {e}")
            self.error.emit(str(e))

    def save_to_json(self, user_id, vector):
        data = {}
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"FinalWorker: Plik {DB_FILE} nie znaleziony. Tworzę nowy.")
            pass
        except json.JSONDecodeError:
            print(f"FinalWorker: Błąd odczytu {DB_FILE}. Nadpisuję plik.")
            pass

        data[user_id] = vector

        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=4)