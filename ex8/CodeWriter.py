"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    file_name = ""
    label_index = 1
    SP_UP = "@SP\nM=M+1\n"
    SP_DOWN = "@SP\nM=M-1\n"
    x_star_equal_y_star = "@{y}\nA=M\nD=M\n@{x}\nA=M\nM=D\n"
    x_star_equal_y = "@{y}\nD=A\n@{x}\nA=M\nM=D\n"
    label_cont = "(CONT{x})\n"
    cont_operation = "@CONT{x}\n0;JMP\n"

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")

        self.func_name = ""
        self.output_file = output_stream

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        self.file_name = filename

    def write_arithmetic(self, command: str, ) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        if command == "add":
            c_hack = self.SP_DOWN + "A=M\nD=M\n" + self.SP_DOWN + "A=M\nM=M+D\n" + self.SP_UP
        elif command == "sub":
            c_hack = self.SP_DOWN + "A=M\nD=M\n" + self.SP_DOWN + "A=M\nM=M-D\n" + self.SP_UP

        elif command == "eq":
            c_hack = self.SP_DOWN + "A=M\nD=M\n@Y\nM=D\n" \
                                    "@YPOS" + str(CodeWriter.label_index) + "\nD;JGE\n" \
                                                                            "@YNEG" + str(
                CodeWriter.label_index) + "\nD;JLT\n" \
                                          "(YPOS" + str(
                CodeWriter.label_index) + ")\n" \
                     + self.SP_DOWN + "A=M\nD=M\n@X\nM=D\n@YPOSXPOS" + str(CodeWriter.label_index) + "\nD;JGE\n" \
                                                                                                     "@YPOSXNEG" + str(
                CodeWriter.label_index) + "\nD;JLT\n" \
                                          "(YNEG" + str(CodeWriter.label_index) + ")\n" \
                     + self.SP_DOWN + "A=M\nD=M\n@X\nM=D\n@YNEGXPOS" + str(CodeWriter.label_index) + "\nD;JGE\n" \
                                                                                                     "@YNEGXNEG" + str(
                CodeWriter.label_index) + "\nD;JLT\n" \
                                          "(YPOSXPOS" + str(
                CodeWriter.label_index) + ")\n@Y\nD=M\n@X\nD=M-D\n@EQ" + str(
                CodeWriter.label_index) + "\nD;JEQ\n@NEQ" + str(CodeWriter.label_index) + "\nD;JNE\n" \
                                                                                          "(YNEGXNEG" + str(
                CodeWriter.label_index) + ")\n@Y\nD=M\n@X\nD=M-D\n@EQ" + str(
                CodeWriter.label_index) + "\nD;JEQ\n@NEQ" + str(
                CodeWriter.label_index) + "\nD;JNE\n" \
                                          "(YPOSXNEG" + str(CodeWriter.label_index) + ")\n@NEQ" + str(
                CodeWriter.label_index) + "\n0;JMP\n" \
                                          "(YNEGXPOS" + str(CodeWriter.label_index) + ")\n@NEQ" + str(
                CodeWriter.label_index) + "\n0;JMP\n" \
                     + "(EQ" + str(
                CodeWriter.label_index) + ")\n@SP\nA=M\nM=-1\n" + self.SP_UP + self.cont_operation.format(
                x=str(CodeWriter.label_index)) \
                     + "(NEQ" + str(
                CodeWriter.label_index) + ")\n@SP\nA=M\nM=0\n" + self.SP_UP + self.label_cont.format(
                x=str(CodeWriter.label_index))
            CodeWriter.label_index += 1

        elif command == "lt":
            c_hack = self.SP_DOWN + "A=M\nD=M\n@Y\nM=D\n" \
                                    "@YPOS" + str(CodeWriter.label_index) + "\nD;JGE\n" \
                                                                            "@YNEG" + str(
                CodeWriter.label_index) + "\nD;JLT\n" \
                                          "(YPOS" + str(
                CodeWriter.label_index) + ")\n" \
                     + self.SP_DOWN + "A=M\nD=M\n@X\nM=D\n@YPOSXPOS" + str(CodeWriter.label_index) + "\nD;JGE\n" \
                                                                                                     "@YPOSXNEG" + str(
                CodeWriter.label_index) + "\nD;JLT\n" \
                                          "(YNEG" + str(CodeWriter.label_index) + ")\n" \
                     + self.SP_DOWN + "A=M\nD=M\n@X\nM=D\n@YNEGXPOS" + str(CodeWriter.label_index) + "\nD;JGE\n" \
                                                                                                     "@YNEGXNEG" + str(
                CodeWriter.label_index) + "\nD;JLT\n" \
                                          "(YPOSXPOS" + str(
                CodeWriter.label_index) + ")\n@Y\nD=M\n@X\nD=M-D\n@LT" + str(
                CodeWriter.label_index) + "\nD;JLT\n@NLT" + str(CodeWriter.label_index) + "\nD;JGE\n" \
                                                                                          "(YNEGXNEG" + str(
                CodeWriter.label_index) + ")\n@Y\nD=M\n@X\nD=M-D\n@LT" + str(
                CodeWriter.label_index) + "\nD;JLT\n@NLT" + str(
                CodeWriter.label_index) + "\nD;JGE\n" \
                                          "(YPOSXNEG" + str(CodeWriter.label_index) + ")\n@LT" + str(
                CodeWriter.label_index) \
                     + "\n0;JMP\n(YNEGXPOS" + str(
                CodeWriter.label_index) + ")\n@NLT" + str(CodeWriter.label_index) + "\n0;JMP\n" \
                     + "(LT" + str(
                CodeWriter.label_index) + ")\n@SP\nA=M\nM=-1\n" + self.SP_UP + self.cont_operation.format(
                x=str(CodeWriter.label_index)) \
                     + "(NLT" + str(
                CodeWriter.label_index) + ")\n@SP\nA=M\nM=0\n" + self.SP_UP + self.label_cont.format(
                x=str(CodeWriter.label_index))
            CodeWriter.label_index += 1

        elif command == "gt":
            c_hack = self.SP_DOWN + "A=M\nD=M\n@Y\nM=D\n" \
                                    "@YPOS" + str(CodeWriter.label_index) + "\nD;JGE\n" \
                                                                            "@YNEG" + str(
                CodeWriter.label_index) + "\nD;JLT\n" \
                                          "(YPOS" + str(
                CodeWriter.label_index) + ")\n" \
                     + self.SP_DOWN + "A=M\nD=M\n@X\nM=D\n@YPOSXPOS" + str(CodeWriter.label_index) + "\nD;JGE\n" \
                                                                                                     "@YPOSXNEG" + str(
                CodeWriter.label_index) + "\nD;JLT\n" \
                                          "(YNEG" + str(CodeWriter.label_index) + ")\n" \
                     + self.SP_DOWN + "A=M\nD=M\n@X\nM=D\n@YNEGXPOS" + str(CodeWriter.label_index) + "\nD;JGE\n" \
                                                                                                     "@YNEGXNEG" + str(
                CodeWriter.label_index) + "\nD;JLT\n" \
                                          "(YPOSXPOS" + str(
                CodeWriter.label_index) + ")\n@Y\nD=M\n@X\nD=M-D\n@GT" + str(
                CodeWriter.label_index) + "\nD;JGT\n@NGT" + str(CodeWriter.label_index) + "\nD;JLE\n" \
                                                                                          "(YNEGXNEG" + str(
                CodeWriter.label_index) + ")\n@Y\nD=M\n@X\nD=M-D\n@GT" + str(
                CodeWriter.label_index) + "\nD;JGT\n@NGT" + str(
                CodeWriter.label_index) + "\nD;JLE\n" \
                                          "(YPOSXNEG" + str(CodeWriter.label_index) + ")\n@NGT" + str(
                CodeWriter.label_index) + "\n0;JMP\n" \
                                          "(YNEGXPOS" + str(CodeWriter.label_index) + ")\n@GT" + str(
                CodeWriter.label_index) + \
                     "\n0;JMP\n" \
                     + "(GT" + str(
                CodeWriter.label_index) + ")\n@SP\nA=M\nM=-1\n" + self.SP_UP + self.cont_operation.format(
                x=str(CodeWriter.label_index)) \
                     + "(NGT" + str(
                CodeWriter.label_index) + ")\n@SP\nA=M\nM=0\n" + self.SP_UP + self.label_cont.format(
                x=str(CodeWriter.label_index))
            CodeWriter.label_index += 1

        elif command == "neg":
            c_hack = self.SP_DOWN + "A=M\nM=-M\n" + self.SP_UP
        elif command == "and":
            c_hack = self.SP_DOWN + "A=M\nD=M\n" + self.SP_DOWN + "A=M\nM=M&D\n" + self.SP_UP
        elif command == "or":
            c_hack = self.SP_DOWN + "A=M\nD=M\n" + self.SP_DOWN + "A=M\nM=M|D\n" + self.SP_UP
        elif command == "not":
            c_hack = self.SP_DOWN + "A=M\nM=!M\n" + self.SP_UP

        elif command == "shiftleft":
            c_hack = self.SP_DOWN + "A=M\nM=M<<\n" + self.SP_UP

        elif command == "shiftright":
            c_hack = self.SP_DOWN + "A=M\nM=M>>\n" + self.SP_UP

        self.output_file.write(c_hack)

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.

        dict_ptr = {'argument': 'ARG', 'local': 'LCL', 'this': 'THIS',
                    'that': 'THAT', 'temp': '5', 'static': '16', '0': 'THIS', '1': 'THAT'}

        if command == "C_PUSH":
            if segment == "constant":
                c_hack = self.x_star_equal_y.format(x="SP", y=str(index)) + self.SP_UP
            elif segment in ['argument', 'local', 'this', 'that']:
                c_hack = "@" + str(index) + "\nD=A\n@" + dict_ptr[segment] + "\nD=D+M\n@addr" + str(
                    CodeWriter.label_index) + "\nM=D\n"
                c_hack += self.x_star_equal_y_star.format(x='SP', y='addr' + str(CodeWriter.label_index))
                c_hack += self.SP_UP
                CodeWriter.label_index += 1
            elif segment == "temp":
                c_hack = "@" + str(index) + "\nD=A\n@" + dict_ptr[segment] + "\nD=D+A\n@addr" + str(
                    CodeWriter.label_index) + "\nM=D\n" + \
                         self.x_star_equal_y_star.format(x='SP', y='addr' + str(CodeWriter.label_index)) + self.SP_UP
                CodeWriter.label_index += 1
            elif segment == "static":
                c_hack = "@" + self.file_name + "." + str(index) + "\nD=M\n@SP\nA=M\nM=D\n" + self.SP_UP

            elif segment == "pointer":
                c_hack = "@" + dict_ptr[str(index)] + "\nD=M\n@SP\nA=M\nM=D\n" + self.SP_UP

        elif command == "C_POP":
            if segment in ['argument', 'local', 'this', 'that']:
                c_hack = "@" + str(index) + "\nD=A\n@" + dict_ptr[segment] + "\nD=D+M\n@addr" + str(
                    CodeWriter.label_index) + "\nM=D\n"
                c_hack += self.SP_DOWN + self.x_star_equal_y_star.format(x='addr' + str(CodeWriter.label_index), y='SP')
                CodeWriter.label_index += 1
            elif segment == "temp":
                c_hack = "@" + str(index) + "\nD=A\n@" + dict_ptr[segment] + "\nD=D+A\n@addr" + str(
                    CodeWriter.label_index) + "\nM=D\n"
                c_hack += self.SP_DOWN + self.x_star_equal_y_star.format(x='addr' + str(CodeWriter.label_index), y='SP')
                CodeWriter.label_index += 1
            elif segment == "pointer":
                c_hack = self.SP_DOWN + "@SP\nA=M\nD=M\n@" + dict_ptr[str(index)] + "\nM=D\n"
            elif segment == "static":
                c_hack = self.SP_DOWN + "@SP\nA=M\nD=M\n" + "@" \
                         + self.file_name + "." + str(index) + "\nM=D\n"

        self.output_file.write(c_hack)

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        c_hack = "(" + self.func_name + "$" + label + ")\n"
        self.output_file.write(c_hack)

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        c_hack = "@" + self.func_name + "$" + label + "\n"
        c_hack += "0;JMP\n"
        self.output_file.write(c_hack)

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        c_hack = self.SP_DOWN + "A=M\nD=M\n@" + self.func_name + "$" + label + "\nD;JNE\n"
        self.output_file.write(c_hack)

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """

        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        self.func_name = function_name
        cont_label = self.func_name + "$CONT" + str(CodeWriter.label_index)
        loop_label = self.func_name + "$FUNC_LOOP" + str(CodeWriter.label_index)

        c_hack = "(" + function_name + ")\n" \
                                       "@" + str(n_vars) + "\nD=A\n@i"+"\nM=D\n" + "@" + cont_label + "\nD;JEQ\n" + \
                 "(" + loop_label + ")\n@SP\nA=M\nM=0\n@SP\nM=M+1\n@i"+"\nM=M-1\nD=M\n" \
                                    "@" + loop_label + "\nD;JGT\n(" + cont_label + ")\n"
        CodeWriter.label_index += 1
        self.output_file.write(c_hack)

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """

        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        five_plus_n_args = 5 + n_args
        return_address = self.file_name+function_name + "$ret" + str(CodeWriter.label_index)
        c_hack = "@" + return_address + "\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        c_hack += "@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        c_hack += "@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        c_hack += "@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        c_hack += "@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        c_hack += "@" + str(five_plus_n_args) + "\nD=A\n@SP\nD=M-D\n@ARG\nM=D\n"
        c_hack += "@SP\n\nD=M\n@LCL\nM=D\n"
        c_hack += "@" + function_name + "\n0;JMP\n"
        c_hack += "(" + return_address + ")\n"
        CodeWriter.label_index += 1
        self.output_file.write(c_hack)

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""

        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        self.output_file.write("//return\n")
        c_hack = "@LCL\nD=M\n@frame" + str(CodeWriter.label_index) + "\nM=D\n"
        c_hack += "@5\nA=D-A\nD=M\n@RETURN_ADDRESS" + str(CodeWriter.label_index) + "\nM=D\n"
        c_hack += self.SP_DOWN + "A=M\nD=M\n@ARG\nA=M\nM=D\n"
        c_hack += "@ARG\nD=M\n@SP\nM=D+1\n"
        c_hack += "@frame" + str(CodeWriter.label_index) + "\nD=M\n@1\nD=D-A\nA=D\nD=M\n@THAT\nM=D\n"
        c_hack += "@frame" + str(CodeWriter.label_index) + "\nD=M\n@2\nD=D-A\nA=D\nD=M\n@THIS\nM=D\n"
        c_hack += "@frame" + str(CodeWriter.label_index) + "\nD=M\n@3\nD=D-A\nA=D\nD=M\n@ARG\nM=D\n"
        c_hack += "@frame" + str(CodeWriter.label_index) + "\nD=M\n@4\nD=D-A\nA=D\nD=M\n@LCL\nM=D\n"
        c_hack += "@RETURN_ADDRESS" + str(CodeWriter.label_index) + "\nA=M\n0;JMP\n"
        CodeWriter.label_index += 1
        self.output_file.write(c_hack)
