from csv import reader
from settings import TILE_SIZE
from tile import *

def import_csv_layout(path):
    with open(path) as map:
        layoutMap = []
        level = reader(map, delimiter = ',')
        for row in level:
            layoutMap.append(list(row))
        return layoutMap

def create_tile_group(Map, Type):
    newList = []
    sprite_group = pygame.sprite.Group()

    for row_index, row in enumerate(Map):
        for col_index, val in enumerate(row):
            if val != "-1":
                x = col_index * TILE_SIZE 
                y = row_index * TILE_SIZE

                if Type not in ["Decoration", "Decoration2", "Decoration3"]:
                    sprite_group.add(ClassDict[Type](x, y, level.tileData[val]))
                else:
                    newList.append(ClassDict[Type](x, y, level.tileData[val]))
    if Type in ["Decoration", "Decoration2", "Decoration3"]:
        sprite_group.add(Combined(newList))

    return sprite_group

def area(x1, y1, x2, y2, x3, y3):
   return abs((x1*(y2-y3) + x2*(y3-y1)+ x3*(y1-y2))/2.0)

def inTriangle(x1, y1, x2, y2, x3, y3, x, y):
    Area = area(x1, y1, x2, y2, x3, y3)
    Area1 = area(x, y, x2, y2, x3, y3)
    Area2 = area(x1, y1, x, y, x3, y3)
    Area3 = area(x1, y1, x2, y2, x, y)

    if Area - 3 <= (Area1 + Area2 + Area3) <= Area + 3:
        return True
    return False

def isNegative(val):
    multipier = 1
    if val < 0:
        multipier = -1
    if val == 0:
        multipier = 0
    return multipier

def clamp_val(minimum, maximum, val):
    if val < minimum:
        val = minimum
    elif val > maximum:
        val = maximum
    return val

def save(self):
    with open('./playerData.txt', 'w') as f:
        f.write(str(self.pos[0]) + "\n")
        f.write(str(self.playerHeight) + "\n")
        f.write(str(self.tracker.pos[1] + self.cameraCorrection) + "\n")
        f.write(str(self.pos[1]) + "\n")

        f.close()