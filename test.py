dictionary = {}
dictionary[(1, 0)] = 10
dictionary[(1, 1)] = 9
dictionary[(2, 0)] = 8
dictionary[(0, 2)] = 7

for x in range(0, 6):
    for y in range(0, 6):
        for chest in dictionary.keys():
            if chest == (x, y):
                print(dictionary[chest])

