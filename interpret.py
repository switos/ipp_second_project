import argparse
import os
import sys
import xml.etree.ElementTree as ET
import re

class Variable:
    def __init__(self, value):
        # Initial values for definedf, type and value attributes
        self.definedf = None
        self.type = None
        self.value = value

class Frame:
    def __init__(self):
        self.variables = {}

    def get_variable(self, name, root):
        if name in self.variables:
            if self.variables[name].value == None:
                print(f"Variable {name} not initialized, error caused by instruction number " + root.get('order'), file=sys.stderr)
                sys.exit(56) 
            return self.variables[name]
        else:
            print(f"Variable {name} not defined, error caused by instruction number " + root.get('order'), file=sys.stderr)
            sys.exit(54)

    def check_variable(self, name):
        if name in self.variables:
            return 1
        else:
            return 0

    def define_variable(self, name):
        if name in self.variables:
                print(f'Variable is being defined twice' , file=sys.stderr) 
                sys.exit(52)
        else:
            self.variables[name] = Variable(None)

    def set_variable(self, name, value=None,type=None):
        if name in self.variables:
            self.variables[name].value = value
            if type!=None:
                self.variables[name].type = type
        else:
            print(f"Variable {name} not defined, error caused by set_variable ", file=sys.stderr)
            sys.exit(54)
    
    def get_type(self,name):
        result = self.variables[name].type
        if result == None:
            return ''
        else:
            return result

class GlobalFrame(Frame):
    def __init__(self):
        self.labels = {}
        super().__init__()
    
    def set_label(self, name, root, order):
        if name in self.labels:
            print(f"Label {name} is being defined twice, error caused by instruction number " + root.get('order'), file=sys.stderr)
            sys.exit(52)
        else:     
            self.labels[name] = order

    def get_label(self, name, root):
        if name in self.labels:
            return self.labels.get(name)
        else:
            print(f"Label {name} not defined, error caused by instruction number " + root.get('order'), file=sys.stderr)
            sys.exit(52)

class XML_validator():
        def __init__(self,root) :
            self.root = root
        def elements_chek(self, root): 
            if (root.tag != 'instruction' or len(root.attrib)!= 2):
                print(f"Wrong xml", file=sys.stderr)
                sys.exit(32)
        def check_instruction_atributes(self, root):
                order = root.get('order')
                opcode = root.get('opcode')
                if (order == None or opcode == None):
                    print(f"Wrong xml", file=sys.stderr)
                    sys.exit(32)
                else:
                    if (not(order.isdigit)) or int(order) < 1:
                        print(f"Wrong xml", file=sys.stderr)
                        sys.exit(32)
        def check_arguments(self, root):
            return
        def child_check(self,root):
            self.elements_chek(root)
            self.check_instruction_atributes(root)
            self.check_arguments(root)
        def validate(self): 
            if not (self.root.tag=='program' and len(self.root.attrib)==1 and self.root.get('language')=='IPPcode23'):
                print(f'Wrong root element', file=sys.stderr)
                sys.exit(32)
            for child in self.root:
                self.child_check(child)    

class Analisator:
    def __init__(self, source, inputf):
        self.instarray = { 
            "CREATEFRAME": "01","POPFRAME":"02","PUSHFRAME": "03", "RETURN":"04", "BREAK":"05", 
            "DEFVAR":"11", "POPS":"12",
            "PUSHS":"21", "WRITE":"22", "EXIT":"23", "DPRINT":"24",
            "MOVE":"31", "INT2CHAR":"32", "STRLEN":"33", "TYPE":"34", "NOT":"35",
            "ADD":"401", "SUB":"402", "MUL":"403", "IDIV":"404", 
            "LT":"421", "GT":"422", "EQ":"423", 
            "AND":"431", "OR":"432", 
            "STRI2INT":"4112", "CONCAT":"44", "GETCHAR":"4113", "SETCHAR":"45", 
            "JUMPIFEQ":"51","JUMPIFNEQ":"52", "READ":"6",
            "CALL":"71", "LABEL":"72", "JUMP":"73"
        }
        self.source = source
        self.input = inputf
        self.gf = GlobalFrame()
        self.local_frames_stack = []
        self.tmpframe = Frame()
        self.order = 1
        self.tff = 0 # temporary frame flag
        self.stack = [] 
        self.callstack = []
        self.jump_flag = 0
        try:
            # Load the XML file
            self.tree = ET.parse(source)
            self.root = self.tree.getroot()
        except ET.ParseError as error:
            # If parsing failed, the file is not well-formed
            print(f"The file is not well-formed XML", file=sys.stderr)
            sys.exit(31)

    def get_type(self, root, tmp_list):
        if tmp_list[0] == 'TF':
            self.frame_defined_check('t',root)
            return self.tmpframe.get_type(tmp_list[1], root)
        elif tmp_list[0] == 'LF':
            self.frame_defined_check('l',root)
            return self.local_frames_stack[-1].get_type(tmp_list[1], root)
        else:
            return self.gf.get_type(tmp_list[1])

    def frame_defined_check(self, frame, root):
        if frame == 'l':
            if len(self.local_frames_stack) == 0:
                print(f'Local frame is not defined, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                sys.exit(55) 
        elif frame == 't':
            if not(self.tff):
                print(f'Temporary frame is not defined, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                sys.exit(55)                 

    def check_var(self, root, tmp_list):
        if tmp_list[0] == 'TF':
            self.frame_defined_check('t',root)
            if not (self.tmpframe.check_variable(tmp_list[1])):
                print(f"Variable {tmp_list[1]} not defined, error caused by instruction number " + root.get('order'), file=sys.stderr)
                sys.exit(54)
        elif tmp_list[0] == 'LF':
            self.frame_defined_check('l',root)
            if not (self.local_frames_stack[-1].check_variable(tmp_list[1])):
                print(f"Variable {tmp_list[1]} not defined, error caused by instruction number " + root.get('order'), file=sys.stderr)
                sys.exit(54)
        else:
            if not (self.gf.check_variable(tmp_list[1])):
                print(f"Variable {tmp_list[1]} not defined, error caused by instruction number " + root.get('order'), file=sys.stderr)
                sys.exit(54)
    
    def get_var(self,root,tmp_list):
        if tmp_list[0] == 'TF':
            self.frame_defined_check('t',root)
            return self.tmpframe.get_variable(tmp_list[1], root)
        elif tmp_list[0] == 'LF':
            self.frame_defined_check('l',root)
            return self.local_frames_stack[-1].get_variable(tmp_list[1], root)
        else:
            return self.gf.get_variable(tmp_list[1], root)

    def def_var(self, root, tmp_list):
        if tmp_list[0] == 'TF':
            self.frame_defined_check('t',root)
            self.tmpframe.define_variable(tmp_list[1])
        elif tmp_list[0] == 'LF':
            self.frame_defined_check('l',root)
            self.local_frames_stack[-1].define_variable(tmp_list[1])
        else:
            self.gf.define_variable(tmp_list[1])

    def set_var(self,root, tmp_list, value=None,type=None):
        if tmp_list[0] == 'TF':
            self.frame_defined_check('t',root)
            self.tmpframe.set_variable(tmp_list[1], value, type)
        elif tmp_list[0] == 'LF':
            self.frame_defined_check('l',root)
            self.local_frames_stack[-1].set_variable(tmp_list[1], value, type)
        else:
            self.gf.set_variable(tmp_list[1], value, type)    

    def get_symb_var(self, root, type, arg):
        if type == 'var':
            var = root.find(arg).text.split('@')
            return self.get_var(root,var)
        else:
            value = root.find(arg).text
            if value == None:
                value = ''
            tmp =  Variable(value) 
            tmp.type = type
            return tmp
    # set a variable with result of aritmetic instructions 
    def arithmetic_instr(self, root, instr, var, var1, var2):
        if (var1.type == 'int' and var2.type == 'int'):
            if instr == 'ADD':
                value = int(var1.value) + int(var2.value)
            elif instr == 'SUB':
                value = int(var1.value) - int(var2.value)
            elif instr == 'MUL':
                value = int(var1.value) * int(var2.value)
            elif instr == 'IDIV':
                if var2.value =='0':
                    print(f'Division by zero, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                    sys.exit(57)
                value = int(var1.value) // int(var2.value)
            self.set_var(root,var,f'{value}','int')
        else:
            print(f'Wrong type of operand in {instr}, error caused by instruction number ' + root.get('order'), file=sys.stderr)
            sys.exit(53)   
            
    def get_label(self,root, label):
        return self.gf.get_label(label,root)

    def set_label(self,root, label, order):
        self.gf.set_label(label, root, order)
    
    def type_compatible(self,root,required_type,var):
        if not(var.type == required_type):
            print(f'Wrong type of operand, oprerand must be {required_type} type, error caused by instruction number ' + root.get('order'), file=sys.stderr)
            sys.exit(53)               
    
    def boolipp2boolreal(self,str):
        if str == 'false':
            return False 
        else:
            return True
    # function that returns result of LT GT EQ
    def relation_instr(self, root, isntr, var, var1, var2):
        if (var1.type == 'nil' or var2.type == 'nil') and isntr !='EQ':
                print(f'Wrong type of operand, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                sys.exit(53)
        elif var1.type == 'nil' or var2.type == 'nil':
            if var1.type == var2.type:
                return 'true'
            else:
                return 'false'
        elif (var1.type == var2.type):
            if var1.type == "string":
                if isntr == 'LT':
                    result = var1.value < var2.value
                elif isntr == 'GT':
                    result = var1.value > var2.value
                elif isntr == 'EQ':
                    result = var1.value == var2.value
            elif var1.type == 'int':
                if isntr == 'LT':
                    result = int(var1.value) < int(var2.value)
                elif isntr == 'GT':
                    result = int(var1.value) > int(var2.value)
                elif isntr == 'EQ':
                    result = int(var1.value) == int(var2.value)
            elif var1.type == 'bool':
                if isntr == 'LT':
                    if var1.value == 'false' and var2.value == 'true':
                        result = 'true'
                    else:
                        result = 'false'
                elif isntr == 'GT':
                    if var1.value == 'true' and var2.value == 'false':
                        result = 'true'
                    else:
                        result = 'false'
                elif isntr == 'EQ':
                    if var1.value == var2.value:
                        result = 'true'
                    else:
                        result = 'false'
            return str(result).lower()
        else:
            print(f'Different or wrong types of operands, error caused by instruction number ' + root.get('order'), file=sys.stderr)
            sys.exit(53)   
    
    def set_after_rel_isntr(self, root, isntr, var, var1, var2):
        val = self.relation_instr(root, isntr, var, var1, var2)
        self.set_var(root, var, val, 'bool')
        
    # helper function for Read instuction
    def read_comparator(self, root, value, type):
        if value == '':
            value = 'nil'
            type  = 'nil'
        else:  
            if (type == 'bool'):
                if value != 'true':
                    value = 'false'
            elif (type == 'int') :
                if not(value.isdigit()):
                    value = 'nil'
                    type  = 'nil'
        tmp_list = [value, type]
        return tmp_list

    def parse_instr(self,root) :
            try:
                tmp = self.instarray[root.get('opcode').upper()] 
            except KeyError:
                print(f'Undefined operation code, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                sys.exit(32)
            if tmp[0] == '0':
                #CREATEFRAME
                if tmp[1] == '1':
                    self.tmpframe = Frame()
                    self.tff = 1
                #PUSHFRAME   
                elif tmp[1] == '3':
                    if self.tff:
                        self.tff = 0
                        self.local_frames_stack.append(self.tmpframe)
                    else:
                        print(f'Temporary frame is not defined, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                        sys.exit(55) 
                #POPFRAME
                elif tmp[1] == '2':
                    if len(self.local_frames_stack):
                            self.tmpframe=self.local_frames_stack.pop()
                            self.tff = 1
                    else:
                        print(f'Local frame is not defined, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                        sys.exit(55) 
                #RETURN
                elif tmp[1] == '4':
                    if len(self.callstack):
                        jump = self.callstack.pop()
                        self.jump_flag = 1
                        self.order = f'{int(jump) + 1}'
                    else:
                        print(f'Call stack is empty, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                        sys.exit(56)
                #BREAK
                elif tmp[1] == '5':
                        print(f'Instruction position is' + root.get('order'), file=sys.stderr)
            #DEFVAR and POPS analyze
            elif tmp[0] == '1':
                tmp_list = root.find('arg1').text.split('@')
                #DEFVAR
                if tmp[1]=='1':
                    self.def_var(root,tmp_list)
                #POPS
                else:
                    if len(self.stack):
                        var = self.stack.pop()
                        self.check_var(root,tmp_list)
                        self.set_var(root,tmp_list,var.value,var.type)
                    else:
                        print(f'Stack is empty, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                        sys.exit(56) 

            elif tmp[0] == '2':
                #PUSHS
                type = root.find('arg1').get('type')
                var = self.get_symb_var(root,type,'arg1')
                if tmp[1] == '1':
                    new_var = Variable(var.value)
                    new_var.type = var.type
                    self.stack.append(new_var)
                # WRITE
                elif tmp[1]== '2':
                        if var.type == 'nil':
                            print('', end='')
                        elif var.type == 'string':
                            str = var.value
                            match = re.findall(r"\\[\d]{3}",str)
                            for i in match:
                                str = str.replace(i, chr(int(i[1:])))
                            print(str, end='')          
                        else:
                            print(var.value, end='') 
                #EXIT
                elif tmp[1]== '3':
                    self.type_compatible(root,'int',var)
                    if re.fullmatch('([0-9]|[1-4][0-9])', var.value) == None:
                        print(f'Unvalid error code, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                        sys.exit(57)
                    else: 
                        sys.exit(int(var.value))
                        
                #DPRINT
                elif tmp[1]== '4':
                    print(var.value, file=sys.stderr)

            elif tmp[0] == '3':
                var1 = root.find('arg1').text.split('@')
                type = root.find('arg2').get('type')
                if not tmp[1] == '4':
                     var2 = self.get_symb_var(root,type,'arg2')
                #MOVE
                if tmp[1] == '1':
                    self.set_var(root,var1,var2.value,var2.type)
                #INT2CHAR
                elif tmp[1] == '2':
                    self.type_compatible(root,'int',var2)
                    try:
                        univalue = chr(int(var2.value))
                    except ValueError:
                        print(f'Unvalid int value it must be in the range of 0-0x10ffff, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                        sys.exit(58)
                    self.set_var(root,var1,univalue,'string')
                #STRLEN
                elif tmp[1] == '3':
                    self.type_compatible(root,'string',var2)
                    self.set_var(root,var1,len(var2.value),'int')
                #TYPE we have problems with uninitialized variable(
                elif tmp[1] == '4':
                    if type == 'var':
                        var2 =  root.find('arg2').text.split('@')
                        self.check_var(root,root.find('arg2').text.split('@'))
                        type = self.get_type(root, var2)
                    else:
                        var2 = self.get_symb_var(root,type,'arg2')
                        type = var2.type
                    self.set_var(root, var1, type, 'string')
                #NOT
                elif tmp[1] == '5':
                    self.type_compatible(root,'bool',var2)
                    res='true'
                    if var2.value == 'true':
                        res='false'
                    self.set_var(root,var1,res,'bool')
            elif tmp[0] == '4':
                var =  root.find('arg1').text.split('@')
                type_1 = root.find('arg2').get('type')
                type_2 = root.find('arg3').get('type')
                var1 = self.get_symb_var(root, type_1, 'arg2')
                var2 = self.get_symb_var(root, type_2, 'arg3')
                self.check_var(root,var)
                if tmp[1] == '0':
                    #ADD
                    if tmp[2] == '1':
                        self.arithmetic_instr(root, 'ADD', var, var1, var2) 
                    #SUB 
                    elif tmp[2] == '2':
                        self.arithmetic_instr(root, 'SUB', var, var1, var2)
                    #MUL
                    elif tmp[2] == '3':
                        self.arithmetic_instr(root, 'MUL', var, var1, var2)
                    #IDIV
                    elif tmp[2] == '4':
                        self.arithmetic_instr(root, 'IDIV', var, var1, var2)
                elif tmp[1] == '2':
                    #LT
                    if tmp[2] == '1':
                        self.set_after_rel_isntr(root,'LT', var, var1, var2)
                    #GT
                    elif tmp[2] == '2':
                        self.set_after_rel_isntr(root,'GT', var, var1, var2)
                    #EQ
                    elif tmp[2] == '3':
                        self.set_after_rel_isntr(root,'EQ', var, var1, var2)
                elif tmp[1]== '3':
                    if var1.type == 'bool' and var1.type == var2.type:
                        #AND
                        if tmp[2] == '1':
                            result = self.boolipp2boolreal(var1.value) and self.boolipp2boolreal(var2.value)    
                            self.set_var(root, var, f'{result}'.lower(),'bool')
                        #OR
                        elif tmp[2] == '2':
                            result = self.boolipp2boolreal(var1.value) or self.boolipp2boolreal(var2.value)    
                            self.set_var(root, var, f'{result}'.lower(),'bool')
                    else:
                        print(f'Wrong operands, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                        sys.exit(53)
                #"STRI2INT":"4112", "GETCHAR":"4113"    
                elif tmp[1] == '1':
                    if var2.type == 'int' and int(var2.value) >= 0 and var1.type == 'string':
                            if int(var2.value) < len(var1.value):  
                                if tmp[3] == '2':
                                    result = ord(var1.value[int(var2.value)])
                                    self.set_var(root, var, result, 'int')
                                elif tmp[3] == '3':
                                    result = var1.value[int(var2.value)]
                                    self.set_var(root, var, result,'string')
                            else:
                                print(len(var1.value),int(var2.value),f'Out of index, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                                sys.exit(58)
                    else:
                        print(f'Wrong operands, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                        sys.exit(53)
                #CONCAT
                elif tmp[1] == '4':
                    if var1.type == var2.type:
                        self.type_compatible(root,'string',var1)
                        result = var1.value + var2.value
                        self.set_var(root, var, result, 'string') 
                    else:
                        print(f'Wrong operands, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                        sys.exit(53)
                #"SETCHAR":"45"
                elif tmp[1] == '5':
                    vars = self.get_var(root, var)
                    if(vars.type == 'string' and var1.type == 'int' and int(var1.value) >=0 and var2.type == 'string'):
                        if int(var1.value) < len(vars.value) and len(var2.value)!=0:
                            strm = vars.value
                            strm = strm[:int(var1.value)] + var2.value[0] + strm[int(var1.value)+1:]
                            self.set_var(root, var, strm, vars.type)
                        else:
                            print(f'Out of index, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                            sys.exit(58)   
                    else:
                        print(f'Wrong operands, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                        sys.exit(53)
            #"JUMIFEQ":"51","JUMPIFNEQ":"52"       
            elif tmp[0] == '5':
                label = root.find('arg1').text
                type_1 = root.find('arg2').get('type')
                type_2 = root.find('arg3').get('type')
                var1 = self.get_symb_var(root, type_1, 'arg2')
                var2 = self.get_symb_var(root, type_2, 'arg3')
                if var1.type == 'nil' or var2.type == 'nil':
                    if var1.type != var2.type:
                        result = 'false'
                    else:
                        print(f'Different or wrong types of operands, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                        sys.exit(53)  
                elif (var1.type == var2.type):
                    var = 'empty_var'
                    result = self.relation_instr(root, 'EQ', var, var1, var2)
                else:
                    print(f'Wrong operands1, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                    sys.exit(53)    
                if tmp[1] == '1':
                    if (self.boolipp2boolreal(result)):
                        self.jump_flag = 1
                        self.order = self.get_label(root, label) 
                elif tmp[1] == '2':
                    if not(self.boolipp2boolreal(result)):
                        self.jump_flag = 1
                        self.order = self.get_label(root, label)
            elif tmp[0] == '6':
                #READ
                if self.input == '-':
                    print(f'Input file is not provided, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                    sys.exit(56)
                var = root.find('arg1').text.split('@')
                type = root.find('arg2').text
                if not (root.find('arg2').get('type') == 'type'):
                    print(f'wrong xml, error caused by instruction number ' + root.get('order'), file=sys.stderr)
                    sys.exit(32)
                input_tmp = self.input.readline().strip()
                value_type = []
                value_type = self.read_comparator(root, input_tmp, type)
                self.check_var(root,var)
                self.set_var(root,var, value_type[0], value_type[1])
            elif tmp[0] == '7' :
                label = root.find('arg1').text
                #CALL
                if tmp[1] == '1':
                    order = int(self.order)+1
                    self.callstack.append(f'{order}')
                    self.jump_flag = 1
                    self.order = self.get_label(root, label)
                #LABEL
                #Skip label instuctiona, cause they was readed byt first run method 
                elif tmp[1] == '2':
                    return
                #JUMP
                elif tmp[1] == '3':
                    self.jump_flag = 1
                    self.order = self.get_label(root,label)
    ## bubble sort for dictionaries representintg xml element as value and order as key
    def bubble_sort_dict_by_key(self,dct):
        keys = list(dct.keys())
        for i in range(len(keys)):
            for j in range(len(keys) - 1):
                if int(keys[j]) > int(keys[j + 1]):
                    keys[j], keys[j + 1] = keys[j + 1], keys[j]
        return {k: dct[k] for k in keys}

    # method that iterates through elements of xml and call parse instr method on each element
    def iterate(self, ordered_childs, order):
        if type(order) != type('str'):
            order = str(order)
        # index is start position representing by current order
        order_index = list(ordered_childs.keys()).index(order)
        for order, child in list(ordered_childs.items())[order_index:]:
            # jump_flag represents jumps that occurs in program
            if self.jump_flag:
                break
            if child.tag != 'instruction':
                    print(f'Wrong element, error caused by instruction number ' + child.get('order'), file=sys.stderr)
                    sys.exit(32)
            self.order = order
            self.parse_instr(child)
        if self.jump_flag:
            #reseting flagjump and call iterate method with after jump order
            self.jump_flag = 0
            self.iterate(ordered_childs, str(int(self.order)-1))
    #bubble sort for list of xml elements by atribbute order 
    def label_bubble_sort(self,arr):
        n = len(arr)
        for i in range(n):
            for j in range(0, n-i-1):
                if arr[j].get('order') > arr[j+1].get('order') :
                    arr[j], arr[j+1] = arr[j+1], arr[j]
        return arr
    
    def parse_labels(self, root):
        label = root.find('arg1').text
        self.set_label(root,label,str(int(self.order)+1))
    # setting labels 
    def first_run(self):
        instructions = self.root.findall("./instruction[@opcode='LABEL']")
        instructions = self.label_bubble_sort(instructions)
        for child in instructions:
            self.order = child.get('order')
            self.parse_labels(child)
    # sorting xml elements by order, setting labels, starting iterate method
    def analyse(self):
        validator = XML_validator(self.root)
        validator.validate()
        ordered_childs = {}
        for child in self.root:
            if child.get('order') in ordered_childs:
                    print(f'Duplicate order error', file=sys.stderr)
                    sys.exit(32)
            else:
                ordered_childs[child.get('order')] = child 
        
        ordered_childs = self.bubble_sort_dict_by_key(ordered_childs)
        first_key = next(iter(ordered_childs))
        self.first_run()
        self.iterate(ordered_childs, first_key)
    
## Main code setcion that parse agruments and then run analyse method of analysator class
parser = argparse.ArgumentParser(description='Help message and exit')
parser.add_argument('--source', metavar='file', help='path to source file')
parser.add_argument('--input', metavar='file', help='path to input file')
args = parser.parse_args()
if not (args.source or args.input):
    print(f'At least one of files needs to be provided', file=sys.stderr)
    sys.exit(10)
source_file = args.source or '-'
input_file = args.input or '-'
if source_file != '-' and not os.path.isfile(source_file):
    print(f'File not found: {source_file}', file=sys.stderr)
    sys.exit(10) 
if input_file != '-' and not os.path.isfile(input_file):
    print(f'File not found: {input_file}', file=sys.stderr)
    sys.exit(10) 

if input_file != '-':
   input_file =  open(input_file,'r')

if source_file != '-':
    # start of analyse
    with open(source_file) as s_f:
        analyse = Analisator(source_file,input_file)
    pass
    analyse.analyse()
    if input_file != '-':
        input_file.close()