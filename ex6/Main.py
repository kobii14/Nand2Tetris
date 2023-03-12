"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    parser = Parser(input_file)
    symbol_table = SymbolTable()
    idx_address = 0
    # first pass
    while parser.has_more_commands():
        if parser.current_instruction=='D=-1':
            print("dd")
        if parser.command_type() != 'L_COMMAND':
            idx_address += 1
        else:  ## L command >>> add new symbol to symbol table
            new_symbol = parser.symbol()
            symbol_table.add_entry(new_symbol, idx_address)
        parser.advance()
    # RETURN TO FIRST INSTRUCTION FOR SECOND PASS
    parser.idx_cur_ins = 0
    if parser.input_file[0].startswith("/"):
        parser.advance()
    else:
        parser.current_instruction = parser.input_file[0]
    # second pass
    n = 16
    while parser.has_more_commands():
        # print(parser.current_instruction)

        if parser.command_type() == 'A_COMMAND':
            n = a_command(parser, symbol_table, n)
        elif parser.command_type() == "C_COMMAND":
            c_command(parser)
        parser.advance()
    # handle the last command
    if parser.current_instruction==parser.input_file[-1]:
        if parser.command_type() == 'A_COMMAND':
            a_command(parser, symbol_table, n)
        elif parser.command_type() == "C_COMMAND":
            c_command(parser)


def a_command(parser: Parser, symbol_table: SymbolTable, n: int):
    symbol = parser.symbol()
    if not symbol.isnumeric():  # XXX isn't numeric
        if symbol_table.contains(symbol):  # XXX in symbol table
            address = symbol_table.symbol_table[symbol]
            binary_rep = format(int(address), 'b')
        else:  # XXX not in symbol table >>> add new entry
            symbol_table.add_entry(symbol, n)
            binary_rep = format(int(n), 'b')
            n += 1
    else:  # XXX IS NUMBER
        binary_rep = format(int(symbol), 'b')
    how_many_add_zeros = 16 - len(binary_rep)
    zeros = "0" * how_many_add_zeros
    binary_rep = zeros + binary_rep
    output_file.write(binary_rep + '\n')
    return n


def c_command(parser: Parser):
    ## GET mnemonics
    dest_MNC = parser.dest()
    comp_MNC = parser.comp()
    jump_MNC = parser.jump()
    ##  CONVERT SUB INSTRUCTION TO BINARY
    dest_bin = Code.dest(dest_MNC)
    comp_bin = Code.comp(comp_MNC)
    jump_bin = Code.jump(jump_MNC)

    if len(comp_bin) == 7:
        c_command_bin = "1" * 3 + comp_bin + dest_bin + jump_bin + '\n'
    else:
        c_command_bin = comp_bin + dest_bin + jump_bin + '\n'

    output_file.write(c_command_bin)


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"

        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)