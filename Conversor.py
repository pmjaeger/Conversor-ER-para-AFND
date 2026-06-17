from __future__ import annotations

from dataclasses import dataclass
from automata.fa.nfa import NFA


# ============================================================
# Nós da árvore sintática da expressão regular
# ============================================================

@dataclass(frozen=True)
class Symbol:
    value: str


@dataclass(frozen=True)
class Epsilon:
    pass


@dataclass(frozen=True)
class UnionNode:
    left: object
    right: object


@dataclass(frozen=True)
class ConcatNode:
    left: object
    right: object


@dataclass(frozen=True)
class StarNode:
    node: object


# ============================================================
# Fragmento de Thompson
# ============================================================

class Fragmento:
    def __init__(self, inicio, fim):
        self.inicio = inicio
        self.fim = fim


# ============================================================
# Parser recursivo da expressão regular
# Grammar:
#   expression := term ('|' term)*
#   term       := factor+
#   factor     := atom ('*')*
#   atom       := SYMBOL | 'ε' | '(' expression ')'
# ============================================================

class RegexParser:
    def __init__(self, texto: str):
        self.texto = texto.replace(" ", "")
        self.i = 0

    def atual(self):
        if self.i >= len(self.texto):
            return None
        return self.texto[self.i]

    def consumir(self, esperado=None):
        c = self.atual()
        if c is None:
            raise ValueError("Fim inesperado da expressão regular.")
        if esperado is not None and c != esperado:
            raise ValueError(f"Esperado '{esperado}', mas encontrado '{c}'.")
        self.i += 1
        return c

    def parse(self):
        if not self.texto:
            raise ValueError("Expressão regular vazia.")

        nodo = self.parse_expression()

        if self.atual() is not None:
            raise ValueError(
                f"Caractere inesperado na posição {self.i}: '{self.atual()}'."
            )

        return nodo

    def parse_expression(self):
        nodo = self.parse_term()

        while self.atual() == "|":
            self.consumir("|")
            direito = self.parse_term()
            nodo = UnionNode(nodo, direito)

        return nodo

    def parse_term(self):
        fatores = []

        while True:
            c = self.atual()
            if c is None or c in ")|":
                break
            fatores.append(self.parse_factor())

        if not fatores:
            raise ValueError(
                f"Termo vazio na posição {self.i}. "
                "Verifique operadores '|' e parênteses."
            )

        nodo = fatores[0]
        for fator in fatores[1:]:
            nodo = ConcatNode(nodo, fator)

        return nodo

    def parse_factor(self):
        nodo = self.parse_atom()

        while self.atual() == "*":
            self.consumir("*")
            nodo = StarNode(nodo)

        return nodo

    def parse_atom(self):
        c = self.atual()

        if c is None:
            raise ValueError("Fim inesperado ao ler um átomo.")

        if c == "(":
            self.consumir("(")
            nodo = self.parse_expression()

            if self.atual() != ")":
                raise ValueError(
                    f"Parêntese ')' esperado na posição {self.i}."
                )

            self.consumir(")")
            return nodo

        if c == "ε":
            self.consumir("ε")
            return Epsilon()

        if c in {"|", ")", "*"}:
            raise ValueError(
                f"Símbolo inválido na posição {self.i}: '{c}'."
            )

        # Símbolo do alfabeto: qualquer caractere que não seja operador
        self.consumir()
        return Symbol(c)


# ============================================================
# Conversor Thompson recursivo
# ============================================================

class ConversorThompson:
    def __init__(self, regex: str):
        self.regex = regex.replace(" ", "")
        self.contador = 0
        self.estados = set()
        self.transicoes = {}

        operadores = {"(", ")", "|", "*"}
        self.alfabeto = {
            c for c in self.regex
            if c not in operadores and c != "ε"
        }

        self.parser = RegexParser(self.regex)

    def novo_estado(self):
        estado = f"q{self.contador}"
        self.contador += 1
        self.estados.add(estado)
        return estado

    def adicionar_transicao(self, origem, simbolo, destino):
        self.transicoes.setdefault(origem, {})
        self.transicoes[origem].setdefault(simbolo, set())
        self.transicoes[origem][simbolo].add(destino)

    # --------------------------------------------------------
    # Construções de Thompson
    # --------------------------------------------------------

    def simbolo(self, c):
        inicio = self.novo_estado()
        fim = self.novo_estado()
        self.adicionar_transicao(inicio, c, fim)
        return Fragmento(inicio, fim)

    def epsilon(self):
        inicio = self.novo_estado()
        fim = self.novo_estado()
        self.adicionar_transicao(inicio, "", fim)
        return Fragmento(inicio, fim)

    def concatenar(self, f1, f2):
        self.adicionar_transicao(f1.fim, "", f2.inicio)
        return Fragmento(f1.inicio, f2.fim)

    def uniao(self, f1, f2):
        inicio = self.novo_estado()
        fim = self.novo_estado()

        self.adicionar_transicao(inicio, "", f1.inicio)
        self.adicionar_transicao(inicio, "", f2.inicio)

        self.adicionar_transicao(f1.fim, "", fim)
        self.adicionar_transicao(f2.fim, "", fim)

        return Fragmento(inicio, fim)

    def estrela(self, f):
        inicio = self.novo_estado()
        fim = self.novo_estado()

        self.adicionar_transicao(inicio, "", f.inicio)
        self.adicionar_transicao(inicio, "", fim)

        self.adicionar_transicao(f.fim, "", f.inicio)
        self.adicionar_transicao(f.fim, "", fim)

        return Fragmento(inicio, fim)

    # --------------------------------------------------------
    # Thompson sobre a árvore sintática
    # --------------------------------------------------------

    def construir(self, nodo):
        if isinstance(nodo, Symbol):
            return self.simbolo(nodo.value)

        if isinstance(nodo, Epsilon):
            return self.epsilon()

        if isinstance(nodo, UnionNode):
            esquerdo = self.construir(nodo.left)
            direito = self.construir(nodo.right)
            return self.uniao(esquerdo, direito)

        if isinstance(nodo, ConcatNode):
            esquerdo = self.construir(nodo.left)
            direito = self.construir(nodo.right)
            return self.concatenar(esquerdo, direito)

        if isinstance(nodo, StarNode):
            interno = self.construir(nodo.node)
            return self.estrela(interno)

        raise ValueError(f"Nó inválido na árvore sintática: {type(nodo)}")

    # --------------------------------------------------------
    # Conversão final
    # --------------------------------------------------------

    def converter(self):
        arvore = self.parser.parse()
        resultado = self.construir(arvore)

        return NFA(
            states=self.estados,
            input_symbols=self.alfabeto,
            transitions=self.transicoes,
            initial_state=resultado.inicio,
            final_states={resultado.fim},
        )
