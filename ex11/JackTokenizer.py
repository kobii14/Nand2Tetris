"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re


def delete_cmds(start_cmd,line):
    end_cmd='*/'
    while start_cmd in line:
        ind1=line.find(start_cmd)
        ind2 = line.find(end_cmd)
        cmd=line[ind1:ind2+2]
        line=line.replace(cmd,"")
    return line


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    # - class: 'class' className '{' classVarDec* subroutineDec* '}'
    # - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    # - type: 'int' | 'char' | 'boolean' | className
    # - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type)
    # - subroutineName '(' parameterList ')' subroutineBody
    # - parameterList: ((type varName) (',' type varName)*)?
    # -
    # - varDec: 'var' type varName (',' varName)* ';'
    # - className: identifier
    # - subroutineName: identifier
    # - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement


    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    list_keyword = ['class', 'constructor', 'function', 'method', 'field',
                    'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
                    'false', 'null', 'this', 'let', 'do', 'if', 'else',
                    'while', 'return']
    list_symbol = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
                   '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#']


    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.commands = []
        pattern = '([;{}\[\])(\s,+\*\.\-/&|<>=~^#])'
        ## delete pre and post spaces
        input_lines = input_stream.read().splitlines()
        i = 0
        n = len(input_lines)
        while i < n:
            if input_lines[i] == '': ##empty line
                i += 1
                continue
            line = input_lines[i].lstrip().rstrip()
            ## check if its */ or /** comment
            line = re.split('(")', line)
            j = 0
            while j < len(line): ## iterate complex object or strings
                if line[j] == '"': ## next elem is string
                    self.commands.append((line[j]+line[j+1]+line[j+2]))
                    j += 3 ## jump to next object
                    continue
                ind1 = line[j].find("/*")
                ind2 = line[j].find("/**")
                if ind1 != -1 or ind2 != -1:  ## there is /* >> comment >>dont add to commands
                    if line[j].find('*/') == -1:  ## end of comment not in this line
                        ## iterate lines until end comment
                        while not input_lines[i].rstrip().lstrip().endswith("*/") and i + 1 < n:
                            i += 1
                        break
                    else:  ## end cmd in this line
                        line[j] = delete_cmds("/*", line[j])
                        line[j] = delete_cmds("/**", line[j])
                flag_backslash_commend = False
                ind_double_backslash = line[j].find('//')
                if ind_double_backslash != -1: ## there is comment >>> delete it
                    line[j] = line[j][:ind_double_backslash]
                    flag_backslash_commend = True ## if true there is // in sub-line so ignore next sub-lines

                 ## complex object
                word_separeted=re.split(pattern,line[j])
                word_separeted_no_empty_elem = list(filter(lambda x: x != '' and x!=' ' and x!='\t', word_separeted))
                self.commands += word_separeted_no_empty_elem
                if flag_backslash_commend: ## go to next line
                    break
                j += 1
            i += 1
        self.cur_ind = 0
        self.cur_tkn = self.commands[self.cur_ind]
        self.last = len(self.commands)


    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if self.cur_ind < self.last:
            return True
        return False

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.cur_ind += 1
        if self.has_more_tokens():
            self.cur_tkn = self.commands[self.cur_ind]

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.cur_tkn in JackTokenizer.list_keyword:
            return "KEYWORD"
        elif self.cur_tkn in JackTokenizer.list_symbol:
            return "SYMBOL"
        elif self.cur_tkn.startswith('"') and self.cur_tkn.endswith('"'):
            return 'STRING_CONST'
        elif self.cur_tkn.isnumeric():
            return 'INT_CONST'
        elif self.cur_tkn.isidentifier():
            return 'IDENTIFIER'


    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.cur_tkn.upper()


    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        return self.cur_tkn

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.cur_tkn

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return int(self.cur_tkn)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        return self.cur_tkn[1:-1]

