import pygame

class Room:
    def __init__(self) -> None:
        self.variables = []
        self.level_complete = False



    def get_variable(self, variables):
        self.variables = variables
        for variable in self.variables:
            if hasattr(variable, 'sprite_type'):
                if variable.sprite_type == 'door':
                    self.door = variable




    def handleLevel_1(self):
        buttons_to_be_pressed = 2
        buttons_pressed = 0

        # O level das caixas
        for variable in self.variables:
            if hasattr(variable, 'sprite_type'):
                if variable.sprite_type == 'button':
                    if variable.interacting:
                        buttons_pressed += 1

        if hasattr(self, 'door'):
            if buttons_pressed == buttons_to_be_pressed:
                self.door.status = 'open'
                self.door.locked = False
                self.door.open = True
                self.door.canCollide.remove(self.door)
            else:
                self.door.status = 'closed'
                self.door.locked = True
                self.door.open = False
                self.door.canCollide.add(self.door)






