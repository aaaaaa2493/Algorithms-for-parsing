from pprint import pprint
import re
from time import sleep


def err(num, string):
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


initial = \
'''
init E
E ->  E - T | T
T -> T * F | F
F -> (E) | D
D -> 0 | \... | 9
'''

specials = ['\eps', '\...']
eps, dots = specials

escaped = ['\->', '\|']


def replace_escaped(string):
    for esc in escaped:
        string = string.replace(esc, esc[1:])
    return string


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
        rule = ''.join(rule.split())
        sp = re.split('(?<!\\\\)[-]{1}[>]{1}', rule)
        if len(sp) > 2: err(3, 'in rule "%s" more than one "->" symbols' % old_rule)
        if len(sp) < 2: err(4, 'in rule "%s" not found any "->" symbols' % old_rule)
        formatted_rules += (sp[0], sp[1]),

if not S0: err(5, 'declaration of initial nonterminal using "init" not found')
if '\\' in S0: err(6, 'initial nonterminal cannot contain special symbol "\\" - "%s"' % S0)

rules = {}
for nonterm, right_side in formatted_rules:
    right_side = [replace_escaped(i) for i in re.split('(?<!\\\\)[|]{1}', right_side) if i != '']
    for i, t in enumerate(right_side):
        old_rules = rules.get(nonterm,[])
        if t not in old_rules:
            if '\\' in t and t not in specials and sum(t.count(j) for j in escaped) != t.count('\\'):
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
                rules[nonterm] = old_rules+[t]

terms = []
nonterms = rules.keys()

for nt1 in nonterms:
    for nt2 in nonterms:
        if nt1 != nt2 and (nt1 in nt2 or nt2 in nt1):
            err(13, 'one nonterminal cannot be substring of another nonterminal - "%s" and "%s"' % (nt1, nt2))


for key in sorted(rules):
    new_rules = []
    for rule in rules[key]:

        if rule == eps:
            new_rules += [eps],
            continue

        for nt in nonterms:
            if nt in rule:
                rule = re.sub('(?<!\\\\)%s' % ''.join(['\^' if i == '^' else '[%s]{1}' % i for i in nt]),
                              '\S' + nt + '\E', rule)

        while True:
            terminals = re.findall('\\\\E([^\\\\]{1})', rule)
            start_terms = re.findall('^[^\\\\]{1}', rule)
            if not (terminals + start_terms): break
            for i in terminals:
                rule = re.sub('(?<=\\\\E)[%s]{1}' % i, '\S' + i + '\E', rule)
            for i in start_terms:
                rule = re.sub('^[%s]{1}' % i, '\S' + i + '\E', rule)

        new_rules += re.findall('(?<=\\\\S)([^\\\\]*)(?=\\\\E)', rule),

    rules[key] = new_rules


for key in sorted(rules):
    for rule in rules[key]:
        for term in rule:
            if term != eps and term not in nonterms and term not in terms:
                terms += term,

print('Recognized nonterms:', ', '.join(nonterms))
print('Recognized terms:', ', '.join(terms))

if S0 not in nonterms:
    err(14, 'initial term "%s" not found in recognized nonterms' % S0)

print()
print('Parsed rules: ')
print_rules(rules)

print()
print('Add new initial nonterm "\S0"')
rules['\S0'] = [[S0]]
print_rules(rules)

index = get_index()

print()
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

print()
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

print()
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

            elif len(rule) == 1 and rule != [eps] and rule[0] not in terms and rules[rule[0]] == [[eps]]:
                rule[:] = [eps]
                something_changed = True

print_rules(rules)

print()
print('Delete single epsilon - rules except in initial nonterminal "%s"' % S0)

for key in sorted(rules):
    if rules[key] == [[eps]]:
        del rules[key]
    elif key != S0:
        rules[key][:] = [i for i in rules[key] if i != [eps]]

print_rules(rules)

print()
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
        err(15, 'found recursive grammar "%s"' % ' -> '.join(list(path[path.index(key):]) + [key]))
    new_path = tuple(list(path) + [key])
    for rule in rules[key]:
        if len(rule) == 1 and rule[0] in nonterms:
            find_cycles(new_path, rule[0], rules, nonterms)


for key in sorted(rules):
    find_cycles((), key, rules, nonterms)

print()
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

print()
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

#pprint(rules)