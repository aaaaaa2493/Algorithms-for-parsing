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

    print('Delete duplicates')

    for key in sorted(rules):
        new_rules = []
        for rule in rules[key]:
            if rule not in new_rules:
                new_rules += rule,
        rules[key][:] = new_rules

    print_rules(rules)

    for key in sorted(rules):
        rules[key][:] = [rule for rule in rules[key] if rule != [key]]

    print('Delete unused rules')

    def depth_search(marked, key, rules):
        marked = tuple(list(marked) + [key])
        for rule in rules[key]:
            for term in rule:
                if term in nonterms and term not in marked:
                    marked = depth_search(marked, term, rules)
        return marked

    used_in_rules = depth_search((), S0, rules)

    for key in sorted(rules):
        if key not in used_in_rules:
            del rules[key]

    print_rules(rules)

    print('Create FIRST set')

    first = {}
    for key in sorted(rules):
        first[key] = []

    something_changed = True
    while something_changed:
        something_changed = False
        for key in reversed(sorted(rules)):
            curr_set = first.get(key, [])
            for rule in rules[key]:
                if rule[0] not in curr_set:
                    if rule[0] in nonterms:
                        curr_index = 0
                        something_changed1 = True
                        while something_changed1:
                            something_changed1 = False

                            for other_set_elem in first.get(rule[curr_index], []):
                                if other_set_elem not in curr_set:
                                    curr_set += other_set_elem,
                                    something_changed = True

                            if [eps] in rules[rule[curr_index]] and curr_index + 1 < len(rule):
                                if rule[curr_index+1] in terms:
                                    if rule[curr_index+1] not in curr_set:
                                        curr_set += rule[curr_index+1],
                                    break
                                else:
                                    curr_index += 1
                                    something_changed1 = True
                    else:
                        curr_set += rule[0],
                        something_changed = True
            first[key] = sorted(curr_set)
            #print('FIRST( %s ) = { %s }' % (key, ', '.join(curr_set)))

    for key in sorted(rules):
        print('FIRST( %s ) = { %s }' % (key, ', '.join(first[key])))

    print()
    print('Create FOLLOW set')

    follow = {S0: [end]}

    for key in sorted(rules):
        if key not in follow:
            follow[key] = []

    something_changed = True
    while something_changed:
        something_changed = False
        for key in sorted(rules):
            curr_follow = follow.get(key, [])
            for other_key in sorted(rules):
                for rule in rules[other_key]:
                    if key in rule:
                        #print('KEY', key, other_key, rule)
                        for curr_index, curr_term in enumerate(rule[:-1]):
                            if rule[curr_index] == key:
                                next_term = rule[curr_index + 1]
                                if next_term in nonterms:
                                    #print('KEYFIRST', key, other_key, next_term, rule, first[next_term])
                                    for term in first[next_term]:
                                        if term not in curr_follow and term != eps:
                                            something_changed = True
                                            curr_follow += term,
                                else:
                                    if next_term not in curr_follow and next_term != eps:
                                        something_changed = True
                                        curr_follow += next_term,
            for other_key in sorted(rules):
                for rule in rules[other_key]:
                    if key in rule:
                        #print('KEY2', key, other_key, rule)
                        for curr_index, curr_term in enumerate(rule[:-1]):
                            if rule[curr_index] == key:
                                if all(next_term in nonterms and eps in first.get(next_term, [])
                                       for next_term in rule[curr_index + 1:]):
                                    for other_follow_elem in follow.get(other_key, []):
                                        if other_follow_elem not in curr_follow:
                                            something_changed = True
                                            curr_follow += other_follow_elem,
                        if rule[-1] == key:
                            for other_follow_elem in follow.get(other_key, []):
                                if other_follow_elem not in curr_follow:
                                    something_changed = True
                                    curr_follow += other_follow_elem,

    for key in sorted(rules):
        print('FOLLOW( %s ) = { %s }' % (key, ', '.join(follow[key])))

if __name__ == '__main__':
    do_LL1()
