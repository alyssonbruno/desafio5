# -*- coding: utf-8 -*-
DEFAULT_FILE = "funcionarios.json"
from rpython.rlib import streamio as sio
from rpython.rlib.objectmodel import r_dict, compute_hash

class Funcionario(object):
    def __init__(self):
        self.id = 0
        self.nome = ""
        self.sobrenome = ""
        self.nome_completo = ""
        self.salario = 0.0
        self.area = ""
        return

    def __eq__(self, other):
        return (self.id != 0) and (self.id == other.id)

    def __hash__(self):
        return compute_hash(self.id)

class Area(object):
    def __init__(self):
        return
    def clear(self):
        self.codigo = ""
        self.nome = ""

class Counter(object):
    def __init__(self):
        self.maiores = []
        self.menores = []
        self.maior_salario = 0.0
        self.menor_salario = 0.0
        self.total_salarios = 0.0
        self.quantidade_funcionarios = 0
        return

    def adiciona(self, funcionario):
        self.total_salarios += funcionario.salario
        self.quantidade_funcionarios += 1
        if self.maior_salario == 0:
            self.maior_salario = funcionario.salario
            self.menor_salario = funcionario.salario
            self.maiores.append(funcionario)
            self.menores.append(funcionario)
            return
        elif self.maior_salario < funcionario.salario:
            self.maiores = []
            self.maior_salario = funcionario.salario
            self.maiores.append(funcionario)
        elif self.maior_salario == funcionario.salario:
            self.maiores.append(funcionario)
        if self.menor_salario > funcionario.salario:
            self.menores = []
            self.menor_salario = funcionario.salario
            self.menores.append(funcionario)
        elif self.menor_salario == funcionario.salario:
            self.menores.append(funcionario)
        return

def inicio_obj_json(eh_func):
    return eh_func

def meio_json(linha, f, eh_funcionario):
    if linha == "\"funcionarios\":[":
        return True
    elif linha == "\"areas\":[":
        return False
    elif linha == ']' or linha == '],':
        return eh_funcionario
    else:
        linha_ = linha.split(':')
        try:
            chave = linha_[0]
            valor = linha_[1]
        except KeyError:
            return eh_funcionario
        if eh_funcionario:
            if valor is None:
                return True
            if valor.startswith('"'): #É uma string, está escrita assim "String", ou "String"
                final=len(valor)-2
                if not valor.endswith(','): #não tem o , no final
                    final += 1
                if final < 1:
                    final = 1
                valor_lista = valor[1:final] #retira as aspas e a vírgula "...",
                if len(valor_lista) >=1:
                    valor_ = valor_lista
                else:
                    return True
            else:
                valor_lista = valor.strip(',') #retira as aspas e a vírgula "...",
                valor_ = valor_lista
            valor = valor_
            if chave=="\"id\"":
                try:
                    f.id = int(valor)
                except ValueError:
                    print "ID ValueError: %s" % valor
                    f.id = 0
                return True
            elif chave == "\"nome\"":
                f.nome = valor
                return True
            elif chave == "\"sobrenome\"":
                f.sobrenome = valor
                f.nome_completo = "%s %s" % (f.nome, f.sobrenome)
                return True
            elif chave=="\"salario\"":
                try:
                    f.salario = float(valor)
                except ValueError:
                    print "Salario ValueError: %s" % valor
                    f.salario = 0.0
                return True
            elif chave == "\"area\"":
                f.area = valor
                return True
            else:
                return True
        else:
            return False

def final_obj_json(f, c):
    geral =  c['global']
    if f.area not  in c:
        c[f.area] = Counter()
    area = c[f.area]
    geral.adiciona(f)
    area.adiciona(f)
    return

def imprime_global(lista_maximo, lista_minimo,salarios, qtde_funcionario):
    avg = salarios/float(qtde_funcionario)
    f = Funcionario()
    for fitem in lista_maximo:
        f = fitem
        print "global_max|%s|%f" % (f.nome_completo, f.salario)
    for fitem in lista_minimo:
        f = fitem
        print "global_min|%s|%f" % (f.nome_completo, f.salario)
    print "global_avg|%f" % avg


def read_file(filename):
    def key_eq(k1,k2):
        k1 = "%s" % k1
        k2 = "%s" % k2
        return k1==k2

    def key_hash(key):
        key = "%s" % key
        return compute_hash(key)

    funcionario = Funcionario()
    counters = {} #r_dict(key_eq,key_hash)
    counters['global'] = Counter()
    eh_funcionario = False
    try:
        f = sio.open_file_as_stream(filename)
        linha = f.readline()
        while linha:
            linha = linha.strip()
            if linha == '{':
                eh_funcionario = inicio_obj_json(eh_funcionario)
                if eh_funcionario:
                    funcionario = Funcionario()
            elif linha == '}' or linha == '},':
                final_obj_json(funcionario, counters)
            else:
                eh_funcionario = meio_json(linha, funcionario, eh_funcionario)
            try:
                linha = f.readline()
            except:
                break
        f.close()
        cobj = Counter()
        fobj = Funcionario()
        for key in counters:
            try:
                cobj = counters[key]
                if key == "global":
                    imprime_global(cobj.maiores,cobj.menores,cobj.total_salarios, cobj.quantidade_funcionarios)
            except ValueError:
                print "ERROR! ERROR! ERROR!"

    except IOError:
        print "Arquivo não encontrado!"

def entry_point(argv):
    file_name = DEFAULT_FILE
    if len(argv)==2:
        file_name = argv[1]
    read_file(file_name)
    return 0

def target(*args):
    return entry_point

if __name__ == "__main__":
    entry_point(None)
