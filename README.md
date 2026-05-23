# LISP Interpreter (6.101)

A Scheme interpreter written in Python. Type expressions, it tokenizes them, builds a parse tree, and evaluates them in nested environments (python frames).

## Running it

```bash
python3 lab.py
```

## How the syntax works

Scheme code is made of **S-expressions** (symbolic expressions). There are only a few kinds of things you can write:

**Atoms** — numbers (`42`, `-3.5`), booleans (`#t`, `#f`), or names/symbols (`x`, `foo`, `+`). Symbols are just strings; the interpreter decides later whether `+` is a variable or an operation.

**Lists** — anything in parentheses. A list is either a function call or a special form:

```scheme
(+ 2 3)           ; => 5
```

The first element is the operator or keyword; the rest are arguments. This is **prefix notation**: the function name comes first, then its arguments. No commas, no infix `2 + 3`.

**The empty list** — `()` is its own value (not a Pair). You’ll see it at the end of linked lists built with `cons`.

**Nesting** — lists can contain lists. The parser turns nested parens into nested Python lists:

```scheme
(+ 2 (- 5 3))     ; parses to something like ['+', 2, ['-', 5, 3]]
```

**Comments** — `;` starts a comment that runs to the end of the line.

### Special forms vs normal calls

Most parenthesized expressions are evaluated by evaluating every subexpression, then applying the first result as a function. A few forms break that rule and are handled inside the interpreter:


| Form        | Role                                               |
| ----------- | -------------------------------------------------- |
| `define`    | bind a name in the current frame                   |
| `lambda`    | create a function                                  |
| `if`        | only evaluate one branch                           |
| `and`, `or` | short-circuit; stop as soon as the answer is known |
| `let`       | local bindings in a new frame                      |
| `set!`      | change an existing binding (searches outward)      |
| `del`       | remove a binding from the *current* frame only     |


Example:

```scheme
(if (< x 0) (- x) x)    ; absolute value — only one of the branches runs
```

### Defining things

```scheme
(define x 10)
(define (square n) (* n n))    ; shorthand for (define square (lambda (n) ...))

(define my-add
  (lambda (a b)
    (+ a b)))
```

`lambda` captures the frame where it was defined. When you call it, parameters are bound in a new child frame and the body is evaluated there.

### Lists from `cons`

Lists are singly-linked chains of `Pair` objects, ending in `()`. `(cons 1 2)` is just a pair, not necessarily a list. A proper list looks like:

```scheme
(cons 1 (cons 2 (cons 3 ())))
; same idea as (list 1 2 3)
```

Use `car` / `cdr` to take the first element or the rest. `list`, `append`, `length`, `list-ref`, and `list?` work on these structures.

### Built-ins...

- Comparisons: `equal?`, `<`, `<=`, `>`, `>=` (all arguments must satisfy the relation)
- `not` — `#f` in, `#t` out; anything else gives `#f`
- `begin` — evaluate each expression for side effects, return the last one

