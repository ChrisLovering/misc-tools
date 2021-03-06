func_sig = 'import random\n\n\ndef is_odd(num: int) -> bool:'
space = ' ' * 4
if_statement = (
    '\n{}if num == {}:'
    '\n{}return {}'
)
else_statement = (
    '\n{}else:'
    '\n{}return bool(random.randint(0, 1))  # Worry about this later\n'
)

with open('is_odd.py', 'w') as f:
    f.write(func_sig)
    for num in range(0, 10000):
        f.write(if_statement.format(space, num, space*2, num % 2 == 1))
    f.write(else_statement.format(space, space*2))
