import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

    ##############################################################################################

#handler for storing the player's items and processing the different types
class Item_Manager:
    def __init__(self, game):
        self.game = game
        self.screen = self.game.screen

        self.items = pygame.sprite.Group()

    #returns a dictionary of all current items and their relative counts
    @property
    def current_items(self) -> dict[str|int]:
        data = {}
        for item in self.items:
            data[item.name] = data.get(item.name, 0) + 1
        return data 

    #general update on all timed and permanent power-ups
    def update(self):
        #sort the item rendering in the bottom right such that
        #timed ones are "at the front" and permanent ones at the back
        non_timed = []
        timed = []
        for item in self.items:
            if item.type_ == "timed": timed.append(item)
            else: non_timed.append(item)
        
        non_timed.sort(key=lambda p: p.name) #sort the permanent ones alphabetically
        timed.sort(key=lambda p: p.timer.t / p.timer.end) #sort timed by their remaining time
        items = non_timed + timed #aggragate the final sorted lists

        #update the items as required
        for i, item in enumerate(items):
            item.update(index=i)