import os

os.system('cls')

names = ("joe", "boe", "goe")

print(",".join(names))


gameboard = [["X" for _ in range(8)] for _ in range(3)]

print(gameboard)

for row in gameboard:
    print(" | ".join(row))
    print("-" * 10)