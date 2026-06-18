from automata.fa.nfa import NFA


class ConversorThompson:
    def __init__(self, regex: str):
        self.regex = regex.replace(" ", "")
        self.pos = 0
        self.cont = 0

        self.estados = set()
        self.alfabeto = set()
        self.transicoes = {}

    def novo_estado(self):
        estado = f"q{self.cont}"
        self.cont += 1
        self.estados.add(estado)
        return estado

    def add_transicao(self, origem, simbolo, destino):
        if origem not in self.transicoes:
            self.transicoes[origem] = {}
        if simbolo not in self.transicoes[origem]:
            self.transicoes[origem][simbolo] = set()

        self.transicoes[origem][simbolo].add(destino)

    def converter(self):
        if not self.regex:
            raise ValueError("A expressão regular está vazia.")

        inicio, fim = self.expressao()

        if self.pos < len(self.regex):
            raise ValueError(
                f"Caractere inesperado na posição {self.pos}: '{self.regex[self.pos]}'. Verifique os parênteses.")

        # =========================================================
        # PÓS-PROCESSAMENTO: Renomear estados para começar em q0
        # =========================================================
        mapa_nomes = {}
        ordem = 0

        # Fazemos uma Busca em Largura (BFS) para nomear na ordem correta
        fila = [inicio]
        mapa_nomes[inicio] = f"q{ordem}"
        ordem += 1

        visitados = {inicio}

        while fila:
            atual = fila.pop(0)
            if atual in self.transicoes:
                # Ordena as transições apenas para garantir consistência
                for simb, destinos in self.transicoes[atual].items():
                    for d in sorted(list(destinos)):
                        if d not in visitados:
                            visitados.add(d)
                            mapa_nomes[d] = f"q{ordem}"
                            ordem += 1
                            fila.append(d)

        # Se sobrou algum estado perdido (garantia de segurança)
        for e in self.estados:
            if e not in mapa_nomes:
                mapa_nomes[e] = f"q{ordem}"
                ordem += 1

        # Atualiza as transições com os novos nomes padronizados
        novas_transicoes = {}
        for origem, trans in self.transicoes.items():
            n_origem = mapa_nomes[origem]
            novas_transicoes[n_origem] = {}
            for simb, dests in trans.items():
                novas_transicoes[n_origem][simb] = {
                    mapa_nomes[d] for d in dests}

        self.estados = set(mapa_nomes.values())
        self.transicoes = novas_transicoes
        inicio = mapa_nomes[inicio]
        fim = mapa_nomes[fim]
        # =========================================================

        return NFA(
            states=self.estados,
            input_symbols=self.alfabeto,
            transitions=self.transicoes,
            initial_state=inicio,
            final_states={fim}
        )

    # ==========================================
    # Funções Recursivas (Parser + Thompson)
    # ==========================================

    def expressao(self):
        # Trata a União (|)
        i1, f1 = self.termo()

        while self.pos < len(self.regex) and self.regex[self.pos] == '|':
            self.pos += 1
            i2, f2 = self.termo()

            # Algoritmo de Thompson para união
            i_novo = self.novo_estado()
            f_novo = self.novo_estado()

            self.add_transicao(i_novo, "", i1)
            self.add_transicao(i_novo, "", i2)
            self.add_transicao(f1, "", f_novo)
            self.add_transicao(f2, "", f_novo)

            i1, f1 = i_novo, f_novo

        return i1, f1

    def termo(self):
        # Trata a Concatenação
        i1, f1 = self.fator()

        # Se o próximo caractere não for união nem fechamento de parêntese, é concatenação
        while self.pos < len(self.regex) and self.regex[self.pos] not in ['|', ')']:
            i2, f2 = self.fator()

            # Algoritmo de Thompson para concatenação
            self.add_transicao(f1, "", i2)

            # O início é o do primeiro, o fim é o do segundo
            f1 = f2

        return i1, f1

    def fator(self):
        # Trata o Fecho de Kleene (*)
        i1, f1 = self.atomo()

        while self.pos < len(self.regex) and self.regex[self.pos] == '*':
            self.pos += 1

            # Algoritmo de Thompson para o fecho estrela
            i_novo = self.novo_estado()
            f_novo = self.novo_estado()

            self.add_transicao(i_novo, "", i1)     # Pula para dentro
            self.add_transicao(i_novo, "", f_novo)  # Pula tudo (zero vezes)
            self.add_transicao(f1, "", i1)         # Repete
            self.add_transicao(f1, "", f_novo)     # Sai

            i1, f1 = i_novo, f_novo

        return i1, f1

    def atomo(self):
        if self.pos >= len(self.regex):
            raise ValueError(
                "Expressão incompleta. Faltam operandos ou há parênteses vazios.")

        c = self.regex[self.pos]

        # Se for parênteses, resolve a expressão de dentro primeiro
        if c == '(':
            self.pos += 1
            inicio, fim = self.expressao()

            if self.pos >= len(self.regex) or self.regex[self.pos] != ')':
                raise ValueError("Faltou fechar um parêntese ')'.")

            self.pos += 1
            return inicio, fim

        # Tratamento de erro para operadores no lugar errado
        if c in ['|', ')', '*']:
            raise ValueError(f"Operador '{c}' usado em local inválido.")

        # Símbolo normal ou Epsilon (ε)
        self.pos += 1
        inicio = self.novo_estado()
        fim = self.novo_estado()

        if c == 'ε':
            self.add_transicao(inicio, "", fim)
        else:
            self.alfabeto.add(c)
            self.add_transicao(inicio, c, fim)

        return inicio, fim
