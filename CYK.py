import sys
sys.dont_write_bytecode = True

from Homsky import *


def do_CYK():
    terms, nonterms, rules = to_homsky()
    set_print(True)

    print('Grammar in normal Homsky form:')
    print_rules(rules)

    print('String to test:')
    print('"%s"' % test)

    print()

    total_length = len(test)

    if total_length == 0:
        if [eps] in rules['\S0']:
            print('Test is empty string and grammar has rule \S0 -> \eps.')
            print_result(True)
        else:
            print('Test is empty string but grammar has not rule \S0 -> \eps.')
            print_result(False)

    memory = {}

    for length in range(1, total_length + 1):
        print()
        print('Start evaluate substrings with length %s' % length)
        print()

        for left in range(total_length - length + 1):
            right = left + length - 1
            print('Evaluate substring [%s, %s] - "%s"' % (left, right, test[left: right + 1]))

            possible_answers = []
            if length == 1:
                for key in rules:
                    for rule in rules[key]:
                        if rule == [test[left]]:
                            possible_answers += key,
                            break

                if not possible_answers:
                    print('Nonterminals not found')
                    print('"%s" contain symbol not represented in grammar - "%s"' % (test, test[left]))
                    print_result(False)

                else:
                    print('Answers found:')
                    for answer in possible_answers:
                        print('%s -> %s' % (answer, test[left]))
                    memory[(left, right)] = possible_answers

            else:
                curr_fst = [left, left]
                curr_snd = [left + 1, right]

                while curr_fst[1] < curr_snd[1]:
                    left_mem = memory[tuple(curr_fst)]
                    right_mem = memory[tuple(curr_snd)]

                    print('Try to process [%s, %s] + [%s, %s] or [%s] + [%s]'
                          % (curr_fst[0], curr_fst[1],
                             curr_snd[0], curr_snd[1],
                             ' '.join(left_mem), ' '.join(right_mem)))

                    local_answers = []
                    for iter_left in left_mem:
                        for iter_right in right_mem:
                            for key in sorted(rules):
                                if [iter_left, iter_right] in rules[key]:
                                    local_answers += (key, iter_left, iter_right),

                    if not local_answers:
                        print('No answers found')

                    else:
                        possible_answers += [l[0] for l in local_answers]
                        print('Answers found:')
                        for answer, iter_left, iter_right in local_answers:
                            print('%s -> %s %s' % (answer, iter_left, iter_right))

                    curr_fst[1] += 1
                    curr_snd[0] += 1

                memory[(left, right)] = possible_answers

            print()

    total_table = [['']*total_length for _ in ' '*total_length]

    for elem in memory:
        total_table[elem[1]][elem[0]] = ' '.join(memory[elem])

    print('Resulting table:')
    print(format_matrix([str(i) for i in range(total_length)],
                        [str(i) for i in range(total_length)],
                        total_table))
    print()

    if '\S0' in memory[(0, total_length - 1)]:
        print('Cell [0, 5] has nonterminal \S0')
        print_result(True)

    else:
        print('Cell [0, 5] has not nonterminal \S0')
        print_result(False)


if __name__ == '__main__':
    do_CYK()
