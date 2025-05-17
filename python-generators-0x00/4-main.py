#!/usr/bin/python3

average_age = __import__("4-stream_ages").compute_average_age

try:
    average: float = average_age()
    print(f"Average age: {average}")
except ArithmeticError as e:
    print(f"Error: {e}")