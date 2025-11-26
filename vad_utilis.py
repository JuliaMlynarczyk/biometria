import numpy as np


def trim_silence_and_validate(audio_data, sample_rate,
# PRÓG WZGLĘDNY 0.05. - wymaga to, aby energia mowy była co najmniej 5% maksymalnej energii szumu/mowy, aby uznać ramkę za mowe
                              threshold_factor=0.05,
# MINIMALNA DŁUGOŚĆ MOWY 1.0s. - odrzuca bardzo krótkie fragmenty
                              min_speech_duration_sec=1.0,
                              min_speech_frames=10):
    ABSOLUTE_MIN_THRESHOLD = 1e-6

    signal = audio_data.flatten()
    FRAME_SIZE_MS = 20  # 20 ms ramki
    FRAME_SIZE = int(sample_rate * FRAME_SIZE_MS / 1000)

    if len(signal) < FRAME_SIZE * min_speech_frames:
        print("VAD_UTIL: Sygnał jest za krótki na analizę VAD.")
        return None

    # Sprawdzenie energii sygnału
    energy = np.array([
        np.sum(signal[i:i + FRAME_SIZE] ** 2)
        for i in range(0, len(signal) - FRAME_SIZE + 1, FRAME_SIZE)
    ])

    # KONTROLA BEZWZGLĘDNA na * 500, aby odrzucać bardzo ciche nagrania
    if np.max(energy) < ABSOLUTE_MIN_THRESHOLD * 500:
        print("VAD_UTIL: Maksymalna energia nagrania jest zbyt niska (cisza/szum tła). Odrzucam.")
        return None

    vad_threshold = threshold_factor * np.max(energy)

    # czy na pewno że próg VAD  nie jest zbyt niski
    vad_threshold = max(vad_threshold, ABSOLUTE_MIN_THRESHOLD)

    speech_frames_indices = np.where(energy > vad_threshold)[0]

    # co najmniej 10 ramek (czyli min. 200ms) ma energię powyżej rygorystycznego progu 0.05 * E_max.
    if len(speech_frames_indices) < min_speech_frames:
        print("VAD_UTIL: Zbyt ciche nagranie lub zbyt krótka mowa. Odrzucam (VAD_FAILED).")
        return None

    start_frame = speech_frames_indices[0]
    end_frame = speech_frames_indices[-1] + 1

    start_sample = start_frame * FRAME_SIZE
    end_sample = min(end_frame * FRAME_SIZE, len(signal))

    speech_segment = signal[start_sample:end_sample]

    # WARUNEK MINIMALNEJ DŁUGOŚCI
    if len(speech_segment) < sample_rate * min_speech_duration_sec:
        # odrzuca segmenty, które są krótsze niż 1 sekunda mowy
        print(
            f"VAD_UTIL: Wykryto mowę, ale jest za krótka ({len(speech_segment) / sample_rate:.2f}s). Odrzucam (VAD_FAILED).")
        return None

    return speech_segment