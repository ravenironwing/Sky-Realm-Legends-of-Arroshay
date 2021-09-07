tiles = [12,2684354572,3221225484,1610612748,2147483660,3758096396,1073741836,536870924,2147483660,3758096396,1073741836,536870924,3221225484,1610612748,12,2684354572]

#tile = 1610612775
tile = 12

#Transforms tiles
horizontalFlip = tile | 0x80000000
verticalFlip = tile | 0x40000000
diagonalFlip = tile | 0x20000000
tile = tile | 0x20000000 | 0x40000000
print(tile)


tileID = tile & ~(0x80000000 | 0x40000000 | 0x20000000) #clear the flags

def return_flags(bitnum):
    tileid = bitnum & ~(0x80000000 | 0x40000000 | 0x20000000)
    if tileid == bitnum & ~(0x20000000):
        return 0x20000000
    elif tileid == bitnum & ~(0x40000000):
        return 0x40000000
    elif tileid == bitnum & ~(0x80000000):
        return 0x80000000
    elif tileid == bitnum & ~(0x40000000 | 0x20000000):
        return (0x40000000 | 0x20000000)
    elif tileid == bitnum & ~(0x80000000 | 0x20000000):
        return (0x80000000 | 0x20000000)
    elif tileid == bitnum & ~(0x80000000 | 0x40000000):
         return (0x80000000 | 0x40000000)
    else:
        return (0x80000000 | 0x40000000 | 0x20000000)

return_flags(tile)