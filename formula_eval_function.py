OPERATORS = {'+': (1, lambda x, y: x + y), '-': (1, lambda x, y: x - y),
             '*': (2, lambda x, y: x * y), '/': (2, lambda x, y: x / y)}


def formula_eval(formula):
    '''
    https://habrahabr.ru/post/273253/

    '''

    def parse(formula_string):
        formula_string = formula_string.replace(' ', '')
        number = ''
        for i, s in enumerate(formula_string):
            if s in '1234567890.':
                number += s
            elif number:
                yield float(number)
                number = ''
            if i == 0 and s == '-':
                number += '-'
            if s == '-' and formula_string[i-1] in OPERATORS:
                number += '-'
            elif s == '-' and formula_string[i+1] == '-':
                yield s
            elif s in '+*/()':
                yield s
        if number:
            yield float(number)

    def shunting_yard(parsed_formula):
        stack = []
        for token in parsed_formula:
            if token in OPERATORS:
                while stack and stack[-1] != "(" and OPERATORS[token][0] <= OPERATORS[stack[-1]][0]:
                    yield stack.pop()
                stack.append(token)
            elif token == ")":
                while stack:
                    x = stack.pop()
                    if x == "(":
                        break
                    yield x
            elif token == "(":
                stack.append(token)
            else:
                yield token
        while stack:
            yield stack.pop()

    def calc(polish):
        stack = []
        for token in polish:
            if token in OPERATORS:
                y, x = stack.pop(), stack.pop()
                stack.append(OPERATORS[token][1](x, y))
            else:
                stack.append(token)
        return stack[0]

    return calc(shunting_yard(parse(formula)))
