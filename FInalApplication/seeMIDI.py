import gradio as gr
import matplotlib.pyplot as plt
import mido
import numpy as np
import tempfile
import pygame
import matplotlib
from music21 import converter, note

matplotlib.use("Agg")

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
    # ---- Carica MIDI ----
    mid = mido.MidiFile(midi_path)

    img_path= generate_pianoroll_image(midi_path)

    # ---- Riproduzione audio ----
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(midi_path)
    pygame.mixer.music.play()

    return img_path, None

with gr.Blocks() as demo:
    gr.Markdown("## 🎹 Visualizzatore e Player MIDI")

    midi_input = gr.File(label="Carica un file MIDI", type="filepath", file_types=[".mid"])

    with gr.Row():
        output_img = gr.Image(label="Pianoroll")
        output_audio = gr.Audio(label="Riproduzione MIDI")  # placeholder

    submit_btn = gr.Button("Elabora MIDI")

    submit_btn.click(
        midi_to_pianoroll_and_audio,
        inputs=[midi_input],
        outputs=[output_img, output_audio]
    )


demo.launch()
