import os
from collections import Counter
import numpy as np
import mido
from music21 import converter, chord, key, note
import pandas as pd


# ----------- FUNZIONI DI ANALISI -----------

def extract_chords(midi_file):
    score = converter.parse(midi_file)
    chords_list = []
    for element in score.recurse().notesAndRests:
        if isinstance(element, chord.Chord):
            chords_list.append(tuple(sorted(p.nameWithOctave for p in element.pitches)))
    return chords_list


def chord_coverage(chords):
    if len(chords) == 0:
        return 0
    return len(set(chords)) / len(chords)


def chord_entropy(chords):
    if len(chords) == 0:
        return 0
    counts = Counter(chords)
    probs = np.array(list(counts.values())) / len(chords)
    return -np.sum(probs * np.log2(probs))


def tonal_compliance(chords, tonic='C#', mode='minor'):
    k = key.Key(tonic, mode)
    tonic_pcs = set(p.pitchClass for p in k.pitches)
    compliant_count = 0
    for c in chords:
        chord_pcs = set(p.midi % 12 for p in chord.Chord(c).pitches)
        if chord_pcs.issubset(tonic_pcs):
            compliant_count += 1
    if len(chords) == 0:
        return 0
    return compliant_count / len(chords)


def harmonic_rhythm(chords, total_bars):
    if total_bars == 0:
        return 0
    changes = sum(1 for i in range(1, len(chords)) if chords[i] != chords[i - 1])
    return changes / total_bars


def ambitus(midi_file):
    score = converter.parse(midi_file)
    pitches = []
    for element in score.recurse().notes:
        if isinstance(element, note.Note):
            pitches.append(element.pitch.midi)
        elif isinstance(element, chord.Chord):
            pitches.extend(p.midi for p in element.pitches)

    if not pitches:
        return 0
    return max(pitches) - min(pitches)


# ----------- ANALISI CARTELLA MIDI -----------

def analyze_midi_folder(folder_path, out_csv="ChordsStatsTemp.csv"):
    results = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".mid", ".midi")):
            path = os.path.join(folder_path, filename)
            chords = extract_chords(path)

            # Stima delle battute (fallback se non c’è time signature)
            try:
                midi_file = mido.MidiFile(path)
                total_bars = max(1, int(midi_file.length / (4 * 60 / midi_file.ticks_per_beat)))
            except:
                total_bars = max(1, len(chords) // 4)

            coverage = chord_coverage(chords)
            entropy = chord_entropy(chords)
            compliance = tonal_compliance(chords)
            hr = harmonic_rhythm(chords, total_bars)
            amb = ambitus(path)

            results.append({
                "File": filename,
                "Chord Coverage": coverage,
                "Chord Entropy": entropy,
                "Tonal Compliance": compliance,
                "Harmonic Rhythm": hr,
                "Ambitus": amb
            })

    # Salva CSV
    df = pd.DataFrame(results)
    df.to_csv(out_csv, index=False)

    # Calcola medie delle metriche
    mean_metrics = df.mean(numeric_only=True).to_dict()

    print("\n--- Medie delle metriche ---")
    for k, v in mean_metrics.items():
        print(f"{k}: {v:.4f}")

    return df, mean_metrics


# ----------- ESEMPIO DI USO -----------

if __name__ == "__main__":
    folder = r"C:\Users\Daniele\PycharmProjects\MIDI converter\FInalApplication"
    analyze_midi_folder(folder)
