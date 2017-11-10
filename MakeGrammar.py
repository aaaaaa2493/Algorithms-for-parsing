import re

old_print = print
file_output = open('output.txt', 'w')
do_print = False


def set_print(boolean):
    global do_print
    do_print = boolean


def print(*args, **kwargs):
    if do_print:
        old_print(*args, **kwargs)
        old_print(*args, **kwargs, file=file_output)


def format_matrix(header,
                  matrix,
                  top_format='{:^{}}',
                  left_format='{:<{}}',
                  cell_format='{:^{}}',
                  row_delim='\n',
                  col_delim=' | '):
    table = [[''] + header] + [[name] + row for name, row in zip(header, matrix)]
    table_format = [['{:^{}}'] + len(header) * [top_format]] \
                 + len(matrix) * [[left_format] + len(header) * [cell_format]]
    col_widths = [max(
                      len(format.format(cell, 0))
                      for format, cell in zip(col_format, col))
                  for col_format, col in zip(zip(*table_format), zip(*table))]
    return row_delim.join(
               col_delim.join(
                   format.format(cell, width)
                   for format, cell, width in zip(row_format, row, col_widths))
               for row_format, row in zip(table_format, table))


def get_sequence():
    i = 1
    while True:
        yield i
        i += 1


def get_index():
    for i in get_sequence():
        yield '\S%s' % i


def get_error_index():
    for i in get_sequence():
        yield 'ERROR %s:' % i


errors = {}
index = get_index()
index_error = get_error_index()


def add_error(identifier, string):
    errors[identifier] = next(index_error), string


def err(identifier, *args):
    set_print(True)
    err_num, string = errors[identifier]
    print('%s %s' % (err_num, string % args))
    quit(0)


add_error('no ->', 'in rule "%s" not found any "->" symbols')
add_error('two nons before ->', 'rule must contain only one nonterminal before "->" - "%s"')
add_error('\\ in nonterm', 'nonterminal can not contain "\\" symbol - "%s"')
add_error('bad escape', 'found illegal escape symbol in "%s"')
add_error('empty before \...', 'before symbol "\..." must be some symbol - "%s"')
add_error('empty after \...',  'after symbol "\..." must be some symbol - "%s"')
add_error('mult symbols before \...', 'before symbol "\..." must be only one symbol in "%s"')
add_error('mult symbols after \...', 'after symbol "\..." must be only one symbol in "%s"')
add_error('a \... b, a > b', 'symbol to the left of "\..." must be less than '
                             'symbol to the right of "\..." in unicode codes')


def print_rules(rules):
    for key in sorted(rules):
        print(key, ' -> ', '  |  '.join(' '.join(i) for i in rules[key]))
    print()


initial = open('grammar.txt').read()

specials = ['\eps', '\...']
eps, dots = specials
hidden_specials = ['\$']
end = hidden_specials[0]

escaped = ['\|', '\\\\']


def replace_escaped(string):
    for esc in escaped:
        string = string.replace(esc, esc[1:])
    return string


def make_grammar():
    all_rules = [i for i in initial.split('\n') if i != '']
    S0 = ''

    formatted_rules = []
    for rule in all_rules:
        old_rule = rule
        sp = rule.split('->', 1)
        if len(sp) < 2: err('no ->', old_rule)
        sp[0] = sp[0].strip()
        if len(sp[0].split()) > 1: err('two nons before ->', rule)
        if '\\' in sp[0]: err('\\ in nonterm', rule)
        if not S0: S0 = sp[0]
        formatted_rules += (sp[0], sp[1]),

    rules = {}
    for nonterm, right_side in formatted_rules:
        right_side = [i.strip() for i in re.split('(?<!\\\\)[|]{1}', right_side) if i.strip() != '']
        for i, t in enumerate(right_side):
            old_rules = rules.get(nonterm, [])
            if t not in old_rules:
                if '\\' in t and t not in specials and sum(t.count(j) for j in escaped) != t.count('\\') - t.count(
                        '\\\\'):
                    err('bad escape', t)
                if t == dots:
                    if i == 0:
                        err('empty before \...', '  |  '.join(right_side))
                    elif i == len(right_side) - 1:
                        err('empty after \...', '  |  '.join(right_side))
                    else:
                        if len(right_side[i - 1]) != 1:
                            err('mult symbols before \...', '  |  '.join(right_side))
                        elif len(right_side[i + 1]) != 1:
                            err('mult symbols after \...', '  |  '.join(right_side))
                        elif ord(right_side[i + 1]) - ord(right_side[i - 1]) < 1:
                            err('a \... b, a > b')
                        else:
                            dotted_symbols = [chr(i) for i in range(ord(right_side[i - 1]) + 1, ord(right_side[i + 1]))]
                            rules[nonterm] = old_rules + dotted_symbols
                else:
                    rules[nonterm] = old_rules + [replace_escaped(t)]

    terms = []
    nonterms = rules.keys()

    for key in sorted(rules):
        new_rules = []
        for rule in rules[key]:

            if rule == eps:
                new_rules += [eps],
                continue

            curr_rules = []

            curr_terms = rule.split()

            for curr_term in curr_terms:
                if curr_term in nonterms:
                    curr_rules += curr_term,

                else:
                    curr_rules += list(curr_term)

            new_rules += curr_rules,

        rules[key] = new_rules

    for key in sorted(rules):
        for rule in rules[key]:
            for term in rule:
                if term != eps and term not in nonterms and term not in terms:
                    terms += term,

    print('Recognized nonterms:', ', '.join(nonterms))
    print('Recognized terms:', ', '.join(terms))

    print()
    print('Parsed rules: ')
    print_rules(rules)

    return S0, terms, nonterms, rules


if __name__ == '__main__':
    set_print(True)
    make_grammar()
