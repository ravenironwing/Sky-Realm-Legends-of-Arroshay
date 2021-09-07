# Takes a list of lists of lista and scales all the values by a factor then rewrites the list of lists of lists to a new file.
infile = open("cp.txt", "r")
outfile = open("scaled_cp.txt", "a")
pos_file_data = infile.readlines()
scale_factor = 0.5
for row in pos_file_data:
    try:
        list_name, list_str = row.split(' = ')
        list_data = eval(list_str)
        print(list_data)
        new_list = []
        for element in list_data:
            new_el = []
            for i, y in enumerate(element):
                if i != 2: # Ignores body part angles and only scales the position offset.
                    x = int(y*scale_factor)
                else:
                    x = y
                new_el.append(x)
            new_list.append(new_el)
        outfile.write(list_name + ' = ' + str(new_list))
        outfile.write("\n")
    except:
        pass
outfile.close()
infile.close()
print("Finished scaling.")


