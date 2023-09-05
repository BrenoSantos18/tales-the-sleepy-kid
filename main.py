

import pygame
from player import Player
from level import Level
from camera import CameraGroup
import time
from settings import *

screen = pygame.display.set_mode((1200,700), pygame.RESIZABLE)
visibleSprites = CameraGroup()
collideSprites = pygame.sprite.Group()



class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.interactSound = pygame.mixer.Sound('assets/sound/sound2.wav')
        self.dialogueSound = pygame.mixer.Sound('assets/sound/sound4.wav')
        self.interactSound.set_volume(0.2)
        self.dialogueSound.set_volume(0.2)

        self.player = Player(visibleSprites, (400, 400), collideSprites)
        self.level = Level([visibleSprites, collideSprites], self.player)
        self.debugging = False
        self.displayingText = False
        self.chat_index = 0

    def run(self):
        current_time = time.time()
        self.level.render()

        while True:
            dt = time.time() - current_time
            current_time = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F3:
                        if self.debugging:
                            self.debugging = False
                        else:
                            self.debugging = True

                    if event.key == pygame.K_TAB:
                        if self.player.inventory.onDisplay:
                            self.player.inventory.onDisplay = False
                        else:
                            self.player.inventory.onDisplay = True


                # Aqui estão os input das classes

                for sprite in visibleSprites.sprites():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            if hasattr(sprite, 'chat_index'):
                                if hasattr(sprite, 'displayingWarning') and sprite.displayingWarning:
                                    self.dialogueSound.play(0)
                                    sprite.chat_index += 1
                                elif sprite.interacting:
                                    self.dialogueSound.play(0)
                                    sprite.chat_index += 1

                        if event.key == pygame.K_e:
                            if hasattr(sprite, 'canInteract'):
                                if sprite.canInteract:
                                    if not sprite.interacting:
                                        if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'door':
                                            pass
                                        else:
                                            self.interactSound.play(0)
                                    sprite.interact()

                    if hasattr(sprite, 'click') or sprite == self.player:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                if sprite == self.player:
                                    if self.player.inventory.onDisplay:
                                        sprite.inventory.click = True
                                else:
                                    sprite.click = True
                        if event.type == pygame.MOUSEBUTTONUP:
                            if event.button == 1:
                                if sprite == self.player:
                                    sprite.inventory.click = False
                                else:
                                    sprite.click = False

            screen.fill((20,20,20))
            visibleSprites.custom_draw(self.player, self.debugging)
            visibleSprites.update(dt)
            self.level.update()

            size = screen.get_size()
            black = pygame.surface.Surface(size)
            black_rect = black.get_rect(topleft = (0,0))

            if visibleSprites.fade:
                visibleSprites.alpha += visibleSprites.transitionTime
                if visibleSprites.alpha > 255:
                    for sprite in visibleSprites.sprites():
                        if hasattr(sprite, "interacting") and sprite.interacting:
                            sprite.interact()

                            if hasattr(sprite,'canChangeMap') and sprite.canChangeMap:
                                self.level.changeMap(sprite.mapToRender)
                                sprite.interacting = False

                    visibleSprites.fade = False
            else:
                visibleSprites.alpha -= 2
                if visibleSprites.alpha < 0:
                    visibleSprites.alpha = 0

            black.set_alpha(visibleSprites.alpha)
            screen.blit(black, black_rect)

            if self.debugging:
                self.debug('Dt', dt, 0)
                self.debug('Pos x', self.player.rect.x, 1)
                self.debug('Pos y', self.player.rect.y, 2)
                self.debug('Direction', self.player.direction, 3)
                self.debug('Is hidden', self.player.hidden, 4)
                self.debug('Speed', self.player.speed, 5)
                self.debug('Holding', self.player.inventory.holdingItem, 6)

            pygame.display.update()

    def debug(self, title, text, line):
        font = pygame.font.SysFont(None, 20)
        text = font.render(f'{title}: {text}', True, 'white')
        text_bg = text.get_rect(topleft= (0,0*line + line*20))
        screen.blit(text, text_bg)


if __name__ == "__main__":
    game = Game()
    game.run()



