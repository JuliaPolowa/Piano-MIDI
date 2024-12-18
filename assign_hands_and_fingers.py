# assignHandsAndFingers.py
import midi_parser

# Define constants
LEFT_HAND_MAX_KEY = 26  # Adjust based on MIDI_WHITE_KEYS range
MIN_DISTANCE_THRESHOLD = 4  # Threshold for moving the hand

class HandState:
    def __init__(self, which_hand):
        self.which_hand = which_hand  # 0 for left, 1 for right
        self.current_hand_position = None
        self.finger_assignments = {}  # finger_number: key_number
        self.key_to_finger = {}        # key_number: finger_number
        self.available_fingers = [1, 2, 3, 4, 5]

    def move_hand(self, key, machine_instructions):
        if self.current_hand_position is not None:
            # Unpress all currently pressed fingers before moving
            for finger, assigned_key in list(self.finger_assignments.items()):
                machine_instructions.append(f"unpress_finger({self.which_hand}, {finger})")
                self.available_fingers.append(finger)
                del self.finger_assignments[finger]
                del self.key_to_finger[assigned_key]
        machine_instructions.append(f"move_hand({self.which_hand}, {key})")
        self.current_hand_position = key

    def press_finger_command(self, key, machine_instructions):
        if self.available_fingers:
            finger = self.available_fingers.pop(0)
            self.finger_assignments[finger] = key
            self.key_to_finger[key] = finger
            machine_instructions.append(f"press_finger({self.which_hand}, {finger})")
        else:
            print(f"No available fingers to press key {key} on hand {self.which_hand}.")

    def unpress_finger_command(self, key, machine_instructions):
        finger = self.key_to_finger.get(key)
        if finger:
            machine_instructions.append(f"unpress_finger({self.which_hand}, {finger})")
            self.available_fingers.append(finger)
            del self.finger_assignments[finger]
            del self.key_to_finger[key]
        else:
            print(f"Key {key} on hand {self.which_hand} was not pressed.")

def assign_hands_and_fingers(events):
    """
    Assign commands to hands and convert them to machine instructions.

    Args:
        events (List[Event]): Sorted list of MIDI events.

    Returns:
        list: List of machine instructions.
    """
    machine_instructions = []
    left_hand = HandState(0)
    right_hand = HandState(1)

    previous_time = 0

    for event in events:
        # Calculate wait time
        wait_time = event.time - previous_time
        if wait_time >= midi_parser.MIN_DELAY_THRESHOLD_MS:
            machine_instructions.append(f"wait({int(wait_time)})")
            previous_time = event.time

        # Select the appropriate hand
        if event.hand == 0:
            hand = left_hand
        elif event.hand == 1:
            hand = right_hand
        else:
            print(f"Unknown hand {event.hand} for key {event.key}. Skipping event.")
            continue

        if event.command == 'press':
            # Determine if the hand needs to move
            if hand.current_hand_position is None or abs(event.key - hand.current_hand_position) > MIN_DISTANCE_THRESHOLD:
                hand.move_hand(event.key, machine_instructions)
            # Assign a finger to the pressed key
            hand.press_finger_command(event.key, machine_instructions)

        elif event.command == 'unpress':
            # Unassign the finger from the key
            hand.unpress_finger_command(event.key, machine_instructions)

    return machine_instructions

def save_to_file(commands, file_name="results/machine_instructions.txt"):
    """
    Save machine instructions to a file.

    Args:
        commands (list): List of machine instructions.
        file_name (str): Destination file path.
    """
    with open(file_name, "w") as file:
        for cmd in commands:
            file.write(cmd + "\n")
    print(f"Machine instructions saved to {file_name}")

def time_correction(list_of_instructions):
    for i, instruction in enumerate(list_of_instructions):
        if instruction.startswith("wait("):
            time_string = instruction[5:-1]  # Remove "wait(" and ")"
            time_in_ms = int(time_string)
            time_in_s = time_in_ms * 1 / 1200
            list_of_instructions[i] = f"wait({int(time_in_s)})"
    return list_of_instructions

# Inside assignHandsAndFingers.py after saving machine_instructions.txt
def save_as_cpp_header(commands, file_name="machine_instructions.h"):
    """ Save commands as a C++ header file """
    with open(file_name, "w") as file:
        file.write("#ifndef MACHINE_INSTRUCTIONS_H\n")
        file.write("#define MACHINE_INSTRUCTIONS_H\n\n")
        file.write("typedef enum {\n")
        file.write("    CMD_WAIT,\n")
        file.write("    CMD_MOVE_HAND,\n")
        file.write("    CMD_PRESS_FINGER,\n")
        file.write("    CMD_UNPRESS_FINGER\n")
        file.write("} CommandType;\n\n")
        file.write("typedef struct {\n")
        file.write("    CommandType type;\n")
        file.write("    int which_hand;  // 0 for left, 1 for right (ignored for CMD_WAIT)\n")
        file.write("    int param;       // key number, finger number, or wait duration\n")
        file.write("} Command;\n\n")
        file.write("const Command commands[] = {\n")
        for cmd in commands:
            if cmd.startswith("wait("):
                duration = cmd[5:-1]
                file.write(f"    {{ CMD_WAIT, -1, {duration} }},\n")
            elif cmd.startswith("move_hand("):
                parts = cmd[10:-1].split(",")
                which_hand = parts[0].strip()
                to_key = parts[1].strip()
                file.write(f"    {{ CMD_MOVE_HAND, {which_hand}, {to_key} }},\n")
            elif cmd.startswith("press_finger("):
                parts = cmd[13:-1].split(",")
                which_hand = parts[0].strip()
                finger = parts[1].strip()
                file.write(f"    {{ CMD_PRESS_FINGER, {which_hand}, {finger} }},\n")
            elif cmd.startswith("unpress_finger("):
                parts = cmd[15:-1].split(",")
                which_hand = parts[0].strip()
                finger = parts[1].strip()
                file.write(f"    {{ CMD_UNPRESS_FINGER, {which_hand}, {finger} }},\n")
        file.write("};\n\n")
        file.write(f"const int numCommands = sizeof(commands) / sizeof(commands[0]);\n\n")
        file.write("#endif\n")
    print(f"Commands saved to {file_name}")
    
if __name__ == "__main__":
    # MIDI file with two tracks: left hand and right hand
    # midi_file = "leftRight.mid"
    # midi_file = "leftRightSimultanous.mid"
    # midi_file = "leftRightSimultanous.mid"
    midi_file = "exampleMIDI/leftRight2.mid"

    # Parse MIDI file into a unified list of events
    events = midi_parser.parse_midi(midi_file)
    
    # Assign hands and convert to machine instructions
    machine_instructions = assign_hands_and_fingers(events)

    machine_instructions = time_correction(machine_instructions)

    save_as_cpp_header(machine_instructions, "machine_instructions.h")

    # Save the machine instructions to a file
    save_to_file(machine_instructions)
