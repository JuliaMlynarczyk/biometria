from PySide6 import QtWidgets, QtCore, QtGui

from LoginWidget import LoginWidget
from RegisterWidget import RegisterWidget
from AnalysisWidget import AnalysisWidget
from AnalysisWorker import AnalysisWorker
from LoginWorker import LoginWorker
from RegisterWorker import RegisterWorker
from RegisterFinalWorker import RegisterFinalWorker
from vad_utilis import trim_silence_and_validate


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.background_pixmap = QtGui.QPixmap("static/background.jpg")

        # tworzenie talii ekranów
        self.setWindowTitle("Voice Biometry")
        self.stack = QtWidgets.QStackedWidget(self)

        # poszczególne ekrany aplikacji
        self.login_screen = LoginWidget()
        self.register_screen = RegisterWidget()
        self.analysis_screen = AnalysisWidget()

        self.stack.addWidget(self.login_screen)
        self.stack.addWidget(self.register_screen)
        self.stack.addWidget(self.analysis_screen)

        # Tworzenie wątków do zarządzania procesami
        self.worker_thread = None
        self.worker = None

        # Zmienne do przechowania wyników z wątku nagrywania
        self._last_recording_data = None
        self._last_recording_success = None

        # Zmienne do przechowania wyników z wątku nagrywania
        self._last_recording_data = None
        self._last_recording_success = None

        # do przechowania wyników z wątku analizy
        self._last_analysis_data = None
        self._last_analysis_fs = None
        self._last_analysis_success = None

        self.setCentralWidget(self.stack)
        self.stack.setCurrentWidget(self.login_screen)

        # Sygnaly do obslugi ekranu nagrywania
        self.login_screen.registerClicked.connect(self.show_register_screen) # Przejscie do rejestracji
        self.login_screen.startLoginProcess.connect(self.handle_login_attempt) #Przejscie do proby zalogowania - login worker

        # Sygnaly do obslugi procesu rejestracji
        self.register_screen.startRecordingAttempt.connect(self.handle_recording_attempt) # Przejscie do nagrywania - register worker
        self.register_screen.startRegisterProces.connect(self.handle_final_registration) # Przejscie do procesu rejestracji - register final worker
        self.register_screen.loginClicked.connect(self.show_login_screen) # Przejscie do logowania po pomyslnej rejestracji

        self.analysis_screen.startAnalysisRecording.connect(self.handle_analysis_recording)
        self.analysis_screen.logOut.connect(self.show_login_screen)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setOpacity(0.3)

        if not self.background_pixmap.isNull():
            scaled_pixmap = self.background_pixmap.scaled(
                self.size(),
                QtCore.Qt.KeepAspectRatioByExpanding,
                QtCore.Qt.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled_pixmap)
        painter.end()
        super().paintEvent(event)

    def show_login_screen(self):
        self.register_screen.reset_progress() # Za kazdym razem resetuje smieci po probach rejestracji
        self.stack.setCurrentWidget(self.login_screen)

    def show_register_screen(self):
        self.stack.setCurrentWidget(self.register_screen)

    def show_analysis_screen(self):
        self.stack.setCurrentWidget(self.analysis_screen)

    # Czyszczenie watkow, pomaga uniknac kolizji
    def cleanup_thread_references(self):
        self.worker_thread = None
        self.worker = None

    # rozpoczecie proby logowania
    def handle_login_attempt(self):
        # Zabezpieczenie przed dzialajacymi watkami
        if self.worker_thread and self.worker_thread.isRunning():
            print("MainWindow: A worker thread is already running. Aborting new request.")
            return

        print("MainWindow: Otrzymano sygnał startLoginProcess.")

        self.worker_thread = QtCore.QThread() # uruchomienie nowega watku
        self.worker = LoginWorker(duration=5)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run) # uruchomienie w watku funkcji run (login worker)
        self.worker.resultReady.connect(self.on_login_result) # otrzymanie sygnalu resultReady
        self.worker.error.connect(self.on_login_error) # wystapienie bledu przy logowaniu

        # "sprzatanie" po watkach - zamykanie watkow
        self.worker.resultReady.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.finished.connect(self.cleanup_thread_references)

        self.worker_thread.start()
        print("MainWindow: Wątek logowania uruchomiony.")

    def on_login_result(self, success, user_id=None):
        print(f"MainWindow: Otrzymano wynik: {success}")

        self.login_screen.stop_ui_feedback(success=success)

        if success:
            self.analysis_screen.set_user(user_id)
            QtCore.QTimer.singleShot(1000, self.show_analysis_screen)
        else:
            pass

    def on_login_error(self, error_message):
        print(f"MainWindow: Otrzymano błąd: {error_message}")
        self.login_screen.show_login_error(error_message)

    def handle_recording_attempt(self):
        # Zabezpieczenie przed dzialajacymi watkami
        if self.worker_thread and self.worker_thread.isRunning():
            print("MainWindow: A worker thread is already running. Aborting new request.")
            return

        self.worker_thread = QtCore.QThread()
        self.worker = RegisterWorker(duration=5)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.recordingReady.connect(self.on_recording_result)
        self.worker.error.connect(self.on_recording_error)

        self.worker.recordingReady.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.finished.connect(self.cleanup_thread_references)
        self.worker_thread.finished.connect(self.process_recording_result)

        self.worker_thread.start()
        print("MainWindow: Wątek rejestracji (próbka) uruchomiony.")

    def on_recording_result(self, audio_data, success):
        print(f"MainWindow: Otrzymano wynik nagrania (success={success}).")
        self._last_recording_data = audio_data
        self._last_recording_success = success

    def on_recording_error(self, error_message):
        print(f"MainWindow: Otrzymano błąd nagrania: {error_message}")
        self._last_recording_data = None
        self._last_recording_success = False
        self.register_screen.stop_ui_feedback(success=False)

    def process_recording_result(self):

        print("MainWindow: Przetwarzanie wyniku nagrania po zakończeniu wątku.")
        if self._last_recording_success is not None:
            self.register_screen.stop_ui_feedback(
                success=self._last_recording_success,
                audio_data=self._last_recording_data
            )
            self._last_recording_data = None
            self._last_recording_success = None


    def handle_final_registration(self, samples_list, user_login):
        if self.worker_thread and self.worker_thread.isRunning():
            print("MainWindow: A worker thread is already running. Aborting new request.")
            return

        print(f"MainWindow: Otrzymano sygnał startRegisterProces z {len(samples_list)} próbkami.")

        self.worker_thread = QtCore.QThread()
        self.worker = RegisterFinalWorker(samples_list, user_login)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.registrationComplete.connect(self.on_final_registration_complete)
        self.worker.error.connect(self.on_final_registration_error)

        self.worker.registrationComplete.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.finished.connect(self.cleanup_thread_references)

        self.worker_thread.start()
        print("MainWindow: Wątek finalnej rejestracji uruchomiony.")

    def on_final_registration_complete(self):
        print("MainWindow: Finalna rejestracja zakończona pomyślnie.")
        self.register_screen.on_final_registration_result(success=True)

    def on_final_registration_error(self, error_message):
        print(f"MainWindow: Błąd podczas finalnej rejestracji: {error_message}")
        self.register_screen.on_final_registration_result(success=False, message=error_message)

    def handle_analysis_recording(self, sample_rate):
        if self.worker_thread and self.worker_thread.isRunning():
            print("MainWindow: Inny wątek jest już uruchomiony. Przerywam.")
            self.analysis_screen.stop_ui_feedback(success=False)
            return

        print(f"MainWindow: Otrzymano sygnał startAnalysisRecording (fs={sample_rate} Hz).")

        self.worker_thread = QtCore.QThread()
        self.worker = AnalysisWorker(duration=2, sample_rate=sample_rate)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.recordingReady.connect(self.on_analysis_result)
        self.worker.error.connect(self.on_analysis_error)

        self.worker.recordingReady.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.finished.connect(self.cleanup_thread_references)

        self.worker_thread.finished.connect(self.process_analysis_result)

        self.worker_thread.start()
        print("MainWindow: Wątek analizy (symulacja) uruchomiony.")

    def on_analysis_result(self, audio_data, sample_rate):
        print(f"MainWindow: Otrzymano wynik nagrania analizy (fs={sample_rate}).")
        self._last_analysis_data = audio_data
        self._last_analysis_fs = sample_rate
        self._last_analysis_success = True

    def on_analysis_error(self, error_message):
        print(f"MainWindow: Otrzymano błąd nagrania analizy: {error_message}")
        self._last_analysis_data = None
        self._last_analysis_fs = None
        self._last_analysis_success = False
        self.analysis_screen.stop_ui_feedback(success=False)

    def process_analysis_result(self):
        print("MainWindow: Przetwarzanie wyniku nagrania analizy.")

        if self._last_analysis_success is None:
            return

        if self._last_analysis_success:
            raw_data = self._last_analysis_data
            fs = self._last_analysis_fs

            print(f"MainWindow: Przetwarzanie VAD dla sygnału fs={fs}...")
            processed_data = trim_silence_and_validate(raw_data, fs) # usuwanie ciszy z sygnałów do analizy

            if processed_data is not None:
                print(f"MainWindow: VAD sukces. Długość sygnału po przycięciu: {len(processed_data)}")
                self.analysis_screen.receive_recording_data(
                    processed_data,
                    fs
                )
            else:
                print("MainWindow: VAD zwrócił None (zbyt cicho/krótko).")
                self.analysis_screen.stop_ui_feedback(success=False)
        else:
            pass

        self._last_analysis_data = None
        self._last_analysis_fs = None
        self._last_analysis_success = None