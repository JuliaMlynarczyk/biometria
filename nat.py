import sounddevice as sd
import numpy as np
import python_speech_features as psf
from scipy.spatial.distance import cosine
import json
import os
import time
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

DATABASE_FILE = "voice_users.json"

# Nagrywanie audio
def record(duration=3, fs=16000):
    print(f"\nNagrywanie ({duration}s, {fs} Hz)...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    print("Nagranie zakończone.")
    return audio.flatten()


# Ekstrakcja cech MFCC
def extract_mfcc(audio, fs=16000):
    mfcc_features = psf.mfcc(audio, samplerate=fs, numcep=26, nfft=512)
    return np.mean(mfcc_features, axis=0)


# Baza użytkowników
def load_database():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_database(database):
    with open(DATABASE_FILE, "w") as f:
        json.dump(database, f, indent=2)


# Porównywanie
def cosine_similarity(a, b):
    return 1 - cosine(a, b)


def identify_user(database, mfcc_vector, threshold=0.8):
    """Zwraca użytkownika z najwyższym dopasowaniem powyżej progu."""
    candidates = []
    for user, data in database.items():
        stored = np.array(data["mfcc"])
        score = cosine_similarity(stored, mfcc_vector)
        if score >= threshold:
            candidates.append((user, score))

    if not candidates:
        return None, 0.0

    # sortowanie po najwyższym score
    best_user, best_score = max(candidates, key=lambda x: x[1])
    return best_user, best_score


# Rejestracja nowego użytkownika
def register_user():
    name = input("\nPodaj nazwę użytkownika: ")
    fs = int(input("Podaj częstotliwość próbkowania (np. 8000, 16000, 44100): "))

    samples = []
    for i in range(3):
        input(f"\nNaciśnij Enter, aby rozpocząć nagrywanie i powiedz hasło 'sprawdź mnie' ({i+1}/3)...")
        audio = record(duration=3, fs=fs)
        mfcc = extract_mfcc(audio, fs)
        samples.append(mfcc)
        time.sleep(1)

    user_mfcc = np.mean(samples, axis=0)

    database = load_database()
    database[name] = {"mfcc": user_mfcc.tolist(), "fs": fs}
    save_database(database)

    print(f"Użytkownik {name} został zapisany w bazie.\n")


# Weryfikacja użytkownika
def verify_user():
    database = load_database()
    if not database:
        print("❌ Brak zapisanych użytkowników! Najpierw zarejestruj kogoś.")
        return

    fs = int(input("Podaj częstotliwość próbkowania do testu (np. 8000, 16000, 44100): "))
    input("\nPowiedz hasło i naciśnij Enter, aby rozpocząć nagrywanie...")
    audio = record(duration=3, fs=fs)
    mfcc = extract_mfcc(audio, fs)

    user, score = identify_user(database, mfcc)

    if user:
        print(f"\n✅ Witaj, {user}! (dopasowanie = {score:.3f})")
    else:
        print(f"\n❌ Nie rozpoznano użytkownika (żaden wynik nie przekroczył progu 0.8).")



# wyświetlanie plot
def visualize_users():
    database = load_database()
    if not database:
        print("❌ Brak użytkowników w bazie!")
        return

    users = list(database.keys())
    vectors = [np.array(database[u]["mfcc"]) for u in users]

    # PCA – redukcja z 13 wymiarów do 2
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(vectors)

    plt.figure(figsize=(7, 5))
    plt.title("Przestrzeń cech głosu użytkowników (PCA 2D)")
    plt.xlabel("Składowa 1 (PC1)")
    plt.ylabel("Składowa 2 (PC2)")

    for i, user in enumerate(users):
        plt.scatter(reduced[i, 0], reduced[i, 1], label=user, s=100)
        plt.text(reduced[i, 0] + 0.02, reduced[i, 1] + 0.02, user, fontsize=10)

    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# clear database
def clear_database():
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
        print("Baza użytkowników została wyczyszczona.")
    else:
        print("Baza już jest pusta.")


# compare components
def compare_mfcc_components():
    database = load_database()
    if not database:
        print("❌ Brak użytkowników w bazie!")
        return

    users = list(database.keys())
    mfccs = [np.array(database[u]["mfcc"]) for u in users]

    plt.figure(figsize=(10, 6))
    plt.title("Porównanie 13 współczynników MFCC między użytkownikami")
    plt.xlabel("Numer współczynnika MFCC")
    plt.ylabel("Wartość")

    for i, user in enumerate(users):
        plt.plot(range(1, len(mfccs[i]) + 1), mfccs[i], marker='o', label=user)

    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()



# --- Menu główne ---
def main():
    while True:
        print("\n=== 🔐 SYSTEM BIOMETRII GŁOSU ===")
        print("1️⃣  Zarejestruj użytkownika")
        print("2️⃣  Zweryfikuj użytkownika")
        print("3️⃣  Zakończ")
        print("4️⃣  Wyczyść bazę użytkowników")
        print("5️⃣  Wizualizuj przestrzeń MFCC użytkowników")
        print("6️⃣  Porównaj współczynniki MFCC między użytkownikami\n")

        choice = input("Wybierz opcję: ")

        if choice == "1":
            register_user()
        elif choice == "2":
            verify_user()
        elif choice == "4":
            clear_database()
        elif choice == "5":
            visualize_users()
        elif choice == "6":
            compare_mfcc_components()
        elif choice == "3":
            print("👋 Do zobaczenia!")
            break
        else:
            print("Nieprawidłowy wybór.")


if __name__ == "__main__":
    main()
