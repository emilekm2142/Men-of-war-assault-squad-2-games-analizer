
#(07?).....060100 - .... to kod jednostki



from collections import defaultdict
def find_and_print_surroundings(file_path, target_sequence, surrounding_bytes=5):
    with open(file_path, 'rb') as f:
        data = f.read()

    # Convert the target sequence from a string to bytes
    target_bytes = bytes.fromhex(target_sequence)

    # Find all occurrences of the target sequence
    positions = [i for i in range(len(data)) if data.startswith(target_bytes, i)]

    # Print the surrounding bytes for each found instance
    for pos in positions:
        # Calculate start and end positions for the surrounding bytes
        start = max(pos - surrounding_bytes, 0)
        end = min(pos + len(target_bytes) + surrounding_bytes, len(data))

        # Get the surrounding bytes
        surrounding = data[start:end]

        # Convert to hexadecimal for display
        print(f"Found at position {pos}: ... {surrounding.hex()} ...")

def find_repeating_patterns(file_path):
    # Dictionary to store patterns and their counts
    pattern_counts = defaultdict(int)

    # Read the binary file
    with open(file_path, 'rb') as f:
        data = f.read()

    # Maximum length of pattern to check
    max_pattern_length = 3

    # Iterate over all possible pattern lengths from 1 to max_pattern_length
    for pattern_length in range(1, max_pattern_length + 1):
        # Slide a window of `pattern_length` over the data
        for i in range(len(data) - pattern_length + 1):
            pattern = data[i:i + pattern_length]
            pattern_counts[pattern] += 1

    # Filter out patterns that repeat more than once
    repeating_patterns = {p: c for p, c in pattern_counts.items() if c > 1}

    return repeating_patterns

find_and_print_surroundings('replay1.qm', '012a')

# Example usage
file_path = 'replay3.qm'
repeats = find_repeating_patterns(file_path)
file_path = 'replay4.qm'
repeats2 = find_repeating_patterns(file_path)
file_path = 'replay5.qm'
repeats3 = find_repeating_patterns(file_path)
file_path = 'replay1.qm'
repeats4 = find_repeating_patterns(file_path)
file_path = 'replay2_nothing.qm'
repeats5 = find_repeating_patterns(file_path)


print("-------")
for pattern, count in repeats.items():
    if (count==10 and
            pattern in repeats2 and repeats2[pattern] == 10 and
            pattern in repeats3 and repeats3[pattern] == 3 and
            pattern in repeats4 and repeats4[pattern] == 5 and
            pattern not in repeats5
    ):
        print(pattern.hex())



file_path_full = 'replay5asdasdadasd.qm'
repeats5 = find_repeating_patterns(file_path_full)
print("-------")
for pattern, count in repeats5.items():
    if pattern.hex() == "060100":
        print(count)