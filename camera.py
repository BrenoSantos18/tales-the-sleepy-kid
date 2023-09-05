import pygame
from settings import *

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

        self.offset = pygame.math.Vector2()
        self.layers = layer

        self.fade = False
        self.alpha = 0
        self.transitionTime = 5


    def custom_draw(self, player, debugging):
        screen = pygame.display.get_surface()
        w, h = screen.get_size()

        self.offset.x = player.rect.centerx - w /2
        self.offset.y = player.rect.centery - h /2


        for layer in self.layers.values():
            for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
                if sprite.z == layer:

                    offset_rect = sprite.rect.copy()

                    offset_rect.center -= self.offset

                    if hasattr(sprite, 'hidden'):
                        if not sprite.hidden:
                            screen.blit(sprite.image, offset_rect)
                    else:
                        screen.blit(sprite.image, offset_rect)

                    if debugging:
                        pygame.draw.rect(screen,'red',offset_rect,5)
                        hitbox_rect = sprite.hitbox.copy()
                        hitbox_rect.center = offset_rect.center
                        pygame.draw.rect(screen,'green',hitbox_rect, 5)


