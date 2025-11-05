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

            # TODO opcjonalnie szukanie urządzenia audio
            #devices = sd.query_devices()
            #if not devices:
            #    raise RuntimeError("Brak dostępnych urządzeń audio!")

            audio_data = sd.rec(
                int(self.duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()
            print("Worker: Nagrywanie zakończone.")

            audio_data = audio_data.flatten()

            # TODO czy w nagraniu coś w ogóle jest żeby wykluczyć cisze
            #energy = np.sum(audio_data ** 2)
            #if energy < 1e-6:
            #    raise ValueError("Worker: Zbyt ciche nagranie, spróbuj ponownie.")

            recording_success = True
            print("Worker: Próbka nagrana poprawnie.")
            self.recordingReady.emit(audio_data, recording_success)



        except Exception as e:
            print(f"Worker: Wystąpił błąd! {e}")
            self.error.emit(str(e))