import sys
sys.dont_write_bytecode = True

from MakeGrammar import *
from time import sleep
from pprint import pprint

def do_LL1():

    set_print(True)
    S0, terms, nonterms, rules = make_grammar()

    print('Avoid left recursion')

    something_changed = True
    while something_changed:
        something_changed = False
        
        for key in sorted(rules):

            consist_key = []
            not_consist = []

            for rule in rules[key]:
                if rule[0] == key:
                    if len(rule) > 1:
                        consist_key += rule[1:],
                else:
                    not_consist += rule,

            if consist_key:

                something_changed = True

                new_rules = []
                rules_for_new_key = [[eps]]
                new_key = next(index)

                for rule in not_consist:
                    if rule != [eps]:
                        new_rules += [rule + [new_key]]
                    else:
                        new_rules += [[new_key]]

                for rule in consist_key:
                    rules_for_new_key += [rule + [new_key]]

                rules[key][:] = new_rules
                rules[new_key] = rules_for_new_key

    print_rules(rules)

    print('Delete epsilon - products')

    something_changed = True
    while something_changed:
        something_changed = False
        for key in sorted(rules):
            new_rules = []
            for rule in rules[key]:
                new_rule = []
                for term in rule:
                    if term in nonterms:
                        if rules[term] != [[eps]]:
                            new_rule += term,
                    else:
                        new_rule += term,
                new_rules += (new_rule if new_rule else [eps]),
            rules[key][:] = new_rules
        for key in sorted(rules):
            if rules[key] == [[eps]]:
                del rules[key]
                something_changed = True
            elif [key] in rules[key]:
                new_rules = [rule for rule in rules[key] if rule != [key]]
                rules[key] = new_rules if new_rules else [[eps]]
                something_changed = True
        for key in sorted(rules):
            new_rules = []
            for rule in rules[key]:
                if rule not in new_rules:
                    new_rules += rule,
            rules[key][:] = new_rules

    print_rules(rules)

    print('Remove double recursion')

    something_changed = True
    while something_changed:
        something_changed = False

        for key in sorted(rules):
            new_rules = []
            for rule in rules[key]:
                if rule[0] <= key and rule[0] in nonterms:
                    something_changed = True
                    for other_rule in rules[rule[0]]:
                        if other_rule != [eps]:
                            new_rules += [other_rule + rule[1:]]
                        else:
                            new_rules += [rule[1:]] if rule[1:] else []

                else:
                    new_rules += rule,

            rules[key][:] = new_rules

            # avoid left recursion

            consist_key = []
            not_consist = []

            for rule in rules[key]:
                if rule[0] == key:
                    if len(rule) > 1:
                        consist_key += rule[1:],
                else:
                    not_consist += rule,

            if consist_key:
                something_changed = True

                new_rules = []
                rules_for_new_key = [[eps]]
                new_key = next(index)

                for rule in not_consist:
                    if rule != [eps]:
                        new_rules += [rule + [new_key]]
                    else:
                        new_rules += [[new_key]]

                for rule in consist_key:
                    rules_for_new_key += [rule + [new_key]]

                rules[key][:] = new_rules
                rules[new_key] = rules_for_new_key

        '''
        for key in sorted(rules):
            if len(rules[key]) == 0:
                something_changed = True
                del rules[key]
                for other_key in sorted(rules):
                    new_rules = []
                    for rule in rules[other_key]:
                        if key in rule:
                            new_rule = []
                            for term in rule:
                                if term != key:
                                    new_rule += term,
                            if not new_rule:
                                new_rule = [eps]
                            new_rules += new_rule,
                        else:
                            new_rules += rule,
                    rules[other_key][:] = new_rules'''

    print_rules(rules)

    print('Isolate biggest common terminals')

    something_changed = True
    while something_changed:
        something_changed = False

        for key in sorted(rules):

            max_start = (0, '')
            for rule in rules[key]:
                curr_count = [i[0] for i in rules[key]].count(rule[0])
                if max_start[0] < curr_count > 1:
                    max_start = curr_count, rule[0]

            all_vars = [rule for rule in rules[key] if rule[0] == max_start[1] and len(rule) > 1]

            if max_start[0] > 1 and len(all_vars) > 1:
                something_changed = True

                curr_max = 1
                while all(rule[:curr_max+1] == all_vars[0][:curr_max+1] for rule in all_vars):
                    curr_max += 1

                max_start = all_vars[0][:curr_max]

                new_key = key + '\''
                if new_key in rules:
                    integer = 2
                    gen_key = new_key + str(integer)
                    while gen_key in rules:
                        integer += 1
                        gen_key = new_key + str(integer)
                    new_key = gen_key

                new_rules = [max_start + [new_key]]
                rules_for_new_key = []

                for rule in rules[key]:
                    if rule[:curr_max] == max_start and len(rule) > 1:
                        rules_for_new_key += rule[curr_max:] if rule[curr_max:] else [eps],
                    else:
                        new_rules += rule,

                rules[new_key] = rules_for_new_key
                rules[key] = new_rules

    print_rules(rules)


if __name__ == '__main__':
    do_LL1()
