import Lexer4







f = open("Source.pr","r")
text = f.read()
result = Lexer4.run("demo", text)

for index in range(len(result)):
    print(result[index])
f.close()

file1 = open('symbolTable.pr', 'w')


file1.write(str("Token"+"\t\t\t"+"Lexeme"+"\t\t\t"+"Description")+"\n")
for index in range(len(result)):
    a=result[index]

    file1.write(str(a))
    file1.write("\n")




file1.close()
