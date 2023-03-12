"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    input_lines = ""
    idx_cur_ins = 0

    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:

        self.input_file = input_file.read().splitlines()
        for i in range(len(self.input_file)):
            self.input_file[i] = self.input_file[i].replace(" ", "")
            index_back_slash = self.input_file[i].find("/")
            if index_back_slash != -1 and index_back_slash!=0:
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
        if self.idx_cur_ins < self.last_instruction - 1:
            return True
        return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        if self.has_more_commands():
            self.idx_cur_ins += 1
            line = self.input_file[self.idx_cur_ins]
            while line.startswith('//') or line == '':
                if self.has_more_commands():
                    self.idx_cur_ins += 1
                    line = self.input_file[self.idx_cur_ins]
                else:
                    return
            command = self.input_file[self.idx_cur_ins]
            self.current_instruction = command
        else:
            return

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self.current_instruction.startswith('@'):
            return "A_COMMAND"
        if self.current_instruction.startswith('(') \
                and self.current_instruction.endswith(')'):
            return "L_COMMAND"
        else:
            return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if self.command_type() == "A_COMMAND":
            return self.current_instruction[1:]

        if self.command_type() == "L_COMMAND":
            return self.current_instruction[1:-1]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() == "C_COMMAND":
            index_of_equal = self.current_instruction.find('=')
            if index_of_equal == -1:
                return 'null'
                # index_of_separator = self.current_instruction.find(';')
                # dest = self.current_instruction[0:index_of_separator]
            else:
                dest = self.current_instruction[0:index_of_equal]
            return dest

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() == "C_COMMAND":
            index_of_equal = self.current_instruction.find('=')
            index_of_separator = self.current_instruction.find(';')
            if index_of_separator != -1:
                comp = self.current_instruction[index_of_equal + 1:index_of_separator]
            else:
                comp = self.current_instruction[index_of_equal + 1:]

        return comp

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() == "C_COMMAND":
            index_of_separator = self.current_instruction.find(';')
        if index_of_separator == -1:
            return 'null'
        jump = self.current_instruction[index_of_separator + 1:]
        return jump
