# LISP Interpreter (6.101)

A Scheme interpreter written in Python. Type expressions, it tokenizes them, builds a parse tree, and evaluates them in nested environments (python frames).

## Running it

```bash
python3 lab.py
```

## Syntax cheat sheet

Everything is either an **atom** (number, `#t`/`#f`, or a name like `x`) or a **list** in parentheses.

```scheme
(+ 2 3)              ; 5 — prefix notation
(+ 2 (- 5 3))
```

`()` is the empty list (Python `[]` internally, not a `Pair`). `;` comments to end of line.

### Truthiness

Only `#f` is false. `0`, `()`, and other values count as true in `if`, `and`, and `or`.

`not` maps `#f` → `#t` and anything else → `#f`.

### Calls vs special forms

**Calls:** evaluate each subexpression, then apply the first result.

**Special forms** (handled in `evaluate`, not as normal calls):

| Form | Behavior |
|------|----------|
| `define` | bind in the current frame |
| `lambda` | create a function (closes over the defining frame) |
| `if` | evaluate predicate; run exactly one branch |
| `and` / `or` | short-circuit; return `#f` or the value that decided the result |
| `let` | evaluate all bindings in the outer frame, then body in a new child frame |
| `set!` | update the nearest existing binding up the frame chain |
| `del` | remove a binding from the **current** frame only; error if not local |

```scheme
(define x 10)
(define (sq n) (* n n))
```

### Lists

Lists are `Pair` chains ending in `()`. `(cons 1 2)` is a pair; `(list 1 2 3)` is a proper list. `append` builds a new list without mutating inputs.

### Built-ins (parent frame)

`+` `-` `*` `/`, `equal?`, comparisons, `not`, `cons` `car` `cdr`, `list` `list?` `length` `list-ref` `append`, `begin`.

`map`, `filter`, and `reduce` are defined in Scheme in `test_files/map_filter_reduce.scm` — load that file (or pass it on the command line) before using them.

