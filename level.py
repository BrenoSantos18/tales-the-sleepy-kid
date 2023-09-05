import pygame
from pytmx.util_pygame import load_pygame
from object import *
from npc import Npc
from settings import *
from challenges import Room


class Level:
    def __init__(self, groups, player):
        self.visibleSprites = groups[0]
        self.obstacleSprites = groups[1]
        self.map = 'home_top'
        self.player = player
        self.puzzles = Room()
        self.day = 0

    def render(self):
        tileSize = 32
        variables = []

        tmx_data = load_pygame(f'assets/tile/map/{self.map}.tmx')

        for map_layer in map_layers[self.map]:
            if map_layer == 'floor':
                for x, y, surface in tmx_data.get_layer_by_name('floor').tiles():
                    Block(self.visibleSprites, (x*tileSize, y * tileSize), surface, False, layer['floor'])

            if map_layer == 'topwall':
                for x, y, surface in tmx_data.get_layer_by_name('topwall').tiles():
                    Block([self.visibleSprites, self.obstacleSprites], (x*tileSize, y * tileSize), surface)

            if map_layer == 'passable':
                for x, y, surface in tmx_data.get_layer_by_name('passable').tiles():
                    Block([self.visibleSprites, self.obstacleSprites], (x*tileSize, y * tileSize), surface, True)

            if map_layer == 'wall':
                for x, y, surface in tmx_data.get_layer_by_name('wall').tiles():
                    Block([self.visibleSprites, self.obstacleSprites], (x*tileSize, y * tileSize), surface, False, layer['wall'])

            if map_layer == 'furniture':
                for obj in tmx_data.get_layer_by_name('furniture'):
                    if hasattr(obj, 'type') and obj.type == 'interactive':
                        Object([self.visibleSprites, self.obstacleSprites], (obj.x, obj.y), obj.image, obj.name, False, False)

                    elif obj.name == 'button':
                        button = PressurePlate(self.visibleSprites, (obj.x, obj.y), obj.image, None)
                        if self.map == 'box_puzzle':
                            variables.append(button)

                    elif obj.name == 'phone':
                        Phone([self.visibleSprites, self.obstacleSprites], (obj.x, obj.y), obj.image)

                    elif obj.name == 'box':
                        MoveableObject([self.visibleSprites, self.obstacleSprites], (obj.x, obj.y), obj.image)
                    elif obj.name == 'bed':
                        Bed([self.visibleSprites, self.obstacleSprites], (obj.x, obj.y), obj.image)

                    elif obj.name == 'stair':
                        Stair(self.visibleSprites, (obj.x, obj.y), obj.image, obj.type,layer['onFloor'])

                    elif obj.name == 'wardrobe':
                        Wardrobe([self.visibleSprites, self.obstacleSprites], (obj.x, obj.y), obj.image)

                    elif obj.name.split('_')[0] == 'door':
                        if hasattr(obj, 'type'):
                            door = Door([self.visibleSprites, self.obstacleSprites], (obj.x, obj.y), obj.image, obj.name.split("_")[1], obj.type)
                            if self.map == 'box_puzzle':
                                variables.append(door)

                        else:
                            Door([self.visibleSprites, self.obstacleSprites], (obj.x, obj.y), obj.image, obj.name.split("_")[1])

                    elif obj.name == 'chair_l' or obj.name == 'chair_r':
                        Chair([self.visibleSprites, self.obstacleSprites], (obj.x, obj.y), obj.image, obj.name)

                    elif obj.name == 'clock':
                        Object(self.visibleSprites, (obj.x, obj.y), obj.image, obj.name, True)

                    elif obj.name == 'floor':
                        StaticObject(self.visibleSprites, (obj.x, obj.y), obj.image, obj.name, layer['onFloor'])
                    else:
                        StaticObject([self.visibleSprites, self.obstacleSprites], (obj.x, obj.y), obj.image, obj.name)

            if map_layer == 'items':
                for obj in tmx_data.get_layer_by_name('items'):
                    Item(self.visibleSprites, (obj.x, obj.y), obj.image, obj.name)

            if map_layer == 'npc':
                for obj in tmx_data.get_layer_by_name('npc'):
                    Npc([self.visibleSprites, self.obstacleSprites], obj.name, (obj.x, obj.y))

            if map_layer == 'spawn':
                for obj in tmx_data.get_layer_by_name('spawn'):
                    self.player.hitbox.x = obj.x *3
                    self.player.hitbox.y = obj.y *3
                    self.player.rect.center = self.player.hitbox.center
                    self.player.status = obj.name


            if map_layer.split('-')[0] == 'hiding':
                for x, y, surface in tmx_data.get_layer_by_name(map_layer).tiles():
                    Hide(self.visibleSprites, (x*tileSize, y * tileSize), surface, map_layer.split('-')[1] )


        for sprite in self.visibleSprites.sprites():
            if sprite != self.player:
                w, h = sprite.image.get_size()
                x, y = sprite.rect.topleft
                new = pygame.transform.scale(sprite.image, (w*3, h*3))
                if sprite.sprite_type == "clock":
                    sprite.scalex = w * 2
                    sprite.scaley = h * 2
                else:
                    sprite.scalex = w * 3
                    sprite.scaley = h * 3

                new_rect = new.get_rect(topleft = (x*3, y*3))
                if hasattr(sprite,'isStair'):
                    new_hitbox = new_rect.inflate(-31 *3, -20 *3)

                elif hasattr(sprite, 'isPassable'):
                    h *= 3
                    new_hitbox = new_rect.inflate(-6, -h/2)

                elif sprite.sprite_type == 'shower':
                    h *= 3
                    w *= 3
                    new_hitbox = new_rect.inflate(-w/1.5, -h/2)
                else:
                    new_hitbox = new_rect.inflate(-6, -h/2)

                if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'npc':
                    sprite.rect.x = sprite.rect.x *3 - sprite.rect.width
                    sprite.rect.y = sprite.rect.y *3 - sprite.rect.height

                    sprite.hitbox.center = sprite.rect.center

                else:
                    sprite.image = new
                    sprite.rect = new_rect
                    sprite.hitbox = new_hitbox

        if self.map == 'box_puzzle':
            self.puzzles.get_variable(variables)
            self.day += 1



    def update(self):
        if self.day == 1:
            self.puzzles.handleLevel_1()





    def changeMap(self, new_map):
        for sprites in self.visibleSprites.sprites():
            if sprites != self.player:
                sprites.kill()

        self.map = new_map

        self.render()



