from math import ceil
def myround(x, base=90):
    return base * round(x/base)

print(myround(320))