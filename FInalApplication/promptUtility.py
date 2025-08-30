import mido
from mido import MidiFile, MidiTrack, Message
import requests
import json


# Endpoint LM Studio

LM_API_URL = "http://127.0.0.1:1234/v1/chat/completions"
headers = {"Content-Type": "application/json"}

# Mappatura note -> numero MIDI
note_map = {
    'C': 0, 'C#': 1, 'C♯': 1, 'Db': 1, 'D♭': 1,
    'D': 2, 'D#': 3, 'D♯': 3, 'Eb': 3, 'E♭': 3,
    'E': 4, 'Fb': 4, 'F♭': 4, 'E#': 5, 'E♯': 5,
    'F': 5, 'F#': 6, 'F♯': 6, 'Gb': 6, 'G♭': 6,
    'G': 7, 'G#': 8, 'G♯': 8, 'Ab': 8, 'A♭': 8,
    'A': 9, 'A#': 10, 'A♯': 10, 'Bb': 10, 'B♭': 10,
    'B': 11, 'Cb': 11, 'C♭': 11, 'B#': 0, 'B♯': 0
}

def clean_note(note_str):
    """
    Pulisce la nota da caratteri indesiderati e assegna l'ottava di default 4 se manca.
    """
    print("BEFORE FIX ", note_str)
    temp = note_str.strip().replace('/', '').replace('"', '').replace("'", "")

    # Se non contiene numero alla fine, aggiungi ottava 4
    if not any(c.isdigit() for c in temp):
        temp += "4"

    print("AFTER FIX", temp)
    return temp

def note_to_midi(note_str):
    note_str = clean_note(note_str)
    if len(note_str) == 2:
        name = note_str[0]
        print(name)
        octave = int(note_str[1])
        print(octave)
    elif len(note_str) == 3:
        name = note_str[0:2]
        print(name)
        octave = int(note_str[2])
        print(octave)
    else:
        raise ValueError(f"Invalid note {note_str}")
    return 12 * (octave + 1) + note_map[name] - 12

def sendPrompt(prompt):
    print(prompt)

    data = {
        "model": "qwen/qwen3-4b-2507",
        "messages": [
            {"role": "user", "content": prompt}  # solo un messaggio
        ],
        "max_tokens": 10000
    }

    # Chiamata POST, già restituisce dict
    response = requests.post(LM_API_URL, json=data).json()

    # Stampa leggibile del dizionario ricevuto
    print(json.dumps(response, indent=2))

    # Estraggo la melodia dalla risposta
    melody_text = response['choices'][0]['message']['content']
    melody = json.loads(melody_text)  # se il testo è un JSON string


    # Parametri MIDI
    bpm = 120
    ticks_per_beat = 480
    midi_file = MidiFile(ticks_per_beat=ticks_per_beat)
    track = MidiTrack()
    midi_file.tracks.append(track)

    # Set tempo
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))

    # Conversione durata
    duration_map = {
        '1/1': 4, '1/2': 2, '1/4': 1, '1/8': 0.5, '1/16': 0.25, '1/32': 0.125
    }

    # Numero di battute per bar (4/4)
    beats_per_bar = 4

    for bar in melody['melody']:
        bar_tick_accum = 0  # tempo accumulato all'interno del bar
        for note_info in bar['notes']:
            notes = note_info['note']
            if isinstance(notes, str):
                notes = [notes]

            midi_notes = [note_to_midi(n) for n in notes]
            ticks = int(duration_map[note_info['duration']] * ticks_per_beat)

            # Note ON simultanee
            for i, mn in enumerate(midi_notes):
                t = bar_tick_accum if i == 0 else 0  # solo la prima nota del gruppo usa il tempo accumulato
                track.append(Message('note_on', note=mn, velocity=note_info['velocity'], time=t))

            # Note OFF simultanee
            for i, mn in enumerate(midi_notes):
                t = ticks if i == 0 else 0
                track.append(Message('note_off', note=mn, velocity=0, time=t))

            bar_tick_accum = 0  # dopo la prima nota del gruppo, il tempo è già assegnato

        # Alla fine del bar, calcolo se servono ticks di padding per raggiungere esattamente 4 battute
        total_ticks_bar = sum(int(duration_map[n['duration']] * ticks_per_beat) for n in bar['notes'])
        bar_padding = int(beats_per_bar * ticks_per_beat) - total_ticks_bar
        if bar_padding > 0:
            # aggiungo un piccolo "note_off fittizio" a note inesistenti solo per avanzare il tempo
            track.append(Message('note_off', note=0, velocity=0, time=bar_padding))

    # Salvataggio
    output_file = 'melody.mid'
    midi_file.save(output_file)
    print(f"File MIDI salvato come {output_file}")

    return output_file
