"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line’s end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """
    arithmetic_list = ['add', 'sub', 'neg', 'eq',
                       'gt', 'lt', 'and', 'or', 'not',
                       'shiftleft', 'shiftright']

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.input_file = input_file.read().splitlines()
        command_list=[]
        for line in self.input_file:
            if line.startswith("//") or line == "":
                continue
            else:
                index_of_backslash = line.find("/")
                if index_of_backslash != -1:
                    line=line[0:index_of_backslash]
                if index_of_backslash != -1:
                    line=line[0:index_of_backslash]

                command_list.append(line)
        self.input_file=command_list

        for i in range(len(self.input_file)):
            index_back_slash = self.input_file[i].find("/")
            if index_back_slash != -1 and index_back_slash != 0:
                self.input_file[i] = self.input_file[i][:index_back_slash]

        self.last_instruction = len(self.input_file)
        self.idx_cur_ins = 0
        if self.input_file[0].startswith("/"):
            self.advance()
        else:
            self.current_instruction = self.input_file[0]

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        if self.idx_cur_ins<self.last_instruction-1:
            return True
        return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        if self.has_more_commands():
            self.idx_cur_ins += 1

            command = self.input_file[self.idx_cur_ins]
            command_one_space = " ".join(command.split())
            self.current_instruction = command_one_space
        else:
            return

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        index_of_first_space = self.current_instruction.find(" ")
        if index_of_first_space == -1:
            command = self.current_instruction
        else:
            command = self.current_instruction[:index_of_first_space]
        if command in self.arithmetic_list:
            return "C_ARITHMETIC"
        elif command == 'push':
            return "C_PUSH"
        elif command == 'pop':
            return "C_POP"
        elif command == 'label':
            return "C_LABEL"
        elif command == 'goto':
            return "C_GOTO"
        elif command == 'if-goto':
            return "C_IF"
        elif command == 'function':
            return "C_FUNCTION"
        elif command == 'return':
            return "C_RETURN"
        elif command == 'call':
            return "C_CALL"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """

        command_list = self.current_instruction.split()
        if self.command_type() == "C_ARITHMETIC":
            return command_list[0]
        else:
            return command_list[1]


    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        command_list = self.current_instruction.split()
        return int(command_list[2])
