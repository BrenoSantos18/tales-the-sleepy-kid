import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.sprite_type = 'enemy'
        self.image = pygame.surface.Surface((80,80))
        self.rect = self.image.get_rect(topleft = (700,200))
        self.direction = pygame.math.Vector2()
        self.speed = 100
        self.toggled = False

    def update(self, dt):
        for sprite in self.groups()[0]:
            if hasattr(sprite, "sprite_type") and sprite.sprite_type == "player":
                self.move(sprite, dt)

                if self.toggled:
                    sprite.attackMode = True
                    sprite.walk_range = sprite.weapon_range

                else:
                    sprite.attackMode = False
                    sprite.walk_range = 0

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()

        if distance < 400 and distance > 80:
            direction = (player_vec - enemy_vec).normalize()

        else:
            direction = pygame.math.Vector2()


        return(distance, direction)


    def move(self, player, dt):
        self.direction = self.get_player_distance_direction(player)[1]

        if self.direction.x < 0:
            self.direction.x = -1

        elif self.direction.x > 0:
            self.direction.x = 1
        else:
            self.direction.x = 0

        if self.direction.y < 0:
            self.direction.y = -1

        elif self.direction.y > 0:
            self.direction.y = 1
        else:
            self.direction.y = 0


        velocity = round(self.speed * dt)

        self.rect.x += self.direction.x * velocity
        self.rect.y += self.direction.y * velocity
