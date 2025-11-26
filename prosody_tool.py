import numpy as np

# Obliczanie energii sygnału
def calculate_energy(signal):
    if len(signal) == 0:
        return 0
    return np.sqrt(np.mean(signal ** 2))

# Częstotliwość z wykorzystaniem autokorelacji
def calculate_pitch_autocorr(signal, fs):

    # Parametry dla glosu ludzkiego Hz
    min_freq = 50
    max_freq = 500

    # Pre-processing
    limit = np.max(np.abs(signal)) * 0.3
    clipped_signal = np.copy(signal)
    clipped_signal[np.abs(clipped_signal) < limit] = 0

    # Autokorelacja
    corr = np.correlate(clipped_signal, clipped_signal, mode='full')
    corr = corr[len(corr) // 2:]  # Keep only positive lags

    min_lag = int(fs / max_freq)
    max_lag = int(fs / min_freq)

    if max_lag >= len(corr):
        max_lag = len(corr) - 1

    search_region = corr[min_lag:max_lag]

    if len(search_region) == 0:
        return 0

    peak_idx = np.argmax(search_region) + min_lag

    if peak_idx == 0:
        return 0

    pitch_hz = fs / peak_idx
    return pitch_hz


def extract_prosodic_features(signal, fs):
    energy = calculate_energy(signal)
    pitch = calculate_pitch_autocorr(signal, fs)

    return np.array([pitch, energy])