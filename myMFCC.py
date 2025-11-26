'''
#TYLKO MFCC STATYCZNE
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

    mfcc -= (np.mean(mfcc, axis=0) + 1e-8)

    mfcc_mean = np.mean(mfcc, axis=0)
    mfcc_std = np.std(mfcc, axis=0)

    combined_features = np.hstack((mfcc_mean, mfcc_std))

    # jeden wektor reprezentujący głos
    return combined_features
    '''


# MFCC STATYCZNE + DELTY
import numpy as np
from scipy.fftpack import dct

def get_delta_features(feat, N=2):
    # cechy delta (pochodna czasowa) dla wektora cech
    if feat.ndim == 1:
        feat = feat.reshape(-1, 1)

    # padding na krawędziach
    padded = np.pad(feat, ((N, N), (0, 0)), mode='edge')
    frames = []

    for t in range(feat.shape[0]):
        # delta: (wsp.t+N - wsp.t-N) + ... / (2 * sum(n^2))
        numerator = sum([n * padded[t + N + n] for n in range(-N, N + 1)])
        denominator = 2 * sum([n ** 2 for n in range(1, N + 1)])
        frames.append(numerator / denominator)

    return np.array(frames)


def extract_features(signal, fs, num_ceps=13, frame_size=0.025, frame_stride=0.01, nfilt=26, NFFT=512):
    # stare MFCC

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

    # FFT
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

    # DCT – właściwe MFCC
    mfcc = dct(filter_banks, type=2, axis=1, norm='ortho')[:, :num_ceps]
    mfcc -= (np.mean(mfcc, axis=0) + 1e-8)  # Normalizacja MFCC


    # NOWA CZĘŚĆ delta i pochodna delty
    # 1) delta (pochodna czasowa)
    delta_mfcc = get_delta_features(mfcc, N=2)

    # 2) delta-delta (pochodna delty)
    delta2_mfcc = get_delta_features(delta_mfcc, N=2)

    # ŁĄCZENIE I UŚREDNIANIE - obliczanie średniej i odchylenia standard dla MFCC, Delta, Delta-Delta

    # wektor cech 1 (MFCC statyczne)
    mfcc_mean = np.mean(mfcc, axis=0)
    mfcc_std = np.std(mfcc, axis=0)

    # wektor cech 2 (delta - dynamika)
    delta_mean = np.mean(delta_mfcc, axis=0)
    delta_std = np.std(delta_mfcc, axis=0)

    # wektor cech 3 (delta-delta)
    delta2_mean = np.mean(delta2_mfcc, axis=0)
    delta2_std = np.std(delta2_mfcc, axis=0)

    # wektor końcowy 78-elementowy: [MFCC_mean, MFCC_std, Delta_mean, Delta_std, Delta2_mean, Delta2_std]
    combined_features = np.hstack((
        mfcc_mean, mfcc_std,
        delta_mean, delta_std,
        delta2_mean, delta2_std
    ))

    return combined_features
