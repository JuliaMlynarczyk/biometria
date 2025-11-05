import numpy as np
from scipy.fftpack import dct

def extract_features(signal, fs, num_ceps=13, frame_size=0.025, frame_stride=0.01, nfilt=26, NFFT=512):
    # pre-emfaza
    emphasized = np.append(signal[0], signal[1:] - 0.97 * signal[:-1])

    # podział na ramki
    frame_len = int(round(frame_size * fs))
    frame_step = int(round(frame_stride * fs))
    signal_len = len(emphasized)
    num_frames = int(np.ceil(float(np.abs(signal_len - frame_len)) / frame_step))

    pad_signal_len = num_frames * frame_step + frame_len
    z = np.zeros((pad_signal_len - signal_len))
    pad_signal = np.append(emphasized, z)

    indices = np.tile(np.arange(0, frame_len), (num_frames, 1)) + \
              np.tile(np.arange(0, num_frames * frame_step, frame_step), (frame_len, 1)).T
    frames = pad_signal[indices.astype(np.int32, copy=False)]

    # okno hamminga - wygładzenie brzegów żeby nie mieć skoków fft
    frames *= np.hamming(frame_len)

    # FFT - przejście z czasu do częstotliwości.
    mag_frames = np.absolute(np.fft.rfft(frames, NFFT))
    pow_frames = ((1.0 / NFFT) * (mag_frames ** 2))

    # filtry mel
    low_mel = 0
    high_mel = 2595 * np.log10(1 + (fs / 2) / 700)
    mel_points = np.linspace(low_mel, high_mel, nfilt + 2)
    hz_points = 700 * (10 ** (mel_points / 2595) - 1)
    bins = np.floor((NFFT + 1) * hz_points / fs)

    fbank = np.zeros((nfilt, int(np.floor(NFFT / 2 + 1))))
    for m in range(1, nfilt + 1):
        f_m_minus = int(bins[m - 1])
        f_m = int(bins[m])
        f_m_plus = int(bins[m + 1])

        for k in range(f_m_minus, f_m):
            fbank[m - 1, k] = (k - bins[m - 1]) / (bins[m] - bins[m - 1])
        for k in range(f_m, f_m_plus):
            fbank[m - 1, k] = (bins[m + 1] - k) / (bins[m + 1] - bins[m])

    filter_banks = np.dot(pow_frames, fbank.T)
    filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
    filter_banks = 20 * np.log10(filter_banks)

    # DCT – właściwe MFCC - kompresuje widmo do kilku współczynników
    mfcc = dct(filter_banks, type=2, axis=1, norm='ortho')[:, :num_ceps]

    # Uśrednienie po ramkach - jeden wektor reprezentujący głos
    return np.mean(mfcc, axis=0)
