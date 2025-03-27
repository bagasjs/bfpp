;; tape[1] = 20
++++++++++[>++++++++++++++++++++<-]>

;; tp = 1
[
    <+  ;; move value from tape[1] to tape[0]
    >>+ ;; move value from tape[1] to tape[2]
    <-  ;; decrement the value of tape[1]
]
;; tp = 1
< ;; move to tape[0]
[
    -
    >+
    <
]

?
>?
>?

;; here's the minified version
;; 
