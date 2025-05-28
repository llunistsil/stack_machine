# Лабораторная работа №4

**ФИО:** Попов Дмитрий Юрьевич (P3313)
**Группа:** <Группа>
**Вариант:** alg | stack | neum | hw | tick | binary | trap | mem | cstr | prob1 | vector

---

## Язык программирования

### Синтаксис (Бэкуса-Наур)

```
<program> ::= <statement>*
<statement> ::= <assignment> | <print_statement> | <input_statement> | <conditional_statement> | <loop_statement>
<assignment> ::= <variable> = <expression>
<print_statement> ::= (/out | >) <expression>
<input_statement> ::= /in <variable>
<conditional_statement> ::= if <expression> : <program> ;
<loop_statement> ::= while <expression> : <program> ;
<expression> ::= <unary_expr> | <expression> ( + | - | * | / | % | && | || | < | > | <= | >= | == | != ) <expression>
<unary_expr> ::= <term> | ! <term>
<term> ::= <variable> | <string_literal> | <number> | ( <expression> )
<variable> ::= [_a-zA-Z]\w*
<string_literal> ::= '[^']*'
<number> ::= [+-]?[1-9]\d*|0
```

### Семантика
- **Стратегия вычислений:** выражения вычисляются в порядке, определяемом приоритетом операторов (стандартный infix → postfix → стековая машина).
- **Области видимости:** все переменные глобальные, область видимости — вся программа.
- **Типизация:** неявная, все значения — целые числа или строки (строки — только в одинарных кавычках, null-terminated в памяти).
- **Литералы:** поддерживаются целые числа и строки.

---

(Дальнейшие разделы будут заполняться по мере реализации)