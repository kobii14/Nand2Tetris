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
from Parser import Parser
from CodeWriter import CodeWriter


def translate_file( input_file: typing.TextIO, output_file: typing.TextIO,bootstrap:bool) -> None:
    """Translates a single file.
    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
    """
    parser = Parser(input_file)
    code_writer = CodeWriter(output_file)
    input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
    code_writer.set_file_name(input_filename)
    end_loop = "(END)\n@END\n0;JMP\n"

     ##bootstrap
    if bootstrap:
        sp_init = "@256\nD=A\n@SP\nM=D\n"
        code_writer.output_file.write(sp_init)
        code_writer.write_call("Sys.init", 0)

    while parser.has_more_commands():
        command_type = parser.command_type()
        command_handle(command_type,parser,code_writer)
        cur_ind=parser.idx_cur_ins
        parser.advance()
        if parser.idx_cur_ins == cur_ind:
            break

    last_command = " ".join(parser.input_file[-1].split())
    if parser.current_instruction == last_command:
        command_type = parser.command_type()
        command_handle(command_type,parser,code_writer)
    code_writer.output_file.write(end_loop)


def command_handle(command_type,parser,code_writer):
    if command_type == "C_PUSH" or command_type == "C_POP":
        arg1 = parser.arg1()
        arg2 = parser.arg2()
        code_writer.write_push_pop(command_type, arg1, arg2)
    elif command_type == "C_ARITHMETIC":
        arg1 = parser.arg1()
        code_writer.write_arithmetic(arg1)
    elif command_type == "C_LABEL":
        arg1 = parser.arg1()
        code_writer.write_label(arg1)
    elif command_type == "C_GOTO":
        arg1 = parser.arg1()
        code_writer.write_goto(arg1)
    elif command_type == "C_IF":
        arg1 = parser.arg1()
        code_writer.write_if(arg1)
    elif command_type == "C_FUNCTION":
        arg1 = parser.arg1()
        arg2 = parser.arg2()
        code_writer.write_function(arg1,arg2)
    elif command_type == "C_CALL":
        arg1 = parser.arg1()
        arg2 = parser.arg2()
        code_writer.write_call(arg1,arg2)
    elif command_type == "C_RETURN":
        code_writer.write_return()


if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    # Parses the input path and calls translate_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    bootstrap = True
    with open(output_path, 'w') as output_file:
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file, bootstrap)
            bootstrap = False