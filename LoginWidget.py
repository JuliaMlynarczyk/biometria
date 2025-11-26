from PySide6 import QtWidgets, QtCore, QtGui

class LoginWidget(QtWidgets.QWidget):
    registerClicked = QtCore.Signal()
    startLoginProcess = QtCore.Signal()

    # UI panelu logowania
    def __init__(self):
        super().__init__()

        self.is_recording = False
        self.record_timer = QtCore.QTimer(self)
        self.record_timer.setSingleShot(True)
        self.record_timer.setInterval(5000)  # 5 sekund
        self.record_timer.timeout.connect(self.stop_ui_feedback)

        self.title = QtWidgets.QLabel("Biometry Voice App", alignment=QtCore.Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")

        self.info = QtWidgets.QLabel("Start recording and say <b>Open sesame</b>", alignment=QtCore.Qt.AlignCenter)
        self.info.setWordWrap(True)
        self.info.setStyleSheet("font-size: 16px; color: #555;")

        self.login = QtWidgets.QLabel("Log in",
                                      alignment=QtCore.Qt.AlignCenter)
        self.login.setStyleSheet("font-size: 16px; color: #555;")

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

        self.registerInfo = QtWidgets.QLabel("Don't have an account?", alignment=QtCore.Qt.AlignCenter)
        self.registerInfo.setStyleSheet("font-size: 16px; color: #555;")
        self.buttonRegister = QtWidgets.QPushButton("Register")

        self.error_label = QtWidgets.QLabel("", alignment=QtCore.Qt.AlignCenter)
        self.error_label.setStyleSheet("font-size: 14px; color: red; font-weight: bold;")
        self.error_label.setVisible(False)

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self.title)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.info)
        main_layout.addWidget(self.login)
        main_layout.addSpacing(20)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.buttonRecord)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.error_label)
        main_layout.addStretch()
        main_layout.addWidget(self.registerInfo)
        main_layout.addWidget(self.buttonRegister)

        main_layout.setContentsMargins(50, 50, 50, 50)
        self.setLayout(main_layout)

        self.buttonRegister.clicked.connect(self.registerClicked.emit)
        self.buttonRecord.clicked.connect(self.start_recording)

    # Rozpoczęcie nagrywania
    def start_recording(self):
        if self.is_recording:
            return

        self.is_recording = True
        self.buttonRecord.setEnabled(False)
        self.error_label.setVisible(False)

        self.buttonRecord.setProperty("recording", True)
        self.buttonRecord.style().unpolish(self.buttonRecord)
        self.buttonRecord.style().polish(self.buttonRecord)

        self.record_timer.start()

        self.startLoginProcess.emit()

    # Zakończenie nagrywania
    def stop_ui_feedback(self, success=None):
        self.record_timer.stop()
        self.is_recording = False
        self.buttonRecord.setEnabled(True)

        self.buttonRecord.setProperty("recording", False)
        self.buttonRecord.style().unpolish(self.buttonRecord)
        self.buttonRecord.style().polish(self.buttonRecord)

        if success is False:
            self.show_login_error("No match found.")

    def show_login_error(self, error_message):
        print("LoginWidget: Showing error: " + error_message)
        self.error_label.setText(f"Login failed! {error_message}")
        self.error_label.setStyleSheet("font-size: 14px; color: red; font-weight: bold;")
        self.error_label.setVisible(True)
        self.stop_ui_feedback(success=False)