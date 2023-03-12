"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """
    unary_list = ['-' , '~' , '^' , '#']
    DOUBLE_SPACE = "  "
    special_tkn = {'<': '&lt;', '>': '&gt;', '&': '&amp;',
                  '"':'&qout'}## hceacl1!!!!!!!
    statement_type = ['let', 'if', 'while', 'do', 'return']
    operator_list=['+' , '-' , '*' , '/' , '&' , '|' , '<' , '>' , '=']

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """

        # output_stream.write("Hello world! \n")
        self.jack_tkn = input_stream
        self.out_stream = output_stream
        self.counter = 0
        self.compile_class()


        # - type: 'int' | 'char' | 'boolean' | className

        # - className: identifier
        # - subroutineName: identifier
        # - varName: identifier

    def compile_class(self) -> None:
        '''class: 'class' className '{' classVarDec* subroutineDec* '}'
        '''
        self.out_stream.write('<class>\n')
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE + self.tkn2xml())  ## class
        self.jack_tkn.advance()
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE + self.tkn2xml())  ## classname
        self.jack_tkn.advance()
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE + self.tkn2xml())  ## {
        self.jack_tkn.advance()
        ##clas var declaration
        while self.jack_tkn.cur_tkn in ['static', 'field']:
            self.counter+=1
            self.compile_class_var_dec()
            self.counter-=1
        ## subroutine declaration
        while self.jack_tkn.cur_tkn in ['constructor', 'function', 'method']:
            self.counter += 1
            self.compile_subroutine()
            self.counter -= 1

        self.out_stream.write(CompilationEngine.DOUBLE_SPACE + self.tkn2xml())  ## }
        self.jack_tkn.advance()
        self.out_stream.write('</class>\n')

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration.
         classVarDec: ('static' | 'field') type varName (',' varName)* ';'"""
        self.out_stream.write((self.counter) * CompilationEngine.DOUBLE_SPACE + '<classVarDec>\n')
        while self.jack_tkn.cur_tkn != ';':
            self.out_stream.write(
                CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## static | field
            self.jack_tkn.advance()
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## ;
        self.jack_tkn.advance()
        self.out_stream.write((self.counter) * CompilationEngine.DOUBLE_SPACE +'</classVarDec>\n')

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        subroutineDec: ('constructor' | 'function' | 'method') =A
                        ('void' | type) =B
                        subroutineName
                        '(' parameterList ')'
                        subroutineBody= '{' varDec* statements '}'
        """
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '<subroutineDec>\n')
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## A
        self.jack_tkn.advance()
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## B
        self.jack_tkn.advance()
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## sunR name
        self.jack_tkn.advance()
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## (
        self.jack_tkn.advance()
        ## param list
        self.counter += 1
        self.compile_parameter_list()
        self.counter -= 1
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## )
        self.jack_tkn.advance()
        ##subroutine
        self.counter += 1
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '<subroutineBody>\n')
        self.counter += 1
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  ## {
        self.jack_tkn.advance()
        ## var declaration
        while self.jack_tkn.cur_tkn == 'var':
            self.compile_var_dec()
        self.counter -= 1
        ## statements
        self.counter += 1
        self.compile_statements()
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  ## }
        self.jack_tkn.advance()
        self.counter -= 1
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '</subroutineBody>\n')
        self.counter -= 1
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '</subroutineDec>\n')

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
         parameterList: ((type varName) (',' type varName)*)?
        """
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '<parameterList>\n')
        while self.jack_tkn.cur_tkn != ')':
            self.out_stream.write(
                CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ##(type name ,)^
            self.jack_tkn.advance()
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '</parameterList>\n')

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # - varDec: 'var' type varName (',' varName)* ';'
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '<varDec>\n')  ##var dec
        while self.jack_tkn.cur_tkn != ';':
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ##(tpye name)^
            self.jack_tkn.advance()
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## ;
        self.jack_tkn.advance()
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '</varDec>\n')  ##var dec

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """

        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '<statements>\n')
        self.counter += 1
        while self.jack_tkn.cur_tkn in CompilationEngine.statement_type:

            if self.jack_tkn.cur_tkn == 'let':
                self.compile_let()
            elif self.jack_tkn.cur_tkn == 'if':
                self.compile_if()
            elif self.jack_tkn.cur_tkn == 'do':
                self.compile_do()
            elif self.jack_tkn.cur_tkn == 'while':
                self.compile_while()
            elif self.jack_tkn.cur_tkn == 'return':
                self.compile_return()
        self.counter -= 1
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '</statements>\n')


    def compile_do(self) -> None:
        """Compiles a do statement."""
        # doStatement: 'do' subroutineCall ';'
        #subroutineCall=subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '<doStatement>\n')
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ##do
        self.jack_tkn.advance()
         ##()
        while self.jack_tkn.cur_tkn != "(":
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ##subroutineName
            self.jack_tkn.advance()
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ##(
        self.jack_tkn.advance()
        self.counter += 1
        self.compile_expression_list()
        self.counter -= 1
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ##)
        self.jack_tkn.advance()
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ##;
        self.jack_tkn.advance()

        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '</doStatement>\n')

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # # - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '<letStatement>\n')
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ##let
        self.jack_tkn.advance()
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ##varname
        self.jack_tkn.advance()
        if self.jack_tkn.cur_tkn == '[':
            self.counter += 1
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml()) ##[
            self.jack_tkn.advance()
            self.compile_expression() ##expression
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())## ]
            self.jack_tkn.advance()
            self.counter -= 1
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## =
        self.jack_tkn.advance()
        self.counter += 1
        self.compile_expression()
        self.counter -= 1
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## ;
        self.jack_tkn.advance()
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '</letStatement>\n')

    def compile_while(self) -> None:

        """Compiles a while statement.
        'while' '(' 'expression' ')' '{' statements '}'
        """
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '<whileStatement>\n')
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ##while
        self.jack_tkn.advance()
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## (
        self.jack_tkn.advance()
        self.counter+=1
        self.compile_expression()
        self.counter -= 1
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## )
        self.jack_tkn.advance()
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## {
        self.jack_tkn.advance()
        self.counter+=1
        self.compile_statements()
        self.counter-=1

        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## }
        self.jack_tkn.advance()
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '</whileStatement>\n')

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # returnStatement: 'return' expression? ';'
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '<returnStatement>\n')
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ##return
        self.jack_tkn.advance()
        if self.jack_tkn.cur_tkn != ';':  ##there is expression
            self.counter+=1
            self.compile_expression()
            self.counter -= 1
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## ;
        self.jack_tkn.advance()
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '</returnStatement>\n')

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        #  ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '<ifStatement>\n')
        self.counter+=1
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter ) + self.tkn2xml())  ##if
        self.jack_tkn.advance()
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  ##(
        self.jack_tkn.advance()
        self.compile_expression()  ##exprssion
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  ##)
        self.jack_tkn.advance()

        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  ## {
        self.jack_tkn.advance()
        self.compile_statements()
        self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  ## }
        self.jack_tkn.advance()
        if self.jack_tkn.cur_tkn == 'else':  ##there is else
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter ) + self.tkn2xml())  ## else
            self.jack_tkn.advance()
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter ) + self.tkn2xml())  ## {
            self.jack_tkn.advance()
            self.compile_statements()
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter ) + self.tkn2xml())  ## }
            self.jack_tkn.advance()
        self.counter-=1
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '</ifStatement>\n')

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # term (op term)*
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '<expression>\n')
        self.counter += 1
        self.compile_term() ##term
        while self.jack_tkn.cur_tkn in CompilationEngine.operator_list:
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  ## op
            self.jack_tkn.advance()
            self.compile_term()
        self.counter -= 1
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '</expression>\n')

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.

        term: integerConstant | stringConstant | keywordConstant | varName |
            varName '['expression']' | subroutineCall | '(' expression ')' |
            unaryOp term
        """
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '<term>\n')
        if self.jack_tkn.commands[self.jack_tkn.cur_ind+1] =='[': ##array var
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  #varname
            self.jack_tkn.advance()
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  # [
            self.jack_tkn.advance()
            self.compile_expression()
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  # ]
            self.jack_tkn.advance()

        elif self.jack_tkn.commands[self.jack_tkn.cur_ind] == '(':
            self.counter += 1
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  # (
            self.jack_tkn.advance()
            self.compile_expression()
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  # )
            self.counter -= 1
            self.jack_tkn.advance()
        ##unary operation
        elif self.jack_tkn.commands[self.jack_tkn.cur_ind] in CompilationEngine.unary_list:
            self.counter+=1
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  # UN_OPERATOR
            self.jack_tkn.advance()
            self.compile_term()
            self.counter -= 1
        ##subroutine call
        elif self.jack_tkn.commands[self.jack_tkn.cur_ind+1]=='(' or self.jack_tkn.commands[self.jack_tkn.cur_ind+1]=='.':
            self.counter+=1
            while self.jack_tkn.cur_tkn!='(': ##name function
                self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  #
                self.jack_tkn.advance()
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  # (
            self.jack_tkn.advance()
            self.compile_expression_list()
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  #)
            self.jack_tkn.advance()
            self.counter-=1
        else:
            self.counter+=1
            self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  # ]
            self.jack_tkn.advance()
            self.counter-=1
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '</term>\n')

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions.
        (expression (',' expression)* )?"""
        #
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '<expressionList>\n')
        while self.jack_tkn.cur_tkn != ')':
            self.counter += 1
            if self.jack_tkn.cur_tkn==',':
                self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter) + self.tkn2xml())  #
                self.jack_tkn.advance()
            self.compile_expression()
            self.counter -= 1
        self.out_stream.write(self.counter * CompilationEngine.DOUBLE_SPACE + '</expressionList>\n')

    def tkn2xml(self):
        """
        convert the token to his xml code according his type
        :return: xml code
        """

        if self.jack_tkn.token_type() == "KEYWORD":
            s1 = ('<', self.jack_tkn.token_type().lower(), '> ', self.jack_tkn.cur_tkn,
                  ' </', self.jack_tkn.token_type().lower(), '>\n')
            return "".join(s1)
        elif self.jack_tkn.token_type() == "SYMBOL":
            if self.jack_tkn.symbol() in ['<', '>', '&']:
                s2 = (
                '<', self.jack_tkn.token_type().lower(), '> ', CompilationEngine.special_tkn[self.jack_tkn.symbol()],
                ' </',
                self.jack_tkn.token_type().lower(), '>\n')
            else:
                s2 = ('<', self.jack_tkn.token_type().lower(), '> ', self.jack_tkn.symbol(), ' </',
                      self.jack_tkn.token_type().lower(), '>\n')
            return ("".join(s2))
        elif self.jack_tkn.token_type() == "INT_CONST":
            s3 = ('<', "integerConstant", '> ', str(self.jack_tkn.int_val()), ' </', 'integerConstant', '>\n')
            return "".join(s3)
        elif self.jack_tkn.token_type() == "STRING_CONST":
            s4 = '<', "stringConstant", '> ', self.jack_tkn.string_val(), ' </', 'stringConstant', '>\n'
            return "".join(s4)
        elif self.jack_tkn.token_type() == "IDENTIFIER":
            s5 = ('<', "identifier", '> ', self.jack_tkn.identifier(), ' </', 'identifier', '>\n')
            return "".join(s5)
