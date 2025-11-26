import time
from PySide6.QtCore import QObject, Signal
import sounddevice as sd

from vad_utilis import trim_silence_and_validate


class RegisterWorker(QObject):

    recordingReady = Signal(object, bool)
    error = Signal(str)

    def __init__(self, duration=5, sample_rate=44100):
        super().__init__()
        self.duration = duration
        self.sample_rate = sample_rate

    def run(self):
        try:
            print("Worker: Rozpoczynam nagrywanie...")

            audio_data = sd.rec(
                int(self.duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()
            print("Worker: Nagrywanie zakończone.")

            speech_segment = trim_silence_and_validate(audio_data, self.sample_rate) # Usuwanie ciszy

            if speech_segment is None:
                self.recordingReady.emit(None, False)
                return

            audio_data = speech_segment

            recording_success = True
            print("Worker: Próbka nagrana poprawnie.")
            self.recordingReady.emit(audio_data, recording_success)



        except Exception as e:
            print(f"Worker: Wystąpił błąd! {e}")
            self.error.emit(str(e))