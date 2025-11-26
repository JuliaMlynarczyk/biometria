import time
import json
import numpy as np
from PySide6.QtCore import QObject, Signal

from myMFCC import extract_features
from prosody_tool import extract_prosodic_features

DB_FILE = 'database.json'

def load_data():
    data = {}
    try:
        with open(DB_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return data

# Zapisanie do bazy danych
def save_to_json(user_login, mfcc_vector, prosody_vector, existing_data):
    existing_data[user_login] = {
        "mfcc": mfcc_vector,
        "prosody": prosody_vector
    }

    with open(DB_FILE, 'w') as f:
        json.dump(existing_data, f, indent=4)


class RegisterFinalWorker(QObject):
    registrationComplete = Signal()
    error = Signal(str)

    def __init__(self, samples, user_login):
        super().__init__()
        self.user_login = user_login
        self.samples = samples

    def run(self):
        try:
            print(f"FinalWorker: Otrzymano {len(self.samples)} próbek.")
            data = load_data()
            if self.user_login in data:
                self.error.emit(f"Użytkownik '{self.user_login}' już istnieje!")
                return

            sample_rate = 44100
            mfcc_list = []
            prosody_list = []

            print("FinalWorker: Ekstrakcja cech (MFCC + Prozodia)...")

            for i, signal in enumerate(self.samples):
                # MFCC
                mfcc = extract_features(signal, sample_rate)
                mfcc_list.append(mfcc)

                # PROSODY
                prosody = extract_prosodic_features(signal, sample_rate)
                prosody_list.append(prosody)

                print(f"   -> Próbka {i + 1}: MFCC={len(mfcc)}, Prosody={prosody}")

            # Uśrednianie wektorów cech
            avg_mfcc = np.mean(np.stack(mfcc_list), axis=0)
            avg_prosody = np.mean(np.stack(prosody_list), axis=0)

            print(f"FinalWorker: Zapisywanie danych dla '{self.user_login}'...")
            save_to_json(self.user_login, avg_mfcc.tolist(), avg_prosody.tolist(), data)

            print("FinalWorker: Rejestracja zakończona.")
            self.registrationComplete.emit()

        except Exception as e:
            print(f"FinalWorker: Błąd! {e}")
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))