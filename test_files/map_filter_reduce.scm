(begin
  (define (map f lst)
    (if (equal? (length lst) 0)
      (list)
      (cons (f (car lst)) (map f (cdr lst)))))

  (define (filter f lst)
    (if (equal? (length lst) 0)
      (list)
      (if (f (car lst))
        (cons (car lst) (filter f (cdr lst)))
        (filter f (cdr lst)))))

  (define (reduce f lst val)
    (if (equal? (length lst) 0)
      val
      (reduce f (cdr lst) (f val (car lst)))))
)
