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


def err(num, string):
    set_print(True)
    print('ERROR %s: %s' % (num, string))
    quit(0)


def get_index():
    i = 1
    while True:
        yield '\S%s' % i
        i += 1


def print_rules(rules):
    for key in sorted(rules):
        print(key, ' -> ', '  |  '.join(' '.join(i) for i in rules[key]))
    print()


initial = open('grammar.txt').read()

specials = ['\eps', '\...']
eps, dots = specials

escaped = ['\|', '\\\\']


def replace_escaped(string):
    for esc in escaped:
        string = string.replace(esc, esc[1:])
    return string


def to_homsky():
    all_rules = [i for i in initial.split('\n') if i != '']
    S0 = ''

    formatted_rules = []
    for rule in all_rules:
        old_rule = rule

        if rule.startswith('init'):
            if S0: err(1, 'multiple definitions of initial nonterminal using "init"')
            try: S0 = ''.join(rule.split(' ', 1)[1].split()) or 0/0
            except: err(2, 'no initial nonterminal after "init" statement')

        else:
            sp = rule.split('->', 1)
            if len(sp) < 2: err(3, 'in rule "%s" not found any "->" symbols' % old_rule)
            sp[0] = sp[0].strip()
            if len(sp[0].split()) > 1: err(4, 'rule must contain only one nonterminal before "->" - "%s"' % rule)
            formatted_rules += (sp[0], sp[1]),

    if not S0: err(5, 'declaration of initial nonterminal using "init" not found')
    if '\\' in S0: err(6, 'initial nonterminal cannot contain special symbol "\\" - "%s"' % S0)

    rules = {}
    for nonterm, right_side in formatted_rules:
        right_side = [i.strip() for i in re.split('(?<!\\\\)[|]{1}', right_side) if i.strip() != '']
        for i, t in enumerate(right_side):
            old_rules = rules.get(nonterm,[])
            if t not in old_rules:
                if '\\' in t and t not in specials and sum(t.count(j) for j in escaped) != t.count('\\') - t.count('\\\\'):
                    err(7, 'found illegal escape symbol in "%s"' % t)
                if t == dots:
                    if i == 0:
                        err(8, 'before symbol "\..." must be some symbol - "%s"' % right_side)
                    elif i == len(right_side) - 1:
                        err(9, 'after symbol "\..." must be some symbol - "%s"' % right_side)
                    else:
                        if len(right_side[i-1]) != 1:
                            err(10, 'before symbol "\..." must be only one symbol in "%s"' % right_side)
                        elif len(right_side[i+1]) != 1:
                            err(11, 'after symbol "\..." must be only one symbol in "%s"' % right_side)
                        elif ord(right_side[i+1]) - ord(right_side[i-1]) < 1:
                            err(12, 'symbol to the left of "\..." must be less than '
                                    'symbol to the right of "\..." in unicode codes')
                        else:
                            dotted_symbols = [chr(i) for i in range(ord(right_side[i-1]) + 1, ord(right_side[i+1]))]
                            rules[nonterm] = old_rules + dotted_symbols
                else:
                    rules[nonterm] = old_rules+[replace_escaped(t)]

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

    if S0 not in nonterms:
        err(13, 'initial term "%s" not found in recognized nonterms' % S0)

    print()
    print('Parsed rules: ')
    print_rules(rules)

    print('Add new initial nonterm "\S0"')
    rules['\S0'] = [[S0]]
    print_rules(rules)

    index = get_index()

    print('Move terms into separate rules')

    separated_terms = {}

    for key in sorted(rules):
        for rule in rules[key]:
            if len(rule) > 1:
                for i, term in enumerate(rule):
                    if term in terms:
                        if term not in separated_terms:
                            new_key = next(index)
                            rules[new_key] = [[term]]
                            rule[i] = new_key
                            separated_terms[term] = new_key
                        else:
                            rule[i] = separated_terms[term]

    print_rules(rules)

    print('Break rules with length more than 2')
    for key in sorted(rules):
        for rule in rules[key]:
            if len(rule) > 2:
                new_key = next(index)
                rules[new_key] = [rule[1:]]
                del rule[1:]
                rule += new_key,
                old_key = new_key
                while len(rules[old_key][0]) > 2:
                    new_key = next(index)
                    rules[new_key] = [rules[old_key][0][1:]]
                    del rules[old_key][0][1:]
                    rules[old_key][0] += new_key,
                    old_key = new_key

    print_rules(rules)
    print('Delete epsilon - rules in rules with two nonterminals')

    something_changed = True
    while something_changed:
        something_changed = False

        for key in sorted(rules):
            for rule in rules[key]:

                if len(rule) == 2:
                    if rules[rule[0]] == [[eps]] and rules[rule[1]] == [[eps]]:
                        rule[:] = [eps]
                        something_changed = True

                    elif rules[rule[0]] != [[eps]] and rules[rule[1]] == [[eps]]:
                        rule[:] = [rule[0]]
                        something_changed = True

                    elif rules[rule[0]] == [[eps]] and rules[rule[1]] != [[eps]]:
                        rule[:] = [rule[1]]
                        something_changed = True

                elif len(rule) == 1 and rule != [eps] and rule[0] in nonterms and rules[rule[0]] == [[eps]]:
                    rule[:] = [eps]
                    something_changed = True

    print_rules(rules)
    print('Delete single epsilon - rules and move single epsilon rule from "%s" to "\S0" if it exists' % S0)

    something_changed = True
    while something_changed:
        something_changed = False
        for key in sorted(rules):
            if key != '\S0':
                if rules[key] == [[eps]]: del rules[key]
                else:
                    if [eps] in rules[key]:
                        something_changed = True
                        new_rules = []
                        for rule in rules[key]:
                            if rule == [eps]:
                                for other_key in sorted(rules):
                                    if key != other_key:
                                        other_new_rules = []
                                        for other_rule in rules[other_key]:
                                            if key in other_rule:
                                                if len(other_rule) == 1:
                                                    other_new_rules += [key],
                                                    if [eps] not in rules[other_key]:
                                                        other_new_rules += [eps],
                                                elif len(other_rule) == 2:
                                                    if other_rule[0] == key and other_rule[1] == key:
                                                        other_new_rules += [key, key],
                                                        if [key] not in rules[other_key]:
                                                            other_new_rules += [key],
                                                        if [eps] not in rules[other_key]:
                                                            other_new_rules += [eps],
                                                    elif other_rule[0] == key and other_rule[1] != key:
                                                        other_new_rules += other_rule,
                                                        if other_rule[1] not in rules[other_key]:
                                                            other_new_rules += [other_rule[1]],
                                                    elif other_rule[0] != key and other_rule[1] == key:
                                                        other_new_rules += other_rule,
                                                        if other_rule[0] not in rules[other_key]:
                                                            other_new_rules += [other_rule[0]],
                                            else:
                                                other_new_rules += other_rule,
                                        rules[other_key][:] = other_new_rules
                                break
                        for rule in rules[key]:
                            if rule != [eps]:
                                if key in rule:
                                    if len(rule) == 2:
                                        if rule[0] == key and rule[1] == key:
                                            new_rules += [key, key],
                                        elif rule[0] == key and rule[1] != key:
                                            new_rules += rule,
                                            if rule[1] not in rules[key]:
                                                new_rules += [rule[1]],
                                        elif rule[0] != key and rule[1] == key:
                                            new_rules += rule,
                                            if rule[0] not in rules[key]:
                                                new_rules += [rule[0]],
                                else:
                                    new_rules += rule,
                        rules[key][:] = new_rules

    print_rules(rules)
    print('Delete duplicates')

    for key in sorted(rules):
        new_rules = []
        for rule in rules[key]:
            if rule not in new_rules:
                new_rules += rule,
        rules[key][:] = new_rules

    print_rules(rules)

    def find_cycles(path, key, rules, nonterms):
        if key in path:
            err(14, 'found recursive grammar "%s"' % ' -> '.join(list(path[path.index(key):]) + [key]))
        new_path = tuple(list(path) + [key])
        for rule in rules[key]:
            if len(rule) == 1 and rule[0] in nonterms:
                find_cycles(new_path, rule[0], rules, nonterms)

    for key in sorted(rules):
        rules[key][:] = [rule for rule in rules[key] if rule != [key]]

    for key in sorted(rules):
        find_cycles((), key, rules, nonterms)

    print('Delete unused rules')

    def depth_search(marked, key, rules):
        marked = tuple(list(marked) + [key])
        for rule in rules[key]:
            for term in rule:
                if term in nonterms and term not in marked:
                    marked = depth_search(marked, term, rules)
        return marked

    used_in_rules = depth_search((), '\S0', rules)

    for key in sorted(rules):
        if key not in used_in_rules:
            del rules[key]

    print_rules(rules)
    print('Remove chain rules')

    something_changed = True
    while something_changed:
        something_changed = False

        for key in sorted(rules):
            new_rules = []
            for rule in rules[key]:
                if len(rule) == 2:
                    new_rules += rule,
                elif len(rule) == 1:
                    if rule[0] in nonterms:
                        new_rules += rules[rule[0]]
                        something_changed = True
                    else:
                        new_rules += rule,
            rules[key][:] = new_rules

    rules[S0][:] = [i for i in rules[S0] if i != [eps]]

    used_in_rules = depth_search((), '\S0', rules)

    for key in sorted(rules):
        if key not in used_in_rules:
            del rules[key]

    print_rules(rules)

    return terms, list(nonterms), rules


if __name__ == '__main__':
    set_print(True)
    to_homsky()
