"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.symbol_table_class = {}
        self.symbol_table_subroutine = {}
        self.count = {"STATIC": 0, "FIELD":0,"ARG": 0, "VAR": 0}


    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.symbol_table_subroutine = {}
        self.count["ARG"] = 0
        self.count["VAR"] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind in ["STATIC", "FIELD"]: ##class variable
            self.symbol_table_class[name] = [type,kind,self.count[kind]]
            self.count[kind] += 1
        elif kind in ["ARG", "VAR"]:## subroutine variable
            self.symbol_table_subroutine[name] = [type, kind, self.count[kind]]
            self.count[kind] += 1


    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        return self.count[kind]

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if name in self.symbol_table_subroutine:
            if  self.symbol_table_subroutine[name][1] =='VAR':
                return 'local'
            else:
                return 'arg'
        elif name in self.symbol_table_class:
            return self.symbol_table_class[name][1].lower()
        else:
            return 'None'

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.symbol_table_subroutine:
            return self.symbol_table_subroutine[name][0]
        elif name in self.symbol_table_class:
            return self.symbol_table_class[name][0]
        else:
            return 'None'


    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.symbol_table_subroutine:
            return self.symbol_table_subroutine[name][2]
        elif name in self.symbol_table_class:
            return self.symbol_table_class[name][2]
        else:
            return 'None'
