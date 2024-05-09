#Global delclarations
#Variables
currentChar = ''
nextToken = 0
error_flag = False

#Token codes
INT_LIT = 10
IDENT = 11
ASSIGN_OP = 20 # =
ADD_OP = 21 # +
SUB_OP = 22 # -
MULT_OP = 23 # *
DIV_OP = 24 # /
LEFT_PAREN = 25 # (
RIGHT_PAREN = 26 # )
EQ_OP = 27 # ==
NEQ_OP = 28 # !=
LT_OP = 29 # <
GT_OP = 30 # >
LTE_OP = 31 # <=
GTE_OP = 32 # >=
PRINT = 33
SEMI_COLON = 34
DO_WHILE = 35
TYPE_INT = 36
EOF = '\0'

results_dict = {}
print_li = []

def lex():
    global tokens, nextToken, currentChar
    if not tokens:
        nextToken = EOF
        return

    currentToken = tokens.pop(0)

    if currentToken.isalpha():
        if currentToken == "print":
            nextToken = PRINT
        elif currentToken == "do":
            nextToken = DO_WHILE
        elif currentToken == "int":
            nextToken = TYPE_INT
        # elif currentToken in ["float", "char", "string", "double"]: #수정
        #     error()
        else:
            nextToken = IDENT
        currentChar = currentToken
    elif currentToken.isdigit():
        nextToken = INT_LIT
        currentChar = currentToken
    else:
        lookup(currentToken)

def lookup(ch):
    global nextToken
    if ch == '(':
        nextToken = LEFT_PAREN
    elif ch == ')':
        nextToken = RIGHT_PAREN
    elif ch == '+':
        nextToken = ADD_OP
    elif ch == '-':
        nextToken = SUB_OP
    elif ch == '*':
        nextToken = MULT_OP
    elif ch == '/':
        nextToken = DIV_OP
    elif ch == '<':
        nextToken = LT_OP
    elif ch == '<=':
        nextToken = LTE_OP
    elif ch == '>':
        nextToken = GT_OP
    elif ch == '>=':
        nextToken = GTE_OP
    elif ch == '=':
        nextToken = ASSIGN_OP
    elif ch == '==':
        nextToken = EQ_OP
    elif ch == '!=':
        nextToken = NEQ_OP
    elif ch == ';':
        nextToken = SEMI_COLON
    else:
        nextToken = EOF


def error():
    global error_flag
    error_flag = True

#<program> → {<declaration>} {<statement>} => 바로 다음이 int면 declaration, 아니면 statement
def program():
    global nextToken
    if not tokens: #엔터만 친 경우
        return
    lex()
    # while nextToken != EOF and not error_flag:
    #     if nextToken == TYPE_INT:
    #         declaration()
    #     else:
    #         statement()
    #     if not tokens:
    #         nextToken = EOF
    while nextToken != EOF and not error_flag:
        if nextToken == TYPE_INT:
            declaration()
        else:
            break
        if not tokens:
            nextToken = EOF
    while nextToken != EOF and not error_flag:
        statement()
        if not tokens:
            nextToken = EOF

    if tokens: #while문 끝났는데 tokens가 있으면 에러
        error()

#<declaration> → <type> <var> ;
def declaration(): #다음에 세미콜론 있는지 확인
    type()
    lex()
    var_name = var()
    lex()
    if nextToken == SEMI_COLON: #선언된 변수는 0으로 초기화
        lex()
        results_dict[var_name] = 0
    else:
        error()

#<statement> → <var> = <aexpr> ; | print <bexpr> ; | print <aexpr> ; |
# do ‘ { ’ {<statement>} ‘ } ’ while ( <bexpr> ) ;
def statement():
    global currentChar, nextToken, results_dict, print_li, error_flag
    if nextToken == PRINT:
        temp = tokens[0]
        if temp.isalnum() or temp == '(': #tokens배열의 맨 앞이 문자나 숫자이면 aexpr
            result = aexpr()
        else: #연산자이면 bexpr
            result = bexpr(currentChar)
        lex()
        if nextToken == SEMI_COLON:
            lex()
            print_li.append(result)
        else:
            error()
    elif nextToken == DO_WHILE: #do로만 체크해서 nextToken을 DO_WHILE로 둔거니까 while이 뒤에 오는지 체크
        print("do while") #{랑 } 체크
        idx = tokens.index(';')
        do_while = tokens[0:idx+1]
        print(do_while)

    elif nextToken == IDENT: #<var> = <aexpr> 경우
        var_name = var()
        lex()
        if nextToken == ASSIGN_OP:
            result = aexpr()
            lex()
            if nextToken == SEMI_COLON:
                lex() #이거 해야하나?
                if var_name in results_dict: #이미 선언된 변수만 가능
                    results_dict[var_name] = result
                else:
                    error()
            else:
                error()
        else:
            error()
    else:
        error()

def bexpr(operand):
    result = 0
    op = relop()  # Get relational operator
    left_operand = aexpr() #Get left operand
    right_operand = aexpr()  # Get right operand

    if op == EQ_OP:
        result = left_operand == right_operand
    elif op == NEQ_OP:
        result = left_operand != right_operand
    elif op == LT_OP:
        result = left_operand < right_operand
    elif op == GT_OP:
        result = left_operand > right_operand
    elif op == LTE_OP:
        result = left_operand <= right_operand
    elif op == GTE_OP:
        result = left_operand >= right_operand
    else:
        error()
    if result:
        result = "TRUE"
    else:
        result = "FALSE"
    return result

def relop():
    global nextToken
    lex()
    if nextToken not in [EQ_OP, NEQ_OP, LT_OP, GT_OP, LTE_OP, GTE_OP]:
        error()
        nextToken = EOF
    return nextToken

def aexpr():
    global nextToken
    # { }니까 계산 안할 경우를 생각해서 첫번째 피연산자를 result에 넣기
    lex()
    # left_operand = operand #근데 이렇게 하면 term()을 호출해서 하는게 아니게됨
    result = term() #첫번째 연산자 term()
    while tokens and tokens[0] in ['+', '-', '–', '*', '/']: #aexpr의 { {( + | - | * | / ) <term>}
        lex()
        if nextToken in [ADD_OP, SUB_OP, MULT_OP, DIV_OP]:
            opToken = nextToken
            lex()
            second_operand = term()  # Parse another term
            if opToken == ADD_OP:
                result += second_operand
            elif opToken == MULT_OP:
                result *= second_operand
            elif opToken == DIV_OP:
                result /= second_operand
            else:
                result -= second_operand
    return int(result)

#<term> → <number> | <var> | ( <aexpr> )
def term():
    global nextToken
    result = 0
    # lex()
    if nextToken == INT_LIT:
        result = number()
    elif nextToken == IDENT:
        var_name = var()
        if var_name in results_dict:
            result = results_dict[var_name]
        else:
            error()
    elif nextToken == LEFT_PAREN:
        result = aexpr()
        lex()
        if nextToken == RIGHT_PAREN:
            return result
        else:
            error()
    return result

def type(): #수정
    global currentChar
    if nextToken != TYPE_INT:
        error()

def dec():
    global currentChar
    return currentChar

def number():
    return int(dec())

def var():
    global currentChar
    result = ''
    # lex()
    if nextToken == IDENT:
        result = alphabet()
    else:
        error()
    return result

def alphabet():
    global currentChar
    return currentChar

# 입력 받기
while True:
    code = input()
    if code == "terminate":
        break
    tokens = code.split()
    program()
    if error_flag:
        print("Syntax Error!!")

    if print_li and error_flag == False:
        print(' '.join(str(result_to_print) for result_to_print in print_li))

    error_flag = False
    results_dict = {}
    print_li = []