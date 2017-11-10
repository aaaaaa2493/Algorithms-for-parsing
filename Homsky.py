import sys
sys.dont_write_bytecode = True

from MakeGrammar import *

add_error('recursion', 'found recursive grammar "%s"')


def to_homsky():

    S0, terms, nonterms, rules = make_grammar()

    print('Add new initial nonterm "\S0"')
    rules['\S0'] = [[S0]]
    print_rules(rules)

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
            err('recursion', ' -> '.join(list(path[path.index(key):]) + [key]))
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
