import pygame
from random import randint
from inventory import Inventory
from settings import *

pygame.mixer.init()
footstep = pygame.mixer.Sound(file='assets/sound/footstep.mp3')


class Player(pygame.sprite.Sprite):
    def __init__(self, group, pos, obstacleSprites):
        super().__init__(group)
        self.z = layer['main']
        self.weight = 1

        self.obstacleSprites = obstacleSprites
        self.sprite_type = "player"
        self.status = 'down'

        #Dependencias de outras classes
        self.inventory = Inventory()
        self.sleeping = False
        self.hidden = False
        self.attacking = False
        self.canMove = True
        self.carringBox = False


        #Animação
        self.frame_index = 0
        self.animation_speed = 200
        self.normal_animation_speed = self.animation_speed
        self.frame_time = 0
        self.animation_time = 0


        #Atributos
        self.attack_range= 60
        self.attack_speed= 400
        self.speed = 250
        self.normal_speed = self.speed
        self.attack_time = 0

        self.canAttack = True
        self.attackMode = False

        self.direction = pygame.math.Vector2()
        self.import_graphics()
        self.rect = self.image.get_rect(center= pos)
        self.hitbox = self.rect.inflate(-10,-100)
        self.target_pos = self.rect.copy()

        #Sound effects
        self.footStepSound = False



    def update(self, dt):
        self.checkCooldown()
        self.get_target_pos()
        self.seeIfCanMove()
        if self.canMove:
            self.input()
            if self.carringBox:
                self.animation_speed = self.normal_animation_speed + 100
                if self.running:
                    self.speed = self.normal_speed / 1.3
                else:
                    self.speed = self.normal_speed / 2
            else:
                if self.running:
                    self.speed = self.normal_speed * 2
                else:
                    self.speed = self.normal_speed

            self.move(dt)

        else:
            for sprite in self.groups()[0]:
                if sprite != self:
                    if hasattr(sprite, 'interacting'):
                        if sprite.interacting:
                            if not sprite.sprite_type == 'stair_down':
                                if not sprite.sprite_type == 'stair_up':
                                    self.direction.xy = [0, 0]
        self.import_graphics()

        if self.inventory.onDisplay:
            self.inventory.showInventory()

        self.soundEffects()


    def soundEffects(self):
        if not self.direction.magnitude() == 0:
            if not self.footStepSound:
                self.footStepSound = True
                footstep.set_volume(0.2)
                footstep.play(-1)

        else:
            footstep.stop()
            self.footStepSound = False




    def get_target_pos(self):
        screen = pygame.display.get_surface()
        if self.status.split('_')[0] == 'up':
            x = self.hitbox.x
            y = self.hitbox.top - 130
            w = self.rect.width
            h = 100

        elif self.status.split('_')[0] == 'down':
            x = self.hitbox.x
            y = self.hitbox.bottom
            w = self.hitbox.width
            h = 100

        elif self.status.split('_')[0] == 'left':
            x = self.hitbox.x - 40
            y = self.hitbox.y
            w = 40
            h = self.rect.height

        elif self.status.split('_')[0] == "right":
            x = self.hitbox.x + self.rect.width
            y = self.hitbox.y
            w = 40
            h = self.rect.height

        self.target_pos = pygame.rect.Rect(x, y, w, h)




    def import_graphics(self):
        if self.direction.x < 0:
            self.status = 'left'

        elif self.direction.x > 0:
            self.status = 'right'

        if self.direction.y < 0:
            self.status = 'up'

        elif self.direction.y > 0:
            self.status = 'down'

        if self.carringBox:
            self.status = self.status.split('_')[0] + "_box"
        else:
            self.status = self.status.split('_')[0]

        if self.direction.magnitude() != 0:
            self.image = pygame.image.load(f'assets/sprites/prota/{self.status}/{self.frame_index}.png')
        else:
            self.image = pygame.image.load(f'assets/sprites/prota/{self.status}/0.png')





    def seeIfCanMove(self):
        for sprite in self.groups()[0]:
            if hasattr(sprite, 'interacting'):
                if not hasattr(sprite, 'moveWhileInteract'):
                    if sprite.interacting:
                        self.canMove = False

        if self.hidden:
            self.canMove = False



    def input(self):
        key = pygame.key.get_pressed()

        if key[pygame.K_w]:
            self.direction.y = -1

        elif key[pygame.K_s]:
            self.direction.y = 1

        else:
            self.direction.y = 0


        if key[pygame.K_a]:
            self.direction.x = -1

        elif key[pygame.K_d]:
            self.direction.x = 1

        else:
            self.direction.x = 0

        if key[pygame.K_LSHIFT]:
            self.running = True
        else:
            self.running = False


    def checkCooldown(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.frame_time > self.animation_speed:
            self.frame_time = pygame.time.get_ticks()

            if self.frame_index < 3:
                self.frame_index += 1

            else:
                self.frame_index = 0


        if current_time - self.attack_time > self.attack_speed:
            self.canAttack = True





    def move(self, dt):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()



        velocity = round(self.speed * dt)

        self.hitbox.x += self.direction.x * velocity
        self.checkCollision('horizontal')
        self.hitbox.y += self.direction.y * velocity
        self.checkCollision('vertical')
        self.rect.center = self.hitbox.center

        screen = pygame.display.get_surface()





    def attack(self):
        distance = self.get_player_distance_direction()[0]

        if distance < self.weapon_range and self.canAttack:
            self.attack_time = pygame.time.get_ticks()
            self.canAttack = False
            self.action = "attacking"


    def checkCollision(self, direction):
        visibleSprite = self.groups()[0]

        for sprite in visibleSprite.sprites():
            if hasattr(sprite,'isStair'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if not sprite.interacting:
                        if direction == 'vertical':
                            if self.direction.y > 0: #going to bottom
                                self.hitbox.bottom = sprite.hitbox.top

                            if self.direction.y < 0: #going to top
                                self.hitbox.top = sprite.hitbox.bottom

                        if direction == 'horizontal':
                            if self.direction.x > 0: #going to right
                                sprite.interact()

                            if self.direction.x < 0: #going to left
                                sprite.interact()


        for sprite in self.obstacleSprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0: #going to right
                        self.hitbox.right = sprite.hitbox.left

                    if self.direction.x < 0: #going to left
                        self.hitbox.left = sprite.hitbox.right

                if direction == 'vertical':
                    if self.direction.y > 0: #going to bottom
                        self.hitbox.bottom = sprite.hitbox.top

                    if self.direction.y < 0: #going to top
                        self.hitbox.top = sprite.hitbox.bottom










