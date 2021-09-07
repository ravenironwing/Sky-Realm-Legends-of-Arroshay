"""

pattern to round edges
[1, 0]
[0, 0],

[0, 1]
[0, 0],

[0, 0]
[1, 0],

[0, 0]
[0, 1]]

simplify detection by counting how many 1's. If there is one find it and replace with rounded edge.
"""

def make_tmx():
    outfile = open("newautomap.tmx", "w")
    header = """<?xml version="1.0" encoding="UTF-8"?>
    <map version="1.4" tiledversion="1.4.1" orientation="orthogonal" renderorder="right-down" width="{mapw}" height="{mapw}" tilewidth="32" tileheight="32" infinite="0" nextlayerid="2" nextobjectid="1">
     <tileset firstgid="1" name="automaptiles" tilewidth="32" tileheight="32" tilecount="72" columns="18">
      <image source="automaptiles.png" width="448" height="32"/>
        <tile id="18">
           <animation>
            <frame tileid="54" duration="100"/>
            <frame tileid="55" duration="100"/>
            <frame tileid="56" duration="100"/>
            <frame tileid="57" duration="100"/>
            <frame tileid="58" duration="100"/>
            <frame tileid="59" duration="100"/>
            <frame tileid="60" duration="100"/>
            <frame tileid="61" duration="100"/>
           </animation>
          </tile>
     </tileset>
     <layer id="1" name="Tile Layer 1" width="{mapw}" height="{mapw}">
      <data encoding="csv">""".format(mapw = str(MAP_SIZE))
    outfile.write(header)
    outfile.write("\n")

    for i, row in enumerate(base_layer_vals):
        row_text = str(row)
        row_text = row_text.replace('[', '')
        row_text = row_text.replace(']', '')
        if i != MAP_SIZE - 1:
            new_row_str = new_row_str + ","
        outfile.write(new_row_str)
        outfile.write("\n")

    for i in range(MAP_SIZE):
        for j in range(MAP_SIZE):
            x = world_noise[i][j]
            newx = int(x * (KINDSOFTILES-1))
            newx = newx + 1  # Gets rid of zeros
            if newx > max_num:
                max_num = newx
            if newx < min_num:
                min_num = newx
            water = 0
            if newx < 6:
                water = WATER_TILE
            new_water_row.append(water)
            new_base_row.append(newx)
        new_row_str = str(new_base_row)
        new_row_str = new_row_str.replace('[', '')
        new_row_str = new_row_str.replace(']', '')
        if i != MAP_SIZE - 1:
            new_row_str = new_row_str + ","
        outfile.write(new_row_str)
        outfile.write("\n")
        base_layer_vals.append(new_base_row)
        water_layer_vals.append(new_water_row)