from turtle import Turtle
import random

c = ['red', 'green', 'blue', 'yellow', 'orange', 'purple']
list = []
turtles = [Turtle(shape='turtle') for i in range(len(c))]

position = (0, 0)

for i in range(len(c)):
    t = turtles[i]
    t.speed(6)
    t.color(c[i])
    t.penup()
    t.position = position
    t.pendown()
    t.forward(i*10+10)