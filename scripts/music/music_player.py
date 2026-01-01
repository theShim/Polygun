import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

from scripts.music.music import SOUNDS

    ##############################################################################################

class Music_Player:
    def __init__(self, game, channel_num = 32):
        self.game = game
        pygame.mixer.set_num_channels(channel_num)

        self.sounds: dict[str, pygame.mixer.Sound] = SOUNDS
        self.pools: dict[str, Sound_Pool] = {}

        self.channel_index = 0
        self.channel_num = channel_num
        self.channels = [pygame.mixer.Channel(i) for i in range(channel_num)]

        self.create_pool("music", 1)
        self.create_pool("sfx", 12, volume=0.7)
        self.create_pool("ui", 4, volume=0.4)
        self.create_pool("ambient", 6, volume=0.7)

    def create_pool(self, name, count, volume=1.0):
        channels = self.channels[self.channel_index : self.channel_index + count]
        if len(channels) < count:
            raise BaseException("Too many channels.")
        
        self.channel_index += count
        self.pools[name] = Sound_Pool(name, channels, volume)

    def play(self, sound: str, pool: str="sfx", loop=False, fadein_ms=0):
        sound = self.sounds.get(sound, None)
        if not sound: raise BaseException(f"{sound} not found.")

        pool = self.pools[pool]
        channel = pool.get_free_channel()
        channel.play(sound, loops=-1 if loop else 0, fade_ms=fadein_ms)

    def stop(self, pool="music", fadeout_ms=1000):
        self.pools[pool].stop(fadeout_ms)

    def set_master_volume(self, vol):
        pygame.mixer.music.set_volume(vol)
        for pool in self.pools.values():
            pool.set_volume(pool.volume * vol)

    def set_pool_volume(self, pool, volume):
        self.pools[pool].set_volume(volume)  

    def save_json(self):
        pass


class Sound_Pool:
    def __init__(self, name, channels, volume=1.0):
        self.name: str = name
        self.channels: list[pygame.mixer.Channel] = channels
        self.volume: float = volume

        for c in self.channels:
            c.set_volume(self.volume)

    def stop(self, fadeout_ms=1000):
        for c in self.channels:
            c.fadeout(fadeout_ms)

    def set_volume(self, vol):
        self.volume = vol
        for c in self.channels:
            c.set_volume(self.volume)

    def get_free_channel(self):
        for c in self.channels:
            if not c.get_busy():
                return c
        return self.channels[0]