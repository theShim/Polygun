import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

    ##############################################################################################

class Music_Player:
    def __init__(self, channel_num = 20):
        pygame.mixer.set_num_channels(channel_num)

        #every sound file loaded
        from scripts.music.music import SOUNDS
        self.sounds = SOUNDS

        #every sound channel to be used, gonna be more later on
        self.background = pygame.mixer.Channel(0)
        self.typing = pygame.mixer.Channel(1)
        self.sound_effects = pygame.mixer.Channel(2)
        self.paint_splats = pygame.mixer.Channel(3)
        self.channels = [
            self.background,
            self.typing,
            self.sound_effects,
            self.paint_splats,
        ]
        self.volumes: list[float] = [ #needs to be the same order as self.channels
            1.,
            0.25,
            1.,
            1,
        ]
        for channel, v in zip(["bg", "type", "sfx", "splat"], self.volumes):
            self.set_vol(v, channel)

    def get_channel(self, channel_name):
        match channel_name:
            case "background" | "bg":
                return self.background
            case "typing" | "type":
                return self.typing
            case "sound_effects" | "sfx":
                return self.sound_effects
            case "paint_splat" | "splat":
                return self.paint_splats
            case _:
                return None
            
    def is_playing(self, channel):
        channel = self.get_channel(channel)
        return channel.get_busy()
            

    #play a specified sound in a specified channel, with the option to constantly loop it
    #sound should be a key straight from the self.sounds dict
    def play(self, sound, channel, loop=False, fade_in=0):  
        if sound == "":
            return
        
        sound_ = self.sounds.get(sound, None)
        if sound_ == None: return print(Exception(f"{sound} not found."))
        channel = self.get_channel(channel)
        channel.play(sound_, loops=-1 if loop else 0, fade_ms=fade_in)

    #queue a song to play after the current one in a specified channel
    def queue_sound(self, sound, channel):  
        sound = self.sounds[sound]
        channel = self.get_channel(channel)
        channel.queue(sound)

    #stop the playback of a specified channel or all, with an optional fade out timer
    def stop(self, channel="all", fadeout_ms=1000):
        if channel == "all":
            for c in self.channels:
                c.fadeout(fadeout_ms)
            return
        
        self.get_channel(channel).fadeout(fadeout_ms)
    
    #change vol with float between 0 and 1 for specified channels
    def set_vol(self, vol: float, channel="all", force=False):
        if channel == "all":
            for i, c in enumerate(self.channels):
                c.set_volume(vol)
                self.volumes[i] = vol
            return
        
        if force:
            self.get_channel(channel).set_volume(vol)
            self.volumes[self.channels.index(self.get_channel(channel))] = vol #updates volume data store
        else:
            clamp = self.volumes[self.channels.index(self.get_channel(channel))]
            self.get_channel(channel).set_volume(vol * clamp)