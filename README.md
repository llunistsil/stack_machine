# Лабораторная работа №4: Стековый процессор с языком ALG

**ФИО:** Попов Дмитрий Юрьевич (P3313)  
**Вариант:** `alg | stack | neum | hw | tick | binary | trap | mem | cstr | prob1`

---

## Язык программирования ALG

### Синтаксис (упрощенная BNF)
```
<program>    ::= <function>+
<function>   ::= "func" ID "(" [ID ("," ID)*] ")" "{" <statement>* "}"
<statement>  ::= <assignment> | <for> | <if> | <return> | <expr> ";"
<assignment> ::= "let" ID "=" <expr> ";"
<for>        ::= "for" "(" <assignment> ";" <expr> ";" <assignment> ")" "{" <statement>* "}"
<if>         ::= "if" "(" <expr> ")" "{" <statement>* "}" ["else" "{" <statement>* "}"]
<expr>       ::= <logical_term> (("&&" | "||") <logical_term>)*
<logical_term> ::= <comparison> (("==" | "!=" | "<" | ">") <comparison>)*
<comparison> ::= <term> (("+" | "-") <term>)*
<term>       ::= <factor> (("*" | "/") <factor>)*
<factor>     ::= INT | ID | "(" <expr> ")" | <call> | <unary_op>
<call>       ::= ID "(" [<expr> ("," <expr>)*] ")"
<unary_op>   ::= ("-" | "!") <factor>
<return>     ::= "return" <expr> ";"`
```