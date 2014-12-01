#!usr/bin/env python

from il_types import *
import arrowc.arrowlang_types as types


class ILGenerator():
    def __init__(self):
        self.reg_table = dict()
        self.reg_counter = 0


    def init_program(self):
        self.program = Program()
        main_func = Function("main", types.FuncType(None, types.prims["unit"]))



