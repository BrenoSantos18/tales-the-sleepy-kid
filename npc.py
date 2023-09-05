import pygame
from settings import *

npc_talk = {
    'Sombra': {
        0: ["Ei!", "Bom te ver por aqui.", "Espero que tudo esteja ocorrendo bem.", "pular texto"],
        1: ["Eu não teho nada para te falar."],
        2: ["Ele te mandou ir dormir, é?", ["Bom.. acho que já está bem tarde.", "Não é mais hora de criança estar acordada. Aliás..."], "Essa é a hora que os monstros acordam, não é?", 'pular texto', {'give_item': 'mom_letter'}],
        3: ["Leia com atenção"]

    },
    'Pai': {
        0: ["Não está com sono, filho?", "Já está bem tarde, vai para a cama.", "Amanhã é um novo dia.","pular texto", {
            'change_npc_talk': ['Sombra', 2],
            'bed': True
            }],
        1: ["Já falei para você ir dormir, rapaz."]
    },
    'Marvin': {
        0: ["Está tento pesadelos de novo, garoto chorão?", "Está tudo bem. Eu te protegerei deles.", "Você já leu a carta?", "....O quê? Você não sabe do que eu estou falando?", "Pergunte ao Sombra. Ele deveria ter te entregado.", "Já é a hora de você ler ela."]
    }
}


class Npc(pygame.sprite.Sprite):
    def __init__(self, groups, name, pos, z=layer['main']):
        super().__init__(groups)
        self.z = z
        self.npc_name = name
        self.sprite_type = 'npc'
        self.status = 'down'
        self.import_graphics()
        self.rect = self.image.get_rect(topleft= pos)
        self.hitbox = self.rect.inflate(-6, -120)


        for sprite in self.groups()[0]:
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == "player":
                self.player = sprite

        self.interacting = False
        self.talk_index = 0
        self.chat_index = 0

        self.talk_list = npc_talk[self.npc_name]

    def import_graphics(self):
        if self.npc_name == 'Pai':
            self.image = pygame.image.load(f'assets/sprites/{self.npc_name.lower()}/{self.status}.png')
        else:
            self.image = pygame.image.load(f'assets/sprites/{self.npc_name.lower()}/down.png')


    def update(self, dt):
        screen = pygame.display.get_surface()
        screen_w, screen_h = screen.get_size()
        font = pygame.font.SysFont(None, 80)

        if self.rect.colliderect(self.player.target_pos):
            if not self.interacting:
                text = font.render("Interact", True, 'white')
                h = text.get_height()
                w = text.get_width()

                text_rect = text.get_rect(topleft = (screen_w - w - 30, screen_h - h - 20))
                screen.blit(text, text_rect)
            self.canInteract = True

        else:
            self.canInteract = False

        self.chat()
        self.get_status()
        self.import_graphics()

    def interact(self):
        if not self.interacting:
            self.interacting = True

    def get_status(self):
        status = self.player.status.split('_')[0]

        if self.interacting:

            if status == "left":
                self.status = 'right'

            elif status == 'right':
                self.status = 'left'

            elif status == 'up':
                self.status = 'down'

            elif status == 'down':
                self.status = 'up'

        else:
            self.status = 'down'



    def chat(self):
        screen = pygame.display.get_surface()
        if self.interacting:
            w, h = screen.get_size()
            font = pygame.font.SysFont(None, 40)

            amount_of_text = len(self.talk_list[self.talk_index])

            if self.chat_index < amount_of_text:
                text = self.talk_list[self.talk_index][self.chat_index]
                i = 0

                if isinstance(text,list):
                    pygame.draw.rect(screen, 'gray', (100, h-250,w-200, 400))
                    for inside_text in text:
                        text = font.render(f"{inside_text}", True, 'black')
                        text_rect = text.get_rect(topleft= (200,h-200 + i * 40))
                        screen.blit(text, text_rect)
                        i += 1

                elif text == 'pular texto':
                    number = self.chat_index + 1

                    if len(self.talk_list[self.talk_index]) > number:
                        check = self.talk_list[self.talk_index][number]

                        if isinstance(check, dict):
                            for change_type, new_info in check.items():
                                if change_type == 'change_npc_talk':
                                    for sprite in self.groups()[0]:
                                        if hasattr(sprite, 'npc_name'):
                                            if new_info[0] == sprite.npc_name:
                                                sprite.talk_index = new_info[1]

                                if change_type == 'bed':
                                    for sprite in self.groups()[0]:
                                        if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'bed':
                                            sprite.canSleep = new_info

                                if change_type == 'give_item':
                                    self.player.inventory.addItem(new_info)

                    self.talk_index += 1

                else:
                    pygame.draw.rect(screen, 'gray', (100, h-250,w-200, 400))
                    text = font.render(f"{self.npc_name}: {text}", True, 'black')
                    text_rect = text.get_rect(topleft= (200,h-200))
                    screen.blit(text, text_rect)

            else:
                self.interacting = False
                self.player.canMove = True
                self.chat_index = 0







