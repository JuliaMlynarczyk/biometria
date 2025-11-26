import time
import numpy as np
import sounddevice as sd

from PySide6.QtCore import QObject, Signal


class AnalysisWorker(QObject):
    recordingReady = Signal(object, int)
    error = Signal(str)

    def __init__(self, duration=5, sample_rate=44100):
        super().__init__()
        self.duration = duration
        self.sample_rate = sample_rate

    def run(self):
        try:
            print(f"AnalysisWorker: Rozpoczynam symulację nagrywania (fs={self.sample_rate} Hz, {self.duration}s)...")

            audio_data = sd.rec(int(self.duration * self.sample_rate),
                                samplerate=self.sample_rate, channels=1, dtype='float32')
            sd.wait()
            signal = audio_data.flatten()

            print(f"AnalysisWorker: Nagranie zakończone")

            self.recordingReady.emit(signal, self.sample_rate)

        except Exception as e:
            print(f"AnalysisWorker: Wystąpił błąd! {e}")
            self.error.emit(str(e))