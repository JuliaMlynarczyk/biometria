import time
import json
import numpy as np
from PySide6.QtCore import QObject, Signal

DB_FILE = 'database.json'

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
            time.sleep(1) #symulacja działania

            #TODO symulacja ektrakcji cech do wektora
            print("FinalWorker: Ekstrakcja cech...")
            time.sleep(1.5) #symulacja działania

            feature_vector = np.random.rand(13)  # Symulowany wektor

            print(f"FinalWorker: Zapisywanie wektora cech dla 'user_XYZ' do {DB_FILE}...")
            self.save_to_json("user_XYZ", feature_vector.tolist())
            time.sleep(0.5)  # Symulacja działania

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