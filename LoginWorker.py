import time
from PySide6.QtCore import QObject, Signal
import sounddevice as sd
import numpy as np
import json
from scipy.spatial.distance import cosine, euclidean

from myMFCC import extract_features
from vad_utilis import trim_silence_and_validate
from prosody_tool import extract_prosodic_features


class LoginWorker(QObject):
    resultReady = Signal(bool, str)
    error = Signal(str)

    def __init__(self, duration=5, sample_rate=44100):
        super().__init__()
        self.duration = duration
        self.sample_rate = sample_rate

        # Wagi cech
        self.WEIGHT_MFCC = 0.8
        self.WEIGHT_PROSODY = 0.2

    def run(self):
        try:
            print("Worker: Rozpoczynam nagrywanie...")
            audio_data = sd.rec(int(self.duration * self.sample_rate),
                                samplerate=self.sample_rate, channels=1, dtype='float32')
            sd.wait()

            signal = trim_silence_and_validate(audio_data, self.sample_rate) # Przycięcie ciszy
            if signal is None:
                self.resultReady.emit(False, None)
                return

            # Ekstrakcja cech
            input_mfcc = extract_features(signal, self.sample_rate)
            input_prosody = extract_prosodic_features(signal, self.sample_rate)

            # Baza danych
            try:
                with open("database.json", "r") as f:
                    db = json.load(f)
            except:
                self.resultReady.emit(False, None)
                return

            best_user = None
            best_score = -1

            for username, user_data in db.items():
                stored_mfcc = np.array(user_data['mfcc'])
                stored_prosody = np.array(user_data['prosody'])

                # Podobieństwo MFCC - cosine
                mfcc_dist = cosine(input_mfcc, stored_mfcc)
                score_mfcc = 1 - mfcc_dist

                # Podobieństwo prosody - Normalized Euclidean
                score_prosody = 0
                dist_p = euclidean(input_prosody, stored_prosody)
                max_accepted_diff = 100.0
                score_prosody = max(0, 1 - (dist_p / max_accepted_diff))

                final_score = (self.WEIGHT_MFCC * score_mfcc) + (self.WEIGHT_PROSODY * score_prosody)

                print(
                    f"User: {username} | MFCC: {score_mfcc:.3f} | Prosody: {score_prosody:.3f} | FINAL: {final_score:.3f}")

                if final_score > best_score:
                    best_score = final_score
                    best_user = username

            if best_score >= 0.9:
                print(f"Worker: Zalogowano {best_user} (Score: {best_score:.3f})")
                self.resultReady.emit(True, best_user)
            else:
                print(f"Worker: Nie rozpoznano (Best: {best_score:.3f})")
                self.resultReady.emit(False, None)

        except Exception as e:
            print(f"Worker Error: {e}")
            self.error.emit(str(e))