import io
from PySide6 import QtWidgets, QtCore, QtGui
import matplotlib.pyplot as plt
import numpy as np
import myMFCC

plt.style.use('default')

class AnalysisWidget(QtWidgets.QWidget):
    logOut = QtCore.Signal()
    startAnalysisRecording = QtCore.Signal(int)

    def __init__(self):
        super().__init__()

        self.signals_data = {}
        self.is_recording = False
        self.record_timer = QtCore.QTimer(self)
        self.record_timer.setSingleShot(True)
        self.record_timer.setInterval(2500)
        self.record_timer.timeout.connect(lambda: self.stop_ui_feedback(None))

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Lewy panel
        controls_widget = QtWidgets.QWidget()
        controls_layout = QtWidgets.QVBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(15)

        self.title = QtWidgets.QLabel("Hello, User")
        self.title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        controls_layout.addWidget(self.title, alignment=QtCore.Qt.AlignTop)

        # Sekcja nagrywania
        recording_group_box = QtWidgets.QGroupBox("1. Select Sampling Rate for Recording")
        recording_layout = QtWidgets.QVBoxLayout()
        self.radio_8k = QtWidgets.QRadioButton("8000 Hz")
        self.radio_16k = QtWidgets.QRadioButton("16000 Hz")
        self.radio_44k = QtWidgets.QRadioButton("44100 Hz")
        self.radio_44k.setChecked(True)
        self.sampling_rate_group = QtWidgets.QButtonGroup(self)
        self.sampling_rate_group.addButton(self.radio_8k, 8000)
        self.sampling_rate_group.addButton(self.radio_16k, 16000)
        self.sampling_rate_group.addButton(self.radio_44k, 44100)
        recording_layout.addWidget(self.radio_8k)
        recording_layout.addWidget(self.radio_16k)
        recording_layout.addWidget(self.radio_44k)
        recording_group_box.setLayout(recording_layout)
        controls_layout.addWidget(recording_group_box)

        # Przycisk nagrywania
        self.BUTTON_DIAMETER = 80
        self.buttonRecord = QtWidgets.QPushButton("")
        icon = QtGui.QIcon("static/microphone_icon.png")
        self.buttonRecord.setIcon(icon)
        self.buttonRecord.setIconSize(QtCore.QSize(48, 48))
        self.buttonRecord.setFixedSize(self.BUTTON_DIAMETER, self.BUTTON_DIAMETER)
        self.buttonRecord.setStyleSheet(f"""
                    QPushButton {{
                        border-radius: {self.BUTTON_DIAMETER / 2}px;
                        border: 2px solid #ccc;
                        background-color: #f5f5f5;
                    }}
                    QPushButton:hover {{ background-color: #e9e9e9; border: 2px solid #aaa; }}
                    QPushButton:pressed {{ background-color: #ddd; }}
                    QPushButton[recording="true"] {{ background-color: #ffe0e0; border: 3px solid #ff0000; }}
                """)
        self.buttonRecord.clicked.connect(self.start_recording)

        btn_cont = QtWidgets.QHBoxLayout()
        btn_cont.addStretch()
        btn_cont.addWidget(self.buttonRecord)
        btn_cont.addStretch()
        controls_layout.addLayout(btn_cont)

        # Sekcja wykresu nagrań
        plot_group_box = QtWidgets.QGroupBox("2. Raw Signal Analysis")
        plot_layout = QtWidgets.QVBoxLayout()
        self.cb_plot_8k = QtWidgets.QCheckBox("8000 Hz")
        self.cb_plot_16k = QtWidgets.QCheckBox("16000 Hz")
        self.cb_plot_44k = QtWidgets.QCheckBox("44100 Hz")
        plot_layout.addWidget(self.cb_plot_8k)
        plot_layout.addWidget(self.cb_plot_16k)
        plot_layout.addWidget(self.cb_plot_44k)
        self.buttonPlot = QtWidgets.QPushButton("Plot Raw Signals")
        self.buttonPlot.setStyleSheet("background-color: #007bff; color: white; padding: 5px;")
        self.buttonPlot.clicked.connect(self.update_plot)
        plot_layout.addWidget(self.buttonPlot)
        plot_group_box.setLayout(plot_layout)
        controls_layout.addWidget(plot_group_box)

        # Sekcja wykresów cech
        features_group = QtWidgets.QGroupBox("3. Feature Comparison")
        features_layout = QtWidgets.QVBoxLayout()
        self.feature_btn_group = QtWidgets.QButtonGroup(self)
        self.feature_btn_group.setExclusive(True)
        self.cb_mfcc = QtWidgets.QCheckBox("MFCC (Avg Magnitude)")
        self.cb_zcr = QtWidgets.QCheckBox("Zero-Crossing Rate")
        self.cb_centroid = QtWidgets.QCheckBox("Spectral Centroid (Mean)")
        self.cb_mfcc.setChecked(True)
        self.feature_btn_group.addButton(self.cb_mfcc)
        self.feature_btn_group.addButton(self.cb_zcr)
        self.feature_btn_group.addButton(self.cb_centroid)
        features_layout.addWidget(self.cb_mfcc)
        features_layout.addWidget(self.cb_zcr)
        features_layout.addWidget(self.cb_centroid)
        self.buttonFeatures = QtWidgets.QPushButton("Compare Features (Bar Plot)")
        self.buttonFeatures.setStyleSheet("background-color: #28a745; color: white; padding: 5px; font-weight: bold;")
        self.buttonFeatures.clicked.connect(self.generate_feature_plot)  # New function
        features_layout.addWidget(self.buttonFeatures)

        features_group.setLayout(features_layout)
        controls_layout.addWidget(features_group)

        controls_layout.addStretch()

        # Wylogowanie
        self.buttonLogout = QtWidgets.QPushButton("Log Out")
        self.buttonLogout.clicked.connect(self.logOut.emit)
        controls_layout.addWidget(self.buttonLogout)

        # Prawy panel - wykres
        self.graph_placeholder = QtWidgets.QLabel("Record signals and select an action.")
        self.graph_placeholder.setAlignment(QtCore.Qt.AlignCenter)
        self.graph_placeholder.setMinimumSize(400, 300)
        self.graph_placeholder.setStyleSheet("background-color: #fafafa; border: 1px solid #ddd;")

        main_layout.addWidget(controls_widget, 1)
        main_layout.addWidget(self.graph_placeholder, 2)

    # Ustalenie użytkownika
    def set_user(self, user_id):
        self.title.setText(f"Hello, {user_id}" if user_id else "Hello, User")

    # Rozpoczęcie nagrywania
    def start_recording(self):
        if self.is_recording: return
        self.is_recording = True
        self.buttonRecord.setEnabled(False)
        self.buttonRecord.setProperty("recording", True)
        self.buttonRecord.style().unpolish(self.buttonRecord)
        self.buttonRecord.style().polish(self.buttonRecord)
        self.record_timer.start()
        selected_fs = self.sampling_rate_group.checkedId()
        self.startAnalysisRecording.emit(selected_fs)

    # Zatrzymanie nagrywania
    def stop_ui_feedback(self, success):
        if not self.is_recording: return
        self.record_timer.stop()
        self.is_recording = False
        self.buttonRecord.setEnabled(True)
        self.buttonRecord.setProperty("recording", False)
        self.buttonRecord.style().unpolish(self.buttonRecord)
        self.buttonRecord.style().polish(self.buttonRecord)
        if success:
            self.graph_placeholder.setText("Recording saved!\nUse 'Plot' buttons to view.")
        elif success is False:
            self.graph_placeholder.setText("Silence detected or Error.\nTry speaking louder.")
        else:
            self.graph_placeholder.setText("Timeout.")

    def receive_recording_data(self, audio_data, sample_rate):
        self.signals_data[sample_rate] = audio_data
        self.stop_ui_feedback(success=True)

        # Automatyczne zaznaczanie po nagraniu
        if sample_rate == 8000:
            self.cb_plot_8k.setChecked(True)
        elif sample_rate == 16000:
            self.cb_plot_16k.setChecked(True)
        elif sample_rate == 44100:
            self.cb_plot_44k.setChecked(True)

    # Tworzenie wykresu
    def update_plot(self):
        print("AnalysisWidget: Plotting raw signals...")
        try:
            plt.figure(figsize=(8, 6))
            plot_colors = {8000: '#FFC0CB', 16000: '#7FFFD4', 44100: '#C875C4'}
            has_data = False

            # normalizacja
            def get_norm(sig):
                m = np.max(np.abs(sig))
                return sig / m if m > 0 else sig

            for fs, color in plot_colors.items():
                # Pobranie odpowiednich check-boxow
                cb = {8000: self.cb_plot_8k, 16000: self.cb_plot_16k, 44100: self.cb_plot_44k}[fs]

                if cb.isChecked() and fs in self.signals_data:
                    sig = self.signals_data[fs]
                    t = np.arange(len(sig)) / fs # dodanie osi czasu
                    plt.plot(t, get_norm(sig), label=f'{fs} Hz', color=color, alpha=0.7)

                    has_data = True

            if has_data:
                plt.title("Signal Comparison (VAD Processed)")
                plt.xlabel("Sample Index")
                plt.ylabel("Normalized Amplitude")
                plt.legend()
                plt.grid(True)

            else:
                plt.text(0.5, 0.5, "No data selected.", ha='center', va='center')

            self._render_plot_to_label()
        except Exception as e:
            print(f"Plot Error: {e}")
            self.graph_placeholder.setText(f"Error: {e}")

    # Obliczanie Zero-Crossing Rate
    def calculate_zcr(self, signal):
        # Zero-Crossing Rate = przejścia przez zero / wszystkie próbki
        zero_crossings = np.nonzero(np.diff(np.sign(signal)))[0]
        return len(zero_crossings) / len(signal)

    # Obliczanie Spectral Centroid - srednia czestotliosc
    def calculate_centroid(self, signal, fs):
        magnitude = np.abs(np.fft.rfft(signal))
        freqs = np.fft.rfftfreq(len(signal), d=1.0 / fs)

        if np.sum(magnitude) == 0: return 0
        return np.sum(freqs * magnitude) / np.sum(magnitude)

    # Obliczanie calosciowego MFCC
    def calculate_mfcc_score(self, signal, fs):

        try:
            mfcc_vector = myMFCC.extract_features(signal, fs)
            return np.linalg.norm(mfcc_vector)
        except Exception as e:
            print(f"MFCC Error: {e}")
            return 0

    # Tworzenie wykresu cech
    def generate_feature_plot(self):
        print("AnalysisWidget: Generating feature comparison bar chart...")
        try:
            available_fs = [fs for fs in [8000, 16000, 44100] if fs in self.signals_data]

            if not available_fs:
                self.graph_placeholder.setText("No recordings available to compare.")
                return

            plt.figure(figsize=(8, 6))

            values = []
            labels = []
            colors = []
            color_map = {8000: '#FFC0CB', 16000: '#7FFFD4', 44100: '#C875C4'}

            feature_name = "Feature"

            is_mfcc = self.cb_mfcc.isChecked()
            is_zcr = self.cb_zcr.isChecked()
            is_cent = self.cb_centroid.isChecked()

            for fs in available_fs:
                sig = self.signals_data[fs]
                val = 0

                if is_mfcc:
                    feature_name = "MFCC (Vector Norm)"
                    val = self.calculate_mfcc_score(sig, fs)
                elif is_zcr:
                    feature_name = "Zero-Crossing Rate"
                    val = self.calculate_zcr(sig)
                elif is_cent:
                    feature_name = "Spectral Centroid (Hz)"
                    val = self.calculate_centroid(sig, fs)

                values.append(val)
                labels.append(f"{fs} Hz")
                colors.append(color_map.get(fs, 'gray'))


            bars = plt.bar(labels, values, color=colors, alpha=0.8)

            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width() / 2., height,
                         f'{height:.2f}', ha='center', va='bottom')

            plt.title(f"Feature Comparison: {feature_name}")
            plt.ylabel("Feature Value")
            plt.xlabel("Sampling Rate")
            plt.grid(axis='y', linestyle='--', alpha=0.7)

            self._render_plot_to_label()

        except Exception as e:
            print(f"Feature Plot Error: {e}")
            self.graph_placeholder.setText(f"Error plotting features:\n{e}")

    def _render_plot_to_label(self):
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(buf.read())
        self.graph_placeholder.setPixmap(pixmap.scaled(
            self.graph_placeholder.size(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        ))
        buf.close()
        plt.close()