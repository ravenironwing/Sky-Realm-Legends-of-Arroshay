import random
import pygame as pg
from settings import MAX_RECURSIONS

vec = pg.math.Vector2
pg.init()

class TilePath():
    def __init__(self, ai, pos = False, gCost = 0, prevTile = None):
        if not pos:
            self.pos = vec(ai.tile_pos)
        else:
            self.pos = pos
        self.map_walls = ai.game.map.walls
        self.ai = ai
        self.gCost = gCost
        self.findHCost()
        self.prevTile = prevTile
        self.closed = False
        self.ai.tile_paths.append(self)
        self.ai_posisions = []
        for ai in self.ai.game.ais:
            self.ai_posisions.append(ai.tile_pos)

    def getTile(self, pos):
        if 0 <= pos[0] < self.ai.game.map.tiles_wide and 0 <= pos[1] < self.ai.game.map.tiles_high:
            return self.map_walls[int(pos[1])][int(pos[0])]
    def findFCost(self):
        self.fCost = self.hCost + self.gCost
    def findHCost(self):
        target = self.ai.target_tile_pos
        self.hCost = int((target-self.pos).magnitude()*10)
        self.findFCost()
    def follow(self, tile): # Retracing steps to find finishing path
        self.ai.found_path.append(self)
        if self.prevTile == None:
            self.ai.temp_target = tile.pos
            self.ai.target_timer = pg.time.get_ticks()
        else:
            self.prevTile.follow(self)
    def close(self):
        self.ai.recursions += 1
        if self.ai.recursions > MAX_RECURSIONS:
            return
        self.closed = True
        self.ai.tile_paths.remove(self)
        for x in range(3):
            for y in range(3):
                pos = self.pos + vec([x-1, y-1])
                tile = self.getTile(pos)
                if pos == self.ai.target_tile_pos:
                    self.follow(self)
                    return
                path = self.ai.getPath(pos)
                if tile or (path is not None and path.closed) or (pos in self.ai_posisions):
                    continue
                dst = 10
                if not (x-1 == 0 or y-1 == 0):
                    dst = 14
                gCost = self.gCost + dst
                if path is not None:
                    if path.gCost > gCost:
                        path.gCost = gCost
                        path.findFCost()
                        path.prevTile = self
                else:
                    TilePath(self.ai, pos, gCost, self)

        lowestCost = self.ai.tile_paths[0]
        for i in self.ai.tile_paths:
            if i.fCost < lowestCost.fCost or (i.fCost == lowestCost.fCost and i.hCost < lowestCost.hCost):
                lowestCost = i
        lowestCost.close()

