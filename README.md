# MeloChords-Generator

**MeloChords-Generator** is an innovative tool designed to facilitate music creation through the integration of advanced language models (LLMs) and MIDI generation. The project provides an intuitive graphical user interface (GUI) that allows both beginners and experienced musicians to generate melodies and chord progressions in MIDI format.  

## Description

MeloChords-Generator enables users to:  
- Create textual prompts and send them to a language model (LLM) to generate musical ideas;   
- Automatically generate MIDI melodies or chord progressions;  
- Visualize, listen to, and download the generated musical content directly from the interface.  

The project aims to achieve two main objectives:  
1. Make music creation more accessible to users with limited knowledge of music theory;  
2. Support music producers during creative blocks by providing inspiration and immediately usable material.

This project leverages the following technologies:  

[![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/Gradio-UI-success?logo=gradio&logoColor=white)](https://gradio.app/)
[![LM Studio](https://img.shields.io/badge/LM%20Studio-LLM-orange)](https://lmstudio.ai/)  
[![Mido](https://img.shields.io/badge/Mido-MIDI-orange?logo=python&logoColor=white)](https://mido.readthedocs.io/)
[![Music21](https://img.shields.io/badge/music21-music-lightgrey?logo=python&logoColor=white)](https://web.mit.edu/music21/)
[![Pygame](https://img.shields.io/badge/Pygame-Audio-blue?logo=pygame&logoColor=white)](https://www.pygame.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-Plotting-red?logo=matplotlib&logoColor=white)](https://matplotlib.org/)
[![Requests](https://img.shields.io/badge/Requests-HTTP-green?logo=python&logoColor=white)](https://docs.python-requests.org/)

## Installation & Setup

To run **MeloChords-Generator**, follow these steps:

### 1. Install LM Studio
Download and install [LM Studio](https://lmstudio.ai/) on your machine.

### 2. Install the LLM
If you want to use the model employed in this project, install the **qwen3-4b-2507** model:

### 3. Enable API
1. Go to the **Developer** section in LM Studio.
2. Activate the LLM to enable the API endpoint.

### 4. Configure Inference Settings
1. Navigate to the **Inference** panel.
2. Set the following parameters:  
   - **Temperature:** 0.8  
   - **Top K Sampling:** 60  
   - **Repeat Penalty:** 1.2

### 5. Enable Structured Output
1. Activate **Structured Output**.
2. Insert the following JSON schema:

```json
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
          "bar": {
            "type": "integer",
            "minimum": 1
          },
          "notes": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "note": {
                  "type": [
                    "string",
                    "array"
                  ],
                  "pattern": "^[A-Ga-g][#b]?[0-9]$"
                },
                "duration": {
                  "type": "string",
                  "pattern": "^(1/1|1/2|1/4|1/8|1/16|1/32)$"
                },
                "velocity": {
                  "type": "integer",
                  "minimum": 0,
                  "maximum": 127
                }
              },
              "required": [
                "note",
                "duration",
                "velocity"
              ]
            }
          }
        },
        "required": [
          "bar",
          "notes"
        ]
      }
    }
  },
  "required": [
    "melody"
  ]
}
```

### 6. Install Python Dependencies
Before running the project, install all required Python libraries:

```bash
pip install gradio mido music21 pygame matplotlib requests
```
## Usage

To start using **MeloChords-Generator**, follow these steps:

1. Ensure all dependencies are installed and LM Studio is properly configured as described in the **Installation & Setup** section.

2. Launch the application by running the main GUI script:

```bash
python GUI.py
```
The graphical interface will open automatically. From there, you can:

- **Select** the musical **Key** and **Type** (Major/Minor).  
- **Choose** what to generate (**Melody** or **Chords**).  
- **Set** the number of **octaves** and **bars**.  
- **Select** allowed **durations** for the musical events.  
- **Click** the **Generate Prompt** button to create a prompt based on your settings.  
- **Click** the **Generate MIDI** button to send the prompt to the LLM and generate the corresponding MIDI file.  
- The generated MIDI will be displayed as a **pianoroll**, and you can **listen** to it or **download** the file directly from the interface.
