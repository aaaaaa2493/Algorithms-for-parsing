import sys
sys.dont_write_bytecode = True

from Homsky import *

test = open('test.txt').read()

def do_CYK():
    terms, nonterms, rules = to_homsky()
    set_print(True)

    print('Grammar in normal Homsky form:')
    print_rules(rules)

    print('String to test:')
    print(test)


if __name__ == '__main__':
    do_CYK()
