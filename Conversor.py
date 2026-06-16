"""
Conversor.py

Reescreve a conversão de regex para AFND usando `automata-lib`.
Retorna um dicionário compatível com o contrato exibido em GUI.py.
"""

from typing import AbstractSet

import automata.fa.nfa as nfa


def _extract_input_symbols(regex: str) -> AbstractSet[str]:
    operators = {'|', '*', '(', ')'}
    return {ch for ch in regex if ch not in operators and not ch.isspace()}


def build_nfa(regex: str) -> dict:
    """Constrói um NFA a partir de `regex` usando automata-lib."""
    if regex is None:
        raise ValueError('Regex não pode ser None')

    regex = regex.strip().replace(' ', '')
    if regex == '':
        raise ValueError('Regex vazio não é suportado')

    input_symbols = _extract_input_symbols(regex)
    try:
        builder = nfa.parse_regex(regex, input_symbols)
    except Exception as exc:
        raise ValueError(f'Regex inválida: {exc}') from exc

    states = sorted(builder._transitions.keys())
    start_state = builder._initial_state
    # Remap states so the initial state is always q0.
    mapping = {start_state: 'q0'}
    other_states = [s for s in states if s != start_state]
    for idx, old in enumerate(other_states, start=1):
        mapping[old] = f'q{idx}'

    transitions = []
    for u in states:
        for sym, targets in sorted(builder._transitions[u].items(), key=lambda item: (str(item[0]), sorted(item[1]))):
            label = 'eps' if sym == '' else sym
            for v in sorted(targets):
                transitions.append((mapping[u], label, mapping[v]))

    return {
        'states': [mapping[start_state]] + [mapping[state] for state in other_states],
        'start': mapping[start_state],
        'accepts': [mapping[state] for state in sorted(builder._final_states)],
        'transitions': transitions,
    }


if __name__ == '__main__':
    from pprint import pprint

    examples = ['a', 'ab', 'a|b', 'a*', 'a(b|c)*', '(a|b)*']
    for ex in examples:
        print('Regex:', ex)
        pprint(build_nfa(ex))
        print('---')
