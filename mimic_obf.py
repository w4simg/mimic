import ast as lOlO
import os as llOO
import sys as lOlI
import time as lOOlO
import random as lII
import shutil as lIOI
import argparse as lIII
import builtins as llII

class lIllO:

    def __init__(self, parent=None, is_class=False):
        self.parent = parent
        self.is_class = is_class
        self.defined = set()
        self.globals = set()
        self.nonlocals = set()
        self.defined_imports = {}
        self.children = []

def llIlO(lIIOO, lOlIO):
    lllIO = lIIOO
    while lllIO is not None:
        if lOlIO in lllIO.globals:
            lOIOO = lllIO
            while lOIOO.parent is not None:
                lOIOO = lOIOO.parent
            return lOIOO
        if lOlIO in lllIO.nonlocals:
            lllIO = lllIO.parent
            while lllIO is not None and lllIO.is_class:
                lllIO = lllIO.parent
            while lllIO is not None:
                if lOlIO in lllIO.defined:
                    return lllIO
                lllIO = lllIO.parent
            return None
        if lOlIO in lllIO.defined:
            return lllIO
        parent = lllIO.parent
        if parent and parent.is_class:
            parent = parent.parent
        lllIO = parent
    return None

def lIOO(llOIO, llIIO):
    lOIIO = llOO.path.relpath(llOIO, llIIO)
    lIOIO, lIlIO = llOO.path.splitext(lOIIO)
    lOOIO = lIOIO.replace(llOO.path.sep, bytes([47]).decode('utf-8')).split(bytes([47]).decode('utf-8'))
    if lOOIO and lOOIO[-1] == bytes([95, 95, 105, 110, 105, 116, 95, 95]).decode('utf-8'):
        lOOIO.pop()
    return bytes([46]).decode('utf-8').join(lOOIO)

def llI(current_module, is_package, llllI, lOllI):
    if not current_module:
        return lOllI or bytes([]).decode('utf-8')
    lIIIO = current_module.split(bytes([46]).decode('utf-8'))
    if not is_package:
        lIIIO = lIIIO[:-1]
    if llllI > 1:
        lIIIO = lIIIO[:-(llllI - 1)]
    if lOllI:
        lIIIO.append(lOllI)
    return bytes([46]).decode('utf-8').join(lIIIO)

def lOOI(lOOlI, llOlI):
    lIllI = lOOlI
    while lIllI is not None:
        if llOlI in lIllI.defined_imports:
            return lIllI.defined_imports[llOlI]
        lIllI = lIllI.parent
    return None

def llIOO(lllOI, lIOlI):
    if isinstance(lllOI, lOlO.Name):
        lIIlI = lOOI(lIOlI, lllOI.id)
        if lIIlI:
            return (lIIlI, [])
        return None
    elif isinstance(lllOI, lOlO.Attribute):
        llIlI = llIOO(lllOI.value, lIOlI)
        if llIlI:
            lOlOI, lOIlI = llIlI
            return (lOlOI, lOIlI + [lllOI.attr])
    return None

class lOI(lOlO.NodeVisitor):

    def __init__(self, project_modules, current_module=None, is_package=False):
        self.current_scope = lIllO()
        self.node_scopes = {}
        self.project_modules = project_modules
        self.current_module = current_module
        self.is_package = is_package

    def visit_Module(self, lIlOI):
        self.node_scopes[lIlOI] = self.current_scope
        self.generic_visit(lIlOI)

    def visit_ClassDef(self, llOOI):
        self.current_scope.defined.add(llOOI.name)
        parent = self.current_scope
        self.current_scope = lIllO(parent=parent, is_class=True)
        parent.children.append(self.current_scope)
        self.node_scopes[llOOI] = self.current_scope
        self.generic_visit(llOOI)
        self.current_scope = parent

    def visit_FunctionDef(self, lIOOI):
        self.current_scope.defined.add(lIOOI.name)
        parent = self.current_scope
        self.current_scope = lIllO(parent=parent)
        parent.children.append(self.current_scope)
        self.node_scopes[lIOOI] = self.current_scope
        for lOOOI in lIOOI.args.posonlyargs + lIOOI.args.args + lIOOI.args.kwonlyargs:
            self.current_scope.defined.add(lOOOI.arg)
        if lIOOI.args.vararg:
            self.current_scope.defined.add(lIOOI.args.vararg.arg)
        if lIOOI.args.kwarg:
            self.current_scope.defined.add(lIOOI.args.kwarg.arg)
        self.generic_visit(lIOOI)
        self.current_scope = parent

    def visit_AsyncFunctionDef(self, llIOI):
        self.visit_FunctionDef(llIOI)

    def visit_Global(self, lIIOI):
        for lOIOI in lIIOI.names:
            self.current_scope.globals.add(lOIOI)

    def visit_Nonlocal(self, lOlII):
        for lllII in lOlII.names:
            self.current_scope.nonlocals.add(lllII)

    def visit_Name(self, lIlII):
        if isinstance(lIlII.ctx, lOlO.Store):
            if lIlII.id not in self.current_scope.globals and lIlII.id not in self.current_scope.nonlocals:
                self.current_scope.defined.add(lIlII.id)

    def visit_MatchAs(self, llOII):
        if llOII.name:
            self.current_scope.defined.add(llOII.name)
        self.generic_visit(llOII)

    def visit_Import(self, lOIII):
        for llIII in lOIII.names:
            lOOII = llIII.asname or llIII.name.split(bytes([46]).decode('utf-8'))[0]
            self.current_scope.defined.add(lOOII)
            if llIII.asname:
                if llIII.name in self.project_modules:
                    self.current_scope.defined_imports[llIII.asname] = llIII.name
            else:
                lIOII = llIII.name.split(bytes([46]).decode('utf-8'))[0]
                self.current_scope.defined_imports[lIOII] = lIOII

    def visit_ImportFrom(self, llOllO):
        if not llOllO.module and llOllO.level == 0:
            return
        if llOllO.level > 0:
            lIlllO = llI(self.current_module, self.is_package, llOllO.level, llOllO.module)
        else:
            lIlllO = llOllO.module or bytes([]).decode('utf-8')
        for lllllO in llOllO.names:
            lIIII = lllllO.asname or lllllO.name
            self.current_scope.defined.add(lIIII)
            lOlllO = str(lIlllO) + bytes([46]).decode('utf-8') + str(lllllO.name) if lIlllO else lllllO.name
            if lOlllO in self.project_modules:
                self.current_scope.defined_imports[lIIII] = lOlllO

class llOI(lOlO.NodeVisitor):

    def __init__(self):
        self.names = set()

    def visit_Name(self, lOOllO):
        self.names.add(lOOllO.id)
        self.generic_visit(lOOllO)

    def visit_FunctionDef(self, lIOllO):
        self.names.add(lIOllO.name)
        self.generic_visit(lIOllO)

    def visit_AsyncFunctionDef(self, llIllO):
        self.names.add(llIllO.name)
        self.generic_visit(llIllO)

    def visit_ClassDef(self, lOIllO):
        self.names.add(lOIllO.name)
        self.generic_visit(lOIllO)

    def visit_Import(self, lllOlO):
        for lIIllO in lllOlO.names:
            self.names.add(lIIllO.asname or lIIllO.name.split(bytes([46]).decode('utf-8'))[0])
        self.generic_visit(lllOlO)

    def visit_ImportFrom(self, lIlOlO):
        for lOlOlO in lIlOlO.names:
            self.names.add(lOlOlO.asname or lOlOlO.name)
        self.generic_visit(lIlOlO)

class lOlOO(lOlO.NodeVisitor):

    def __init__(self):
        self.keywords = set()

    def visit_Call(self, lOOOlO):
        for llOOlO in lOOOlO.keywords:
            if llOOlO.arg:
                self.keywords.add(llOOlO.arg)
        self.generic_visit(lOOOlO)

class lIIlO(lOlO.NodeVisitor):

    def __init__(self):
        self.private_attrs = set()

    def visit_Attribute(self, lIOOlO):
        if self.lIO(lIOOlO.attr):
            self.private_attrs.add(lIOOlO.attr)
        self.generic_visit(lIOOlO)

    def visit_FunctionDef(self, llIOlO):
        if self.lIO(llIOlO.name):
            self.private_attrs.add(llIOlO.name)
        self.generic_visit(llIOlO)

    def visit_Name(self, lOIOlO):
        if isinstance(lOIOlO.ctx, lOlO.Store) and self.lIO(lOIOlO.id):
            self.private_attrs.add(lOIOlO.id)
        self.generic_visit(lOIOlO)

    def lIO(self, lIIOlO):
        return lIIOlO.startswith(bytes([95]).decode('utf-8')) and (not lIIOlO.endswith(bytes([95, 95]).decode('utf-8'))) and (lIIOlO != bytes([95]).decode('utf-8'))

class lIOlO:

    def __init__(self, style=bytes([104, 101, 120]).decode('utf-8')):
        self.style = style
        self.counter = 0
        self.existing = set()

    def get_next(self):
        while True:
            self.counter += 1
            if self.style == bytes([99, 111, 110, 102, 117, 115, 105, 110, 103]).decode('utf-8'):
                lOlIlO = [bytes([108]).decode('utf-8'), bytes([79]).decode('utf-8'), bytes([73]).decode('utf-8')]
                llIIlO = self.counter
                lIlIlO = []
                while llIIlO > 0:
                    lIlIlO.append(lOlIlO[llIIlO % 3])
                    llIIlO //= 3
                lOIIlO = bytes([108]).decode('utf-8') + bytes([]).decode('utf-8').join(lIlIlO)
            elif self.style == bytes([99, 104, 105, 110, 101, 115, 101]).decode('utf-8'):
                lIIIlO = [bytes([230, 158, 129]).decode('utf-8'), bytes([230, 151, 160]).decode('utf-8'), bytes([229, 189, 177]).decode('utf-8'), bytes([231, 167, 152]).decode('utf-8'), bytes([229, 175, 134]).decode('utf-8'), bytes([233, 154, 144]).decode('utf-8'), bytes([232, 151, 143]).decode('utf-8'), bytes([108]).decode('utf-8'), bytes([79]).decode('utf-8'), bytes([73]).decode('utf-8'), bytes([95]).decode('utf-8')]
                lOOIlO = lIIIlO + [bytes([48]).decode('utf-8'), bytes([49]).decode('utf-8'), bytes([50]).decode('utf-8'), bytes([51]).decode('utf-8'), bytes([52]).decode('utf-8'), bytes([53]).decode('utf-8'), bytes([54]).decode('utf-8'), bytes([55]).decode('utf-8'), bytes([56]).decode('utf-8'), bytes([57]).decode('utf-8'), bytes([120]).decode('utf-8'), bytes([100]).decode('utf-8'), bytes([101]).decode('utf-8'), bytes([99]).decode('utf-8')]
                llIIlO = self.counter
                lllIlO = llIIlO % len(lIIIlO)
                lIOIlO = lIIIlO[lllIlO]
                llIIlO //= len(lIIIlO)
                lIlIlO = []
                while llIIlO > 0:
                    llOIlO = llIIlO % len(lOOIlO)
                    lIlIlO.append(lOOIlO[llOIlO])
                    llIIlO //= len(lOOIlO)
                lOIIlO = lIOIlO + bytes([]).decode('utf-8').join(lIlIlO)
            else:
                lOIIlO = bytes([95, 48, 120]).decode('utf-8') + format(self.counter, bytes([120]).decode('utf-8'))
            if lOIIlO not in self.existing:
                return lOIIlO

class llllO(lOlO.NodeTransformer):

    def visit_Module(self, llllOO):
        self.generic_visit(llllOO)
        self.lI(llllOO.body)
        return llllOO

    def visit_ClassDef(self, lOllOO):
        self.generic_visit(lOllOO)
        self.lI(lOllOO.body)
        return lOllOO

    def visit_FunctionDef(self, lIllOO):
        self.generic_visit(lIllOO)
        self.lI(lIllOO.body)
        return lIllOO

    def visit_AsyncFunctionDef(self, llOlOO):
        self.generic_visit(llOlOO)
        self.lI(llOlOO.body)
        return llOlOO

    def lI(self, body):
        if not body:
            return
        lOOlOO = body[0]
        if isinstance(lOOlOO, lOlO.Expr) and isinstance(lOOlOO.value, lOlO.Constant) and isinstance(lOOlOO.value.value, str):
            body.pop(0)
            if not body:
                body.append(lOlO.Pass())

class lOOOO(lOlO.NodeTransformer):

    def visit_JoinedStr(self, lllOOO):
        if not lllOOO.values:
            return lOlO.Constant(value=bytes([]).decode('utf-8'))
        lIlOOO = []
        for lIOlOO in lllOOO.values:
            if isinstance(lIOlOO, lOlO.Constant):
                lIlOOO.append(lIOlOO)
            elif isinstance(lIOlOO, lOlO.FormattedValue):
                lOlOOO = self.visit(lIOlOO.value)
                if lIOlOO.format_spec:
                    lOIlOO = self.visit(lIOlOO.format_spec)
                    lIlOOO.append(lOlO.Call(func=lOlO.Name(id=bytes([102, 111, 114, 109, 97, 116]).decode('utf-8'), ctx=lOlO.Load()), args=[lOlOOO, lOIlOO], keywords=[]))
                else:
                    lIlOOO.append(lOlO.Call(func=lOlO.Name(id=bytes([115, 116, 114]).decode('utf-8'), ctx=lOlO.Load()), args=[lOlOOO], keywords=[]))
            else:
                lIlOOO.append(self.visit(lIOlOO))
        llIlOO = lIlOOO[0]
        for lIIlOO in lIlOOO[1:]:
            llIlOO = lOlO.BinOp(left=llIlOO, op=lOlO.Add(), right=lIIlOO)
        return llIlOO

class lIOOO(lOlO.NodeTransformer):

    def __init__(self, llOOOO, decoder_name=bytes([95, 48, 120, 95, 100, 101, 99]).decode('utf-8')):
        self.level = llOOOO
        self.decoder_name = decoder_name
        self.string_count = 0
        self.in_decoder = False

    def visit_FunctionDef(self, lOOOOO):
        if lOOOOO.name == self.decoder_name:
            self.in_decoder = True
            self.generic_visit(lOOOOO)
            self.in_decoder = False
            return lOOOOO
        self.generic_visit(lOOOOO)
        return lOOOOO

    def visit_AsyncFunctionDef(self, lIOOOO):
        if lIOOOO.name == self.decoder_name:
            self.in_decoder = True
            self.generic_visit(lIOOOO)
            self.in_decoder = False
            return lIOOOO
        self.generic_visit(lIOOOO)
        return lIOOOO

    def visit_Constant(self, lOlIOO):
        if isinstance(lOlIOO.value, str):
            if self.in_decoder:
                return lOlIOO
            if self.level == bytes([98, 97, 115, 105, 99]).decode('utf-8'):
                return lOlIOO
            self.string_count += 1
            if self.level == bytes([109, 101, 100, 105, 117, 109]).decode('utf-8'):
                llIOOO = lOlIOO.value.encode(bytes([117, 116, 102, 45, 56]).decode('utf-8'))
                return lOlO.Call(func=lOlO.Attribute(value=lOlO.Call(func=lOlO.Name(id=bytes([98, 121, 116, 101, 115]).decode('utf-8'), ctx=lOlO.Load()), args=[lOlO.List(elts=[lOlO.Constant(value=lIlIOO) for lIlIOO in llIOOO], ctx=lOlO.Load())], keywords=[]), attr=bytes([100, 101, 99, 111, 100, 101]).decode('utf-8'), ctx=lOlO.Load()), args=[lOlO.Constant(value=bytes([117, 116, 102, 45, 56]).decode('utf-8'))], keywords=[])
            else:
                llOIOO = lII.randint(1, 255)
                lOIOOO = [ord(lIIOOO) ^ llOIOO for lIIOOO in lOlIOO.value]
                return lOlO.Call(func=lOlO.Name(id=self.decoder_name, ctx=lOlO.Load()), args=[lOlO.Tuple(elts=[lOlO.Constant(value=lllIOO) for lllIOO in lOIOOO], ctx=lOlO.Load()), lOlO.Constant(value=llOIOO)], keywords=[])
        return lOlIOO

class lOII(lOlO.NodeTransformer):

    def visit_Constant(self, llIIOO):
        if isinstance(llIIOO.value, int) and (not isinstance(llIIOO.value, bool)):
            if abs(llIIOO.value) < 1000000:
                lOOIOO = lII.randint(100, 100000)
                lIOIOO = llIIOO.value ^ lOOIOO
                return lOlO.BinOp(left=lOlO.Constant(value=lIOIOO), op=lOlO.BitXor(), right=lOlO.Constant(value=lOOIOO))
        elif isinstance(llIIOO.value, bool):
            lOOIOO = lII.randint(10, 100)
            if llIIOO.value:
                return lOlO.Compare(left=lOlO.Constant(value=lOOIOO), ops=[lOlO.Eq()], comparators=[lOlO.Constant(value=lOOIOO)])
            else:
                return lOlO.Compare(left=lOlO.Constant(value=lOOIOO), ops=[lOlO.NotEq()], comparators=[lOlO.Constant(value=lOOIOO)])
        return llIIOO

class lllOO(lOlO.NodeTransformer):

    def __init__(self, lOllIO, lIIIOO, llllIO, lOIIOO):
        self.scope_tree = lOllIO
        self.node_scopes = lIIIOO
        self.builtins_module_name = llllIO
        self.getattr_name = lOIIOO
        self.builtin_names = set(dir(llII))

    def visit_Name(self, lOOlIO):
        if isinstance(lOOlIO.ctx, lOlO.Load) and lOOlIO.id in self.builtin_names:
            if lOOlIO.id.startswith(bytes([95, 95]).decode('utf-8')) and lOOlIO.id.endswith(bytes([95, 95]).decode('utf-8')):
                return lOOlIO
            lIllIO = self.node_scopes.get(lOOlIO)
            if lIllIO:
                llOlIO = llIlO(lIllIO, lOOlIO.id)
                if llOlIO is not None:
                    return lOOlIO
            return lOlO.Call(func=lOlO.Name(id=self.getattr_name, ctx=lOlO.Load()), args=[lOlO.Name(id=self.builtins_module_name, ctx=lOlO.Load()), lOlO.Constant(value=lOOlIO.id)], keywords=[])
        return lOOlIO

class lIlI(lOlO.NodeTransformer):

    def __init__(self, lIOlIO=bytes([95, 115, 116, 97, 116, 101, 95]).decode('utf-8')):
        self.state_var_prefix = lIOlIO
        self.counter = 0

    def visit_FunctionDef(self, llIlIO):
        self.generic_visit(llIlIO)
        if not (llIlIO.name.startswith(bytes([95, 95]).decode('utf-8')) and llIlIO.name.endswith(bytes([95, 95]).decode('utf-8'))):
            llIlIO.body = self.lO(llIlIO.body)
        return llIlIO

    def visit_AsyncFunctionDef(self, lOIlIO):
        self.generic_visit(lOIlIO)
        if not (lOIlIO.name.startswith(bytes([95, 95]).decode('utf-8')) and lOIlIO.name.endswith(bytes([95, 95]).decode('utf-8'))):
            lOIlIO.body = self.lO(lOIlIO.body)
        return lOIlIO

    def lO(self, body):
        llOOIO = []
        lOOOIO = []
        for lIOOIO in body:
            if isinstance(lIOOIO, (lOlO.Global, lOlO.Nonlocal)):
                llOOIO.append(lIOOIO)
            else:
                lOOOIO.append(lIOOIO)
        if len(lOOOIO) < 2 or self.llO(lOlO.Module(body=lOOOIO, type_ignores=[])):
            return body
        self.counter += 1
        lIlIIO = str(self.state_var_prefix) + str(self.counter)
        lOlIIO = len(lOOOIO)
        lIIlIO = lII.sample(range(1000, 99999), lOlIIO + 1)
        llIOIO = lIIlIO[0]
        lOIOIO = lIIlIO[-1]
        lllIIO = []
        for lllOIO in range(lOlIIO):
            lllIIO.append((lIIlIO[lllOIO], lOOOIO[lllOIO], lIIlIO[lllOIO + 1]))
        lII.shuffle(lllIIO)
        lOlOIO = lOlO.Assign(targets=[lOlO.Name(id=lIlIIO, ctx=lOlO.Store())], value=lOlO.Constant(value=llIOIO))
        lIlOIO = lOlO.Compare(left=lOlO.Name(id=lIlIIO, ctx=lOlO.Load()), ops=[lOlO.NotEq()], comparators=[lOlO.Constant(value=lOIOIO)])
        lIIOIO = self.lOO(lllIIO, lIlIIO)
        llOIIO = lOlO.While(test=lIlOIO, body=lIIOIO, orelse=[])
        return llOOIO + [lOlOIO, llOIIO]

    def llO(self, lIOIIO):
        for lOOIIO in lOlO.walk(lIOIIO):
            if isinstance(lOOIIO, (lOlO.Yield, lOlO.YieldFrom)):
                return True
        return False

    def lOO(self, lIlllI, llOllI):
        lOOllI = []
        for llIIIO, lOlllI, lllllI in reversed(lIlllI):
            lOIIIO = []
            if isinstance(lOlllI, list):
                lOIIIO.extend(lOlllI)
            else:
                lOIIIO.append(lOlllI)
            lIIIIO = lOlO.Assign(targets=[lOlO.Name(id=llOllI, ctx=lOlO.Store())], value=lOlO.Constant(value=lllllI))
            lOIIIO.append(lIIIIO)
            test = lOlO.Compare(left=lOlO.Name(id=llOllI, ctx=lOlO.Load()), ops=[lOlO.Eq()], comparators=[lOlO.Constant(value=llIIIO)])
            lOOllI = [lOlO.If(test=test, body=lOIIIO, orelse=lOOllI)]
        return lOOllI

class lOIO(lOlO.NodeTransformer):

    def __init__(self, lIOllI, lOIllI, llIllI, project_modules, project_globals, current_module, is_package=False):
        self.node_scopes = lIOllI
        self.mappings = lOIllI
        self.private_attr_map = llIllI
        self.project_modules = project_modules
        self.project_globals = project_globals
        self.current_module = current_module
        self.is_package = is_package
        self.current_scope = None

    def visit_Module(self, lIIllI):
        self.current_scope = self.node_scopes[lIIllI]
        self.generic_visit(lIIllI)
        return lIIllI

    def visit_ClassDef(self, lIlOlI):
        lllOlI = self.current_scope
        llOOlI = (lllOlI, lIlOlI.name)
        if llOOlI in self.mappings:
            lIlOlI.name = self.mappings[llOOlI]
        elif self.project_globals is not None and self.current_module is not None:
            lOlOlI = (self.current_module, lIlOlI.name)
            if lOlOlI in self.project_globals:
                lIlOlI.name = self.project_globals[lOlOlI]
        self.current_scope = self.node_scopes[lIlOlI]
        self.generic_visit(lIlOlI)
        self.current_scope = lllOlI
        return lIlOlI

    def visit_FunctionDef(self, lOIOlI):
        lOOOlI = self.current_scope
        if lOOOlI and lOOOlI.is_class and (lOIOlI.name in self.private_attr_map):
            lOIOlI.name = self.private_attr_map[lOIOlI.name]
        else:
            lIIOlI = (lOOOlI, lOIOlI.name)
            if lIIOlI in self.mappings:
                lOIOlI.name = self.mappings[lIIOlI]
            elif self.project_globals is not None and self.current_module is not None:
                lIOOlI = (self.current_module, lOIOlI.name)
                if lIOOlI in self.project_globals:
                    lOIOlI.name = self.project_globals[lIOOlI]
        self.current_scope = self.node_scopes[lOIOlI]
        for llIOlI in lOIOlI.args.posonlyargs + lOIOlI.args.args + lOIOlI.args.kwonlyargs:
            lIIOlI = (self.current_scope, llIOlI.arg)
            if lIIOlI in self.mappings:
                llIOlI.arg = self.mappings[lIIOlI]
        if lOIOlI.args.vararg:
            lIIOlI = (self.current_scope, lOIOlI.args.vararg.arg)
            if lIIOlI in self.mappings:
                lOIOlI.args.vararg.arg = self.mappings[lIIOlI]
        if lOIOlI.args.kwarg:
            lIIOlI = (self.current_scope, lOIOlI.args.kwarg.arg)
            if lIIOlI in self.mappings:
                lOIOlI.args.kwarg.arg = self.mappings[lIIOlI]
        self.generic_visit(lOIOlI)
        self.current_scope = lOOOlI
        return lOIOlI

    def visit_AsyncFunctionDef(self, lllIlI):
        return self.visit_FunctionDef(lllIlI)

    def visit_Name(self, llOIlI):
        if self.current_scope and self.current_scope.is_class and (llOIlI.id in self.private_attr_map):
            llOIlI.id = self.private_attr_map[llOIlI.id]
            return llOIlI
        lOlIlI = llIlO(self.current_scope, llOIlI.id)
        if lOlIlI:
            lOOIlI = (lOlIlI, llOIlI.id)
            if lOOIlI in self.mappings:
                llOIlI.id = self.mappings[lOOIlI]
            elif lOlIlI.parent is None and self.project_globals is not None and (self.current_module is not None):
                lIlIlI = (self.current_module, llOIlI.id)
                if lIlIlI in self.project_globals:
                    llOIlI.id = self.project_globals[lIlIlI]
        return llOIlI

    def visit_Attribute(self, llllOI):
        self.generic_visit(llllOI)
        if llllOI.attr in self.private_attr_map:
            llllOI.attr = self.private_attr_map[llllOI.attr]
            return llllOI
        llIIlI = llIOO(llllOI.value, self.current_scope)
        if llIIlI:
            lOllOI, lOIIlI = llIIlI
            lIIIlI = str(lOllOI) + bytes([46]).decode('utf-8') + str(bytes([46]).decode('utf-8').join(lOIIlI)) if lOIIlI else lOllOI
            if lIIIlI in self.project_modules and self.project_globals is not None:
                lIOIlI = (lIIIlI, llllOI.attr)
                if lIOIlI in self.project_globals:
                    llllOI.attr = self.project_globals[lIOIlI]
        return llllOI

    def visit_Import(self, llIlOI):
        for lOOlOI in llIlOI.names:
            lIllOI = lOOlOI.asname or lOOlOI.name.split(bytes([46]).decode('utf-8'))[0]
            llOlOI = llIlO(self.current_scope, lIllOI)
            if llOlOI:
                lOIlOI = (llOlOI, lIllOI)
                if lOIlOI in self.mappings:
                    lOOlOI.asname = self.mappings[lOIlOI]
                elif llOlOI.parent is None and self.project_globals is not None and (self.current_module is not None):
                    lIOlOI = (self.current_module, lIllOI)
                    if lIOlOI in self.project_globals:
                        lOOlOI.asname = self.project_globals[lIOlOI]
        return llIlOI

    def visit_ImportFrom(self, lIOOOI):
        if lIOOOI.level > 0:
            llOOOI = llI(self.current_module, self.is_package, lIOOOI.level, lIOOOI.module)
        else:
            llOOOI = lIOOOI.module or bytes([]).decode('utf-8')
        for lOlOOI in lIOOOI.names:
            lIIlOI = lOlOOI.asname or lOlOOI.name
            lOOOOI = False
            if llOOOI in self.project_modules and self.project_globals is not None:
                lllOOI = (llOOOI, lOlOOI.name)
                if lllOOI in self.project_globals:
                    lOlOOI.name = self.project_globals[lllOOI]
                    lOOOOI = True
            lIlOOI = llIlO(self.current_scope, lIIlOI)
            if lIlOOI:
                llIOOI = (lIlOOI, lIIlOI)
                if llIOOI in self.mappings:
                    lOlOOI.asname = self.mappings[llIOOI]
                elif lOOOOI and self.project_globals is not None:
                    lOlOOI.asname = lOlOOI.name
        return lIOOOI

    def visit_Global(self, lIlIOI):
        lOIOOI = []
        for lOlIOI in lIlIOI.names:
            lIIOOI = llIlO(self.current_scope, lOlIOI)
            if lIIOOI:
                llOIOI = (lIIOOI, lOlIOI)
                if llOIOI in self.mappings:
                    lOIOOI.append(self.mappings[llOIOI])
                elif lIIOOI.parent is None and self.project_globals is not None and (self.current_module is not None):
                    lllIOI = (self.current_module, lOlIOI)
                    if lllIOI in self.project_globals:
                        lOIOOI.append(self.project_globals[lllIOI])
                    else:
                        lOIOOI.append(lOlIOI)
                else:
                    lOIOOI.append(lOlIOI)
            else:
                lOIOOI.append(lOlIOI)
        lIlIOI.names = lOIOOI
        return lIlIOI

    def visit_Nonlocal(self, lOIIOI):
        lOOIOI = []
        for llIIOI in lOIIOI.names:
            lIOIOI = llIlO(self.current_scope, llIIOI)
            if lIOIOI:
                lIIIOI = (lIOIOI, llIIOI)
                if lIIIOI in self.mappings:
                    lOOIOI.append(self.mappings[lIIIOI])
                else:
                    lOOIOI.append(llIIOI)
            else:
                lOOIOI.append(llIIOI)
        lOIIOI.names = lOOIOI
        return lOIIOI

def lOOO(lOOOII, llIOII, lIIlII, project_modules=None, project_globals=None, current_module=None, is_package=False, keyword_args=None):
    lIllII = lOlO.parse(lOOOII)
    decoder_name = bytes([95, 48, 120, 95, 115, 116, 114, 105, 110, 103, 95, 100, 101, 99, 111, 100, 101, 114]).decode('utf-8')
    lllOII = decoder_name
    if llIOII in (bytes([115, 116, 114, 111, 110, 103]).decode('utf-8'), bytes([101, 120, 116, 114, 101, 109, 101]).decode('utf-8')):
        llOlII = bytes([10, 100, 101, 102, 32]).decode('utf-8') + str(decoder_name) + bytes([40, 98, 44, 32, 107, 41, 58, 10, 32, 32, 32, 32, 114, 101, 115, 32, 61, 32, 91, 93, 10, 32, 32, 32, 32, 100, 117, 109, 109, 121, 32, 61, 32, 107, 32, 42, 32, 50, 10, 32, 32, 32, 32, 102, 111, 114, 32, 120, 32, 105, 110, 32, 98, 58, 10, 32, 32, 32, 32, 32, 32, 32, 32, 118, 97, 108, 32, 61, 32, 120, 32, 94, 32, 107, 10, 32, 32, 32, 32, 32, 32, 32, 32, 118, 97, 108, 32, 61, 32, 118, 97, 108, 32, 43, 32, 100, 117, 109, 109, 121, 10, 32, 32, 32, 32, 32, 32, 32, 32, 118, 97, 108, 32, 61, 32, 118, 97, 108, 32, 45, 32, 100, 117, 109, 109, 121, 10, 32, 32, 32, 32, 32, 32, 32, 32, 114, 101, 115, 46, 97, 112, 112, 101, 110, 100, 40, 99, 104, 114, 40, 118, 97, 108, 41, 41, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 34, 34, 46, 106, 111, 105, 110, 40, 114, 101, 115, 41, 10]).decode('utf-8')
        lIlOII = lOlO.parse(llOlII).body
        lIllII.body = lIlOII + lIllII.body
    lIllII = llllO().visit(lIllII)
    lIllII = lOOOO().visit(lIllII)
    if keyword_args is None:
        lOOIII = lOlOO()
        lOOIII.visit(lIllII)
        keyword_args = lOOIII.keywords
        lllIII = 0
    llOIII = {}
    if llIOII in (bytes([109, 101, 100, 105, 117, 109]).decode('utf-8'), bytes([115, 116, 114, 111, 110, 103]).decode('utf-8'), bytes([101, 120, 116, 114, 101, 109, 101]).decode('utf-8')):
        llIIII = llOI()
        llIIII.visit(lIllII)
        lIOOII = llIIII.names
        lOIOII = lIOlO(style=lIIlII)
        lOIOII.existing = lIOOII
        llOOII = lOI(project_modules or set(), current_module, is_package)
        llOOII.visit(lIllII)
        llIlII = llOOII.current_scope
        llllII = llOOII.node_scopes
        lOlOII = lIIlO()
        lOlOII.visit(lIllII)
        lOlIII = lOlOII.private_attrs
        lIIOII = {}
        for attr in lOlIII:
            while True:
                lIOIII = lOIOII.get_next()
                if lIOIII not in lIOOII:
                    lIIOII[attr] = lIOIII
                    break
        llOIII = lllO(lIllII, llIlII, llllII, lOIOII, keyword_args, project_globals=project_globals, current_module=current_module)
        lllIII = len(llOIII) + len(lIIOII)
        lOllII = lOIO(llllII, llOIII, lIIOII, project_modules or set(), project_globals, current_module, is_package)
        lIllII = lOllII.visit(lIllII)
        if llIOII in (bytes([115, 116, 114, 111, 110, 103]).decode('utf-8'), bytes([101, 120, 116, 114, 101, 109, 101]).decode('utf-8')):
            if llIlII and (llIlII, decoder_name) in llOIII:
                lllOII = llOIII[llIlII, decoder_name]
            elif project_globals is not None and current_module is not None:
                lIlIII = (current_module, decoder_name)
                if lIlIII in project_globals:
                    lllOII = project_globals[lIlIII]
        llOOII = lOI(project_modules or set(), current_module, is_package)
        llOOII.visit(lIllII)
        llllII = llOOII.node_scopes
        llIlII = llOOII.current_scope
    else:
        llllII = {}
        llIlII = None
        lllOII = decoder_name
    lOOlII = lIOOO(llIOII, decoder_name=lllOII)
    lIllII = lOOlII.visit(lIllII)
    if llIOII == bytes([101, 120, 116, 114, 101, 109, 101]).decode('utf-8'):
        lIllII = lOII().visit(lIllII)
    if llIOII == bytes([101, 120, 116, 114, 101, 109, 101]).decode('utf-8'):
        lOIlII = lllOO(llIlII, llllII, bytes([95, 48, 120, 95, 98, 117, 105, 108, 116, 105, 110, 115]).decode('utf-8'), bytes([95, 48, 120, 95, 103, 101, 116, 97, 116, 116, 114]).decode('utf-8'))
        lIllII = lOIlII.visit(lIllII)
    if llIOII == bytes([101, 120, 116, 114, 101, 109, 101]).decode('utf-8'):
        lIllII = lIlI().visit(lIllII)
    if llIOII == bytes([101, 120, 116, 114, 101, 109, 101]).decode('utf-8'):
        llOlII = bytes([10, 105, 109, 112, 111, 114, 116, 32, 98, 117, 105, 108, 116, 105, 110, 115, 32, 97, 115, 32, 95, 48, 120, 95, 98, 117, 105, 108, 116, 105, 110, 115, 10, 95, 48, 120, 95, 103, 101, 116, 97, 116, 116, 114, 32, 61, 32, 95, 48, 120, 95, 98, 117, 105, 108, 116, 105, 110, 115, 46, 103, 101, 116, 97, 116, 116, 114, 10]).decode('utf-8')
        lIlOII = lOlO.parse(llOlII).body
        lIllII.body = lIlOII + lIllII.body
    lOlO.fix_missing_locations(lIllII)
    lIOlII = lOlO.unparse(lIllII)
    try:
        lOlO.parse(lIOlII)
    except Exception as e:
        raise ValueError(bytes([71, 101, 110, 101, 114, 97, 116, 101, 100, 32, 99, 111, 100, 101, 32, 105, 115, 32, 115, 121, 110, 116, 97, 99, 116, 105, 99, 97, 108, 108, 121, 32, 105, 110, 118, 97, 108, 105, 100, 58, 32]).decode('utf-8') + str(e))
    return (lIOlII, lllIII, lOOlII.string_count)

def lllO(lIIlllO, lOlOllO, lOIIII, lIOlllO, keyword_args, project_globals=None, current_module=None):
    llllllO = {}
    lOOlllO = set(dir(llII))
    llOlllO = {bytes([95, 95, 109, 97, 105, 110, 95, 95]).decode('utf-8'), bytes([95, 95, 110, 97, 109, 101, 95, 95]).decode('utf-8'), bytes([109, 97, 105, 110]).decode('utf-8'), bytes([115, 101, 108, 102]).decode('utf-8'), bytes([99, 108, 115]).decode('utf-8')}
    lllOllO = lOlOllO
    for lOllllO in lllOllO.defined:
        if lOllllO.startswith(bytes([95, 95]).decode('utf-8')) and lOllllO.endswith(bytes([95, 95]).decode('utf-8')):
            continue
        if lOllllO in lOOlllO or lOllllO in llOlllO:
            continue
        if project_globals is not None and current_module is not None:
            llIlllO = (current_module, lOllllO)
            if llIlllO in project_globals:
                lIllllO = project_globals[llIlllO]
            else:
                lIllllO = lIOlllO.get_next()
                project_globals[llIlllO] = lIllllO
        else:
            lIllllO = lIOlllO.get_next()
        llllllO[lllOllO, lOllllO] = lIllllO

    def lOIlllO(lIOOllO):
        if not lIOOllO.is_class:
            for llOOllO in lIOOllO.defined:
                if llOOllO.startswith(bytes([95, 95]).decode('utf-8')) and llOOllO.endswith(bytes([95, 95]).decode('utf-8')):
                    continue
                if llOOllO in lOOlllO or llOOllO in llOlllO:
                    continue
                if llOOllO in keyword_args:
                    continue
                lOOOllO = lIOlllO.get_next()
                llllllO[lIOOllO, llOOllO] = lOOOllO
        for lIlOllO in lIOOllO.children:
            lOIlllO(lIlOllO)
    for lIIIII in lllOllO.children:
        lOIlllO(lIIIII)
    return llllllO

def lllI(llIOllO, llOIllO, lIlIllO, lllIllO):
    with open(llIOllO, bytes([114]).decode('utf-8'), encoding=bytes([117, 116, 102, 45, 56]).decode('utf-8')) as lOIOllO:
        lIOIllO = lOIOllO.read()
    lIIOllO, lOlIllO, lOOIllO = lOOO(lIOIllO, lIlIllO, lllIllO)
    with open(llOIllO, bytes([119]).decode('utf-8'), encoding=bytes([117, 116, 102, 45, 56]).decode('utf-8')) as lOIOllO:
        lOIOllO.write(lIIOllO)
    return {bytes([102, 105, 108, 101, 115, 95, 112, 114, 111, 99, 101, 115, 115, 101, 100]).decode('utf-8'): 1, bytes([114, 101, 110, 97, 109, 101, 100, 95, 105, 100, 101, 110, 116, 105, 102, 105, 101, 114, 115]).decode('utf-8'): lOlIllO, bytes([115, 116, 114, 105, 110, 103, 115, 95, 111, 98, 102, 117, 115, 99, 97, 116, 101, 100]).decode('utf-8'): lOOIllO, bytes([101, 114, 114, 111, 114, 115]).decode('utf-8'): []}

def lIlO(lIIOOlO, lOOOOlO, lOOIOlO, lOlOOlO):
    lIIOOlO = llOO.path.abspath(lIIOOlO)
    lOOOOlO = llOO.path.abspath(lOOOOlO)
    lOOlOlO = []
    llllIlO = []
    for llOlOlO, lIOOOlO, lIIIllO in llOO.walk(lIIOOlO):
        if llOO.path.commonpath([llOlOlO, lOOOOlO]) == lOOOOlO:
            continue
        for lOllOlO in lIIIllO:
            lIIlOlO = llOO.path.join(llOlOlO, lOllOlO)
            llllOlO = llOO.path.relpath(lIIlOlO, lIIOOlO)
            if lOllOlO.endswith(bytes([46, 112, 121]).decode('utf-8')):
                lOOlOlO.append((lIIlOlO, llllOlO))
            else:
                llllIlO.append((lIIlOlO, llllOlO))
    project_modules = set()
    llIlOlO = {}
    for lIIlOlO, llllOlO in lOOlOlO:
        lIlOOlO = lIOO(lIIlOlO, lIIOOlO)
        project_modules.add(lIlOOlO)
        llIlOlO[lIIlOlO] = lIlOOlO
    keyword_args = set()
    lIOIOlO = set()
    for lIIlOlO, llIIllO in lOOlOlO:
        try:
            with open(lIIlOlO, bytes([114]).decode('utf-8'), encoding=bytes([117, 116, 102, 45, 56]).decode('utf-8')) as lIOlOlO:
                lIIIOlO = lIOlOlO.read()
            lOIIllO = lOlO.parse(lIIIOlO)
            llOlIlO = llOI()
            llOlIlO.visit(lOIIllO)
            lIOIOlO.update(llOlIlO.names)
            lIllIlO = lOlOO()
            lIllIlO.visit(lOIIllO)
            keyword_args.update(lIllIlO.keywords)
        except Exception as e:
            print(bytes([87, 97, 114, 110, 105, 110, 103, 58, 32, 70, 97, 105, 108, 101, 100, 32, 116, 111, 32, 112, 97, 114, 115, 101, 32]).decode('utf-8') + str(lIIlOlO) + bytes([58, 32]).decode('utf-8') + str(e))
    llIIOlO = lIOlO(style=lOlOOlO)
    llIIOlO.existing = lIOIOlO
    project_globals = {}
    llOOOlO = set(dir(llII))
    lOIIOlO = {bytes([95, 95, 109, 97, 105, 110, 95, 95]).decode('utf-8'), bytes([95, 95, 110, 97, 109, 101, 95, 95]).decode('utf-8'), bytes([109, 97, 105, 110]).decode('utf-8'), bytes([115, 101, 108, 102]).decode('utf-8'), bytes([99, 108, 115]).decode('utf-8')}
    for lIIlOlO, llIIllO in lOOlOlO:
        lIlOOlO = llIlOlO.get(lIIlOlO)
        if not lIlOOlO:
            continue
        project_globals[lIlOOlO, bytes([95, 48, 120, 95, 115, 116, 114, 105, 110, 103, 95, 100, 101, 99, 111, 100, 101, 114]).decode('utf-8')] = llIIOlO.get_next()
        try:
            with open(lIIlOlO, bytes([114]).decode('utf-8'), encoding=bytes([117, 116, 102, 45, 56]).decode('utf-8')) as lIOlOlO:
                lIIIOlO = lIOlOlO.read()
            lOIIllO = lOlO.parse(lIIIOlO)
            lOIlOlO = llOO.path.basename(lIIlOlO) == bytes([95, 95, 105, 110, 105, 116, 95, 95, 46, 112, 121]).decode('utf-8')
            llOIOlO = lOI(project_modules, lIlOOlO, lOIlOlO)
            llOIOlO.visit(lOIIllO)
            lOIOOlO = llOIOlO.current_scope
            for lllIOlO in lOIOOlO.defined:
                if lllIOlO.startswith(bytes([95, 95]).decode('utf-8')) and lllIOlO.endswith(bytes([95, 95]).decode('utf-8')):
                    continue
                if lllIOlO in llOOOlO or lllIOlO in lOIIOlO:
                    continue
                lIllOlO = (lIlOOlO, lllIOlO)
                if lIllOlO not in project_globals:
                    project_globals[lIllOlO] = llIIOlO.get_next()
        except Exception:
            pass
    if not llOO.path.exists(lOOOOlO):
        llOO.makedirs(lOOOOlO)
    for lIIlOlO, llllOlO in llllIlO:
        lIlIOlO = llOO.path.join(lOOOOlO, llllOlO)
        llIOOlO = llOO.path.dirname(lIlIOlO)
        if not llOO.path.exists(llIOOlO):
            llOO.makedirs(llIOOlO)
        lIOI.copy2(lIIlOlO, lIlIOlO)
    lOlIOlO = {bytes([102, 105, 108, 101, 115, 95, 112, 114, 111, 99, 101, 115, 115, 101, 100]).decode('utf-8'): 0, bytes([114, 101, 110, 97, 109, 101, 100, 95, 105, 100, 101, 110, 116, 105, 102, 105, 101, 114, 115]).decode('utf-8'): 0, bytes([115, 116, 114, 105, 110, 103, 115, 95, 111, 98, 102, 117, 115, 99, 97, 116, 101, 100]).decode('utf-8'): 0, bytes([101, 114, 114, 111, 114, 115]).decode('utf-8'): []}
    for lIIlOlO, llllOlO in lOOlOlO:
        lIlIOlO = llOO.path.join(lOOOOlO, llllOlO)
        llIOOlO = llOO.path.dirname(lIlIOlO)
        if not llOO.path.exists(llIOOlO):
            llOO.makedirs(llIOOlO)
        lIlOOlO = llIlOlO[lIIlOlO]
        lOIlOlO = llOO.path.basename(lIIlOlO) == bytes([95, 95, 105, 110, 105, 116, 95, 95, 46, 112, 121]).decode('utf-8')
        try:
            with open(lIIlOlO, bytes([114]).decode('utf-8'), encoding=bytes([117, 116, 102, 45, 56]).decode('utf-8')) as lIOlOlO:
                lIIIOlO = lIOlOlO.read()
            lllOOlO, lOllIlO, lOOlIlO = lOOO(lIIIOlO, lOOIOlO, lOlOOlO, project_modules=project_modules, project_globals=project_globals, current_module=lIlOOlO, is_package=lOIlOlO, keyword_args=keyword_args)
            with open(lIlIOlO, bytes([119]).decode('utf-8'), encoding=bytes([117, 116, 102, 45, 56]).decode('utf-8')) as lIOlOlO:
                lIOlOlO.write(lllOOlO)
            lOlIOlO[bytes([102, 105, 108, 101, 115, 95, 112, 114, 111, 99, 101, 115, 115, 101, 100]).decode('utf-8')] += 1
            lOlIOlO[bytes([114, 101, 110, 97, 109, 101, 100, 95, 105, 100, 101, 110, 116, 105, 102, 105, 101, 114, 115]).decode('utf-8')] += lOllIlO
            lOlIOlO[bytes([115, 116, 114, 105, 110, 103, 115, 95, 111, 98, 102, 117, 115, 99, 97, 116, 101, 100]).decode('utf-8')] += lOOlIlO
        except Exception as e:
            lOlIOlO[bytes([101, 114, 114, 111, 114, 115]).decode('utf-8')].append((llllOlO, str(e)))
            print(bytes([69, 114, 114, 111, 114, 32, 111, 98, 102, 117, 115, 99, 97, 116, 105, 110, 103, 32]).decode('utf-8') + str(llllOlO) + bytes([58, 32]).decode('utf-8') + str(e))
    return lOlIOlO

def lOIlO():
    lIOlIlO = bytes([10, 92, 48, 51, 51, 91, 49, 59, 51, 53, 109, 32, 95, 95, 32, 32, 95, 95, 32, 95, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 95, 32, 32, 32, 32, 32, 32, 10, 124, 32, 32, 92, 47, 32, 32, 40, 95, 41, 32, 32, 32, 32, 32, 32, 32, 32, 32, 40, 95, 41, 32, 32, 32, 32, 32, 10, 124, 32, 92, 32, 32, 47, 32, 124, 95, 32, 95, 32, 95, 95, 32, 95, 95, 95, 32, 32, 95, 32, 32, 95, 95, 95, 32, 10, 124, 32, 124, 92, 47, 124, 32, 124, 32, 124, 32, 39, 95, 32, 96, 32, 95, 32, 92, 124, 32, 124, 47, 32, 95, 95, 124, 10, 124, 32, 124, 32, 32, 124, 32, 124, 32, 124, 32, 124, 32, 124, 32, 124, 32, 124, 32, 124, 32, 124, 32, 40, 95, 95, 32, 10, 124, 95, 124, 32, 32, 124, 95, 124, 95, 124, 95, 124, 32, 124, 95, 124, 32, 124, 95, 124, 95, 124, 92, 95, 95, 95, 124, 32, 92, 48, 51, 51, 91, 48, 109, 10, 92, 48, 51, 51, 91, 49, 59, 51, 54, 109, 32, 32, 32, 32, 32, 65, 83, 84, 45, 66, 97, 115, 101, 100, 32, 80, 121, 116, 104, 111, 110, 32, 83, 111, 117, 114, 99, 101, 32, 79, 98, 102, 117, 115, 99, 97, 116, 111, 114, 32, 118, 49, 46, 48, 46, 48, 92, 48, 51, 51, 91, 48, 109, 10, 92, 48, 51, 51, 91, 49, 59, 51, 55, 109, 32, 32, 32, 32, 32, 67, 111, 109, 112, 97, 116, 105, 98, 108, 101, 32, 119, 105, 116, 104, 32, 80, 121, 116, 104, 111, 110, 32, 51, 46, 49, 48, 43, 32, 124, 32, 83, 105, 110, 103, 108, 101, 32, 83, 99, 114, 105, 112, 116, 92, 48, 51, 51, 91, 48, 109, 10]).decode('utf-8')
    print(lIOlIlO)

def llOOO(lIlOIlO, lOIlIlO, lllOIlO):
    print(bytes([10, 27, 91, 49, 59, 51, 50, 109, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 27, 91, 48, 109]).decode('utf-8'))
    print(bytes([27, 91, 49, 59, 51, 50, 109, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 79, 66, 70, 85, 83, 67, 65, 84, 73, 79, 78, 32, 67, 79, 77, 80, 76, 69, 84, 69, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 27, 91, 48, 109]).decode('utf-8'))
    print(bytes([27, 91, 49, 59, 51, 50, 109, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 27, 91, 48, 109]).decode('utf-8'))
    print(bytes([32, 70, 105, 108, 101, 115, 32, 80, 114, 111, 99, 101, 115, 115, 101, 100, 58, 32, 32, 32, 32, 32, 32]).decode('utf-8') + str(lIlOIlO[bytes([102, 105, 108, 101, 115, 95, 112, 114, 111, 99, 101, 115, 115, 101, 100]).decode('utf-8')]))
    print(bytes([32, 73, 100, 101, 110, 116, 105, 102, 105, 101, 114, 115, 32, 82, 101, 110, 97, 109, 101, 100, 58, 32, 32]).decode('utf-8') + str(lIlOIlO[bytes([114, 101, 110, 97, 109, 101, 100, 95, 105, 100, 101, 110, 116, 105, 102, 105, 101, 114, 115]).decode('utf-8')]))
    print(bytes([32, 83, 116, 114, 105, 110, 103, 115, 32, 79, 98, 102, 117, 115, 99, 97, 116, 101, 100, 58, 32, 32, 32]).decode('utf-8') + str(lIlOIlO[bytes([115, 116, 114, 105, 110, 103, 115, 95, 111, 98, 102, 117, 115, 99, 97, 116, 101, 100]).decode('utf-8')]))
    print(bytes([32, 80, 114, 111, 99, 101, 115, 115, 105, 110, 103, 32, 84, 105, 109, 101, 58, 32, 32, 32, 32, 32, 32]).decode('utf-8') + format(lOIlIlO, bytes([46, 51, 102]).decode('utf-8')) + bytes([32, 115, 101, 99, 111, 110, 100, 115]).decode('utf-8'))
    if llOO.path.isfile(lllOIlO):
        llOOIlO = llOO.path.getsize(lllOIlO)
        print(bytes([32, 79, 117, 116, 112, 117, 116, 32, 70, 105, 108, 101, 32, 83, 105, 122, 101, 58, 32, 32, 32, 32, 32]).decode('utf-8') + format(llOOIlO, bytes([44]).decode('utf-8')) + bytes([32, 98, 121, 116, 101, 115]).decode('utf-8'))
    elif llOO.path.isdir(lllOIlO):
        lOIOIlO = 0
        for llIlIlO, lIIlIlO, lIOOIlO in llOO.walk(lllOIlO):
            for lOlOIlO in lIOOIlO:
                lOIOIlO += llOO.path.getsize(llOO.path.join(llIlIlO, lOlOIlO))
        print(bytes([32, 79, 117, 116, 112, 117, 116, 32, 70, 111, 108, 100, 101, 114, 32, 83, 105, 122, 101, 58, 32, 32, 32]).decode('utf-8') + format(lOIOIlO, bytes([44]).decode('utf-8')) + bytes([32, 98, 121, 116, 101, 115]).decode('utf-8'))
    print(bytes([32, 79, 117, 116, 112, 117, 116, 32, 76, 111, 99, 97, 116, 105, 111, 110, 58, 32, 32, 32, 32, 32, 32]).decode('utf-8') + str(lllOIlO))
    if lIlOIlO[bytes([101, 114, 114, 111, 114, 115]).decode('utf-8')]:
        print(bytes([27, 91, 49, 59, 51, 49, 109, 10, 69, 114, 114, 111, 114, 115, 32, 69, 110, 99, 111, 117, 110, 116, 101, 114, 101, 100, 58, 27, 91, 48, 109]).decode('utf-8'))
        for llIOIlO, lOOOIlO in lIlOIlO[bytes([101, 114, 114, 111, 114, 115]).decode('utf-8')]:
            print(bytes([32, 45, 32]).decode('utf-8') + str(llIOIlO) + bytes([58, 32]).decode('utf-8') + str(lOOOIlO))
    print(bytes([27, 91, 49, 59, 51, 50, 109, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 27, 91, 48, 109]).decode('utf-8'))

def lOllO():
    print(bytes([10, 83, 101, 108, 101, 99, 116, 32, 79, 98, 102, 117, 115, 99, 97, 116, 105, 111, 110, 32, 76, 101, 118, 101, 108, 58]).decode('utf-8'))
    print(bytes([32, 91, 49, 93, 32, 66, 97, 115, 105, 99, 32, 32, 32, 45, 32, 83, 116, 114, 105, 112, 115, 32, 99, 111, 109, 109, 101, 110, 116, 115, 47, 100, 111, 99, 115, 116, 114, 105, 110, 103, 115, 46]).decode('utf-8'))
    print(bytes([32, 91, 50, 93, 32, 77, 101, 100, 105, 117, 109, 32, 32, 45, 32, 83, 116, 114, 105, 112, 115, 32, 99, 111, 109, 109, 101, 110, 116, 115, 47, 100, 111, 99, 115, 116, 114, 105, 110, 103, 115, 44, 32, 114, 101, 110, 97, 109, 101, 115, 32, 108, 111, 99, 97, 108, 32, 118, 97, 114, 105, 97, 98, 108, 101, 115, 44, 32, 101, 115, 99, 97, 112, 101, 115, 32, 115, 116, 114, 105, 110, 103, 115, 46]).decode('utf-8'))
    print(bytes([32, 91, 51, 93, 32, 83, 116, 114, 111, 110, 103, 32, 32, 45, 32, 83, 116, 114, 105, 112, 115, 32, 99, 111, 109, 109, 101, 110, 116, 115, 47, 100, 111, 99, 115, 116, 114, 105, 110, 103, 115, 44, 32, 114, 101, 110, 97, 109, 101, 115, 32, 103, 108, 111, 98, 97, 108, 115, 47, 108, 111, 99, 97, 108, 115, 44, 32, 88, 79, 82, 32, 101, 110, 99, 114, 121, 112, 116, 115, 32, 115, 116, 114, 105, 110, 103, 115, 46, 32, 40, 82, 101, 99, 111, 109, 109, 101, 110, 100, 101, 100, 41]).decode('utf-8'))
    print(bytes([32, 91, 52, 93, 32, 69, 120, 116, 114, 101, 109, 101, 32, 45, 32, 83, 116, 114, 111, 110, 103, 32, 43, 32, 99, 111, 110, 116, 114, 111, 108, 32, 102, 108, 111, 119, 32, 102, 108, 97, 116, 116, 101, 110, 105, 110, 103, 32, 43, 32, 109, 97, 116, 104, 32, 111, 98, 102, 117, 115, 99, 97, 116, 105, 111, 110, 32, 43, 32, 98, 117, 105, 108, 116, 105, 110, 32, 104, 105, 100, 105, 110, 103, 46]).decode('utf-8'))
    while True:
        lIIOIlO = input(bytes([76, 101, 118, 101, 108, 32, 91, 49, 45, 52, 93, 58, 32]).decode('utf-8')).strip()
        if lIIOIlO == bytes([49]).decode('utf-8'):
            return bytes([98, 97, 115, 105, 99]).decode('utf-8')
        elif lIIOIlO == bytes([50]).decode('utf-8'):
            return bytes([109, 101, 100, 105, 117, 109]).decode('utf-8')
        elif lIIOIlO == bytes([51]).decode('utf-8'):
            return bytes([115, 116, 114, 111, 110, 103]).decode('utf-8')
        elif lIIOIlO == bytes([52]).decode('utf-8'):
            return bytes([101, 120, 116, 114, 101, 109, 101]).decode('utf-8')
        print(bytes([27, 91, 49, 59, 51, 49, 109, 73, 110, 118, 97, 108, 105, 100, 32, 99, 104, 111, 105, 99, 101, 46, 32, 84, 114, 121, 32, 97, 103, 97, 105, 110, 46, 27, 91, 48, 109]).decode('utf-8'))

def llOlO(lllIIlO):
    if lllIIlO == bytes([98, 97, 115, 105, 99]).decode('utf-8'):
        return bytes([104, 101, 120]).decode('utf-8')
    print(bytes([10, 83, 101, 108, 101, 99, 116, 32, 73, 100, 101, 110, 116, 105, 102, 105, 101, 114, 32, 82, 101, 110, 97, 109, 105, 110, 103, 32, 83, 116, 121, 108, 101, 58]).decode('utf-8'))
    print(bytes([32, 91, 49, 93, 32, 72, 101, 120, 97, 100, 101, 99, 105, 109, 97, 108, 32, 40, 96, 95, 48, 120, 49, 97, 96, 41, 32, 45, 32, 67, 108, 101, 97, 110, 32, 97, 110, 100, 32, 115, 116, 97, 110, 100, 97, 114, 100, 46]).decode('utf-8'))
    print(bytes([32, 91, 50, 93, 32, 67, 111, 110, 102, 117, 115, 105, 110, 103, 32, 40, 96, 108, 79, 49, 108, 73, 79, 96, 41, 32, 32, 32, 45, 32, 72, 97, 114, 100, 32, 116, 111, 32, 100, 105, 115, 116, 105, 110, 103, 117, 105, 115, 104, 32, 105, 110, 32, 116, 121, 112, 105, 99, 97, 108, 32, 101, 100, 105, 116, 111, 114, 115, 46]).decode('utf-8'))
    print(bytes([32, 91, 51, 93, 32, 77, 105, 120, 101, 100, 32, 67, 104, 105, 110, 101, 115, 101, 47, 69, 110, 103, 108, 105, 115, 104, 32, 40, 96, 230, 158, 129, 95, 108, 49, 79, 96, 41, 32, 45, 32, 67, 111, 110, 102, 117, 115, 101, 115, 32, 98, 111, 116, 104, 32, 104, 117, 109, 97, 110, 32, 114, 101, 97, 100, 101, 114, 115, 32, 97, 110, 100, 32, 115, 105, 109, 112, 108, 101, 32, 115, 99, 114, 105, 112, 116, 115, 46]).decode('utf-8'))
    while True:
        style = input(bytes([83, 116, 121, 108, 101, 32, 91, 49, 45, 51, 93, 58, 32]).decode('utf-8')).strip()
        if style == bytes([49]).decode('utf-8'):
            return bytes([104, 101, 120]).decode('utf-8')
        elif style == bytes([50]).decode('utf-8'):
            return bytes([99, 111, 110, 102, 117, 115, 105, 110, 103]).decode('utf-8')
        elif style == bytes([51]).decode('utf-8'):
            return bytes([99, 104, 105, 110, 101, 115, 101]).decode('utf-8')
        print(bytes([27, 91, 49, 59, 51, 49, 109, 73, 110, 118, 97, 108, 105, 100, 32, 99, 104, 111, 105, 99, 101, 46, 32, 84, 114, 121, 32, 97, 103, 97, 105, 110, 46, 27, 91, 48, 109]).decode('utf-8'))

def llIO():
    print(bytes([10, 45, 45, 45, 32, 79, 98, 102, 117, 115, 99, 97, 116, 101, 32, 83, 105, 110, 103, 108, 101, 32, 70, 105, 108, 101, 32, 45, 45, 45]).decode('utf-8'))
    while True:
        lOlIIlO = input(bytes([68, 114, 97, 103, 32, 38, 32, 100, 114, 111, 112, 32, 102, 105, 108, 101, 32, 112, 97, 116, 104, 32, 104, 101, 114, 101, 32, 40, 111, 114, 32, 116, 121, 112, 101, 32, 112, 97, 116, 104, 41, 58, 32]).decode('utf-8')).strip().strip(bytes([39, 34]).decode('utf-8'))
        if not lOlIIlO:
            return
        if not llOO.path.isfile(lOlIIlO):
            print(bytes([27, 91, 49, 59, 51, 49, 109, 69, 114, 114, 111, 114, 58, 32, 70, 105, 108, 101, 32, 110, 111, 116, 32, 102, 111, 117, 110, 100, 46, 27, 91, 48, 109]).decode('utf-8'))
            continue
        break
    llOIIlO = lOllO()
    style = llOlO(llOIIlO)
    lOOIIlO = lOlIIlO.rsplit(bytes([46]).decode('utf-8'), 1)[0] + bytes([95, 111, 98, 102, 46, 112, 121]).decode('utf-8')
    lIOIIlO = input(bytes([79, 117, 116, 112, 117, 116, 32, 112, 97, 116, 104, 32, 91]).decode('utf-8') + str(lOOIIlO) + bytes([93, 58, 32]).decode('utf-8')).strip().strip(bytes([39, 34]).decode('utf-8'))
    if not lIOIIlO:
        lIOIIlO = lOOIIlO
    llIIIlO = lOOlO.time()
    print(bytes([10, 79, 98, 102, 117, 115, 99, 97, 116, 105, 110, 103, 32]).decode('utf-8') + str(llOO.path.basename(lOlIIlO)) + bytes([46, 46, 46]).decode('utf-8'))
    try:
        lIlIIlO = lllI(lOlIIlO, lIOIIlO, llOIIlO, style)
        llOOO(lIlIIlO, lOOlO.time() - llIIIlO, lIOIIlO)
    except Exception as e:
        print(bytes([27, 91, 49, 59, 51, 49, 109, 79, 98, 102, 117, 115, 99, 97, 116, 105, 111, 110, 32, 102, 97, 105, 108, 101, 100, 58, 32]).decode('utf-8') + str(e) + bytes([27, 91, 48, 109]).decode('utf-8'))

def lIIO():
    print(bytes([10, 45, 45, 45, 32, 79, 98, 102, 117, 115, 99, 97, 116, 101, 32, 80, 114, 111, 106, 101, 99, 116, 32, 70, 111, 108, 100, 101, 114, 32, 45, 45, 45]).decode('utf-8'))
    while True:
        lOIIIlO = input(bytes([68, 114, 97, 103, 32, 38, 32, 100, 114, 111, 112, 32, 102, 111, 108, 100, 101, 114, 32, 112, 97, 116, 104, 32, 104, 101, 114, 101, 32, 40, 111, 114, 32, 116, 121, 112, 101, 32, 112, 97, 116, 104, 41, 58, 32]).decode('utf-8')).strip().strip(bytes([39, 34]).decode('utf-8'))
        if not lOIIIlO:
            return
        if not llOO.path.isdir(lOIIIlO):
            print(bytes([27, 91, 49, 59, 51, 49, 109, 69, 114, 114, 111, 114, 58, 32, 68, 105, 114, 101, 99, 116, 111, 114, 121, 32, 110, 111, 116, 32, 102, 111, 117, 110, 100, 46, 27, 91, 48, 109]).decode('utf-8'))
            continue
        break
    lllllOO = lOllO()
    style = llOlO(lllllOO)
    lOlllOO = lOIIIlO.rstrip(bytes([47, 92]).decode('utf-8')) + bytes([95, 111, 98, 102]).decode('utf-8')
    lIlllOO = input(bytes([79, 117, 116, 112, 117, 116, 32, 102, 111, 108, 100, 101, 114, 32, 112, 97, 116, 104, 32, 91]).decode('utf-8') + str(lOlllOO) + bytes([93, 58, 32]).decode('utf-8')).strip().strip(bytes([39, 34]).decode('utf-8'))
    if not lIlllOO:
        lIlllOO = lOlllOO
    llOllOO = lOOlO.time()
    print(bytes([10, 79, 98, 102, 117, 115, 99, 97, 116, 105, 110, 103, 32, 112, 114, 111, 106, 101, 99, 116, 32]).decode('utf-8') + str(llOO.path.basename(lOIIIlO)) + bytes([46, 46, 46]).decode('utf-8'))
    try:
        lIIIIlO = lIlO(lOIIIlO, lIlllOO, lllllOO, style)
        llOOO(lIIIIlO, lOOlO.time() - llOllOO, lIlllOO)
    except Exception as e:
        print(bytes([27, 91, 49, 59, 51, 49, 109, 79, 98, 102, 117, 115, 99, 97, 116, 105, 111, 110, 32, 102, 97, 105, 108, 101, 100, 58, 32]).decode('utf-8') + str(e) + bytes([27, 91, 48, 109]).decode('utf-8'))

def lIlOO():
    lOIlO()
    while True:
        print(bytes([10, 27, 91, 49, 59, 51, 54, 109, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 27, 91, 48, 109]).decode('utf-8'))
        print(bytes([27, 91, 49, 59, 51, 54, 109, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 77, 73, 77, 73, 67, 32, 79, 66, 70, 85, 83, 67, 65, 84, 79, 82, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 27, 91, 48, 109]).decode('utf-8'))
        print(bytes([27, 91, 49, 59, 51, 54, 109, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 27, 91, 48, 109]).decode('utf-8'))
        print(bytes([32, 91, 49, 93, 32, 79, 98, 102, 117, 115, 99, 97, 116, 101, 32, 83, 105, 110, 103, 108, 101, 32, 80, 121, 116, 104, 111, 110, 32, 70, 105, 108, 101]).decode('utf-8'))
        print(bytes([32, 91, 50, 93, 32, 79, 98, 102, 117, 115, 99, 97, 116, 101, 32, 80, 114, 111, 106, 101, 99, 116, 32, 70, 111, 108, 100, 101, 114]).decode('utf-8'))
        print(bytes([32, 91, 51, 93, 32, 69, 120, 105, 116]).decode('utf-8'))
        print(bytes([27, 91, 49, 59, 51, 54, 109, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 27, 91, 48, 109]).decode('utf-8'))
        lOOllOO = input(bytes([83, 101, 108, 101, 99, 116, 32, 97, 110, 32, 111, 112, 116, 105, 111, 110, 32, 91, 49, 45, 51, 93, 58, 32]).decode('utf-8')).strip()
        if lOOllOO == bytes([51]).decode('utf-8'):
            print(bytes([10, 71, 111, 111, 100, 98, 121, 101, 33]).decode('utf-8'))
            break
        elif lOOllOO == bytes([49]).decode('utf-8'):
            llIO()
        elif lOOllOO == bytes([50]).decode('utf-8'):
            lIIO()
        else:
            print(bytes([27, 91, 49, 59, 51, 49, 109, 73, 110, 118, 97, 108, 105, 100, 32, 99, 104, 111, 105, 99, 101, 46, 32, 80, 108, 101, 97, 115, 101, 32, 115, 101, 108, 101, 99, 116, 32, 49, 44, 32, 50, 44, 32, 111, 114, 32, 51, 46, 27, 91, 48, 109]).decode('utf-8'))

def main():
    lIIllOO = lIII.ArgumentParser(description=bytes([77, 105, 109, 105, 99, 58, 32, 80, 114, 111, 102, 101, 115, 115, 105, 111, 110, 97, 108, 32, 65, 83, 84, 45, 66, 97, 115, 101, 100, 32, 80, 121, 116, 104, 111, 110, 32, 79, 98, 102, 117, 115, 99, 97, 116, 111, 114]).decode('utf-8'))
    lIIllOO.add_argument(bytes([45, 102]).decode('utf-8'), bytes([45, 45, 102, 105, 108, 101]).decode('utf-8'), help=bytes([80, 97, 116, 104, 32, 116, 111, 32, 97, 32, 115, 105, 110, 103, 108, 101, 32, 80, 121, 116, 104, 111, 110, 32, 102, 105, 108, 101, 32, 116, 111, 32, 111, 98, 102, 117, 115, 99, 97, 116, 101]).decode('utf-8'))
    lIIllOO.add_argument(bytes([45, 100]).decode('utf-8'), bytes([45, 45, 100, 105, 114, 101, 99, 116, 111, 114, 121]).decode('utf-8'), help=bytes([80, 97, 116, 104, 32, 116, 111, 32, 97, 32, 102, 111, 108, 100, 101, 114, 47, 112, 114, 111, 106, 101, 99, 116, 32, 116, 111, 32, 111, 98, 102, 117, 115, 99, 97, 116, 101]).decode('utf-8'))
    lIIllOO.add_argument(bytes([45, 111]).decode('utf-8'), bytes([45, 45, 111, 117, 116, 112, 117, 116]).decode('utf-8'), help=bytes([79, 117, 116, 112, 117, 116, 32, 112, 97, 116, 104, 32, 40, 102, 105, 108, 101, 32, 110, 97, 109, 101, 32, 102, 111, 114, 32, 115, 105, 110, 103, 108, 101, 45, 102, 105, 108, 101, 44, 32, 102, 111, 108, 100, 101, 114, 32, 110, 97, 109, 101, 32, 102, 111, 114, 32, 112, 114, 111, 106, 101, 99, 116, 41]).decode('utf-8'))
    lIIllOO.add_argument(bytes([45, 108]).decode('utf-8'), bytes([45, 45, 108, 101, 118, 101, 108]).decode('utf-8'), choices=[bytes([98, 97, 115, 105, 99]).decode('utf-8'), bytes([109, 101, 100, 105, 117, 109]).decode('utf-8'), bytes([115, 116, 114, 111, 110, 103]).decode('utf-8'), bytes([101, 120, 116, 114, 101, 109, 101]).decode('utf-8')], default=None, help=bytes([79, 98, 102, 117, 115, 99, 97, 116, 105, 111, 110, 32, 108, 101, 118, 101, 108, 58, 32, 98, 97, 115, 105, 99, 44, 32, 109, 101, 100, 105, 117, 109, 44, 32, 115, 116, 114, 111, 110, 103, 44, 32, 101, 120, 116, 114, 101, 109, 101]).decode('utf-8'))
    lIIllOO.add_argument(bytes([45, 115]).decode('utf-8'), bytes([45, 45, 115, 116, 121, 108, 101]).decode('utf-8'), choices=[bytes([104, 101, 120]).decode('utf-8'), bytes([99, 111, 110, 102, 117, 115, 105, 110, 103]).decode('utf-8'), bytes([99, 104, 105, 110, 101, 115, 101]).decode('utf-8')], default=bytes([104, 101, 120]).decode('utf-8'), help=bytes([86, 97, 114, 105, 97, 98, 108, 101, 32, 114, 101, 110, 97, 109, 105, 110, 103, 32, 115, 116, 121, 108, 101, 58, 32, 104, 101, 120, 44, 32, 99, 111, 110, 102, 117, 115, 105, 110, 103, 44, 32, 99, 104, 105, 110, 101, 115, 101]).decode('utf-8'))
    lIIllOO.add_argument(bytes([45, 105]).decode('utf-8'), bytes([45, 45, 105, 110, 116, 101, 114, 97, 99, 116, 105, 118, 101]).decode('utf-8'), action=bytes([115, 116, 111, 114, 101, 95, 116, 114, 117, 101]).decode('utf-8'), help=bytes([70, 111, 114, 99, 101, 32, 105, 110, 116, 101, 114, 97, 99, 116, 105, 118, 101, 32, 109, 111, 100, 101]).decode('utf-8'))
    args = lIIllOO.parse_args()
    if len(lOlI.argv) == 1 or args.interactive:
        lIlOO()
    else:
        if not args.file and (not args.directory):
            print(bytes([69, 114, 114, 111, 114, 58, 32, 89, 111, 117, 32, 109, 117, 115, 116, 32, 115, 112, 101, 99, 105, 102, 121, 32, 101, 105, 116, 104, 101, 114, 32, 45, 102, 47, 45, 45, 102, 105, 108, 101, 32, 111, 114, 32, 45, 100, 47, 45, 45, 100, 105, 114, 101, 99, 116, 111, 114, 121, 46]).decode('utf-8'))
            lOlI.exit(1)
        lOIllOO = args.level or bytes([115, 116, 114, 111, 110, 103]).decode('utf-8')
        style = args.style
        lllOlOO = lOOlO.time()
        if args.file:
            lIOllOO = args.file.strip(bytes([39, 34]).decode('utf-8'))
            if not llOO.path.isfile(lIOllOO):
                print(bytes([69, 114, 114, 111, 114, 58, 32, 70, 105, 108, 101, 32, 110, 111, 116, 32, 102, 111, 117, 110, 100, 58, 32]).decode('utf-8') + str(lIOllOO))
                lOlI.exit(1)
            lOlOlOO = args.output or lIOllOO.rsplit(bytes([46]).decode('utf-8'), 1)[0] + bytes([95, 111, 98, 102, 46, 112, 121]).decode('utf-8')
            print(bytes([79, 98, 102, 117, 115, 99, 97, 116, 105, 110, 103, 32, 102, 105, 108, 101, 58, 32]).decode('utf-8') + str(lIOllOO) + bytes([32, 45, 62, 32]).decode('utf-8') + str(lOlOlOO) + bytes([32, 40, 76, 101, 118, 101, 108, 58, 32]).decode('utf-8') + str(lOIllOO) + bytes([44, 32, 83, 116, 121, 108, 101, 58, 32]).decode('utf-8') + str(style) + bytes([41, 46, 46, 46]).decode('utf-8'))
            try:
                llIllOO = lllI(lIOllOO, lOlOlOO, lOIllOO, style)
                llOOO(llIllOO, lOOlO.time() - lllOlOO, lOlOlOO)
            except Exception as e:
                print(bytes([79, 98, 102, 117, 115, 99, 97, 116, 105, 111, 110, 32, 102, 97, 105, 108, 101, 100, 58, 32]).decode('utf-8') + str(e))
                lOlI.exit(1)
        else:
            lIOllOO = args.directory.strip(bytes([39, 34]).decode('utf-8'))
            if not llOO.path.isdir(lIOllOO):
                print(bytes([69, 114, 114, 111, 114, 58, 32, 68, 105, 114, 101, 99, 116, 111, 114, 121, 32, 110, 111, 116, 32, 102, 111, 117, 110, 100, 58, 32]).decode('utf-8') + str(lIOllOO))
                lOlI.exit(1)
            lOlOlOO = args.output or lIOllOO.rstrip(bytes([47, 92]).decode('utf-8')) + bytes([95, 111, 98, 102]).decode('utf-8')
            print(bytes([79, 98, 102, 117, 115, 99, 97, 116, 105, 110, 103, 32, 112, 114, 111, 106, 101, 99, 116, 58, 32]).decode('utf-8') + str(lIOllOO) + bytes([32, 45, 62, 32]).decode('utf-8') + str(lOlOlOO) + bytes([32, 40, 76, 101, 118, 101, 108, 58, 32]).decode('utf-8') + str(lOIllOO) + bytes([44, 32, 83, 116, 121, 108, 101, 58, 32]).decode('utf-8') + str(style) + bytes([41, 46, 46, 46]).decode('utf-8'))
            try:
                llIllOO = lIlO(lIOllOO, lOlOlOO, lOIllOO, style)
                llOOO(llIllOO, lOOlO.time() - lllOlOO, lOlOlOO)
            except Exception as e:
                print(bytes([79, 98, 102, 117, 115, 99, 97, 116, 105, 111, 110, 32, 102, 97, 105, 108, 101, 100, 58, 32]).decode('utf-8') + str(e))
                lOlI.exit(1)
if __name__ == bytes([95, 95, 109, 97, 105, 110, 95, 95]).decode('utf-8'):
    main()