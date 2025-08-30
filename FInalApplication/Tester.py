import os
import numpy as np
import pandas as pd
from collections import Counter
import math
from music21 import converter, note, chord


# --- FUNZIONI DI SUPPORTO ---

def classify_duration(d):
    """Arrotonda la durata ai valori standard."""
    standard = [4.0, 2.0, 1.0, 0.5, 0.25, 0.125]
    return min(standard, key=lambda x: abs(x - d))


def entropy_distribution(distribution):
    """Entropia di Shannon di una distribuzione di valori."""
    total = sum(distribution.values())
    probs = [v / total for v in distribution.values() if total > 0]
    return -sum(p * math.log2(p) for p in probs if p > 0)


def duration_distribution(durations):
    counts = Counter(durations)
    total = sum(counts.values())
    return {d: counts[d] / total for d in counts}


def ambitus(notes):
    return max(notes) - min(notes) if notes else 0


def note_entropy(notes):
    counts = Counter(notes)
    return entropy_distribution(counts)


def interval_stats(notes):
    intervals = [abs(notes[i + 1] - notes[i]) for i in range(len(notes) - 1)]
    return {
        "mean_interval": np.mean(intervals) if intervals else 0,
        "std_interval": np.std(intervals) if intervals else 0,
        "interval_counts": dict(Counter(intervals))
    }


def ngram_repetition(notes, n=3):
    ngrams = [tuple(notes[i:i + n]) for i in range(len(notes) - n + 1)]
    counts = Counter(ngrams)
    repeated = sum(1 for v in counts.values() if v > 1)
    return repeated / len(ngrams) if ngrams else 0


def melodic_contour(notes):
    contour = [np.sign(notes[i + 1] - notes[i]) for i in range(len(notes) - 1)]
    asc = sum(1 for c in contour if c > 0)
    desc = sum(1 for c in contour if c < 0)
    zero = sum(1 for c in contour if c == 0)
    return {"ascending": asc, "descending": desc, "repeated": zero}


def tonal_compliance(notes, key_notes=[1, 3, 4, 6, 8, 9, 11]):
    """Percentuale di note che appartengono alla scala di C# minore naturale."""
    if not notes:
        return 0
    in_key = sum(1 for n in notes if n % 12 in key_notes)
    return in_key / len(notes)


# --- FUNZIONE PER STAMPARE NOTE ---
def print_midi_notes(score, file_path):
    print(f"\nFile analizzato: {file_path}\n")
    print(f"{'Offset':<10}{'Pitch':<10}{'MIDI':<10}{'Duration':<10}")
    print("-" * 50)

    for el in score.recurse().notesAndRests:
        if isinstance(el, note.Note):
            print(f"{el.offset:<10}{el.name:<10}{el.pitch.midi:<10}{el.quarterLength:<10}")
        elif isinstance(el, chord.Chord):
            notes_str = " ".join(n.name for n in el.notes)
            print(f"{el.offset:<10}{notes_str:<10}{'Chord':<10}{el.quarterLength:<10}")
        else:
            print(f"{el.offset:<10}{'Rest':<10}{'-':<10}{el.quarterLength:<10}")


# --- ESTRAZIONE FEATURE ---

def extract_features(file_path):
    try:
        score = converter.parse(file_path)
        print(" That is the score")
        # Stampa le note del file
        print_midi_notes(score, file_path)

        notes, durations = [], []

        for el in score.recurse().notes:
            if isinstance(el, note.Note):
                notes.append(el.pitch.midi)
                durations.append(classify_duration(el.quarterLength))

        if not notes:
            return None

        # --- Metriche richieste ---
        amb = ambitus(notes)
        pitch_ent = note_entropy(notes)
        intervals = interval_stats(notes)
        ngram_rep = ngram_repetition(notes, n=3)
        contour = melodic_contour(notes)
        tonal_comp = tonal_compliance(notes)
        dist_dur = duration_distribution(durations)

        features = {
            "File": os.path.basename(file_path),
            "Ambitus (Range)": amb,
            "Pitch Entropy": pitch_ent,
            "Motif Repetition (3-gram)": ngram_rep,
            "Melodic Contour - Ascending": contour["ascending"],
            "Melodic Contour - Descending": contour["descending"],
            "Melodic Contour - Repeated": contour["repeated"],
            "Tonal Compliance": tonal_comp,
            "Intervals - Mean": intervals["mean_interval"],
            "Intervals - Std": intervals["std_interval"],
        }

        # Aggiungi distribuzione delle durate con nomi chiari
        for dur, perc in dist_dur.items():
            features[f"Note Duration Distribution ({dur})"] = perc

        return features

    except Exception as e:
        return {"File": os.path.basename(file_path), "Error": str(e)}


# --- ANALISI CARTELLA MIDI ---

def analyze_midi_folder(folder_path, save_csv=True, out_file="Chords Stats Qwen.csv"):
    results = []
    for fname in os.listdir(folder_path):
        if fname.lower().endswith((".mid", ".midi")):
            feat = extract_features(os.path.join(folder_path, fname))
            if feat:
                results.append(feat)

    df = pd.DataFrame(results)

    # Salva CSV per plottaggi futuri
    if save_csv:
        df.to_csv(out_file, index=False)

    # Calcola media e deviazione standard delle metriche numeriche
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    summary = pd.DataFrame({
        "Mean": df[numeric_cols].mean(),
        "Std": df[numeric_cols].std()
    })

    return df, summary


# --- USO ---
df, summary = analyze_midi_folder(
    r"C:\Users\Daniele\PycharmProjects\MIDI converter\FInalApplication",
    save_csv=True,
    out_file="QwenTestMelody.csv"
)

print("\nTabella completa (prime 5 righe):")
print(df.head())
print("\nStatistiche di sintesi (media e std):")
print(summary)
