import json

with open('chord_templates.json', 'r') as fp:
    """read from JSON file to get chord templates"""
    templates_json = json.load(fp)

chords = ['G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'Gm', 'G#m', 'Am', 'A#m', 'Bm', 'Cm', 'C#m',
          'Dm', 'D#m', 'Em', 'Fm', 'F#m']
nested_cof = ['G', 'Bm', 'D', 'F#m', 'A', 'C#m', 'E', 'G#m', 'B', 'D#m', 'F#', 'A#m', 'C#', "Fm", "G#", 'Cm', 'D#',
              'Gm', 'A#', 'Dm', 'F', 'Am', 'C', 'Em']
templates = []

for chord in chords:
    templates.append(templates_json[chord])

