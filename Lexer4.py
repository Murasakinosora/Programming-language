import TokenVal


class Tokenize:
    def __init__(self,desc_, type_,ln1_,val=None):
        self.ln1 = ln1_
        self.val = val
        self.type = type_
        self.desc = desc_


    def __repr__(self):
        if self.val: return f'{self.ln1}\t\t\t{self.val}\t\t\t{self.type}\t\t\t{self.desc}'
        return f'{self.type}'


class Scan:
    def __init__(self, idx, col, ln, text, fn):
        self.idx = idx
        self.col = col
        self.ln = ln
        self.text = text
        self.fn = fn

    def advance(self, current):
        self.idx += 1
        self.col += 1

        if current == "\n":
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Scan(self.idx, self.ln, self.col, self.text, self.fn)


class Lex:

    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Scan(-1, 0, -1, fn, text)
        self.current = None
        self.advance()
        self.counter = 0

    def advance(self):
        self.pos.advance(self.current)
        self.current = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def token(self):

        tokens = []

        while self.current != None:

            if self.current in ' ':
                self.advance()
            elif self.current == '?':
                tokens.append(self.scomment())
                self.advance()
            elif self.current == '|':
                tokens.append(self.mcomment())
                self.advance()
            elif self.current == '^':
                tokens.append(self.dcomment())
                self.advance()
            elif self.current == '(':
                tokens.append(Tokenize(str("OPENING PARENTHESIS"), TokenVal.DEL,self.pos.ln+2, TokenVal.LPAR))

                self.advance()
            elif self.current == ')':
                tokens.append(Tokenize(str("CLOSING PARENTHESES"), TokenVal.DEL,self.pos.ln+2, TokenVal.RPAR))

                self.advance()
            elif self.current in '\n':
                self.pos.ln += -1
                self.advance()
            elif self.current in TokenVal.DIGITS:
                tokens.append(self.num_fn())
                self.advance()
            elif self.current in TokenVal.CHAR:
                a = self.checker()
                if  a != 9:
                   tokens.append(a)
                   self.advance()
                elif a == 9:
                    print("Identifiers must not exceed 30 characters " + str(self.pos.ln + 2) + ":" + self.current)
                    tokens = []
                    break;

            elif self.current == '~':

                tokens.append(Tokenize(str("LINE TERMINATOR"), TokenVal.DEL,self.pos.ln+2, str("~")))
                self.pos.ln += +1
                self.advance()
            elif self.current == '"':
                tokens.append(self.create_str())
                self.advance()
            elif self.current == "'":
                tokens.append(self.create_str2())
                self.advance()
            elif self.current == '<':
                tokens.append(self.create_less())
                self.advance()
            elif self.current == '>':
                tokens.append(self.create_greater())
                self.advance()
            elif self.current == '{':
                tokens.append(Tokenize(str("OPENING CURLY BRACE"), TokenVal.DEL,self.pos.ln+2, TokenVal.LCUR))
                self.advance()
            elif self.current == '}':
                tokens.append(Tokenize(str("CLOSING CURLY BRACE"), TokenVal.DEL,self.pos.ln+2,TokenVal.RCUR))
                self.advance()
            elif self.current == '+':
                if self.text[self.pos.idx+2] == "+" and self.current == "+":
                   print("test")
                   tokens.append(Tokenize(str("ARITHMETIC OPERATOR"), TokenVal.PLUS, self.pos.ln + 2, str("+")))
                   self.pos.ln += +1
                   self.advance()
                else:
                   tokens.append(Tokenize(str("ARITHMETIC OPERATOR"), TokenVal.PLUS, self.pos.ln + 2, str("+")))
                   self.advance()

            elif self.current == '-':
                if self.text[self.pos.idx + 2] == "-" and self.current == "-":
                    print("test")
                    tokens.append(Tokenize(str("ARITHMETIC OPERATOR"), TokenVal.MINUS, self.pos.ln + 2, str("-")))
                    self.pos.ln += +1
                    self.advance()
                else:
                    tokens.append(Tokenize(str("ARITHMETIC OPERATOR"), TokenVal.MINUS, self.pos.ln + 2, str("-")))
                    self.advance()
            elif self.current == '*':
                tokens.append(self.create_mul())
                self.advance()
            elif self.current == '/':
                if self.text[self.pos.idx + 2] == "/" and self.current == "/":
                    print("test")
                    tokens.append(Tokenize(str("ARITHMETIC OPERATOR"), TokenVal.DIV, self.pos.ln + 2, str("/")))
                    self.pos.ln += +1
                    self.advance()
                else:
                    tokens.append(Tokenize(str("ARITHMETIC OPERATOR"), TokenVal.DIV, self.pos.ln + 2, str("/")))
                    self.advance()
            elif self.current == '!':
                tokens.append(self.create_not())
                self.advance()
            elif self.current == '=':
                if self.text[self.pos.idx + 1] == '!':
                    print("Syntax Error at line" + str(self.pos.ln + 2) + ": '!' after '='")
                    tokens = ''
                    break
                else:
                    tokens.append(self.create_eq())
                    self.advance()
            elif self.current == '%':
                tokens.append(Tokenize(str("ARITHMETIC OPERATOR"), TokenVal.MOD,self.pos.ln+2, str("%")))
                self.advance()
            else:
                print("Error: Illegal Character at line " + str(self.pos.ln + 2) + ":" + self.current)
                tokens = ''
                break
        tokens.append(TokenVal.EOF)
        return tokens

    def num_fn(self):
        num = ''
        dot_count = 0

        a=0

        while self.current != None and self.current in TokenVal.DIGITS + '.':

            if self.current == '.':
                if dot_count == 1: break
                dot_count += 1
                num += '.'
            else:
                num += self.current
            self.advance()

        if dot_count == 0:
            self.pos.idx = self.pos.idx - 1

            if self.text[self.pos.idx - 1] == '"':
                return Tokenize(str(TokenVal.desc13), TokenVal.CON,a+2, int(num))
            elif self.text[self.pos.idx - 1] != '"':
                return Tokenize(str(TokenVal.desc3), TokenVal.INT,self.pos.ln+2, int(num))
        else:
            self.pos.idx = self.pos.idx - 1

            if self.text[self.pos.idx - 1] == '"':
                return Tokenize(str(TokenVal.desc13), TokenVal.CON,a+2, float(num))
            elif self.text[self.pos.idx - 1] != '"':
                return Tokenize(str(TokenVal.desc14),TokenVal.FLOAT,self.pos.ln+2, float(num))

    def checker(self):

        str1 = ''
        q = 0
        w = 0


        if self.text[self.pos.idx - 1] == "'":
            q = q + 1
        elif self.text[self.pos.idx - 1] == '"':
            w = w + 1

        while self.current != None and self.current in TokenVal.CHAR:
            str1 += self.current
            self.advance()



        if q == 1:
            self.pos.idx = self.pos.idx - 1
            return Tokenize(str(TokenVal.desc15), TokenVal.CON,self.pos.ln+2, str(str1))
        elif w == 1:
            self.pos.idx = self.pos.idx - 1
            return Tokenize(str(TokenVal.desc13), TokenVal.CON,self.pos.ln+2, str(str1))
        TT = TokenVal.CON if str1 in TokenVal.CONSTANTS else TokenVal.ID
        TK = TokenVal.KY if str1 in TokenVal.KEYWORDS else TokenVal.ID


        if TK != TokenVal.ID and TT == TokenVal.ID:
            self.pos.idx = self.pos.idx - 1
            if self.text[self.pos.idx - 1] == "'":
                return Tokenize(str(TokenVal.desc13), TokenVal.CON,self.pos.ln+2, str(str1))
            elif self.text[self.pos.idx - 1] == '"':
                return Tokenize(str(TokenVal.desc13), TokenVal.CON,self.pos.ln+2, str(str1))
            elif str1 == "INT":
                return Tokenize(str(TokenVal.desc1), TK,self.pos.ln+2, str(str1))
            elif str1 == "FLOAT":
                return Tokenize(str(TokenVal.desc2), TK,self.pos.ln+2, str(str1))
            elif str1 == "SCAN":
                return Tokenize(str(TokenVal.desc4), TK,self.pos.ln+2, str(str1))
            elif str1 == "SHOW":
                return Tokenize(str(TokenVal.desc5), TK,self.pos.ln+2, str(str1))
            elif str1 == "CHAR":
                return Tokenize(str(TokenVal.desc6), TK,self.pos.ln+2, str(str1))
            elif str1 == "BOOL":
                return Tokenize(str(TokenVal.desc7), TK,self.pos.ln+2, str(str1))
            elif str1 == "STRING":
                return Tokenize(str(TokenVal.desc8), TK,self.pos.ln+2, str(str1))
            elif str1 == "if":
                return Tokenize(str(TokenVal.desc9), TK,self.pos.ln+2, str(str1))
            elif str1 == "then":
                return Tokenize(str(TokenVal.desc9), TK,self.pos.ln+2, str(str1))
            elif str1 == "else":
                return Tokenize(str(TokenVal.desc9), TK,self.pos.ln+2, str(str1))
            elif str1 == "REPEAT":
                return Tokenize(str(TokenVal.desc10), TK,self.pos.ln+2, str(str1))
            elif str1 == "DO":
                return Tokenize(str(TokenVal.desc10), TK,self.pos.ln+2, str(str1))
            elif str1 == "continue":
                return Tokenize(str(TokenVal.desc11), TK,self.pos.ln+2, str(str1))
            elif str1 == "break":
                return Tokenize(str(TokenVal.desc11), TK,self.pos.ln+2, str(str1))
            elif str1 == "NOT":
                return Tokenize(str(TokenVal.desc12), TK,self.pos.ln+2, str(str1))
            elif str1 == "AND":
                return Tokenize(str(TokenVal.desc12), TK,self.pos.ln+2, str(str1))
            elif str1 == "OR":
                return Tokenize(str(TokenVal.desc12), TK,self.pos.ln+2, str(str1))
            elif str1 == "CLASS":
                return Tokenize(str("CLASS DECLARATION"),TK,self.pos.ln+2, str(str1))

        else:
            if len(str1) > 30:
                return 9
            else:
                self.pos.idx = self.pos.idx - 1
                return Tokenize(str("Variable" + " " + str1), TokenVal.ID,self.pos.ln+2, str(str1))

    def create_mul(self):

        if self.text[self.pos.idx + 1] == '*':
            self.pos.idx += 1
            self.advance()
            return Tokenize(str("ARITHMETIC OPERATOR"), TokenVal.POW,self.pos.ln+2, str("**"))


        else:
            if self.text[self.pos.idx + 2] == "*" and self.current == "*":
                print("test")
                self.advance()
                return Tokenize(str("ARITHMETIC OPERATOR"), TokenVal.MUL,self.pos.ln+2, str("*"))

            else:

                return Tokenize(str("ARITHMETIC OPERATOR"), TokenVal.MUL,self.pos.ln+2, str("*"))



    def create_eq(self):

        if self.text[self.pos.idx + 1] == '=':
            self.pos.idx += 1
            return Tokenize(str("RELATIONAL OPERATOR"), TokenVal.EE,self.pos.ln+2, str("=="))

        else:

            return Tokenize(str("Assignment Operator"), TokenVal.EQ,self.pos.ln+2, str("="))

    def create_str(self):
        if self.current == '"':
            return Tokenize(str("DOUBLE QUOTATION"), TokenVal.DEL,self.pos.ln+2, str('"'))
        else:
            strs = ''
            self.advance()
            while self.current != None and self.current != '"':
                strs += self.current
                self.advance()
            return Tokenize(str(TokenVal.desc13), TokenVal.STRNG,self.pos.ln+2, str(strs))

    def create_str2(self):
        if self.current == "'":
            return Tokenize(str("SINGLE QUOTATION"), TokenVal.DEL,self.pos.ln+2, str("'"))
        else:
            strs1 = ''
            self.advance()
            while self.current != None and self.current != "'":
                strs1 += self.current
                self.advance()
            return Tokenize(str(TokenVal.desc15), TokenVal.CHR,self.pos.ln+2, str(strs1))

    def create_less(self):
        self.advance()
        if self.current == "=":
            return Tokenize(TokenVal.ROP, TokenVal.LTE,self.pos.ln+2, str("<="))
        else:
            self.pos.idx = self.pos.idx - 1
            return Tokenize(TokenVal.ROP, TokenVal.LT,self.pos.ln+2, str("<"))

    def create_greater(self):
        self.advance()
        if self.current == "=":

            return Tokenize(TokenVal.ROP, TokenVal.GTE,self.pos.ln+2, str(">="))
        else:
            self.pos.idx = self.pos.idx - 1
            return Tokenize(TokenVal.ROP, TokenVal.GT,self.pos.ln+2, str(">"))

    def create_not(self):
        if self.text[self.pos.idx + 1] == "=":
            self.pos.idx = self.pos.idx + 1
            return Tokenize(TokenVal.ROP, TokenVal.NE,self.pos.ln+2, str("!="))
        else:
            return Tokenize(TokenVal.ROP, TokenVal.N,self.pos.ln+2, str("!"))

    def scomment(self):
        scomm = ''
        if self.current == '?':
            self.advance()
            while self.current != None and self.current != '?' and self.current != "\n":
                scomm += self.current
                self.advance()
            else:
                return Tokenize(str("SINGLE LINE COMMENT"), TokenVal.COM,self.pos.ln+2, str(scomm))

    def mcomment(self):
        mcomm = ''
        if self.current == '|':

            self.advance()
            while self.current != None and self.current != '|':
                if self.current != "\n":
                    mcomm += self.current
                    self.advance()
                else:
                    self.advance()
            else:
                return Tokenize(str("MULTILINE COMMENT"), TokenVal.COM,self.pos.ln+2, str(mcomm))

    def dcomment(self):
        dcomm = ''
        if self.current == '^':
            self.advance()
            while self.current != None and self.current != '^':
                if self.current != '.':
                    dcomm += self.current
                    self.advance()
                else:
                    self.advance()

            return Tokenize(str("DOCUMENTATION"), TokenVal.COM,self.pos.ln+2, str(dcomm))




def run(text, fn):
    lexer = Lex(text, fn)
    result = lexer.token()


    return result
