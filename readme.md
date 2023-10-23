### Example code snippets in the raw language and the abstracted language respectively: 

### Task 1

Raw:
```
1 C + 1 M -> 1 C2 + 1 M2
1 M -> 1 M2
1 C2 + 1 C -> 1 T + 1 C
1 M2 + 1 C -> 1 T + 1 C
1 C -> 1 T
1 M2 -> 1 P
1 C2 -> 1 P
```

Abstracted:
```
f1:
    addclean(C, M, T)
f2:
    addclean(C, M, P)
isbigger(C, M, is_bigger)
executeif(is_bigger, f1)
executeifnot(is_bigger, f2)
```

Translation:
```
f1 -> f1_token_0
f1_token_0 + C -> T + f1_token_0
f1_token_0 + M -> T + f1_token_0
f1_token_0 -> 0

f2 -> f2_token_0
f2_token_0 + C -> P + f2_token_0
f2_token_0 + M -> P + f2_token_0
f2_token_0 -> 0



Final goal:
```
if C > M:
    addclean(C, M, T)
else:
    addclean(C, M, P)
```

### Task 2

Raw:

```
Limits:
l <= 1
Instructions:
0 -> z + l
z + c -> c2 + z
z + m -> m2 + z
z -> 0
c2 -> c + f
m2 -> m + f
```

Abstracted:

```
add(c, m, f)
```

Translation:

```

```

Final goal:

```
add(c, m, f)
```

### Task 3

Raw:

```
z + c + m2 -> m + c + z
z -> 0
m + c -> f + c + m2
c -> z
m2 -> 0
```

Abstracted:

```
f1:
    recipe((c), (c2, f))
f2:
    recipe((c2), (c, f))

executeif(repeatforclean(m, f1), c)
executeif(repeatforclean(m, f2), c2)
```

Translation:

```
f1 -> f1_token_0
f1_token_0 + c -> f1_token_0 + c2 + f
f1_token_0 -> 0

f2 -> f2_token_0
f2_token_0 + c2 -> f2_token_0 + c + f
f2_token_0 -> 0

c + m -> f1 + c
c2 + m -> f2 + c2
```