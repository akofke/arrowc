#!usr/bin/env python

from il_types import *
import arrowc.arrowlang_types as types


class ILGenerator():
    def __init__(self):
        self.reg_table = dict()
        self.reg_counter = [0]

        self.program = Program()

    def get_register(self):
        val = self.reg_counter[-1]
        self.reg_counter[-1] += 1
        return val

    def init_program(self):
        main_func = Function("main", types.FuncType(None, types.prims["unit"]), 0)
        main_b_0 = BasicBlock()



