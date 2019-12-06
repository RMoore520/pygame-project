#The Big Yeet - platform game
import pygame as pg
import random
from settings import *
from sprites import *
from os import path

class Game:
    def __init__(self):
        #initialize pygame, create window
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.playingToughSong = False
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        #load high scores
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        #load spritesheet image
        img_dir = path.join(self.dir, 'img')
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        #cloud load_images
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(pg.image.load(path.join(img_dir, 'cloud{}.png'.format(i))).convert())
        # Load space images
        self.space_images = []
        for i in range(1, 3):
            self.space_images.append(pg.image.load(path.join(img_dir, 'space{}.png'.format(i))).convert())
        #load sounds
        self.snd_dir = path.join(self.dir, 'snd')
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'jump_02.wav'))
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'oh-yeah_4.wav'))
        self.mobtouch_sound1 = pg.mixer.Sound(path.join(self.snd_dir, 'killed1.wav'))
        self.mobtouch_sound2 = pg.mixer.Sound(path.join(self.snd_dir, 'killed2.wav'))

    def new(self):
        #Start new Game
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        self.space = pg.sprite.Group()
        self.player = Player(self)
        for plat in PLATFORM_LIST:
            Platform(self, *plat)
        self.mob_timer = 0
        pg.mixer.music.load(path.join(self.snd_dir, 'happy-sandbox.wav'))
        for i in range(8):
            c = Cloud(self)
            c.rect.y += 500
        self.run()

    def run(self):
        #Game loop
        pg.mixer.music.play(loops = -1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)

    def update(self):
        # Game loop update
        self.all_sprites.update()
        if self.score > 2000 and self.score < 2050:#and self.playingToughSong == False: # Plays funky music once a certain score is reached
            pg.mixer.music.load(path.join(self.snd_dir, 'space-music.wav'))
            pg.mixer.music.play(loops = -1)
            self.playingToughSong = True
            print("PLAYING IT")
        # Spawn enemies
        now = pg.time.get_ticks()
        # Spawn more enemies based on score.
        if self.score < 500:
            spawnRate = 7000
        elif self.score < 1000:
            spawnRate = 6000
        elif self.score < 2000:
            spawnRate = 4000
        elif self.score < 4000:
            spawnRate = 2000
        else:
            spawnRate = 1500
        if now - self.mob_timer > spawnRate + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Mob(self, self.score)
        #if a mob is hit
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False, pg.sprite.collide_mask)
        if mob_hits:
            soundchoice = random.randrange(0, 100)
            if soundchoice < 50:
                self.mobtouch_sound1.play()
            else:
                self.mobtouch_sound2.play()
            self.playing = False
        #check if player hits platform - only if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.x < lowest.rect.right + 10 and \
                    self.player.pos.x > lowest.rect.left - 10: #separate line
                    if self.player.pos.y < lowest.rect.centery:
                        self.player.pos.y = lowest.rect.top
                        self.player.vel.y = 0
                        self.player.jumping = False

        #if player reaches top 1/4 of screen
        if self.player.rect.top <= HEIGHT / 4:
            if random.randrange(100) < 1:
                if self.score < 2000:
                    Cloud(self)
                else:
                    Space(self)
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y / 2), 2)
            for space in self.space:
                space.rect.y += max(abs(self.player.vel.y / 2), 2)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10
        #if player touches a powerup
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False

        #Death!
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()

        if len(self.platforms) == 0:
            soundchoice = random.randrange(0, 100)
            if soundchoice < 50:
                self.mobtouch_sound1.play()
            else:
                self.mobtouch_sound2.play()
            self.playing = False

        # Spawn new platforms to keep some average number
        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            p = Platform(self, random.randrange(0, WIDTH - width), random.randrange(-35, -20))
            self.platforms.add(p)
            self.all_sprites.add(p)

    def events(self):
        #Game loop events
        for event in pg.event.get():
            #check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE or event.key == pg.K_w or event.key == pg.K_UP:
                    self.player.jump()
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE or event.key == pg.K_w or event.key == pg.K_UP:
                    self.player.jump_cut()

    def draw(self):
        #Game loop draw
        if self.score < 500:
            self.screen.fill(SKYBLUE)
        elif self.score < 1000:
            self.screen.fill(LIGHTBLUE)
        elif self.score < 1500:
            self.screen.fill(DARKBLUE)
        elif self.score < 2000:
            self.screen.fill(DARKERBLUE)
        elif self.score < 2500:
            self.screen.fill(DARKESTBLUE)
        else:
            self.screen.fill(BLACK)

        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        #after drawing everything, flip display
        pg.display.flip()

    def show_start_screen(self):
        #Game start screen
        pg.mixer.music.load(path.join(self.snd_dir, 'Yippee.wav'))
        pg.mixer.music.play(loops = -1)
        self.screen.fill(LIGHTBLUE)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Arrows (or 'A' and 'D') to move, Space ('W' or Arrow) to jump", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press any key to play", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def show_go_screen(self):
        #Game over screen
        if not self.running:
            return
        pg.mixer.music.load(path.join(self.snd_dir, 'sad-piano.wav'))
        pg.mixer.music.play(loops = -1)
        self.screen.fill(RED)
        self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press any key to play again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYDOWN:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
