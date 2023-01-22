

import numpy
import random


class GridSquare(tuple):
    col = property(lambda self: self[0])
    row = property(lambda self: self[1])


class History:

    def __init__(self, grid_maker):

        self.grid_maker = grid_maker
        self._memory = []

    words = property(lambda self: tuple(item[0] for item in self._memory))

    def add(self, word, starting_point, axis):

        self._memory.append([word, starting_point, axis, self.grid_maker.grid.copy(),
                             {"horizontal" : self.grid_maker.starts["horizontal"].copy(),
                              "vertical" : self.grid_maker.starts["vertical"].copy()},
                             self.grid_maker.banned_words.copy()])
        # print(self.grid_maker.banned_words)

    def clear(self):

        self._memory.clear()

    def pop(self):

        return self._memory.pop()


class GridMaker:

    preset = False

    def __init__(self):

        self.grid = numpy.array([])
        self.starts = {"horizontal" : [], "vertical" : []}
        self.history = History(self)
        self.banned_words = []
        self.rebranches = 0

    def add_starting_point(self, axis, row, col):

        self.starts[axis].append(GridSquare((col, row)))

        if axis == "horizontal":
            self.starts[axis].sort(key=lambda point: point[1])
        else:
            self.starts[axis].sort()

    def create(self):

        self.grid = numpy.array([
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
        self.starts = {"horizontal" : [], "vertical" : []}
        self.history.clear()
        self.rebranches = 0

        for i in range(5):
            self.add_starting_point("horizontal", row=i, col=0)
            self.add_starting_point("vertical", row=0, col=i)

        current_axis = "vertical"  # starts with horizontal

        blocked = False
        while blocked is False:

            current_axis = "vertical" if current_axis == "horizontal" else "horizontal"
            current_start_list = self.starts[current_axis]

            if not current_start_list:
                if not self.starts["vertical" if current_axis == "horizontal" else "horizontal"]:
                    return self.grid  # DONE !!!
                continue

            starting_point = current_start_list.pop(0)

            word = self.find_word(current_axis, starting_point)

            if word is None:
                # There is 0 or 1 square for the word
                continue

            elif word is False:
                # No match

                if self.rebranches % 20 == 0:
                    print(self.grid)
                # print(self.grid)

                old_starting_point = starting_point
                wrong_word, starting_point, axis, self.grid, self.starts, self.banned_words = self.history.pop()
                self.banned_words.append(wrong_word)
                # self.starts[current_axis].insert(0, old_starting_point)
                current_axis = "vertical" if axis == "horizontal" else "horizontal"
                self.starts[axis].insert(0, starting_point)
                self.rebranches += 1

                # print("WRONG", wrong_word, starting_point, axis, "            ", self.starts)
                if self.rebranches < 500:
                    continue
                else:
                    # return None
                    continue

            else:
                self.write(word, current_axis, starting_point)
                self.banned_words.clear()

    def find_word(self, axis, starting_point):

        if axis == "horizontal":
            space = list(self.get_row(row=starting_point.row, from_col=starting_point.col))
        else:
            space = list(self.get_col(col=starting_point.col, from_row=starting_point.row))

        try:
            index = space.index('■')

        except ValueError:
            pass

        else:
            if index < 2:
                return None

            else:
                space = space[:index]

        startswith = ""
        for letter in space:
            if letter == ' ':
                break
            startswith += letter

        if starting_point == (0, 0):

            if axis == "horizontal":  # first word
                # if self.banned_words:
                #     print("A BANNED START WORD :", self.banned_words)
                #     exit()
                while True:
                    word = random.choice(words_by_len[10])
                    if word[0] in 'xy':
                        continue  # only xenophobie & yougoslave are valid
                    if word in self.banned_words:
                        continue
                    return word

            else:  # second word
                availible = words_by_len[10].copy()
                random.shuffle(availible)
                while True:
                    if not availible:
                        return False
                    word = availible.pop()
                    if word in self.history.words:
                        continue
                    if word in self.banned_words:
                        continue
                    if word[0] == startswith:
                        return word

        try:
            matching_words = words_by_start[startswith]

        except KeyError:
            # print(f'No word starts with {startswith}')
            return False

        # if end is None:
        max_length = len(space)
        matching_words = list(word for word in matching_words if length_without_hyphen(word) <= max_length)

        if not matching_words:
            # print(f'No word starts with {startswith} and has a length less than or equal to {max_length}')
            return False

        letter_constraints = []
        for i, letter in enumerate(space):
            if i < len(startswith):
                continue
            if letter != ' ':
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

            # check for duplicates
            if potential_word in self.history.words:
                continue

            # check for ban
            if potential_word in self.banned_words:
                continue

            # check for perpendicular future words
            if axis == "horizontal":

                potential_word_plus_end = potential_word
                if starting_point.col + len(potential_word) < 10:
                    potential_word_plus_end += '■'
                for i, letter in enumerate(potential_word_plus_end):

                    if i < len(startswith):
                        continue
                    if i in letter_constraints:
                        continue

                    letter_case = (starting_point.col + i, starting_point.row)  # (col, row)
                    start_other_axis = letter
                    if start_other_axis == '■':
                        start_other_axis = ''
                    before_case = list(letter_case)
                    # before_case = GridSquare(letter_case)

                    while True:
                        before_case[1] -= 1

                        if before_case[1] < 0:
                            break

                        case = self.get_letter(col=before_case[0], row=before_case[1])
                        if case == '■':
                            break
                        if case == ' ':
                            start_other_axis = ""
                        else:
                            start_other_axis = case + start_other_axis

                    if letter == '■':
                        if not start_other_axis in words:
                            match = False
                            break
                    else:
                        if not start_other_axis in words_by_start:
                            match = False
                            break
            else:

                potential_word_plus_end = potential_word
                if starting_point.row + len(potential_word) < 10:
                    potential_word_plus_end += '■'
                for i, letter in enumerate(potential_word_plus_end):

                    if i < len(startswith):
                        continue
                    if i in letter_constraints:
                        continue

                    letter_case = (starting_point.col, starting_point.row + i)  # (col, row)
                    start_other_axis = letter
                    if start_other_axis == '■':
                        start_other_axis = ''
                    before_case = list(letter_case)
                    # before_case = GridSquare(letter_case)

                    while True:
                        before_case[0] -= 1

                        if before_case[0] < 0:
                            break

                        case = self.get_letter(col=before_case[0], row=before_case[1])
                        if case == '■':
                            break
                        if case == ' ':
                            start_other_axis = ""
                        else:
                            start_other_axis = case + start_other_axis


                    if letter == '■':
                        if not start_other_axis in words:
                            match = False
                            break
                    else:
                        if not start_other_axis in words_by_start:
                            match = False
                            break

            if match is False:
                continue

            return potential_word

        if word is None:
            # print(f"No word matches the conditions from {starting_point}")
            return False

    def get_col(self, col, from_row):

        return self.grid[from_row:, col]

    def get_letter(self, col, row):

        return self.grid[row, col]

    def get_row(self, row, from_col):

        return self.grid[row, from_col:]

    def set_col(self, word, col, from_row):

        word_len = len(word)
        self.grid[from_row:from_row + word_len, col] = list(word)

    def set_row(self, word, row, from_col):

        word_len = len(word)
        self.grid[row, from_col:from_col + word_len] = list(word)

    def write(self, word, axis, starting_point):

        shortened_word = word.replace('-', '')
        word_len = len(shortened_word)
        black_square = None

        self.history.add(shortened_word, starting_point, axis)  # save before write

        if axis == "horizontal":
            self.set_row(word=shortened_word, row=starting_point.row, from_col=starting_point.col)
            if starting_point.col + word_len < 10:
                black_square = GridSquare((starting_point.col + word_len, starting_point.row))
        else:
            self.set_col(word=shortened_word, col=starting_point.col, from_row=starting_point.row)
            if starting_point.row + word_len < 10:
                black_square = GridSquare((starting_point.col, starting_point.row + word_len))

        if black_square is not None and self.get_letter(*black_square) != '■':
            assert self.get_letter(*black_square) == ' '
            self.grid[black_square.row, black_square.col] = '■'

            if black_square.col < 8:
                self.add_starting_point("horizontal", col=black_square.col + 1, row=black_square.row)
            if black_square.row < 8:
                self.add_starting_point("vertical", col=black_square.col, row=black_square.row + 1)

        # print(shortened_word, axis, starting_point)
        # a = self.get_letter(col=1, row=0)
        # b = self.grid[0,1]


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


import time
start_time = time.time()

grid_maker = GridMaker()
trials = 0
while True:
    trials += 1
    grid = grid_maker.create()
    if grid is not None:
        print(grid)

        time_used = time.time() - start_time
        print(f" SUCCESS !!!! after {trials} trials, {grid_maker.rebranches} rebranches and "
              f"{format_time(time=time_used, formatter='%H hours, %M minutes and %S seconds')} !!\n")
        break
    else:
        print(grid_maker.grid)

if False:
    with open(f"grille{int(time.time())}.txt", 'w', encoding='utf8') as writer:
        for i in range(10):

            row = grid[i, :]

            word = ""
            for char in row:
                word += char

            writer.write(word + '\n')

        writer.write(f"\nFound after {trials} trials and "
                     f"{format_time(time=time_used, formatter='%H hours, %M minutes and %S seconds')}")
