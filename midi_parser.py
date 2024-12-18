# midi_parser.py
import mido

# Corrected MIDI to white key mapping (starting from 1:C)
MIDI_WHITE_KEYS = [
    24, 26, 28, 29, 31, 33, 35, 36, 38, 40, 41, 43, 45, 47, 
    48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 
    72, 74, 76, 77, 79, 81, 83, 84, 86, 88, 89, 91, 93, 95, 
    96, 98, 100, 101, 103, 105, 107, 108
]

# Octave-key mapping
OCTAVE_KEY_MAP = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

# Threshold for small delay (in ms)
MIN_DELAY_THRESHOLD_MS = 75

# Enable/Disable Key Conversion for Debugging
DEBUG_CONVERT_TO_CK = False

def enable_debug_convert_to_ck():
    global DEBUG_CONVERT_TO_CK
    DEBUG_CONVERT_TO_CK = True

def disable_debug_convert_to_ck():
    global DEBUG_CONVERT_TO_CK
    DEBUG_CONVERT_TO_CK = False

def midi_to_white_key(midi_note):
    """ Translate MIDI note to white key number (1...52) """
    if midi_note in MIDI_WHITE_KEYS:
        return MIDI_WHITE_KEYS.index(midi_note) + 1
    return None

def translate_key(key_number):
    """ Translate key number to (octave):(key) format """
    shifted_index = key_number - 1
    octave = 1 + shifted_index // 7
    key = OCTAVE_KEY_MAP[shifted_index % 7]
    return f"{octave}:{key}"

class Event:
    def __init__(self, time, hand, command, key):
        self.time = time  # Absolute time in ms
        self.hand = hand  # 0 for left, 1 for right
        self.command = command  # 'press' or 'unpress'
        self.key = key  # Key number

    def __lt__(self, other):
        return self.time < other.time

def parse_midi(midi_file_path):
    """ 
    Parse MIDI file and return a unified list of events with absolute times and hand assignments.
    
    Returns:
        List[Event]: Sorted list of events based on absolute time.
    """
    mid = mido.MidiFile(midi_file_path)
    events = []
    track_start_times = [0] * len(mid.tracks)  # Track start times

    for i, track in enumerate(mid.tracks):
        current_time = 0
        for msg in track:
            if not msg.is_meta:
                current_time += msg.time * 1000  # Convert seconds to ms

                if msg.type == 'note_on' and msg.velocity > 0:
                    key = midi_to_white_key(msg.note)
                    if key:
                        hand = msg.channel  # Assuming channel 0: left, 1: right
                        events.append(Event(current_time, hand, 'press', key))

                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    key = midi_to_white_key(msg.note)
                    if key:
                        hand = msg.channel  # Assuming channel 0: left, 1: right
                        events.append(Event(current_time, hand, 'unpress', key))

    # Sort events by their absolute time
    events.sort()
    return events

def convert_keys_to_ck(commands):
    """ Convert keys to (octave):(key) format if enabled """
    converted = []
    for cmd in commands:
        if cmd.startswith("press") or cmd.startswith("unpress"):
            command_type, keys_str = cmd.split("(")
            keys = keys_str[:-1].split(",")
            translated_keys = [translate_key(int(k)) for k in keys]
            converted.append(f"{command_type}({','.join(translated_keys)})")
        else:
            converted.append(cmd)
    return converted

def save_to_file(commands, file_name="results/results.txt"):
    """ Save commands to a file """
    with open(file_name, "w") as file:
        for cmd in commands:
            file.write(cmd + "\n")
    print(f"Commands saved to {file_name}")


if __name__ == "__main__":
    # midi_file = "simple_example.mid" 
    # midi_file = "moreExpanded.mid" 
    # midi_file = "leftRight.mid" 
    midi_file = "exampleMIDI/leftRightSimultanous.mid"
    left, right = parse_midi(midi_file)
    save_to_file(left, 'results/left.txt')
    save_to_file(right, 'results/right.txt')
    print("Commands saved to results.txt")
