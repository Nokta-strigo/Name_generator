#!/usr/bin/python3
from heapq import heappushpop, heappush, heappop, heapify

# parameters to be set up
input_file_name = "ru_female_names.txt"  # where from get list of existing names to generate Markov matrix
number_of_names_to_generate = 4000  # number of highest probability names to output
min_name_len = 2  # minimum name length to output
max_name_len = 15  # maximum name length to output


# we must count \n and \r chars too
min_name_len += 2
max_name_len += 2

def normalize_probability(dict_chars):
    """Receives dictionary of {char:number of entries} values, returns dictionary of {char:probability}"""
    norm_from = sum(dict_chars.values(), 0)
    for c in dict_chars.keys():
        dict_chars[c] /= norm_from
    return dict_chars


def generate_names_with_probabilities(name_beginning, probability):
    """Recursive function. If the last char is \r, pushes the name into the list of generated names.
    Otherwise adds one char to name_beginning, recalculates probability of the new name beginning and recurses"""
    if len(name_beginning) > max_name_len:  # The name is growing too long
        return
    cur_char1 = name_beginning[-1]
    if cur_char1 == '\r':
        if len(name_beginning) >= min_name_len:
            probability *= name_length_probabilities[len(name_beginning)]
            heappushpop(names, (probability, name_beginning))
    elif probability * maximum_expected_name_length_probability[len(name_beginning)+1] < names[0][0]:  # Simple optimization. Since the probability of name can't increase, if it's probability is already too low, can simply skip this name_beginning
        return
    else:
        for next_char1 in letter_from[cur_char1]:
            generate_names_with_probabilities(name_beginning + next_char1, probability * letter_from[cur_char1].get(next_char1, 0))


# Read the given dictionary file into memory
existing_names = set()
max_existing_name_len = 0
for name in open(input_file_name, 'rt'):
    name = '\n' + name.upper().strip('\n\r') + '\r'  # '\n' means the char before the first letter, '\r' - after the last letter
    if name != '\n\r':
        existing_names.add(name)
        if len(name) > max_existing_name_len:
            max_existing_name_len = len(name)

# Build the Markov chain and histogram of name lengths
letter_from = {}  # The transition matrix
name_length_probabilities = [0] * (max_existing_name_len + 1)
for name in existing_names:
    name_length_probabilities[len(name)] += 1
    for i in range(len(name) - 1):
        cur_char = name[i]
        next_char = name[i+1]
        if cur_char not in letter_from.keys():
            letter_from[cur_char] = {next_char: 1}
        else:
            letter_from[cur_char][next_char] = letter_from[cur_char].get(next_char, 0) + 1

for char in letter_from.keys():
    letter_from[char] = normalize_probability(letter_from[char])

for i in range(len(name_length_probabilities)):
    name_length_probabilities[i] /= len(existing_names)

max_name_len = min(max_name_len, len(name_length_probabilities) - 1)

maximum_expected_name_length_probability = []  # used for optimization
for i in range(len(name_length_probabilities)):
    maximum_expected_name_length_probability.append(max(name_length_probabilities[i:]))
maximum_expected_name_length_probability.append(0)

# Initialise the output heap
names = []
for i in range(number_of_names_to_generate):
    heappush(names, (0, ''))
heapify(names)

# Generate names
generate_names_with_probabilities('\n', 1)

# Sort and output generated names
names_sorted = []
while len(names) > 0:
    names_sorted.append(heappop(names))

for name in names_sorted[::-1]:
    print(name[1].strip('\n\r').capitalize())
