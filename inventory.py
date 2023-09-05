import pygame

items = {
    'key_father_room': {
        'name': "Father Room's Key",
        'description': 'A chave do quarto do meu pai.',
    },
    'basement_key': {
        'name': "Basement's Key",
        'description': 'A chave do porão.',
    },
    'mom_letter': {
        'name': "My Mother's letter",
        'description': 'Tem o cheiro dela...',
    }
}

class Inventory:
    def __init__(self):
        self.inventory = {}
        self.click = False
        self.holdingItem = {}

        self.onDisplay = False

    def addItem(self, item):
        if len(self.inventory) == 0:
            self.holdingItem = items[item]
        self.inventory[item] = items[item]



    def showInventory(self):
        screen = pygame.display.get_surface()
        i = 0

        max = len(self.inventory)
        font = pygame.font.SysFont(None, 40)
        small_font = pygame.font.SysFont(None, 20)

        if max > 0:
            for item, item_info in self.inventory.items():
                image = pygame.image.load(f'assets/objects/item/{item}.png')
                image_scale = pygame.transform.scale(image, (50,50))
                image_rect = image_scale.get_rect(topleft= (100, 100 + 50*i))
                screen.blit(image_scale, image_rect)

                if self.holdingItem == item_info:
                    pygame.draw.rect(screen, 'green', image_rect, 5)


                if image_rect.collidepoint(pygame.mouse.get_pos()):
                    description = small_font.render(item_info['description'], True, 'black')
                    d_w = description.get_height()
                    description_rect = description.get_rect(topleft= (150, 100 + image_rect.height/2 - d_w / 2 + 50*i))

                    pygame.draw.rect(screen, "white", description_rect.inflate(10,20))

                    screen.blit(description, description_rect)

                    if self.click:
                        self.holdingItem = items[item]



                i += 1



        else:
            text = font.render('No items', True, 'black')
            text_rect = text.get_rect(topleft= (100, 100))
            screen.blit(text, text_rect)


