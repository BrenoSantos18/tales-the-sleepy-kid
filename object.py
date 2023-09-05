import pygame
from settings import *
from npc import Npc
from inventory import items
from settings import layer



object_description = {
    'clock': ["Está quebrado.", "Ou talvez não. Quem sabe ele não quer me dizer algo?"],
}



class Block(pygame.sprite.Sprite):
    def __init__(self, groups, pos, image = pygame.surface.Surface((32,32)), isPassable = False, z = layer['main']):
        super().__init__(groups)
        self.z = z
        self.sprite_type = 'block'
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)
        if isPassable:
            h = self.rect.height * 3
            self.hitbox = self.rect.inflate(-6, -h/2)
            self.hitY = self.hitbox.y
            self.isPassable= True

class Hide(pygame.sprite.Sprite):
    def __init__(self, groups, pos, image, key, z=layer['overlay']):
        super().__init__(groups)
        self.z = z
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)

        self.key = items[key]
        self.sprite_type = "hide_overlay"

    def update(self, dt):
        self.checkDoor()

    def checkDoor(self):
        for sprite in self.groups()[0]:
            if hasattr(sprite, 'key'):
                if sprite.sprite_type != 'hide_overlay':
                    if sprite.key == self.key:
                        self.door = sprite


class StaticObject(Interactive):
    def __init__(self, groups, pos, image, sprite_type, z=layer['main']):
        super().__init__(groups, pos, image, z)
        self.sprite_type = sprite_type

    def update(self, dt):
        if self.sprite_type == 'clock':
            self.import_graphics()


class Object(Interactive):
    def __init__(self, groups, pos, image, name, hasAnimationTrigger = False, hasText = True, z=layer['main']):
        super().__init__(groups, pos, image, z)

        self.name = name
        self.hasText = hasText

        self.animationTrigger = hasAnimationTrigger
        if self.hasText:
            self.description = object_description[self.name]
        else:
            self.canInteractAgain = True
            self.moveWhileInteract = True

        self.sprite_type = self.name
        self.chat_index = 0

    def update(self, dt):
        self.checkDistanceFromPlayer()


        if not self.hasText:
            if self.interacting:
                self.status = 'interact'
            else:
                self.status = 'idle'
        self.import_graphics()

        if self.hasText:
            self.draw_chat_box()

    def interact(self):
        if not self.interacting:
            self.interacting = True
        else:
            self.interacting = False

    def draw_chat_box(self):
        screen = pygame.display.get_surface()
        w, h = screen.get_size()
        font = pygame.font.SysFont(None, 40)

        max = len(self.description)
        if self.interacting:
            if self.chat_index < max:
                pygame.draw.rect(screen, 'gray', (100, h-250,w-200, 400))
                text = font.render(f"{self.description[self.chat_index]}", True, 'black')
                text_rect = text.get_rect(topleft= (200,h-200))
                screen.blit(text, text_rect)
            else:
                self.chat_index = 0
                self.player.canMove = True
                self.interacting = False


class Item(Interactive):
    def __init__(self, groups, pos, image, name,z=layer['floor']):
        super().__init__(groups, pos, image, z)
        self.name = name
        self.isItem = True
        self.image = pygame.image.load(f'assets/objects/item/{self.name}.png')
        self.rect = self.image.get_rect(topleft = pos)

    def update(self, dt):
        self.checkDistanceFromPlayer()

    def interact(self):
        self.player.inventory.addItem(self.name)
        self.kill()


class MoveableObject(Interactive):
    def __init__(self, groups, pos, image,z=layer['main']):
        super().__init__(groups, pos, image, z)
        self.beingHold = False
        self.hidden = False
        self.colided = False
        self.weight = 2
        self.canPressureButton = True
        self.moveWhileInteract = True
        self.obstacleSprite = self.groups()[1]

    def update(self, dt):
        self.checkDistanceFromPlayer()
        if self.beingHold:
            if self.player.status.split('_')[0] == 'down':
                self.hitbox.midtop = self.player.target_pos.center
            if self.player.status.split('_')[0] == 'up':
                self.hitbox.midbottom = self.player.target_pos.center
            if self.player.status.split('_')[0] == 'left':
                self.hitbox.bottomright = self.player.target_pos.midbottom
                self.hitbox.y -= 50
            if self.player.status.split('_')[0] == 'right':
                self.hitbox.bottomleft = self.player.target_pos.midbottom
                self.hitbox.y -= 50
            self.rect.center = self.hitbox.center



    def interact(self):
        if not self.beingHold:
            if not self.player.carringBox:
                self.beingHold = True
                self.hidden = True
                self.obstacleSprite.remove(self)
                self.player.carringBox = True
                self.interacting = True
        else:
            for sprite in self.obstacleSprite.sprites():
                if sprite.rect.colliderect(self.hitbox):
                    self.colided = True
            if not self.colided:
                self.beingHold = False
                self.interacting = False
                self.hidden = False
                self.obstacleSprite.add(self)
                self.player.carringBox = False
            self.colided = False



class PressurePlate(Interactive):
    def __init__(self, groups, pos, image, action, weight = 1, z = layer['onFloor']):
        super().__init__(groups, pos, image, z)
        self.weight_needed = weight
        self.visibleSprite = self.groups()[0]
        self.canChangeMap = True
        self.action = action
        self.sprite_type = 'button'
        self.playSound = False
        self.moveWhileInteract = True
        self.canInteractAgain = True

        self.sound = pygame.mixer.Sound('assets/sound/button.mp3')

    def update(self,dt):
        check = False
        for sprite in self.visibleSprite:
            if hasattr(sprite,'canPressureButton') or sprite == self.player:
                if sprite.hitbox.colliderect(self.hitbox):
                    if not sprite.hidden:
                        if sprite.weight >= self.weight_needed:
                            if self.playSound:
                                self.playSound = False
                                self.sound.play(0)
                            check = True

        if check:
            self.status = 'interact'
            self.interacting = True
        else:
            self.playSound = True
            self.status = 'idle'
            self.interacting = False

        self.import_graphics()


    def makeAction(self, level = None):
        if self.action == 'wake':
            self.transition('house', level, False, (320, 170))


class Stair(Interactive):
    def __init__(self, groups, pos, image, place, z=layer['main']):
        super().__init__(groups, pos, image, z)

        if place == 'home_base':
            self.playerPos = (1353,1416)
            self.sprite_type = 'stair_down'

        if place == 'home_top':
            self.playerPos = (1425,1035)
            self.sprite_type = 'stair_up'

        self.isStair = True

        self.player_status = 'left'


        self.canChangeMap = True
        self.mapToRender = place


    def update(self, dt):
        if self.interacting:
            self.player.hitbox.x += 1
            if self.sprite_type == "stair_up":
                self.player.hitbox.y -= 1
            else:
                self.player.hitbox.y += 1
            self.player.direction.y = 0
            self.player.direction.x = 1
            self.player.rect.center = self.player.hitbox.center

    def interact(self):
        if not self.interacting:
            self.interacting = True
            self.groups()[0].transitionTime = 5
            self.transition()

        else:
            self.player.canMove = True




class Bed(Interactive):
    def __init__(self, groups, pos, image,z=layer['main']):
        super().__init__(groups, pos, image, z)

        self.canChangeMap = True
        self.sprite_type = 'bed'
        self.status = 'idle'
        self.canSleep = False
        self.has_scene = True
        self.hasTransition = True
        self.wakingUp = False

    def update(self, dt):
        self.checkDistanceFromPlayer()

        self.import_graphics()

        if self.interacting:
            self.canInteract = False

        self.textBox("can't sleep")

    def interact(self):
        if self.canSleep:
            self.interacting = True
            self.status = 'sleeping'
            self.canSleep = False
            self.player.hidden = True
            self.player.sleeping = True
            self.wakingUp = True
            self.transition()

            self.player_status = self.player.status.split("_")[0]

            if self.canChangeMap:
                self.mapToRender = 'box_puzzle'

        else:
            if not self.wakingUp:
                self.displayingWarning = True
            else:
                self.wakingUp = False
                self.interacting = False
                self.status = "idle"
                self.canSleep = True
                self.player.hidden = False
                self.player.sleeping = False
                self.player.canMove = True


class Chair(Interactive):
    def __init__(self, groups, pos, image, sprite_type, z=layer['main']):
        super().__init__(groups, pos, image, z)

        self.sprite_type = sprite_type

    def update(self, dt):
        self.checkDistanceFromPlayer()

        self.import_graphics()

        if self.interacting:
            self.canInteract = True

    def interact(self):
        if self.interacting:
            self.interacting = False
            self.player.hidden = False
            self.player.canMove = True
            self.status = "idle"

        else:
            self.status = 'sitting'
            self.interacting = True
            self.player.hidden = True



class Chest(Interactive):
    def __init__(self, groups, pos, size,z = layer['main']):
        super().__init__(groups, pos, size,z)

        self.sprite_type = 'chest'
        self.open = False
        self.click = False

    def update(self, dt):
        self.checkDistanceFromPlayer()
        self.drawChest()

    def interact(self):
        if not self.open:
            self.open = True


    def drawChest(self):
        if self.open:
            surface = pygame.display.get_surface()
            h, w = surface.get_size()
            bg = pygame.draw.rect(self.surface, 'brown', (h/4, w/4, h/2, w/2))

            x = bg.x + bg.width
            y = bg. y

            close_button = pygame.draw.circle(self.surface, 'black', (x, y), 30)

            if close_button.collidepoint(pygame.mouse.get_pos()) and self.click:
                self.open = False
                self.player.canMove = True



class Wardrobe(Interactive):
    def __init__(self, groups, pos, image,z = layer['main']):
        super().__init__(groups, pos, image,z)
        self.sprite_type = 'wardrobe'
        self.status = 'idle'


    def update(self, dt):
        self.checkDistanceFromPlayer()
        self.import_graphics()



    def interact(self):
        if self.player.hidden:
            self.status = 'idle'
            self.interacting = False
            self.player.hidden = False
            self.player.canMove = True
        else:
            self.status = 'hidden'
            self.interacting = True
            self.player.hidden = True


class Door(Interactive):
    def __init__(self, groups, pos, image, direction, key = None,z = layer['main']):
        super().__init__(groups, pos, image,z)
        self.direction = direction
        self.open = False
        self.sprite_type = 'door'
        pygame.mixer.init()
        self.doorSound = pygame.mixer.Sound('assets/sound/door.mp3')
        self.unlockDoorSound = pygame.mixer.Sound('assets/sound/unlock_door.mp3')


        if key != None:
            if key != 'locked':
                self.key = items[key]
            self.locked = True
        else:
            self.locked = False

        self.status = 'closed'


        self.canCollide = self.groups()[1]

    def update(self,dt):
        self.checkDistanceFromPlayer()

        self.import_graphics()

        self.textBox('door_locked')

    def interact(self):
        if not self.open:
            if self.locked:
                if len(self.player.inventory.holdingItem) != 0:
                    if self.player.inventory.holdingItem['name'] == self.key['name']:
                        for sprite in self.groups()[0]:
                            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'hide_overlay':
                                if sprite.key == self.key:
                                    sprite.kill()

                        self.status = 'open'
                        self.locked = False
                        self.open = True
                        self.canCollide.remove(self)
                        self.unlockDoorSound.play(0)

                    else:
                        self.displayingWarning = True
                else:
                    self.displayingWarning = True

            else:
                self.doorSound.play(0)
                self.status = 'open'
                self.open = True
                self.canCollide.remove(self)
        else:
            self.doorSound.play(0)
            self.status = 'closed'
            self.open = False
            self.canCollide.add(self)

    def import_graphics(self):
        self.frame_max = 0

        bottomright = self.rect.bottomright
        top = self.rect.topright

        image = pygame.image.load('assets/objects/map/door_v_open.png')
        image_scale = pygame.transform.scale(image, (self.scalex, self.scaley))
        h = image.get_height()
        image_rect = image_scale.get_rect(bottomright=bottomright)
        hitbox = image_rect.inflate(-6, -h/2)

        self.image = pygame.image.load(f'assets/objects/map/{self.sprite_type}_{self.direction}_{self.status}.png')

        if self.direction == 'h':
            if self.status == 'open':
                self.image = pygame.transform.scale(self.image, (self.scalex, self.scaley + self.scaley/2.5))
            else:
                self.image = pygame.transform.scale(self.image, (self.scalex, self.scaley))

            self.rect = self.image.get_rect(bottomright = bottomright)

        else:
            if self.status == 'closed':
                self.image = pygame.transform.scale(self.image, (self.scalex, self.scaley + self.scaley/2.5))

            else:
                self.image = pygame.transform.scale(self.image, (self.scalex, self.scaley))

            self.rect = self.image.get_rect(topright = top)


        self.hitbox = hitbox





class Phone(Interactive):
    def __init__(self, groups, pos, image, z=layer['main']):
        super().__init__(groups, pos, image, z)
        self.click = False
        self.diskNumber = []
        self.lastCalledNumber = []
        self.actualMenu = 'phone'
        self.displayWarning = False

    def update(self, dt):
        self.checkDistanceFromPlayer()

        if self.interacting and not self.displayingWarning:
            if self.actualMenu == 'phone':
                self.phoneMenu()
            elif self.actualMenu == 'list':
                self.listLastCalled()

        self.textBox('wrong_number')

    def interact(self):
        self.interacting = True

    def phoneMenu(self):
        screen = pygame.display.get_surface()
        w, h = screen.get_size()
        x, y = [w/4, h/4]

        font = pygame.font.SysFont(None, 60)
        numbers = [1,2,3,4,5,6,7,8,9,'DEL',0, 'CALL']

        main_bg = pygame.draw.rect(screen, 'black', (x, y, w/2, h/2))
        diskedBg = pygame.draw.rect(screen, 'black', (x, y -100, w/2, 100))

        close = pygame.draw.circle(screen, 'red', (x+w/2, y-100), 30)


        lastCalledText = font.render('Histórico', True, 'black')
        lastCalledTextW = lastCalledText.get_width()
        lastCalledTextRect = lastCalledText.get_rect(topleft = (x + w/2 - lastCalledTextW , y))

        lastCalled = pygame.draw.rect(screen, 'white', (x+w/2 - lastCalledTextW, y, lastCalledTextW, 50))
        screen.blit(lastCalledText, lastCalledTextRect)

        h_dir = 0
        v_dir = 0

        i = 0

        for number in self.diskNumber:
            diskedNumber = font.render(f'{number}', True, 'white')
            disk_w = diskedNumber.get_width()
            diskedNumber_rect = diskedNumber.get_rect(topleft = (x + 5 +disk_w * i, y - 100))
            screen.blit(diskedNumber, diskedNumber_rect)

            i += 1

        for number in numbers:
            text = font.render(f'{number}', True, 'black')
            centralx, centraly = [text.get_width(), text.get_height()]

            xPos, yPos = [x + 90*h_dir,y+ 90*v_dir]
            text_rect = text.get_rect(topleft = (xPos + 40 -centralx/2, yPos + 40-centraly/2))
            box = pygame.draw.rect(screen, 'white', (xPos,yPos, 80, 80))
            screen.blit(text, text_rect)
            h_dir += 1
            if h_dir == 3:
                v_dir += 1
                h_dir = 0

            if box.collidepoint(pygame.mouse.get_pos()) and self.click:
                self.click = False
                if isinstance(number, int):
                    if len(self.diskNumber) < 9:
                        self.diskNumber.append(number)

                elif number == 'CALL':
                    max_number = ''
                    for number in self.diskNumber:
                        max_number = max_number + str(number)

                    value = number_list.get(max_number)

                    if value:
                        self.lastCalledNumber.append(self.diskNumber)
                    else:
                        self.displayingWarning = True

                    self.diskNumber = []

                elif number == 'DEL':
                    self.diskNumber = []

        if close.collidepoint(pygame.mouse.get_pos()) and self.click:
            self.diskNumber = []
            self.interacting = False
            self.player.canMove = True


        if lastCalled.collidepoint(pygame.mouse.get_pos()) and self.click:
            self.actualMenu = 'list'

    def listLastCalled(self):
        screen = pygame.display.get_surface()
        w, h = screen.get_size()
        x, y = [w/4, h/4]
        font = pygame.font.SysFont(None, 60)
        minorFont = pygame.font.SysFont(None, 30)

        main_bg = pygame.draw.rect(screen, 'black', (x, y, w/2, h/2))
        close = pygame.draw.circle(screen, 'red', (x+w/2, y-100), 30)

        i_h = 0
        i_v = 0
        for calls in self.lastCalledNumber:
            max_number = ''
            for number in calls:
                max_number = max_number + str(number)

            diskedContact = font.render(f'{number_list[max_number]}', True, 'white')
            diskContact_w = diskedContact.get_width()
            diskedContact_rect = diskedContact.get_rect(topleft = (x + 5 +diskContact_w * i_h, y + 45 *i_v))
            screen.blit(diskedContact, diskedContact_rect)

            i_v += 1

            for number in calls:
                diskedNumber = minorFont.render(f'{number}', True, 'white')
                disk_w = diskedNumber.get_width()
                diskedNumber_rect = diskedNumber.get_rect(topleft = (x + 5 +disk_w * i_h, y + 45 *i_v))
                screen.blit(diskedNumber, diskedNumber_rect)
                i_h += 1
            i_h = 0
            i_v += 1

        if close.collidepoint(pygame.mouse.get_pos()) and self.click:
            self.diskNumber = []
            self.actualMenu = 'phone'
            self.interacting = False
            self.player.canMove = True









