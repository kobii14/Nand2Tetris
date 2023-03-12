"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

from SymbolTable import SymbolTable
from VMWriter import VMWriter
from JackTokenizer import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """
    unary_list = {'-':'neg', '~':'not', '^':'shiftleft', '#':'shiftright'}
    special_tkn = {'<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&qout'}
    statement_type = ['let', 'if', 'while', 'do', 'return']
    operator_list = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    dict_operators={'+':"add",'-':'sub','=':"eq", '>':"gt", '<':"lt",
                    '&':"AND", '|':"OR", '<<':"shiftleft", '>>':"shifright"}
    SEG= {"static": "static", "local": 'local', "field": "this",'arg': 'argument'}

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.jack_tkn = input_stream
        self.writer = VMWriter(output_stream)
        self.symbol_table = SymbolTable()
        self.counter = 0
        self.label = 0
        self.compile_class()

    def compile_class(self) -> None:
        self.jack_tkn.advance() ##class
        self.class_name=self.jack_tkn.cur_tkn ##class name
        self.jack_tkn.advance() ##{
        ##clas var declaration
        self.jack_tkn.advance()  ##var
        while self.jack_tkn.cur_tkn in ['static', 'field']:
            self.compile_class_var_dec()
        ## subroutine declaration
        while self.jack_tkn.cur_tkn in ['constructor', 'function', 'method']:
            self.compile_subroutine()

        self.jack_tkn.advance()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration.
         classVarDec: ('static' | 'field') type varName (',' varName)* ';'"""
        kind_var = self.jack_tkn.cur_tkn.upper()
        self.jack_tkn.advance()
        type_var = self.jack_tkn.cur_tkn
        self.jack_tkn.advance()
        while self.jack_tkn.cur_tkn != ';':
            self.symbol_table.define(self.jack_tkn.cur_tkn, type_var, kind_var)
            self.jack_tkn.advance()
            if self.jack_tkn.cur_tkn == ';':
                break
            self.jack_tkn.advance()  ##??????
        self.jack_tkn.advance()  ## go after ;

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
        self.symbol_table.start_subroutine()
        type_func = self.jack_tkn.cur_tkn
        self.jack_tkn.advance()  ##B
        void_flag = self.jack_tkn.cur_tkn
        self.jack_tkn.advance()  ## subr name
        subr_name=self.class_name+'.'+self.jack_tkn.cur_tkn
        if type_func == 'method':
            self.symbol_table.define('this', self.class_name, 'ARG')
        self.jack_tkn.advance()  ## (
        self.jack_tkn.advance()
        ## param list
        n_args=self.compile_parameter_list()
        self.jack_tkn.advance()
        ## subroutine
        ##{
        self.jack_tkn.advance()
        ## var declaration
        n_loclas=0
        while self.jack_tkn.cur_tkn == 'var':
            n_loclas += self.compile_var_dec()
        self.writer.write_function(subr_name, n_loclas)
        if type_func == 'method':
            self.writer.write_push('argument',0)
            self.writer.write_pop('pointer',0)
        if type_func == 'constructor':
            n=0
            for j in self.symbol_table.symbol_table_class.values():
                if j[1]=='FIELD':
                    n+=1
            self.writer.write_push('constant',n)
            self.writer.write_call('Memory.alloc',1)
            self.writer.write_pop('pointer',0)
        ## statements
        self.compile_statements()
        self.jack_tkn.advance()

    def compile_parameter_list(self) -> int:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
         parameterList: ((type varName) (',' type varName)*)?
        """
        n_args=0
        while self.jack_tkn.cur_tkn != ')':
            arg_type = self.jack_tkn.cur_tkn
            self.jack_tkn.advance()
            arg_name = self.jack_tkn.cur_tkn
            kind = 'ARG'
            self.symbol_table.define(arg_name, arg_type, kind)
            n_args+=1
            if self.jack_tkn.cur_tkn == ')':
                break
            self.jack_tkn.advance()
            if self.jack_tkn.cur_tkn == ',':
                self.jack_tkn.advance()
        return n_args

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # - varDec: 'var' type varName (',' varName)* ';'
        self.jack_tkn.advance()
        var_type = self.jack_tkn.cur_tkn
        count_vars=0
        while self.jack_tkn.cur_tkn != ';':
            self.jack_tkn.advance()
            var_name = self.jack_tkn.cur_tkn
            self.symbol_table.define(var_name,var_type,'VAR')
            count_vars += 1
            self.jack_tkn.advance()
            if self.jack_tkn.cur_tkn == ';':
                break
        self.jack_tkn.advance()
        return count_vars

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
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

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # doStatement: 'do' subroutineCall ';'
        ##do Output.printInt(1 + (2 * 3));
        # subroutineCall=subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'
        self.jack_tkn.advance()
        self.subroutine_call()
        self.writer.write_pop('temp',0)
        self.jack_tkn.advance()
        self.jack_tkn.advance()

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # # - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        self.jack_tkn.advance() ## VARNAME
        var_name=self.jack_tkn.cur_tkn
        self.jack_tkn.advance() ## [ OR =
        flag_arr=False
        if self.jack_tkn.cur_tkn == '[':
            flag_arr = True
            self.jack_tkn.advance()
            self.compile_expression()  ##expression
            self.jack_tkn.advance()
            seg = self.symbol_table.kind_of(var_name)
            idx = self.symbol_table.index_of(var_name)
            self.writer.write_push(CompilationEngine.SEG[seg],idx)
            self.writer.write_arithmetic('ADD')
        self.jack_tkn.advance() ## EXP after =
        self.compile_expression()
        if flag_arr:
            self.writer.write_pop('temp',0)
            self.writer.write_pop('pointer',1)
            self.writer.write_push('temp',0)
            self.writer.write_pop('that',0)
        else:
            seg=self.symbol_table.kind_of(var_name)
            idx=self.symbol_table.index_of(var_name)
            if seg == 'field':
                self.writer.write_pop('this',idx)
            else:
                self.writer.write_pop(CompilationEngine.SEG[seg], idx)
        self.jack_tkn.advance()## ;

    def compile_while(self) -> None:

        """Compiles a while statement.
        'while' '(' 'expression' ')' '{' statements '}'
        """
        # self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ##while
        self.jack_tkn.advance()
        # self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## (
        self.jack_tkn.advance()
        label1='WHILE_EXP'+str(self.label) ## L1
        label2 = 'WHILE_END'+str(self.label) ## L2
        self.label+=1
        self.writer.write_label(label1)
        self.compile_expression()
        self.writer.write_arithmetic('NOT')
        # self.out_stream.write(CompilationEngine.DOUBLE_SPACE * (self.counter + 1) + self.tkn2xml())  ## )
        self.jack_tkn.advance()
        self.jack_tkn.advance()
        self.writer.write_if(label2)
        self.compile_statements()
        self.writer.write_goto(label1)
        self.writer.write_label(label2)
        self.jack_tkn.advance()

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # returnStatement: 'return' expression? ';'
        self.jack_tkn.advance()
        if self.jack_tkn.cur_tkn != ';':  ##there is expression
            self.compile_expression()
        else: ## void func
            self.writer.write_push('constant',0)
        self.writer.write_return()
        self.jack_tkn.advance()

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        #  ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        label1='IF_TRUE'+str(self.label) ## L1
        label2 = 'IF_FALSE'+str(self.label) ## L2
        self.label += 1
        self.jack_tkn.advance()##  (
        self.jack_tkn.advance() ## exp
        self.compile_expression()  ##exprssion
        self.jack_tkn.advance() ## )
        self.writer.write_arithmetic('NOT')
        self.writer.write_if(label1)
        self.jack_tkn.advance()
        self.compile_statements()
        self.jack_tkn.advance()
        self.writer.write_goto(label2)
        self.writer.write_label(label1)
        if self.jack_tkn.cur_tkn == 'else':  ##there is else
            self.jack_tkn.advance()
            self.jack_tkn.advance()
            self.compile_statements()
            self.jack_tkn.advance()
        self.writer.write_label(label2)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # term (op term)*

        self.compile_term()  ##term
        while self.jack_tkn.cur_tkn in CompilationEngine.operator_list:
            op = self.jack_tkn.cur_tkn
            self.jack_tkn.advance()
            self.compile_term()
            if op == '*':
                self.writer.write_call('Math.multiply',2)
            elif op == '/':
                self.writer.write_call('Math.divide', 2)
            else:
                self.writer.write_arithmetic(CompilationEngine.dict_operators[op])

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
        flag_arr=False
        token = self.jack_tkn.cur_tkn
        seg = self.symbol_table.kind_of(token)
        if self.jack_tkn.token_type() == 'STRING_CONST':
            string = self.jack_tkn.string_val()
            length = len(string)
            string_ascii=self.jack_tkn.string_val().encode(encoding="ascii")
            self.writer.write_push('constant',length)
            self.writer.write_call('String.new',1)
            for char in string_ascii:
                self.writer.write_push('constant',char)
                self.writer.write_call('String.appendChar', 2)
            self.jack_tkn.advance()
        elif token == 'this':
            self.writer.write_push('pointer', 0)
            self.jack_tkn.advance()
        elif token == 'true':
            self.writer.write_push('constant',0)
            self.writer.write_arithmetic('NOT')
            self.jack_tkn.advance()
        elif token=='false' or token == 'null':
            self.writer.write_push('constant', 0)
            self.jack_tkn.advance()
        elif token == '(':
            self.jack_tkn.advance()
            self.compile_expression()
            self.jack_tkn.advance()
        ##array
        elif self.jack_tkn.commands[self.jack_tkn.cur_ind + 1] == '[':
            self.jack_tkn.advance() ##arr
            self.jack_tkn.advance() ##[
            self.compile_expression() ##exp
            self.jack_tkn.advance() ##]
            idx = self.symbol_table.index_of(token)
            self.writer.write_push(CompilationEngine.SEG[seg], idx)
            self.writer.write_arithmetic('ADD')
            self.writer.write_pop('pointer',1)
            self.writer.write_push('that',0)
            flag_arr = True
        ##unary operation
        elif self.jack_tkn.cur_tkn in CompilationEngine.unary_list:
            op=self.jack_tkn.cur_tkn
            self.jack_tkn.advance()
            self.compile_term()
            self.writer.write_arithmetic(CompilationEngine.unary_list[op])
        ##subroutine call
        elif self.jack_tkn.commands[self.jack_tkn.cur_ind + 1] == '(' or\
                self.jack_tkn.commands[self.jack_tkn.cur_ind + 1] == '.':
            self.subroutine_call()
            self.jack_tkn.advance()
        elif seg != 'None':
            idx = self.symbol_table.index_of(token)
            self.writer.write_push(CompilationEngine.SEG[seg],idx)
            self.jack_tkn.advance()
        elif self.jack_tkn.token_type() == 'INT_CONST':
            self.writer.write_push('constant', self.jack_tkn.int_val())
            self.jack_tkn.advance()


        else:  ##????
            self.jack_tkn.advance()

        return flag_arr

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions.
        (expression (',' expression)* )?"""
        count=0
        while self.jack_tkn.cur_tkn != ')':
            if self.jack_tkn.cur_tkn == ',':
                self.jack_tkn.advance()
            self.compile_expression()
            count += 1
        return count

    def subroutine_call(self):
        subr_name = ''
        flag_method = False
        while self.jack_tkn.cur_tkn != "(":
            subr_name += self.jack_tkn.cur_tkn
            self.jack_tkn.advance()
        if '.' in subr_name:
            arr_name_sub=subr_name.split('.')
            if arr_name_sub[0] in self.symbol_table.symbol_table_subroutine or\
                arr_name_sub[0] in self.symbol_table.symbol_table_class:## it's a var_name
                seg=self.symbol_table.kind_of(arr_name_sub[0])
                idx=self.symbol_table.index_of(arr_name_sub[0])
                self.writer.write_push(CompilationEngine.SEG[seg],idx)##push var name as first argument
                flag_method=True
        else: ##method of this
            self.writer.write_push('pointer', 0)
            flag_method=True
        self.jack_tkn.advance() ## go after (
        n_args=self.compile_expression_list() ##push ret of args
        if flag_method:
            n_args=n_args+1
            idx_point = subr_name.find('.')
            if idx_point!=-1:
                subr_name =self.symbol_table.type_of(arr_name_sub[0])+ '.'+subr_name[idx_point + 1:]
            else:
                subr_name = self.class_name + '.' + subr_name
        self.writer.write_call(subr_name,n_args)

