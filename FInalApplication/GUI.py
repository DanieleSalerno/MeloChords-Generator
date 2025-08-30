import promptUtility
import gradio as gr
import matplotlib.pyplot as plt
import tempfile
import pygame
import matplotlib
from music21 import converter, note
matplotlib.use("Agg")


def genera_promptOLD(key, scala, typeOfMusic, octave,bars,durations):
    prompt = ""
    GeneratedScale, GeneratedChords = generate_chords(key, scala)
    print("Scale:", GeneratedScale)
    print("Triads:", GeneratedChords["triads"])
    print("Seventh:", GeneratedChords["sevenths"])
    print("Suspended:", GeneratedChords["suspended"])
    print("Extended:", GeneratedChords["extended"])
    octString="equals to 3"
    if(octave==2):
        octString="between 3 and 4"
    elif(octave == 3):
        octString="between 3 and 5"


    if(typeOfMusic=="Melody"):
        InstructionPart = f"""You are a music generator. You must produce melodies in JSON format.\n\nEvery musical event must be a single note (example: "{key}4").Never use arrays like {fixchordsIntro(GeneratedChords["triads"])}. Always use a single string representing one pitch with octave.\nImportant: Do NOT only create ascending or descending scales. \n """
        requirements= f"""Requirements:
        - Each bar must contain durations that sum to 1.
        
        - Key: {key} {scala}.  
        - Length: {bars} bars.  
        - Allowed octaves: {octString} 
        - Allowed notes: {GeneratedScale} (with octave numbers). 
        - Allowed durations:{", ".join(durations)}
        - Vary dynamics: velocity between 60 and 120.   
        """
        formatString = """- Output must strictly follow this JSON schema: \n ```json
        {
          "schema": "http://json-schema.org/draft-07/schema#",
          "title": "Melody",
          "type": "object",
          "properties": {
            "melody": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "bar": { "type": "integer", "minimum": 1 },
                  "notes": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "note": { "type": "string", "pattern": "^[A-Ga-g][#b]?[0-9]|rest$" },
                        "duration": { "type": "string", "pattern": "^(1/1|1/2|1/4|1/8|1/16)$" },
                        "velocity": { "type": "integer", "minimum": 0, "maximum": 127 }
                      },
                      "required": ["note", "duration", "velocity"]
                    }
                  }
                },
                "required": ["bar", "notes"]
              }
            }
          },
          "required": ["melody"]
        }"""


    elif(typeOfMusic=="Chords"):
        examplechord= GeneratedChords["triads"][0]
        examplechord = ['"'+note + str(4)+'"' for note in examplechord]
        print(examplechord)
        InstructionPart = f"""You are a music generator.You must produce chord progressions in JSON format.\n\nEvery musical event must be a chord (two or more notes played together), expressed as an array of strings with octave (example: {examplechord}.\n Never use a single note like "{key}4".  \nUse arrays of 2, 3, 4, or 5 notes. Vary chord sizes across the progression. \n"""

        requirements=f"""Requirements:
        - Key: {key} {scala}.  
        - Length: {bars} bars.  
        - Allowed octaves: {octString}       
        - Allowed chord types:
         - Remember the format "Note#ORbOctave"
        - Triads: {fixchords(GeneratedChords["triads"])}
        - Seventh chords: {fixchords(GeneratedChords["sevenths"])}
        - Suspended chords: {fixchords(GeneratedChords["suspended"])}
        - Extended chords: {fixchords(GeneratedChords["extended"])}
        - Each bar must contain durations that sum to 1.
        - Allowed durations:{", ".join(durations)}
        - Vary dynamics: velocity between 60 and 120.  """

        formatString = """```json
        {
          "schema": "http://json-schema.org/draft-07/schema#",
          "title": "Melody",
          "type": "object",
          "properties": {
            "melody": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "bar": { "type": "integer", "minimum": 1 },
                  "notes": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "note": {
                          "type": "array",
                          "items": { "type": "string", "pattern": "^[A-Ga-g][#b]?[0-9]|rest$" },
                          "minItems": 2,
                          "maxItems": 5
                        },
                        "duration": { "type": "string", "pattern": "^(1/1|1/2|1/4|1/8|1/16)$" },
                        "velocity": { "type": "integer", "minimum": 0, "maximum": 127 }
                      },
                      "required": ["note", "duration", "velocity"]
                    }
                  }
                },
                "required": ["bar", "notes"]
              }
            }
          },
          "required": ["melody"]
        }

        """

    prompt = InstructionPart + requirements + formatString
    return prompt,gr.update(interactive=True)


import itertools

# Tutte le note con semitoni
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Pattern intervalli
PATTERNS = {
    "major": [2, 2, 1, 2, 2, 2, 1],
    "minor": [2, 1, 2, 2, 1, 2, 2]
}

def generate_pianoroll_image(midi_path):

    score = converter.parse(midi_path)

    score= score.transpose(12)

    for midi_pitch in range(48, 84):  # C3=48, B5=83
        n = note.Note()
        n.pitch.midi = midi_pitch
        n.quarterLength = 0  # durata 0
        score.insert(0, n)





    pr = score.plot('pianoroll')       # genera il plot
    # Salva la figura corrente in PNG
    img_path = tempfile.mktemp(suffix=".png")
    plt.gcf().savefig(img_path)
    plt.close()

    return img_path


def midi_to_pianoroll_and_audio(midi_path, num_bars=8, ticks_per_bar=32):

    img_path= generate_pianoroll_image(midi_path)

    # ---- Riproduzione audio ----
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(midi_path)
    pygame.mixer.music.play()

    return img_path, None

def generate_scale(tonic: str, mode: str):
    """Genera le note della scala a partire da tonica e tipo (maggiore/minore)."""
    tonic_index = NOTES.index(tonic)
    pattern = PATTERNS[mode.lower()]
    scale = [NOTES[tonic_index % 12]]
    idx = tonic_index
    for step in pattern:
        idx += step
        scale.append(NOTES[idx % 12])
    return scale[:-1]  # tolgo l'ottava duplicata

def chord_from_scale(scale, degree, chord_type="triad"):
    """Genera un accordo dal grado dato e tipo (triad, seventh, sus, extended)."""
    n = len(scale)
    root = degree % n
    if chord_type == "triad":
        return [scale[root], scale[(root+2) % n], scale[(root+4) % n]]
    elif chord_type == "seventh":
        return [scale[root], scale[(root+2) % n], scale[(root+4) % n], scale[(root+6) % n]]
    elif chord_type == "suspended":
        return [scale[root], scale[(root+1) % n], scale[(root+4) % n]]  # esempio: sus2
    elif chord_type == "extended":
        return [scale[root], scale[(root+2) % n], scale[(root+4) % n], scale[(root+6) % n], scale[(root+8) % n]]
    else:
        return []

def fixchords(chords):
    result = ', '.join(['[' + ','.join(note) + ']' for note in chords])
    return result

def fixchordsIntro(chords):

    result = ', '.join(['[' + ','.join([f'"{note}{4}"' for note in triad]) + ']' for triad in chords])
    return result

def generate_chords(key="C", mode="maggiore"):
    scale = generate_scale(key, mode)
    chords = {
        "triads": [chord_from_scale(scale, i, "triad") for i in range(7)],
        "sevenths": [chord_from_scale(scale, i, "seventh") for i in range(7)],
        "suspended": [
            [scale[0], scale[1], scale[4]],  # I sus2
            [scale[0], scale[3], scale[4]],  # I sus4
            [scale[4], scale[5], scale[1]],  # V sus2
            [scale[4], scale[0], scale[1]]   # V sus4
        ],
        "extended": [
            chord_from_scale(scale, 0, "extended"),
            chord_from_scale(scale, 4, "extended"),
            chord_from_scale(scale, 1, "extended"),
            chord_from_scale(scale, 3, "extended")
        ]
    }
    return scale, chords

    # Esempio


def launchprompt(prompt):
    midi_path=promptUtility.sendPrompt(prompt)
    print("creatingpianoroll")
    img, audio = midi_to_pianoroll_and_audio(midi_path)
    print("updating GUI")
    # restituisci come dictionary per aggiornare i componenti


    return gr.update(value=img), gr.update(value=audio), gr.update(value=midi_path)



"""
demo = gr.Interface(
    fn=genera_promptOLD,
    inputs=[
        gr.Dropdown(choices=["C", "C#","D", "D#", "E", "F", "F#",
                             "G", "G#", "A", "A#", "B"], label="Key"),
        gr.Radio(choices=["Major", "Minor"], label="Type"),
        gr.Radio(choices=["Chords", "Melody","Chords and Melody"], label="What to generate"),
        gr.Slider(minimum=1, maximum=3, step=1, label="Number of octave"),
        gr.Radio(choices=["4", "8", "12"], label="Bars"),
        gr.CheckboxGroup(choices=["1", "1/2", "1/4", "1/8", "1/16", "1/32"], label= "Durations")
    ],
    outputs=gr.Textbox(label="Prompt generato"),
    allow_flagging=False
    
    
)


with gr.Blocks() as demo:
    # Input come nel tuo Interface
    key = gr.Dropdown(choices=["C", "C#", "D", "D#", "E", "F", "F#",
                               "G", "G#", "A", "A#", "B"], label="Key")
    type_ = gr.Radio(choices=["Major", "Minor"], label="Type")
    what = gr.Radio(choices=["Chords", "Melody", "Chords and Melody"], label="What to generate")
    octave = gr.Slider(minimum=1, maximum=3, step=1, label="Number of octave")
    bars = gr.Radio(choices=["4", "8", "12"], label="Bars")
    durations = gr.CheckboxGroup(choices=["1", "1/2", "1/4", "1/8", "1/16", "1/32"], label="Durations")

    # Output del prompt
    GeneratedPrompt = gr.Textbox(label="Generated Prompt")


    # Pulsante per generare il prompt
    genera_btn = gr.Button("Genera Prompt")
    genera_btn.click(
        fn=genera_promptOLD,
        inputs=[key, type_, what, octave, bars, durations],
        outputs=GeneratedPrompt
    )

    # Pulsante per usare il prompt
    lancia_btn = gr.Button("Generated MIDI")
    lancia_btn.click(
        fn=launchprompt,  # la tua funzione che prende il prompt
        inputs=GeneratedPrompt,

    )

demo.launch()"""

with gr.Blocks() as demo:
    gr.Markdown("## LLM MIDI Generator")

    # --- Sezione generatore di prompt ---
    with gr.Row():
        with gr.Column():
            key = gr.Dropdown(choices=["C", "C#", "D", "D#", "E", "F", "F#",
                                       "G", "G#", "A", "A#", "B"], label="Key")
            type_ = gr.Radio(choices=["Major", "Minor"], label="Type")
            what = gr.Radio(choices=["Chords", "Melody"], label="What to generate")
            octave = gr.Slider(minimum=1, maximum=3, step=1, label="Number of octave")
            bars = gr.Radio(choices=["4", "8", "12"], label="Bars")
            durations = gr.CheckboxGroup(choices=["1", "1/2", "1/4", "1/8", "1/16", "1/32"], label="Durations")
        with gr.Column():
            GeneratedPrompt = gr.Textbox(label="Generated Prompt",lines=21)
    with gr.Row():
        genera_btn = gr.Button("Genera Prompt",variant="huggingface")
        lancia_btn = gr.Button("Generate MIDI", variant="huggingface", interactive=False)
        genera_btn.click(
                fn=genera_promptOLD,
                inputs=[key, type_, what, octave, bars, durations],
                outputs=[GeneratedPrompt,lancia_btn]
        )




    gr.Markdown("---")  # separatore visivo

    # --- Sezione caricamento e visualizzazione MIDI ---
    with gr.Column():
        output_img = gr.Image(label="Pianoroll",)
        output_audio = gr.Audio(label="Riproduzione MIDI")  # placeholder
        download_midi = gr.File(label="Scarica MIDI")
        lancia_btn.click(
            fn=launchprompt,
            inputs=GeneratedPrompt,
            outputs=[output_img, output_audio,download_midi]
        )

demo.launch()


