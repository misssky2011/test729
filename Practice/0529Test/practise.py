import math

try:
    num = float(input("Enter a number to find its square root:"))
    if num < 0:
        raise ValueError("Cannot compute square root of a negative number.")
    result = math.sqrt(num)
    print(f"The square root of {num} is {result}")
except ValueError as e:
    print("Error:", e)

grades = {
    "Alice": 85,
    "Bob": 92,
    "Charlie": 88,
    "David": 79
}
average_grade = sum(grades.values()) / len(grades)
print("Average grade:", average_grade)

def decorator(func):
    def wrapper(*args, **kwargs):
        print("Function is about to execute...")
        result = func(*args, **kwargs)
        print("Function has executed.")
        return result
    return wrapper

@decorator
def add_numbers(a, b):
    return a + b
        
print("Result:", add_numbers(3, 4))

