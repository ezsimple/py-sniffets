# %%
import turtle as t
import random

t.setup(width=800, height=600)

def player(color: str):
    _t = t.Turtle()
    _t.shape('turtle')
    _t.color(color)

    _t.penup()
    _t.goto(0, -200)  # Move the turtle to the bottom-center of the screen (x=0, y=-200)
    _t.pendown()
    return _t

def running(_t: t.Turtle, direction: str, angle: int):
    _t.speed(random.randint(0,10))
    if direction == 'forward':
        _t.forward(40)
        _t.left(360/a)
    
    if direction == 'backward':
        _t.backward(40)
        _t.right(360/a)


t1 = player('red')
t2 = player('green')

a = 36
for i in range(a):
    running(t1, 'forward', a) 
    running(t2, 'backward', a)

t.bye()
