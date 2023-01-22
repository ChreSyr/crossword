

import numpy
import random


class Starts(dict):
    current_axis = 0
    def add_start(self, axis, row, col):
        axis = 1 if axis == "vertical" else 0
        self[axis].append((col, row))
    def change_current_axis(self):
        if self.current_axis == 1:
            self.current_axis = 0
        else:
            self.current_axis = 1


def format_time(time, formatter=None):
    """
    Function who create a string from a time and a formatter
    The time value is considered as seconds

    It uses letters in formatter in order to create the appropriate string:
        - %D : days
        - %H : hours
        - %M : minutes
        - %S : seconds
        - %m : milliseconds

    Examples :

        format_time(time=600, formatter="%H hours and %M minutes") -> "10 hours and 0 minutes"

    """

    formatter_is_unset = formatter is None
    if formatter is None:
        formatter = "%D:%H:%M:%S:%m"

    require_days = formatter.count("%D")
    require_hours = formatter.count("%H")
    require_minutes = formatter.count("%M")
    require_seconds = formatter.count("%S")
    require_milliseconds = formatter.count("%m")

    # Days
    days = int(time // 86400)
    if require_days:
        formatter = formatter.replace("%D", "{:0>2}".format(days))
        time = time % 86400

    # Hours
    hours = int(time // 3600)
    if require_hours:
        formatter = formatter.replace("%H", "{:0>2}".format(hours))
        time = time % 3600

    # Minutes
    minutes = int(time // 60)
    if require_minutes:
        formatter = formatter.replace("%M", "{:0>2}".format(minutes))
        time = time % 60

    # Seconds
    if require_seconds:
        formatter = formatter.replace("%S", "{:0>2}".format(int(time)))
        time = time % 1

    # milliseconds
    if require_milliseconds:
        formatter = formatter.replace("%m", "{:0>3}".format(int(time * 1000)))

    if formatter_is_unset:
        while formatter.startswith("00:") and len(formatter) > 6:
            formatter = formatter[3:]

    return formatter

def intersection(lst1, lst2):
    return [value for value in lst1 if value in lst2]

def length_without_hyphen(word):
    return len(word) - word.count('-')

words = []
words_by_len = {}
words_by_start = {"" : words}

for i in range(1, 21):
    words_by_len[i] = []

max_len = 0
with open("dictionnaire.txt", 'r', encoding='utf8') as reader:

    for line in reader.readlines():
        word = line.strip()

        length = length_without_hyphen(word)
        max_len = max(max_len, length)

        if length <= 10:
            words.append(word)
            words_by_len[length].append(word)

            chars = ""
            for char in word:
                chars += char
                try:
                    words_by_start[chars].append(word)
                except KeyError:
                    words_by_start[chars] = [word]


def get_grid():

    starts = Starts({
        0 : [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9)],  # horizontal
        1 : [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0)]   # vertical
    })

    grid = numpy.array([
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ])

    blocked = False
    while blocked is False:

        current_axis = starts.current_axis
        starts.change_current_axis()
        current_start_list = starts[current_axis]

        if not current_start_list:
            if not starts[1 if current_axis == 0 else 0]:
                break  # DONE !!!
            continue

        current_start = current_start_list.pop(0)

        if current_axis == 0:
            sub_grid = grid[current_start[1],current_start[0]:]
        else:
            sub_grid = grid[current_start[1]:,current_start[0]]

        space = list(sub_grid)

        try:
            index = space.index('■')

        except ValueError:
            pass

        else:
            space = space[:index]

            if index < 2:
                continue

        start = ""
        for char in space:
            if char == ' ':
                break
            start += char

        if current_start == (0, 0):

            if start == "":
                word = random.choice(words_by_len[10])  # first word
            else:
                ok = False
                while not ok:
                    word = random.choice(words_by_len[10])
                    if word[0] == start:
                        ok = True

        else:

            try:
                matching_words = words_by_start[start]

            except KeyError:
                # print(f'No word starts with {start}')
                blocked = True
                continue

            # if end is None:
            max_length = len(space)
            matching_words = list(word for word in matching_words if length_without_hyphen(word) <= max_length)

            if not matching_words:
                # print(f'No word starts with {start} and has a length less than or equal to {max_length}')
                blocked = True
                continue

            letter_constraints = []
            for i, char in enumerate(space):
                if i < len(start):
                    continue
                if char != ' ':
                    letter_constraints.append(i)

            random.shuffle(matching_words)
            word = None

            for potential_word in matching_words:

                potential_word = potential_word.replace('-', '')

                length = length_without_hyphen(potential_word)

                # if there is a letter after the end of the potential word
                if length < max_length:
                    if space[length] not in (' ', '■'):
                        continue

                # check for letters on the way
                match = True
                if letter_constraints:
                    for index in letter_constraints:
                        if len(potential_word) <= index:
                            continue
                        if space[index] != potential_word[index]:
                            match = False
                            break
                if match is False:
                    continue

                # check for perpendicular future words
                if current_axis == 0:  # horizontal
                    for i, letter in enumerate(potential_word):

                        if i < len(start):
                            continue
                        if i in letter_constraints:
                            continue

                        letter_case = (current_start[0] + i, current_start[1])  # (col, row)
                        start_other_axis = letter
                        before_case = list(letter_case)

                        while True:
                            before_case[1] -= 1

                            if before_case[1] < 0:
                                break

                            case = grid[before_case[1],before_case[0]]
                            if case == '■':
                                break
                            if case == ' ':
                                start_other_axis = ""
                            else:
                                start_other_axis = case + start_other_axis

                        try:
                            words_by_start[start_other_axis]  # potential_perpendicular_words

                        except KeyError:  # No word can be perpendicular
                            match = False
                            break
                else:
                    for i, letter in enumerate(potential_word):

                        if i < len(start):
                            continue
                        if i in letter_constraints:
                            continue

                        letter_case = (current_start[0], current_start[1] + i)  # (col, row)
                        start_other_axis = letter
                        before_case = list(letter_case)

                        while True:
                            before_case[0] -= 1

                            if before_case[0] < 0:
                                break

                            case = grid[before_case[1],before_case[0]]
                            if case == '■':
                                break
                            if case == ' ':
                                start_other_axis = ""
                            else:
                                start_other_axis = case + start_other_axis

                        try:
                            words_by_start[start_other_axis]  # potential_perpendicular_words

                        except KeyError:  # No word can be perpendicular
                            match = False
                            break
                if match is False:
                    continue

                word = potential_word
                break

            if word is None:
                # print(f"No word matches the conditions from {current_start}")
                blocked = True
                continue

        shorted_word = word.replace('-', '')
        word_len = len(shorted_word)

        black_square = None

        if current_axis == 0:
            grid[current_start[1],current_start[0]:current_start[0] + word_len] = list(shorted_word)
            if current_start[0] + word_len < 10:
                black_square = (current_start[1], current_start[0] + word_len)
        else:
            grid[current_start[1]:current_start[1] + word_len,current_start[0]] = list(shorted_word)
            if current_start[1] + word_len < 10:
                black_square = (current_start[1] + word_len, current_start[0])

        if black_square is not None and grid[black_square[0], black_square[1]] != '■':
            assert grid[black_square[0], black_square[1]] == ' '
            grid[black_square[0], black_square[1]] = '■'

            if black_square[0] < 8:
                starts.add_start("vertical", row=black_square[0] + 1, col=black_square[1])
            if black_square[1] < 8:
                starts.add_start("horizontal", row=black_square[0], col=black_square[1] + 1)

    print(grid)
    if blocked is False:
        return grid

import time
start_time = time.time()

trials = 0
while True:
    trials += 1
    grid = get_grid()
    if grid is not None:
        print(grid)

        time_used = time.time() - start_time
        print(f" SUCCESS !!!! after {trials} trials and "
              f"{format_time(time=time_used, formatter='%H hours, %M minutes and %S seconds')} !!\n")
        break

with open(f"grille{int(time.time())}.txt", 'w', encoding='utf8') as writer:
    for i in range(10):

        row = grid[i, :]

        word = ""
        for char in row:
            word += char

        writer.write(word + '\n')

    writer.write(f"\nFound after {trials} trials and "
                 f"{format_time(time=time_used, formatter='%H hours, %M minutes and %S seconds')}")
