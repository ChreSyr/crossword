

import random


class Grid(tuple):

    def __str__(self):
        return '[' + '\n '.join(str(line) for line in self) + ']'

    def copy(self):
        return Grid((line.copy() for line in self))

    def get_letter(self, col, row):

        return self[row][col]

    def reset(self):
        for line in self:
            line.clear()
            for _ in range(10):
                line.append(' ')

    def set_letter(self, letter, col, row):

        self[row][col] = letter


class GridSquare(tuple):
    col = property(lambda self: self[0])
    row = property(lambda self: self[1])

class EditableGridSquare(list):
    col = property(lambda self: self[0], lambda self, val: self.__setitem__(0, val))
    row = property(lambda self: self[1], lambda self, val: self.__setitem__(1, val))


class History:

    def __init__(self, grid_maker):

        self.grid_maker = grid_maker
        self._memory = []

    def add(self, letter, coord):

        self._memory.append([letter, coord, self.grid_maker.grid.copy(), self.grid_maker.invalid_letters.copy()])

    def clear(self):

        self._memory.clear()

    def pop(self):

        return self._memory.pop()


class GridMaker:

    ALPHABET = "abcdefghijklmnopqrstuvwxyz"
    ALPHABET_BY_FREQUENCE = "eeeeeeeeeeeeaaaaaaaiiiiiissssssnnnnnnrrrrrrtttttooooolllluuuudddcccmmppgbvhfqyxjkwz"

    def __init__(self):

        self.grid = Grid(([], [], [], [], [], [], [], [], [], []))
        self.current_pos = None
        self.history = History(self)
        self.invalid_letters = []
        self.rebranches = 0
        self.rebranch_origin = None

    def create(self):

        self.grid.reset()
        self.current_pos = GridSquare((0, 0))
        self.history.clear()
        self.invalid_letters = []
        self.rebranches = 0
        self.rebranch_origin = None

        while self.current_pos:

            starting_point = self.current_pos
            self.current_pos = None

            letter = self.find_letter(starting_point)

            if letter is False:
                # No match

                if verbose == "a little":
                    if self.rebranches % 1000 == 0:
                        print(self.grid)

                if self.rebranch_origin is None:
                    self.rebranch_origin = starting_point

                go_to_vertical_problem = starting_point.col == 0

                try:
                    wrong_letter, starting_point, self.grid, self.invalid_letters = self.history.pop()

                except IndexError:
                    assert len(self.invalid_letters) == 26
                    assert starting_point == (0, 0)
                    print(" NO MATCH - every possibility has been explored")
                    return None

                if go_to_vertical_problem:
                    while starting_point.col != self.rebranch_origin.col:
                        wrong_letter, starting_point, self.grid, self.invalid_letters = self.history.pop()

                self.invalid_letters.append(wrong_letter)
                self.current_pos = starting_point
                self.rebranches += 1

            else:

                self.history.add(letter, starting_point)  # save before write
                self.grid.set_letter(letter, *starting_point)
                if starting_point.col < 9:
                    self.current_pos = GridSquare((starting_point.col + 1, starting_point.row))
                elif starting_point.row < 9:
                    self.current_pos = GridSquare((0, starting_point.row + 1))
                self.invalid_letters.clear()
                self.rebranch_origin = None

            if verbose == "yes":
                print(self.grid)

        return self.grid  # DONE !!!

    def find_letter(self, coord):

        space = self.grid[coord.row]

        for index, letter in enumerate(reversed(space)):
            if letter == '■':
                space = space[10 - index:]
                break

        startswith = ""
        for letter in space:
            if letter == ' ':
                break
            startswith += letter

        if startswith not in words_by_start:
            return False

        shuffled_alphabet = self.get_advanced_shuffled_alphabet()
        if 0 not in coord:
            shuffled_alphabet.append('■')

        for letter in shuffled_alphabet:

            if letter in self.invalid_letters:
                continue

            if letter == '■':

                if startswith != "" and startswith not in words:
                    self.invalid_letters.append(letter)
                    continue

                # prevent letters in jail
                if coord.row > 0 and self.grid.get_letter(col=coord.col, row=coord.row - 1) != '■':
                    if coord.col > 0 and self.grid.get_letter(col=coord.col - 1, row=coord.row - 1) != '■':
                        pass
                    elif coord.col < 9 and self.grid.get_letter(col=coord.col + 1, row=coord.row - 1) != '■':
                        pass
                    elif coord.row > 1 and self.grid.get_letter(col=coord.col, row=coord.row - 2) != '■':
                        pass
                    else:
                        self.invalid_letters.append('■')
                        continue

                # prevent last row's letter in jail
                if coord.row == 9:
                    if coord.col > 1 and self.grid.get_letter(col=coord.col - 2, row=coord.row) != '■':
                        pass
                    elif self.grid.get_letter(col=coord.col - 1, row=coord.row - 1) != '■':
                        pass
                    else:
                        self.invalid_letters.append('■')
                        continue

                # prevent last letter in jail
                if coord == (8, 9) and self.grid.get_letter(col=9, row=8) == '■':
                    self.invalid_letters.append('■')
                    continue


            else:
                if startswith + letter not in words_by_start:
                    self.invalid_letters.append(letter)
                    continue

                elif coord.row == 0:
                    match = False
                    for horizontal_word in words_by_start[startswith + letter]:
                        if len(horizontal_word) == 10:
                            match = True
                            break
                    if match is False:
                        self.invalid_letters.append(letter)
                        continue

                max_length = len(space)
                matching_words = list(word for word in words_by_start[startswith + letter] if len(word) <= max_length)

                if not matching_words:
                    self.invalid_letters.append(letter)
                    continue

            before_case = EditableGridSquare(coord)  # (col, row)
            vertical_start = letter

            # getting the vertical word
            while True:
                before_case.row -= 1

                if before_case.row < 0:
                    break

                case = self.grid.get_letter(col=before_case.col, row=before_case.row)
                if case == '■':
                    break
                if case == ' ':
                    raise AssertionError
                else:
                    vertical_start = case + vertical_start

            if letter == '■':
                vertical_start = vertical_start[:-1]
                if vertical_start == "" or vertical_start in words:
                    return letter
                else:
                    self.invalid_letters.append(letter)
                    continue

            if not vertical_start in words_by_start:
                self.invalid_letters.append(letter)
                continue

            vertical_max = 9 - coord.row + len(vertical_start)
            vertical_words = words_by_start[vertical_start]

            if coord.col == 0:
                for vertical_word in vertical_words:
                    if len(vertical_word) == 10:
                        return letter

            else:
                for vertical_word in vertical_words:
                    if len(vertical_word) <= vertical_max:
                        return letter

            # If we reach this line, then the letter doesn't match the conditions
            self.invalid_letters.append(letter)

        return False

    def get_shuffled_alphabet(self):

        list_abc = list(self.ALPHABET)
        random.shuffle(list_abc)
        return list_abc

    def get_advanced_shuffled_alphabet(self):
        """
        Return an alphabet shuffled, where the most used letters have more chances to be first
        exemples:
            gneposbdftauirlkhmqvwxcyjz
            nserukogmdalptcbiqhfvzywjx
            etadsunmjrvpyilcxfobqzkghw
            tlndemvsfcuorigaxqyhzpjwkb
            lcsueimtwrjoadnyxkfqgphbvz
            yletiacrxspbondmufzhgkjwqv
            utbsaprneikzclowdmxvjhyfgq
            yonermdvtsbicafpkhgqljxuzw
            zedasrliogvpckfjnbhtuxqwmy
        """

        list_abc = list(self.ALPHABET_BY_FREQUENCE)
        random.shuffle(list_abc)
        # print(''.join(list_abc))
        # for letter in ABC:
        #     for i in range(list_abc.count(letter) - 1):
        #         list_abc.remove(letter)
        for _ in range(11):
            list_abc.remove('e')
        for _ in range(6):
            list_abc.remove('a')
        for _ in range(5):
            list_abc.remove('i')
            list_abc.remove('s')
            list_abc.remove('n')
            list_abc.remove('r')
        for _ in range(4):
            list_abc.remove('t')
            list_abc.remove('o')
        for _ in range(3):
            list_abc.remove('l')
            list_abc.remove('u')
        for _ in range(2):
            list_abc.remove('d')
            list_abc.remove('c')
        for _ in range(1):
            list_abc.remove('m')
            list_abc.remove('p')
        list_abc.reverse()
        return list_abc


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

words = []
hyphen_words = {}
words_by_len = {}
words_by_start = {"" : words}
alphabet = "abcdefghijklmnopqrstuvwxyz"
for l in alphabet:
    words.append(l)
    words_by_start[l] = [l]

for i in range(1, 21):
    words_by_len[i] = []

max_len = 0

def get_input(question, valid_answers):
    if len(valid_answers) == 2:
        question += f" type '{valid_answers[0]}' or '{valid_answers[1]}' : "
    elif len(valid_answers) == 3:
        question += f" type '{valid_answers[0]}', '{valid_answers[1]}' or '{valid_answers[2]}' : "
    else:
        raise NotImplemented
    while True:
        answer = input(question)
        if answer in valid_answers:
            return answer
        else:
            print("Wrong input :", answer)

difficulty = get_input("Which difficulty do you want ?", ("easy", "difficult"))
verbose = get_input("Do you want to keep track of the research ?", ("yes", "a little", "no"))
save = get_input("Do you want to save the result ?", ("yes", "no"))
nb_searches = get_input("Do you want to search once or forever? ?", ("once", "forever"))

def is_fine(word):

    return True

    def is_voyelle(letter):
        return letter in "aeiouy"

    before = None
    for letter in word:
        now = is_voyelle(letter)
        if now == before:
            return False
        before = now

    return True

with open("dictionnaire.txt" if difficulty == "easy" else "fat_dictionnaire.txt", 'r', encoding='utf8') as reader:

    for line in reader.readlines():
        word = line.strip().lower()

        if '-' in word:
            shortened_word = word.replace('-', '')
            hyphen_words[shortened_word] = word
            word = shortened_word

        # if not is_fine(word):
        #     continue

        length = len(word)
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
    print(grid_maker.grid)
    if grid is not None:
        time_used = time.time() - start_time
        print(f" SUCCESS !!!! after {grid_maker.rebranches} rebranches and "
              f"{format_time(time=time_used, formatter='%H hours, %M minutes and %S seconds')} !!\n")

        if save == "yes":
            with open(f"crosswords/crossword n°{int(time.time())}.txt", 'w', encoding='utf8') as writer:
                for i in range(10):

                    row = grid[i, :]
                    writer.write(' '.join(row) + '\n')

                writer.write(f"\nFound after {grid_maker.rebranches} rebranches and "
                             f"{format_time(time=time_used, formatter='%H hours, %M minutes and %S seconds')}")

    if nb_searches == "once":
        break
