import pygame
from pygame.sprite import AbstractGroup
from os import walk, path
import pygame
from settings import *

def import_folder(path):
    surface_list = []

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
    return surface_list

def get_size(start_path = '.'):
    i = 0
    for dirpath, dirnames, filenames in walk(start_path):
        for f in filenames:
            i += 1

    i -= 1

    return i

number_list = {
    '190':'Emergência'
}

layer = {
    'floor': 0,
    'wall': 1,
    'onFloor': 2,
    'main': 3,
    'overlay': 4
}


map_layers = {
    'home_top': ['floor', 'topwall', 'passable', 'spawn', 'wall', 'hiding-key_father_room','npc','furniture','items'],
    'home_base': ['floor', 'topwall', 'hiding-basement_key', 'spawn', 'wall','furniture'],
    'box_puzzle': ['floor', 'wall', 'topwall', 'spawn', 'furniture']
}

def get_player_distance(player, target):
    target_vec = pygame.math.Vector2(target.rect.center)
    player_vec = pygame.math.Vector2(player.rect.center)
    distance = (target_vec - player_vec).magnitude()

    return distance


class Interactive(pygame.sprite.Sprite):
    def __init__(self, groups, pos, image, z = layer['main']):
        super().__init__(groups)
        self.z = z
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-6, -23)
        self.status = 'idle'
        self.sprite_type = ''
        self.pos = list(pos)
        self.pos[0] *= 3
        self.pos[1] *= 3
        self.pos = tuple(self.pos)
        self.canInteractAgain = False


        self.frame_index = 0
        self.animation_speed = 2000
        self.animate_time = 0
        self.animationTrigger = False

        self.displayingWarning = False
        self.chat_index = 0

        for sprite in self.groups()[0]:
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == "player":
                self.player = sprite

        self.canInteract = False
        self.interacting = False

    def import_graphics(self):

        if self.animationTrigger:
            path = f'assets/objects/map/{self.sprite_type}'
            self.frame_max = get_size(path)
        else:
            self.frame_max = 0

        self.checkCooldown()


        if self.animationTrigger:
            self.image = pygame.image.load(f'assets/objects/map/{self.sprite_type}/{self.frame_index}.png')
            self.image = pygame.transform.scale(self.image, (self.scalex, self.scaley))
            self.rect = self.image.get_rect(topleft = self.pos)
            self.hitbox.center = self.rect.center

        else:
            self.image = pygame.image.load(f'assets/objects/map/{self.sprite_type}_{self.status}.png')
            self.image = pygame.transform.scale(self.image, (self.scalex, self.scaley))
            self.rect = self.image.get_rect(topleft = self.pos)
            self.hitbox.center = self.rect.center

    def checkCooldown(self):
        current_time = pygame.time.get_ticks()

        if self.frame_max != 0:
            if current_time - self.animate_time > self.animation_speed:
                self.animate_time = pygame.time.get_ticks()
                if self.frame_index == self.frame_max:
                    if self.sprite_type == 'door' and self.animationTrigger:
                        self.animationTrigger = False

                    self.frame_index = 0
                else:
                    self.frame_index += 1

    def checkDistanceFromPlayer(self):
        screen = pygame.display.get_surface()
        screen_w, screen_h = screen.get_size()
        font = pygame.font.SysFont(None, 80)

        check = True
        if self.hitbox.colliderect(self.player.target_pos):
            if not self.hitbox.colliderect(self.player.hitbox) or hasattr(self, 'isItem'):
                for sprite in self.groups()[0]:
                    if hasattr(sprite, 'canInteract'):
                        if sprite != self:
                            if sprite.canInteract or sprite.interacting:
                                if hasattr(sprite, 'canInteractAgain'):
                                    if not sprite.canInteractAgain:
                                        check = False
                                else:
                                    check = False


                if check:
                    if not self.interacting:
                        text = font.render("Interact", True, 'white')
                        h = text.get_height()
                        w = text.get_width()

                        text_rect = text.get_rect(topleft = (screen_w - w - 30, screen_h - h - 20))
                        screen.blit(text, text_rect)
                    self.canInteract = True

                else:
                    self.canInteract = False

            else:
                self.canInteract = False

        else:
            self.canInteract = False

    def transition(self, map = None, interact = False, level = None, playerpos = (0,0)):
        group = self.groups()[0]
        group.fade = True

    def textBox(self,context):
        screen = pygame.display.get_surface()

        w, h = screen.get_size()
        font = pygame.font.SysFont(None, 40)

        amount_of_text = len(context_text[context])

        if self.displayingWarning:

            if self.chat_index < amount_of_text:
                text = context_text[context]
                i = 0

                if isinstance(text,list):
                    pygame.draw.rect(screen, 'gray', (100, h-250,w-200, 400))
                    for inside_text in text:
                        text = font.render(f"{inside_text}", True, 'black')
                        text_rect = text.get_rect(topleft= (200,h-200 + i * 40))
                        screen.blit(text, text_rect)
                        i += 1

                else:
                    pygame.draw.rect(screen, 'gray', (100, h-250,w-200, 400))
                    text = font.render(f"{text}", True, 'black')
                    text_rect = text.get_rect(topleft= (200,h-200))
                    screen.blit(text, text_rect)

            else:
                self.chat_index = 0
                self.player.canMove = True
                self.displayingWarning = False








context_text = {
    "door_locked": ['Está trancada.'],
    "wrong_number": ["Eu não reconheço este número."],
    "can't sleep": ['Não posso dormir ainda.']
}


