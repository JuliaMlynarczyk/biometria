from PySide6 import QtWidgets, QtCore, QtGui

class RegisterWidget(QtWidgets.QWidget):
    startRegisterProces = QtCore.Signal(list, str)
    startRecordingAttempt = QtCore.Signal()
    loginClicked = QtCore.Signal()

    # UI rejestracji
    def __init__(self):
        super().__init__()

        self.is_recording = False
        self.progress_step = 0
        self.MAX_STEPS = 5
        self.STYLE_INCOMPLETE = "background-color: #ffaaaa; border: 1px solid #cc0000; border-radius: 4px;"
        self.STYLE_COMPLETE = "background-color: #aaffaa; border: 1px solid #00cc00; border-radius: 4px;"

        self.audio_samples = []

        self.record_timer = QtCore.QTimer(self)
        self.record_timer.setSingleShot(True)
        self.record_timer.setInterval(5500)  # 5 sekund + zapas na przetwarzanie
        self.record_timer.timeout.connect(lambda: self.stop_ui_feedback(success=False))

        self.buttonBack = QtWidgets.QPushButton()
        self.buttonBack.setIcon(QtGui.QIcon("static/home.png"))
        self.buttonBack.setIconSize(QtCore.QSize(32, 32))
        self.buttonBack.setFixedSize(50, 50)
        self.buttonBack.setCursor(QtCore.Qt.PointingHandCursor)
        self.buttonBack.setToolTip("Back to login")
        self.buttonBack.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #f0f0f0;
                        border-radius: 25px;
                    }
                """)
        self.buttonBack.clicked.connect(self.loginClicked.emit)

        self.title = QtWidgets.QLabel("Biometry Voice App", alignment=QtCore.Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")

        self.id_info = QtWidgets.QLabel("Login: ")
        self.id_input = QtWidgets.QLineEdit(self)
        self.id_input.setPlaceholderText("Login...")
        self.id_input.setMaximumWidth(100)

        self.login_error_label = QtWidgets.QLabel("", alignment=QtCore.Qt.AlignCenter)
        self.login_error_label.setStyleSheet("font-size: 14px; color: red;")
        self.login_error_label.setVisible(False)

        self.progress = QtWidgets.QLabel(
            f"Start recording (Step {self.progress_step + 1} from {self.MAX_STEPS})<br>and say <b>Open sesame</b>",
            alignment=QtCore.Qt.AlignCenter)
        self.progress.setWordWrap(True)
        self.progress.setStyleSheet("font-size: 16px; color: #555;")

        self.progress_layout = QtWidgets.QHBoxLayout()
        self.progress_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_indicators = []
        for _ in range(self.MAX_STEPS):
            indicator = QtWidgets.QLabel("")
            indicator.setFixedSize(50, 15)
            indicator.setStyleSheet(self.STYLE_INCOMPLETE)
            self.progress_indicators.append(indicator)
            self.progress_layout.addWidget(indicator)

        self.BUTTON_DIAMETER = 80
        self.buttonRecord = QtWidgets.QPushButton("")
        icon = QtGui.QIcon("static/microphone_icon.png")
        self.buttonRecord.setIcon(icon)
        self.buttonRecord.setIconSize(QtCore.QSize(48, 48))
        self.buttonRecord.setFixedSize(self.BUTTON_DIAMETER, self.BUTTON_DIAMETER)
        self.buttonRecord.setStyleSheet(f"""
                            QPushButton {{
                                border-radius: {self.BUTTON_DIAMETER / 2}px; /* Połowa z 80 = 40px */
                                border: 2px solid #ccc;
                                background-color: #f5f5f5;
                            }}
                            QPushButton:hover {{
                                background-color: #e9e9e9;
                                border: 2px solid #aaa;
                            }}
                            QPushButton:pressed {{
                                background-color: #ddd;
                            }}
                            QPushButton[recording="true"] {{
                            background-color: #ffe0e0; border: 3px solid #ff0000;
                            }}
                        """)

        self.buttonLogin = QtWidgets.QPushButton("Log in")
        self.buttonLogin.setStyleSheet("""
                    QPushButton {
                        font-size: 16px;
                        font-weight: bold;
                        color: white;
                        background-color: #007bff;
                        border: none;
                        padding: 10px 0;
                        border-radius: 5px;
                    }
                    QPushButton:hover { background-color: #0056b3; }
                    QPushButton:pressed { background-color: #004085; }
                """)
        self.buttonLogin.setMinimumSize(120, 40)
        self.buttonLogin.setVisible(False)
        self.buttonLogin.clicked.connect(self.loginClicked.emit)

        main_layout = QtWidgets.QVBoxLayout()

        top_bar_layout = QtWidgets.QHBoxLayout()
        top_bar_layout.addWidget(self.buttonBack)
        top_bar_layout.addStretch()

        main_layout.addLayout(top_bar_layout)

        main_layout.addWidget(self.title)
        main_layout.addSpacing(10)

        id_layout = QtWidgets.QHBoxLayout()
        id_layout.addWidget(self.id_info, alignment=QtCore.Qt.AlignRight)
        id_layout.addWidget(self.id_input, alignment=QtCore.Qt.AlignLeft)
        main_layout.addLayout(id_layout)

        main_layout.addWidget(self.login_error_label)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.progress)
        main_layout.addSpacing(15)
        main_layout.addLayout(self.progress_layout)
        main_layout.addSpacing(20)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.buttonRecord)
        button_layout.addWidget(self.buttonLogin)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        main_layout.setContentsMargins(50, 50, 50, 50)
        self.setLayout(main_layout)

        self.buttonRecord.clicked.connect(self.start_recording)

    # Rozpoczęcie nagrywania
    def start_recording(self):
        if self.is_recording:
            return

        user_login = self.id_input.text().strip()

        if not user_login:
            self.login_error_label.setText("Login cannot be empty.")
            self.login_error_label.setVisible(True)
            return

        self.login_error_label.setVisible(False)

        if self.progress_step >= self.MAX_STEPS:
            self.progress.setText("<b>Register successful!</b>")
            return

        self.is_recording = True
        self.buttonRecord.setEnabled(False)

        self.buttonRecord.setProperty("recording", True)
        self.buttonRecord.style().unpolish(self.buttonRecord)
        self.buttonRecord.style().polish(self.buttonRecord)

        self.progress.setText("Recording...")
        self.record_timer.start()

        self.startRecordingAttempt.emit()

    # Zakończenie nagrywania
    def stop_ui_feedback(self, success=None, audio_data=None):
        if not self.is_recording:
            return

        self.record_timer.stop()
        self.is_recording = False
        self.buttonRecord.setEnabled(True)

        self.buttonRecord.setProperty("recording", False)
        self.buttonRecord.style().unpolish(self.buttonRecord)
        self.buttonRecord.style().polish(self.buttonRecord)

        if success is True:
            if self.progress_step < self.MAX_STEPS:
                self.progress_indicators[self.progress_step].setStyleSheet(self.STYLE_COMPLETE)
                self.progress_step += 1

                if audio_data is not None:
                    self.audio_samples.append(audio_data)
                    print(f"RegisterWidget: Zapisano próbkę {self.progress_step}/{self.MAX_STEPS}")

            if self.progress_step == self.MAX_STEPS:
                self.progress.setText("<b>Processing...</b>")
                self.buttonRecord.setVisible(False)
                self.buttonLogin.setVisible(True)
                self.buttonLogin.setEnabled(False)

                user_login = self.id_input.text().strip()
                self.startRegisterProces.emit(self.audio_samples, user_login)
            else:
                self.progress.setText(
                    f"Success! (Step {self.progress_step + 1} z {self.MAX_STEPS})<br>Press to record again.")

        elif success is False:
            self.progress.setText(f"Rocording failed. (Step {self.progress_step + 1} z {self.MAX_STEPS})<br>Try again.")

        else:
            self.progress.setText(
                f"Timeout. (Step {self.progress_step + 1} z {self.MAX_STEPS})<br>Try again.")

    # Czyszczenie postępu przed kolejną rejestracją
    def reset_progress(self):
        self.progress_step = 0
        self.audio_samples.clear()
        self.id_input.clear()
        for indicator in self.progress_indicators:
            indicator.setStyleSheet(self.STYLE_INCOMPLETE)

        self.progress.setText(
            f"Start recording (Step {self.progress_step + 1} from {self.MAX_STEPS})<br>and say <b>Open sesame</b>")

        self.buttonRecord.setEnabled(True)
        self.buttonRecord.setVisible(True)
        self.buttonLogin.setVisible(False)
        self.buttonLogin.setEnabled(True)
        self.buttonLogin.setText("Log in")

    def show_login_error(self, error_message):
        print("MainWindow: Login error" + error_message)

    def on_final_registration_result(self, success, message=None):
        self.buttonLogin.setEnabled(True)

        if success:
            self.progress.setText("<b>Register successful!</b><br>You can login now.")
            self.audio_samples.clear()
        else:
            self.progress.setText(f"<b>Registration failed!</b><br>{message}")
            self.buttonLogin.setText("Back to Login")

