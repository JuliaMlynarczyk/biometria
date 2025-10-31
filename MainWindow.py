import PySide6
from PySide6 import QtWidgets, QtCore

from LoginWidget import LoginWidget
from RegisterWidget import RegisterWidget
from AnalysisWidget import AnalysisWidget
from LoginWorker import LoginWorker

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

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

        self.worker_thread = None
        self.worker = None

        self.setCentralWidget(self.stack)
        self.stack.setCurrentWidget(self.login_screen)

        self.login_screen.registerClicked.connect(self.show_register_screen)
        self.login_screen.startLoginProcess.connect(self.handle_login_attempt)

    def show_login_screen(self):
        self.stack.setCurrentWidget(self.login_screen)

    def show_register_screen(self):
        self.stack.setCurrentWidget(self.register_screen)

    def show_analysis_screen(self):
        self.stack.setCurrentWidget(self.analysis_screen)

    def handle_login_attempt(self):

        print("MainWindow: Otrzymano sygnał startLoginProcess.")

        self.worker_thread = QtCore.QThread()
        self.worker = LoginWorker(duration=5)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.resultReady.connect(self.on_login_result)
        self.worker.error.connect(self.on_login_error)


        self.worker.resultReady.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker_thread.quit)
        #self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        # Wystartuj wątek (to asynchronicznie wywoła worker.run())
        self.worker_thread.start()
        print("MainWindow: Wątek logowania uruchomiony.")

    def on_login_result(self, success):
        print(f"MainWindow: Otrzymano wynik: {success}")

        self.login_screen.stop_ui_feedback(success=success)

        if success:
            QtCore.QTimer.singleShot(1000, self.show_analysis_screen)
        else:
            pass

    def on_login_error(self, error_message):
        print(f"MainWindow: Otrzymano błąd: {error_message}")
        self.login_screen.show_login_error(error_message)


