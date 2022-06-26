# PROGRAM HEADER
# Program Name: Monster Game with GUI
# Programmer: Raymond Pan
# Date: June 18, 2022
# Description: This is a two-player Monster battling game. Each player gets a Monster with the type that they prefer and
#   take turns commanding their Monsters to attack the other player's Monster. The objective of the game is to lower
#   the HP of your opponent's Monster to zero.
# Input: The type of the Monster, the name of the Monster, what move the user would like to use (using buttons), whether
#   they want to check the stats of the Monsters (using buttons), whether they want to restore health or stamina (using
#   stamina), they have to click in the message box to view the next message, they can click the close button to quit
#   out of the program, they can click the quit button in the game over screen to exit the program, the tutorial text
#   file, the background image, the icon effect images, the sprite images, the music, the sound effects and the arrow
#   image.

# importing modules and declaring variables
import pygame
import random

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

# dimensions of window
WIDTH = 1080
LENGTH = 721

# RGB values of colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 204, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (102, 255, 255)
SALMON_PINK = (255, 128, 149)
CRIMSON = (220, 20, 60)
DEEP_SKY = (0, 191, 255)
DIRT = (27, 92, 49)

# variables used in the game
in_play = True
clicked = False
move = False
hit = False
over = False
tie = False
switch = False
played = False
cycle_letter = False
previous_blink = False
hit_count = 0
mes_index = 0
screen = 0
message = ''

# music used in the game
hit_sound = pygame.mixer.Sound('Music/hit.wav')
theme = pygame.mixer.Sound('Music/victorysong.wav')
end_theme = pygame.mixer.Sound('Music/endmusic.wav')
b_press = pygame.mixer.Sound('Music/buttonpress.wav')
heal_sound = pygame.mixer.Sound('Music/heal.wav')

# setting the volume
theme.set_volume(0.5)
hit_sound.set_volume(0.5)
b_press.set_volume(1)
heal_sound.set_volume(1)

# images used in the game
background = pygame.image.load('Background/pokemonbackgroundv2.jpg')
arrow = pygame.image.load('Background/arrow.png')
burn = pygame.transform.scale(pygame.image.load('Effects/burn.png'), (60, 24))
poison = pygame.transform.scale(pygame.image.load('Effects/poison.png'), (60, 24))
sleep = pygame.transform.scale(pygame.image.load('Effects/sleep.png'), (60, 24))
duck = pygame.transform.scale(pygame.image.load('Effects/duck.png'), (45, 45))

# text that is used later
font = pygame.font.SysFont('dinalternate', 30)
winner = font.render('WINNER', True, BLUE)
loser = font.render('LOSER', True, BLUE)


# the parent class of the type-specific classes
class Monster:
    # initializing an instance of Monster and assigning values to its necessary attributes
    # the stats are randomly generated between predetermined upper and lower limits
    # this is what the elements in the burn, poison, confusion, and sleep lists represent:
    # [is the status active?, how many rounds are left before the status goes away]
    # each player gets 2 potions and 2 elixirs at the start
    # attributes for the sprites are also initialized
    def __init__(self, element):
        self.name = None
        self.element = element
        self.health = random.randint(190, 220)
        self.initial_health = self.health
        self.offense = random.randint(30, 40)
        self.defense = random.randint(20, 30)
        self.speed = random.randint(5, 10)
        self.stamina = random.randint(240, 260)
        self.initial_stamina = self.stamina
        self.burn = [False, 4]
        self.poison = [False, 4]
        self.confusion = [False, 4]
        self.sleep = [False, 3]
        self.potions = 2
        self.elixr = 2

        self.bx = 200
        self.by = 320
        self.fx = 700
        self.fy = 130
        self.cx = None
        self.cy = None
        self.sprites = []
        self.current_sprite = 0
        self.image = None
        self.hit = [False, 3]
        self.turn = False

    attacks = None

    # gets the current image for the sprite
    def get_current(self):
        self.image = self.sprites[self.current_sprite]

    # moves the sprite from one side to the other and changes the current sprite image
    # sprite will have its back towards the camera if it is going
    # otherwise, it will have its front towards the camera
    def move_side(self):
        if self.turn:
            self.cx = self.fx
            self.cy = self.fy
            self.current_sprite = 0
            self.turn = False
        else:
            self.cx = self.bx
            self.cy = self.by
            self.current_sprite = 1
            self.turn = True

        self.get_current()

    # creates a list of buttons for the attack moves
    def draw_moves(self):
        x = 250
        y = 560
        texts = self.attacks
        coord = []
        blist = []
        for buttons in range(4):
            coord.append((x, y))
            x += 200

        for n, xy in enumerate(coord):
            button = Button(BLUE, DEEP_SKY, xy[0], xy[1], 180, 80, BLACK, texts[n])
            blist.append(button)
            button.draw(win, 20, BLACK)

        return blist

    # displays all the stats of a Monster
    def display_stats(self, player, start):
        x = start[0]
        y = start[1]
        texts = [f'[{player}] {self.name}\'s Stats!', f'Element: {self.element}', f'HP: {self.health}',
                 f'Offense: {self.offense}', f'Defense: {self.defense}', f'Speed: {self.speed}',
                 f'Stamina: {self.stamina}']
        coord = []
        for sentence in range(7):
            coord.append((x, y))
            if sentence == 0:
                y += 30
            elif sentence == 1:
                x += 150
            else:
                x += 130

        for n, xy in enumerate(coord):
            font = pygame.font.SysFont('dinalternate', 18)
            text = font.render(texts[n], True, BLUE)
            win.blit(text, xy)

    # draws the health of one Monster
    def draw_health(self):
        if self.health < 0:
            self.health = 0
        text = f'{self.health}/{self.initial_health}'
        font = pygame.font.SysFont('copperplate', 34)
        text = font.render(text, True, BLACK)
        if self.turn:
            win.blit(text, (780, 355))
        else:
            win.blit(text, (230, 95))

    # draws the current effect that Monster has
    def draw_icon(self):
        xy1 = (630, 350)
        xy2 = (80, 90)
        if self.turn:
            if self.burn[0]:
                win.blit(burn, xy1)
            elif self.poison[0]:
                win.blit(poison, xy1)
            elif self.confusion[0]:
                win.blit(duck, xy1)
            elif self.sleep[0]:
                win.blit(sleep, xy1)
        else:
            if self.burn[0]:
                win.blit(burn, xy2)
            elif self.poison[0]:
                win.blit(poison, xy2)
            elif self.confusion[0]:
                win.blit(duck, xy2)
            elif self.sleep[0]:
                win.blit(sleep, xy2)

    # draws the Monster onto the screen
    # it is responsible for making the bobbing animation
    # the Monster will be drawn on the left side if it is their turn
    # otherwise it will be drawn on the right side
    def draw(self, move, hit):
        if self.turn:
            if not self.cx:
                self.cx = self.bx
                self.cy = self.by
            else:
                if move and not self.hit[0]:
                    if self.cy == self.by:
                        self.cy -= 15
                    else:
                        self.cy += 15
                elif hit and self.hit[0]:
                    if not self.hit[1]:
                        self.hit[0] = False
                        self.hit[1] = 3
                    if self.current_sprite == 1:
                        self.current_sprite = 3
                        self.hit[1] -= 1
                        self.get_current()
                    else:
                        self.current_sprite = 1
                        self.get_current()
            win.blit(self.image, [self.cx, self.cy])

        else:
            if not self.cx:
                self.cx = self.fx
                self.cy = self.fy
            else:
                if move and not self.hit[0]:
                    if self.cy == self.fy:
                        self.cy -= 15
                    else:
                        self.cy += 15
                elif hit and self.hit[0]:
                    if not self.hit[1]:
                        self.hit[0] = False
                        self.hit[1] = 3
                    if self.current_sprite == 0:
                        self.current_sprite = 2
                        self.hit[1] -= 1
                        self.get_current()
                    else:
                        self.current_sprite = 0
                        self.get_current()
            win.blit(self.image, [self.cx, self.cy])

    # the purpose of this function is to let the attacker use its special attack
    # performs checks such as "does the Monster have enough stamina to attack?", "will the enemy Monster
    #   dodge the attack?", "is the Monster confused?"
    # the method will return True if Monster doesn't have enough stamina for this move
    # the get_confused method will execute if the Monster is confused
    # the damage is determined based on the attacker's offense stats and the victim's defense stats
    # the damage is randomized between its offense stat plus 6 and plus 12
    # the damage is increased if the Monster's type is strong against the enemy's type
    # the damage is decreased if the Monster's type is weak against the enemy's type
    # the damage dealt and the effectiveness of the attack is printed
    def special_attack(self, enemy):
        global message
        strong = None
        weak = None
        if self.stamina < 40:
            message = f'Sorry, {self.name} doesn\'t have enough stamina to perform this attack'
            draw_message()
            return False
        else:
            self.stamina -= 40
        if self.confusion[0]:
            confused = self.get_confused(random.randint(self.offense + 6, self.offense + 12))
            if confused:
                return True
        damage = random.randint(self.offense + 6, self.offense + 12) - int(enemy.defense * 0.3)
        if self.effective(enemy)[0]:
            damage += 5
            strong = True
        elif self.effective(enemy)[1]:
            damage -= 12
            weak = True
        if self.dodge(enemy):
            message = f'Oh no! {self.name}\'s attack missed'
            draw_message()
        else:
            enemy.health -= damage
            enemy.hit[0] = True
            hit_sound.play()
            message = f'{self.name} used {self.attacks[0]} and dealt {damage} damage to {enemy.name}'
            draw_message()
            if strong:
                message = f'Wow, {self.attacks[0]} was super effective against {enemy.name}'
                draw_message()
            elif weak:
                message = f'{self.attacks[0]} was not very effective'
                draw_message()
        return True

    # comments for special_attack apply for this method
    # the upper and bottom limits of the damage is lower than that of the special_attack
    def rapid_attack(self, enemy):
        global message
        strong = None
        weak = None
        if self.stamina < 30:
            message = f'Sorry, {self.name} doesn\'t have enough stamina to perform this attack'
            draw_message()
            return False
        else:
            self.stamina -= 30
        attack = True
        count = 0

        # this loop allows the Monster to attack multiple times
        # everytime the loop iterates the code uses the get_burned_poison method to check if the Monster is burned or
        # poisoned and deals damage to them accordingly
        while attack:
            count += 1
            if self.confusion[0]:
                confused = self.get_confused(random.randint(self.offense - 4, self.offense - 2))
                if confused:
                    self.get_burned_poisoned(enemy)
                    enemy.get_burned_poisoned(self)
                    random_num = random.randint(0, 10)
                    if random_num < 6 and enemy.status() and not count == 5:
                        attack = True
                    else:
                        attack = False
                    continue
            damage = random.randint(self.offense - 8, self.offense - 6) - int(enemy.defense * 0.3)
            if self.effective(enemy)[0]:
                damage += 5
                strong = True
            elif self.effective(enemy)[1]:
                damage -= 5
                weak = True
            if self.dodge(enemy):
                message = f'Oh no! {self.name}\'s attack missed'
                draw_message()
            else:
                enemy.health -= damage
                enemy.hit[0] = True
                hit_sound.play()
                message = f'{self.name} used {self.attacks[1]} and dealt {damage} damage to {enemy.name}'
                draw_message()
                if strong:
                    message = f'Wow, {self.attacks[1]} was super effective against {enemy.name}'
                    draw_message()
                elif weak:
                    message = f'{self.attacks[1]} was not very effective against {enemy.name}'
                    draw_message()
            self.get_burned_poisoned(enemy)
            enemy.get_burned_poisoned(self)
            random_num = random.randint(0, 10)
            if random_num < 6 and enemy.status() and not count == 5:
                attack = True
            else:
                attack = False

        message = f'{self.name} used {self.attacks[1]} {count} time(s)'
        draw_message()
        return True

    # comments for special_attack method apply for this method
    # the upper and bottom limits of the damage is lower than that of the special_attack but higher than that of the
    #   rapid_attack
    def normal_attack(self, enemy):
        global message
        strong = None
        weak = None
        if self.stamina < 20:
            message = f'Sorry, {self.name} doesn\'t have enough stamina to perform this attack'
            draw_message()
            return False
        else:
            self.stamina -= 20
        if self.confusion[0]:
            confused = self.get_confused(random.randint(self.offense - 4, self.offense - 2))
            if confused:
                return True
        damage = random.randint(self.offense - 4, self.offense - 2) - int(enemy.defense * 0.3)
        if self.effective(enemy)[0]:
            damage += 5
            strong = True
        elif self.effective(enemy)[1]:
            damage -= 5
            weak = True
        if self.dodge(enemy):
            message = f'Oh no! {self.name}\'s attack missed'
            draw_message()
        else:
            enemy.health -= damage
            enemy.hit[0] = True
            hit_sound.play()
            message = f'{self.name} used {self.attacks[2]} and dealt {damage} damage to {enemy.name}'
            draw_message()
            if strong:
                message = f'Wow, {self.attacks[2]} was super effective against {enemy.name}'
                draw_message()
            elif weak:
                message = f'{self.attacks[2]} was not very effective against {enemy.name}'
                draw_message()
        return True

    # method that deals chip damage to the Monster if they are burned or poisoned
    # the damage is randomized using the enemy's offense stat and Monster's defense stat
    # damage is increased or decreased based on the enemy's effectiveness against the Monster
    # once the enemy is burned or poisoned for 4 rounds, their burn or poison status is reset
    def get_burned_poisoned(self, enemy):
        global message
        if self.burn[0] or self.poison[0]:
            damage = random.randint(enemy.offense - 18, enemy.offense - 14) - int(self.defense * 0.3)
            if enemy.effective(self)[0]:
                damage += 3
            elif enemy.effective(self)[1]:
                damage -= 3
            if self.burn[0]:
                if self.burn[1] == 0:
                    self.burn[0] = False
                    self.burn[1] = 4
                    return
                self.health -= damage
                message = f'{self.name} was burned... {self.name} lost {damage} health'
                draw_message()
                self.burn[1] -= 1
            elif self.poison[0]:
                if self.poison[1] == 0:
                    self.poison[0] = False
                    self.poison[1] = 4
                    return
                self.health -= damage
                message = f'{self.name} was poisoned... {self.name} lost {damage} health'
                draw_message()
                self.poison[1] -= 1

    # method that will determine whether a confused Monster will hit itself or maintain its accuracy
    # 30 percent chance the Monster will maintain its accuracy
    # the damage that the Monster will deal to itself is half of the damage it was originally supposed to deal to the
    #   enemy
    # the confusion status of the Monster is reset once the Monster has been confused for 4 of its attacking rounds
    def get_confused(self, damage):
        global message
        chance = random.randint(0, 10)
        if self.confusion[1] == 0:
            message = f'{self.name} snapped out of its confusion!'
            draw_message()
            self.confusion[0] = False
            self.confusion[1] = 4
            return False
        elif chance <= 3:
            message = f'{self.name} miraculously maintained its accuracy despite of its confusion!'
            draw_message()
            self.confusion[1] -= 1
            return False
        else:
            damage1 = int(damage / 2)
            self.health -= damage1
            message = f'{self.name} accidentally hurt itself by confusion... {self.name} lost {damage1} health'
            draw_message()
            self.confusion[1] -= 1
            return True

    # method that will check if the Monster is still sleeping or is waking up
    # 20 percent chance the Monster will wake up early, but Monster will always be asleep the round right after they get
    #   the sleep status
    # the Monster will always wake up after it sleeps for 3 of its attacking rounds
    def get_sleep(self):
        global message
        chance = random.randint(0, 10)
        if (chance <= 2 and not self.sleep[1] == 3) or self.sleep[1] == 0:
            message = f'{self.name} woke up!'
            draw_message()
            self.sleep[0] = False
            self.sleep[1] = 3
            return False
        else:
            message = f'{self.name} is still sleeping...'
            draw_message()
            self.sleep[1] -= 1
            return True

    # method that lets player regen 100 of its Monster's HP
    # no health will be regenerated if you have no potions or the Monster is already is full health
    def restore_health(self):
        global message
        if self.potions == 0:
            message = f'{self.name} has no potions left'
            draw_message()
            return False
        elif self.health == self.initial_health:
            message = f'{self.name} is already at full heath'
            draw_message()
            return False
        else:
            self.health += 100
            self.potions -= 1
            heal_sound.play()
            if self.health > self.initial_health:
                self.health = self.initial_health
            message = f'{self.name} regenerated 100 HP'
            draw_message()
            return True

    # method that lets player regen 80 of its Monster's stamina
    # no stamina will be regenerated if you have no elixirs or the Monster is already is full stamina
    def restore_stamina(self):
        global message
        if self.elixr == 0:
            message = f'{self.name} has no elixirs left'
            draw_message()
            return False
        elif self.stamina == self.initial_stamina:
            message = f'{self.name} is already at full stamina'
            draw_message()
            return False
        else:
            self.stamina += 80
            self.elixr -= 1
            heal_sound.play()
            if self.stamina > self.initial_stamina:
                self.stamina = self.initial_stamina
            message = f'{self.name} regenerated 80 stamina'
            draw_message()
            return True

    # check if the Monster has collapsed
    def status(self):
        if self.health <= 0:
            return False
        else:
            return True

    # method that allows user to see if their Monster is effective or ineffective against an enemy Monster
    def effective(self, enemy):
        if self.element == 'fire' and enemy.element == 'grass':
            return [True, False]
        elif self.element == 'fire' and enemy.element == 'normal':
            return [False, False]
        elif self.element == 'fire' and enemy.element == 'ghost':
            return [False, True]
        elif self.element == 'grass' and enemy.element == 'fire':
            return [False, True]
        elif self.element == 'grass' and enemy.element == 'normal':
            return [False, False]
        elif self.element == 'grass' and enemy.element == 'ghost':
            return [True, False]
        elif self.element == 'ghost' and enemy.element == 'fire':
            return [True, False]
        elif self.element == 'ghost' and enemy.element == 'grass':
            return [False, True]
        elif self.element == 'ghost' and enemy.element == 'normal':
            return [False, False]
        elif self.element == 'normal' and enemy.element == 'fire':
            return [False, False]
        elif self.element == 'normal' and enemy.element == 'grass':
            return [False, False]
        elif self.element == 'normal' and enemy.element == 'ghost':
            return [False, False]
        elif self.element == 'fire' and enemy.element == 'fire':
            return [False, True]
        elif self.element == 'grass' and enemy.element == 'grass':
            return [False, True]
        elif self.element == 'normal' and enemy.element == 'normal':
            return [False, True]
        elif self.element == 'ghost' and enemy.element == 'ghost':
            return [False, True]

    # checks if Monster currently has a special effect/status
    def has_effect(self):
        if self.burn[0] or self.poison[0] or self.confusion[0] or self.sleep[0]:
            return True
        else:
            return False

    # method that asks the player to input a correct name for their Monster
    # default name is used if nothing is inputted
    def get_name(self, player):
        print(f'You got {self.name}!')
        while True:
            name = input(f'\n[{player}] What name would you want to give to {self.name} (leave empty if no change)? ')
            if name.isalpha():
                print(f'{self.name}\'s new name is {name}')
                self.name = name
                return
            elif name == '':
                return
            else:
                print('Please enter a name that only contains letters')

    # things to check after each round
    # checks if the monsters are poisoned, burned, or unconscious
    # returns the bool value of whether the game is over or not
    def checker(self, enemy, pname, pname2):
        global message
        self.get_burned_poisoned(enemy)
        enemy.get_burned_poisoned(self)
        if not enemy.status():
            message = f'[{pname2}] {enemy.name} has fallen and [{pname}] {self.name} is the Champion!'
            draw_message()
            return True
        else:
            return False

    # returns whether the Monster has successfully dodged another Monster's attack
    # the chance is based on the enemy Monster's speed stat
    @staticmethod
    def dodge(enemy):
        rand_num = int(random.random() * 100)
        if rand_num <= enemy.speed:
            return True
        else:
            return False

    # creates an instance of a type of Monster based on the preferred type of the user
    # returns that object to the main program
    @staticmethod
    def make_monster(typ):
        if typ == 'fire' or typ == 'f':
            return Fire('fire')
        elif typ == 'grass' or typ == 'g':
            return Grass('grass')
        elif typ == 'normal' or typ == 'n':
            return Normal('normal')
        elif typ == 'ghost' or typ == 'gh':
            return Ghost('ghost')

    # gets what type of Monster the user wants
    # handles invalid inputs
    @staticmethod
    def get_type():
        while True:
            ele = input('\nChoose between "fire", "grass", "normal", or "ghost" [f, g, n, gh]: ')
            if ele in ['fire', 'grass', 'normal', 'ghost', 'f', 'g', 'n', 'gh']:
                break
            else:
                print('Invalid input, try again')
        return ele


# fire type-specific class that inherits the state and behavior of the Monster class
# things that are unique to the fire type include the default names, attack names, sprite images, and the burn attack
class Fire(Monster):
    # using the initialization method from the parent class to construct an instance of Fire
    # a random type-specific default name is assigned to the name attribute
    def __init__(self, element):
        Monster.__init__(self, element)
        self.name = random.choice(['Burny', 'Hopflame', 'Wukong'])
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/infernape front.png'), (200, 200)))
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/infernape back.png'), (175, 175)))
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/infernape front hit.png'), (200, 200)))
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/infernape back hit.png'), (175, 175)))
        self.image = self.sprites[self.current_sprite]

    attacks = ['FIRE BLITZ', 'FLAME KICKS', 'FIRE BREATH', 'BURN']

    # method that gives the enemy a burned effect upon its invocation
    # enemy will gain the burn status if they don't have another active effect
    # the Monster's stamina will be checked to see if it has enough stamina to perform this attack
    # a message will be printed to indicate if the attack was successful
    # method will return True if the attack cannot be used
    def effect_attack(self, enemy):
        global message
        if not enemy.has_effect():
            if self.stamina < 20:
                message = f'Sorry, {self.name} doesn\'t have enough stamina to perform this attack'
                draw_message()
                return False
            else:
                self.stamina -= 20
            enemy.burn[0] = True
            enemy.hit[0] = True
            hit_sound.play()
            message = f'{enemy.name} has the burned effect for the next four rounds! (including this one)'
            draw_message()
            return True
        else:
            message = f'You cannot use this attack because {enemy.name} is already affected by an effect'
            draw_message()
            return False


# grass type-specific class that inherits the state and behavior of the Monster class
# things that are unique to the grass type include the default names, attack names, sprite images, and the poison attack
class Grass(Monster):
    # using the initialization method from the parent class to construct an instance of Grass
    # a random type-specific default name is assigned to the name attribute
    def __init__(self, element):
        Monster.__init__(self, element)
        self.name = random.choice(['Rootay', 'Venus', 'Calabash'])
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/sceptile front.png'), (200, 200)))
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/sceptile back.png'), (200, 200)))
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/sceptile front hit.png'), (200, 200)))
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/sceptile back hit.png'), (200, 200)))
        self.image = self.sprites[self.current_sprite]

    attacks = ['FOREST COLLAPSE', 'LEAF BLADES', 'SUN POWER', 'POISON']

    # comments used to describe the effect_attack from Fire class can be used here
    # the only difference is that the method gives enemies a poisoned status
    def effect_attack(self, enemy):
        global message
        if not enemy.has_effect():
            if self.stamina < 20:
                message = f'Sorry, {self.name} doesn\'t have enough stamina to perform this attack'
                draw_message()
                return False
            else:
                self.stamina -= 20
            enemy.poison[0] = True
            enemy.hit[0] = True
            hit_sound.play()
            message = f'{enemy.name} has the poisoned effect for the next four rounds! (including this one)'
            draw_message()
            return True
        else:
            message = f'You cannot use this attack because {enemy.name} is already affected by an effect'
            draw_message()
            return False


# normal type-specific class that inherits the state and behavior of the Monster class
# things that are unique to the normal type include the default names, attack names, sprite images, and the confusion
#   attack
class Normal(Monster):
    # using the initialization method from the parent class to construct an instance of Normal
    # a random type-specific default name is assigned to the name attribute
    def __init__(self, element):
        Monster.__init__(self, element)
        self.name = random.choice(['Pillar', 'Styfer', 'Yupper'])
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/herdier front.png'), (230, 230)))
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/herdier back.png'), (230, 230)))
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/herdier front hit.png'), (230, 230)))
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/herdier back hit.png'), (230, 230)))
        self.image = self.sprites[self.current_sprite]

    attacks = ['BRUTE FORCE', 'HEADBUTT', 'BITE', 'CONFUSION']

    # comments used to describe the effect_attack from Fire class can be used here
    # the only difference is that the method gives enemies a confused status
    def effect_attack(self, enemy):
        global message
        if not enemy.has_effect():
            if self.stamina < 20:
                message = f'Sorry, {self.name} doesn\'t have enough stamina to perform this attack'
                draw_message()
                return False
            else:
                self.stamina -= 20
            enemy.confusion[0] = True
            enemy.hit[0] = True
            hit_sound.play()
            message = f'{enemy.name} has the confused effect for the next four rounds it attacks!'
            draw_message()
            return True
        else:
            message = f'You cannot use this attack because {enemy.name} is already affected by an effect'
            draw_message()
            return False


# ghost type-specific class that inherits the state and behavior of the Monster class
# things that are unique to the ghost type include the default names, attack names, sprite images, and the sleep attack
class Ghost(Monster):
    # using the initialization method from the parent class to construct an instance of Ghost
    # a random type-specific default name is assigned to the name attribute
    def __init__(self, element):
        Monster.__init__(self, element)
        self.name = random.choice(['Misso', 'Ghoul', 'Smogger'])
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/gengar front.png'), (200, 200)))
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/gengar back.png'), (200, 200)))
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/gengar front hit.png'), (200, 200)))
        self.sprites.append(pygame.transform.scale(pygame.image.load('Pokemons/gengar back hit.png'), (200, 200)))
        self.image = self.sprites[self.current_sprite]

    attacks = ['EVIL SPIRITS', 'SMOG BALL', 'INFECTION', 'SLEEP']

    # comments used to describe the effect_attack from Fire class can be used here
    # differences: gives enemy a sleeping status, there is a 30 percent chance of the attack failing
    # if the attack fails, the turn goes to the other player
    def effect_attack(self, enemy):
        global message
        if not enemy.has_effect():
            if self.stamina < 20:
                message = f'\nSorry, {self.name} doesn\'t have enough stamina to perform this attack'
                draw_message()
                return False
            else:
                self.stamina -= 20
            chance = random.randint(0, 10)
            if chance <= 7:
                enemy.sleep[0] = True
                enemy.hit[0] = True
                hit_sound.play()
                message = f'{enemy.name} has the sleep effect for a maximum of 3 of its attacking rounds!'
                draw_message()
                return True
            else:
                message = f'Sleep attack failed...'
                draw_message()
                return True
        else:
            message = f'You cannot use this attack because {enemy.name} is already affected by an effect'
            draw_message()
            return False


# Button class that allows for easy creation of buttons
# each button can have its unique color, hover color, coordinate, dimensions, and text color
class Button:
    def __init__(self, color, over_color, x, y, width, height, text_color, text=''):
        self.color = color
        self.ori_color = color
        self.over_color = over_color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.text_color = text_color
        self.is_click = False

    # this method draws the button along with its outline and text
    # the button will change colors depending on if the mouse is over it
    def draw(self, window, textSize, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(window, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        if self.is_over():
            self.color = self.over_color
        else:
            self.color = self.ori_color

        if not self.is_click:
            pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height), 0)
        else:
            pygame.draw.rect(window, self.color, (self.x + 5, self.y + 5, self.width - 10, self.height - 10), 0)

        if self.text != '':
            font = pygame.font.SysFont('dinalternate', textSize)
            text = font.render(self.text, True, self.text_color)
            window.blit(text,
                        (self.x + (self.width / 2 - text.get_width() / 2),
                         self.y + (self.height / 2 - text.get_height() / 2)))

    # checks if the mouse is within the button using math
    def is_over(self):
        pos = pygame.mouse.get_pos()
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height:
            return True
        else:
            return False


# the two Monsters switches sides on the screen
# we will go back to main screen
def change_turn(sw, pl1, pl2):
    global screen
    if sw:
        pl1.move_side()
        pl2.move_side()
        screen = 0


# function draws messages with a text animations using a nested game loop
def draw_message():
    global message
    global mes_index
    global screen
    global move
    global hit
    global cooldown_st_mov
    global cooldown_cur_mov
    global cooldown_st_hit
    global cooldown_cur_hit
    global in_play
    previous_screen = screen
    screen = 3
    breakout = False
    while True:
        if not in_play:
            break
        draw_screen(move, hit, message, mes_index, over, tie)
        mes_index += 1
        cooldown_cur_mov = pygame.time.get_ticks()
        cooldown_cur_hit = pygame.time.get_ticks()

        # get the current image for the sprites
        p1.get_current()
        p2.get_current()

        # cooldown for moving animation
        if cooldown_cur_mov - cooldown_st_mov >= 500:
            move = True
            cooldown_st_mov = cooldown_cur_mov
        else:
            move = False

        # cooldown for change the color of the Monster
        if cooldown_cur_hit - cooldown_st_hit >= 200:
            hit = True
            cooldown_st_hit = cooldown_cur_hit
        else:
            hit = False

        for i in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if i.type == pygame.QUIT:
                in_play = False
            if i.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(0, int(win.get_height() * 0.75), win.get_width(),
                               int(win.get_height() * 0.25)).collidepoint(pos):
                    breakout = True
        if breakout:
            mes_index = 0
            if previous_screen == 4:
                screen = 4
            else:
                screen = 1
            break

        clock.tick(60)


# this feeds the draw_screen function with the correct letters at the correct positions to create the text animation
def display_message(message, index, move):
    global previous_blink
    x = 180
    y = 550
    coord = []
    new_line = False
    blinker = False
    font = pygame.font.SysFont('dinalternate', 30)
    blink = font.render('_', True, BLUE)

    for n, letter in enumerate(message):
        coord.append((x, y))
        if letter in 'mwMW':
            x += 22
        elif letter in 'ftilIL':
            x += 8
        else:
            x += 14
        if n % 45 == 0 and n != 0:
            if letter == ' ':
                x = 180
                y += 35
            else:
                new_line = True

        if letter == ' ' and new_line:
            x = 180
            y += 35
            new_line = False

    if index >= len(message) - 1:
        index = len(message) - 1
        blinker = True

    if move:
        if previous_blink:
            previous_blink = False
        else:
            previous_blink = True

    if not previous_blink:
        blinker = False

    for n in range(index + 1):
        text = font.render(message[n], True, BLUE)
        win.blit(text, coord[n])
        if blinker:
            win.blit(blink, (coord[-1][0] + 16, coord[-1][1]))


# draws what is necessary on every screen
# this includes background, Monsters, health, and effect icons
def draw_necessary(move, hit):
    win.blit(background, (0, 0))
    p1.draw(move, hit)
    p2.draw(move, hit)
    p1.draw_health()
    p2.draw_health()
    p1.draw_icon()
    p2.draw_icon()


# draws the screen based on which screen we are currently on and whether the game is over or tied
def draw_screen(move, hit, message, mes_index, over, tie):
    if not over and not tie:
        draw_necessary(move, hit)

        # main screen, draws the 3 tasks users can perform
        if screen == 0:
            battle.draw(win, 35, BLACK)
            stats.draw(win, 35, BLACK)
            heal.draw(win, 35, BLACK)

        # battle screen, draws the move buttons and also back button
        elif screen == 1:
            if p1.turn:
                p1.draw_moves()
            else:
                p2.draw_moves()
            win.blit(arrow, (50, 530))

        # stats screen, displays the stats and draws the back button
        elif screen == 2:
            p1.display_stats('Player 1', (200, 540))
            p2.display_stats('Player 2', (200, 630))
            win.blit(arrow, (50, 530))

        # message screen, displays the message with a cool text animation
        elif screen == 3:
            display_message(message, mes_index, move)

        # heal screen, draws the heal buttons and also back button
        elif screen == 4:
            health.draw(win, 20, BLACK)
            stamina.draw(win, 20, BLACK)
            win.blit(arrow, (50, 530))

    # game is either over or tied
    else:
        # make the Monsters face toward the camera and make the background dirt colored
        p1.current_sprite = 0
        p2.current_sprite = 0
        p1.get_current()
        p2.get_current()
        win.fill(DIRT)

        # the winner Monster is placed in the green rectangle labeled "winner" and the loser Monster is placed in the
        #   red rectangle labeled "loser"
        # if it's a tie, both Monsters are placed in green rectangles labeled "winner"
        if not tie:
            pygame.draw.rect(win, GREEN, (win.get_width() // 2 - 350, win.get_height() // 2 - 300, 300, 480))
            pygame.draw.rect(win, RED, (win.get_width() // 2 + 50, win.get_height() // 2 - 300, 300, 480))
            win.blit(winner, (win.get_width() // 2 - 200 - winner.get_width() // 2, win.get_height() // 2 + 140))
            win.blit(loser, (win.get_width() // 2 + 200 - loser.get_width() // 2, win.get_height() // 2 + 140))
        else:
            pygame.draw.rect(win, GREEN, (win.get_width() // 2 - 350, win.get_height() // 2 - 300, 300, 480))
            pygame.draw.rect(win, GREEN, (win.get_width() // 2 + 50, win.get_height() // 2 - 300, 300, 480))
            win.blit(winner, (win.get_width() // 2 - 200 - winner.get_width() // 2, win.get_height() // 2 + 140))
            win.blit(winner, (win.get_width() // 2 + 200 - winner.get_width() // 2, win.get_height() // 2 + 140))

        if p1.status():
            win.blit(p1.image, (win.get_width() // 2 - 200 - 100, win.get_height() // 2 - 200))
            win.blit(p2.image, (win.get_width() // 2 + 200 - 100, win.get_height() // 2 - 200))
        else:
            win.blit(p2.image, (win.get_width() // 2 - 200 - 100, win.get_height() // 2 - 200))
            win.blit(p1.image, (win.get_width() // 2 + 200 - 100, win.get_height() // 2 - 200))

        # the quit button is drawn at the middle bottom
        quit_game.draw(win, 30, BLACK)

    pygame.display.update()


# the instructions are read from a text file called readme.txt and printed to the screen
f = open('readme.txt', 'r')
print(f.read())
f.close()

# the players choose what type they want their Monsters to be, the get_type method is called to do this
# the type-specific Monster object is instantiated and created using the make_monster method
# then they have the option to change the default names of the Monsters, the get_name method is used
# after they are done setting up their Monsters, the stats of their Monsters are displayed
print('\n[Player 1] Choose an element for your Monster')
p1_type = Monster.get_type()
p1 = Monster.make_monster(p1_type)
p1.get_name('Player 1')
print('\n[Player 2] Choose an element for your Monster')
p2_type = Monster.get_type()
p2 = Monster.make_monster(p2_type)
p2.get_name('Player 2')

# to determine who goes first, we compare the speed stats of the two Monsters
# if the speed stats are the same, a coin is flipped to determine who goes first
if p1.speed > p2.speed:
    print(f'\n\n[Player 1] {p1.name} is going first because it\'s faster than {p2.name}')
    p1.turn = True
    p1.current_sprite = 1
elif p2.speed > p1.speed:
    print(f'\n\n[Player 2] {p2.name} is going first because it\'s faster than {p1.name}')
    p2.turn = True
    p2.current_sprite = 1
else:
    coin = random.getrandbits(1)
    turn = bool(coin)
    if coin:
        print(f'\n\nDue to similar speed stats, a coin was rolled and [Player 1] {p1.name} is going first')
        p1.turn = True
        p1.current_sprite = 1
    else:
        print(f'\n\nDue to similar speed stats, a coin was rolled and [Player 2] {p2.name} is going first')
        p2.turn = True
        p2.current_sprite = 1

# setting up the window and opening it
win = pygame.display.set_mode((WIDTH, LENGTH))
pygame.display.set_caption('Monster Battle 1')

# music is played and will be played indefinitely since game is starting
theme.play(-1)

# the menu buttons are initialized/created
battle = Button(CRIMSON, RED, win.get_width() / 2 - 480, 535, 300, 150, BLACK, 'BATTLE')
stats = Button(CRIMSON, RED, win.get_width() / 2 - 150, 535, 300, 150, BLACK, 'STATS')
heal = Button(CRIMSON, RED, win.get_width() / 2 + 180, 535, 300, 150, BLACK, 'HEAL')
health = Button(DARK_GREEN, GREEN, win.get_width() // 2 - 200, 560, 180, 80, BLACK, 'HEALTH')
stamina = Button(DARK_GREEN, GREEN, win.get_width() // 2 + 20, 560, 180, 80, BLACK, 'STAMINA')
quit_game = Button(CRIMSON, RED, win.get_width() / 2 - 100, 600, 200, 100, BLACK, 'QUIT')

# getting the time passed
cooldown_st_mov = pygame.time.get_ticks()
cooldown_st_hit = pygame.time.get_ticks()

# game loop will run until in_play is false
while in_play:

    # drawing and updating the screen
    draw_screen(move, hit, message, mes_index, over, tie)

    # this is for iterating through a message to perform the text animation
    if cycle_letter:
        mes_index += 1

    # get the current time passed
    cooldown_cur_mov = pygame.time.get_ticks()
    cooldown_cur_hit = pygame.time.get_ticks()

    # get the current image for the sprites
    p1.get_current()
    p2.get_current()

    # cooldown for moving animation
    if cooldown_cur_mov - cooldown_st_mov >= 500:
        move = True
        cooldown_st_mov = cooldown_cur_mov
    else:
        move = False

    # cooldown for change the color of the Monster
    if cooldown_cur_hit - cooldown_st_hit >= 200:
        hit = True
        cooldown_st_hit = cooldown_cur_hit
    else:
        hit = False

    # if Monster run out of stamina and doesn't have elixir but the other Monster still has stamina, its turn is
    #   skipped
    # if Monster is sleeping, their turn is skipped
    if p1.turn and not over and not tie:
        if p1.stamina < 20 and p2.stamina >= 20 and p1.elixr == 0:
            message = f'{p1.name} no longer has enough stamina to attack.'
            draw_message()
            change_turn(True, p1, p2)
        if p1.sleep[0]:
            still_sleeping = p1.get_sleep()
            if still_sleeping:
                change_turn(True, p1, p2)
            else:
                screen = 0
    elif p2.turn and not over and not tie:
        if p2.stamina < 20 and p1.stamina >= 20 and p2.elixr == 0:
            message = f'{p2.name} no longer has enough stamina to attack.'
            draw_message()
            change_turn(True, p1, p2)
        if p2.sleep[0]:
            still_sleeping = p2.get_sleep()
            if still_sleeping:
                change_turn(True, p1, p2)
            else:
                screen = 0

    # if both players run out of stamina and don't have any elixirs left, the game is a tie
    if p1.stamina < 20 and p2.stamina < 20 and p1.elixr == 0 and p2.elixr == 0 and not over and not tie:
        message = f'{p1.name} and {p2.name} are both exhausted. The result of this battle is a tie!'
        draw_message()
        tie = True

    # listening for the user inputs
    for i in pygame.event.get():
        pos = pygame.mouse.get_pos()

        # no button is pressed if mouse button is up
        if i.type == pygame.MOUSEBUTTONUP:
            battle.is_click = False
            stats.is_click = False
            heal.is_click = False

        # if player press the x, program is over
        if i.type == pygame.QUIT:
            in_play = False

        # checking for clicks
        if i.type == pygame.MOUSEBUTTONDOWN:

            # only check if game is not over or tied
            if not over and not tie:

                # checking if the main screen buttons are pressed
                # screen gets changed based on which button is pressed
                if screen == 0:
                    if battle.is_over():
                        b_press.play()
                        battle.is_click = True
                        screen = 1
                    elif stats.is_over():
                        b_press.play()
                        stats.is_click = True
                        screen = 2
                    elif heal.is_over():
                        b_press.play()
                        heal.is_click = True
                        screen = 4

                # if we are on the battle screen, check if the move buttons are pressed
                # if they are, check which move button is pressed and its corresponding attack move method is called
                # if the attack was successful, the turns are switched and the Monsters switch sides
                # then the game checks if any Monster fainted. If yes, game is over.
                # the checker method also makes the Monsters get burned or poisoned if they have those effects
                elif screen == 1:
                    if p1.turn:
                        blist = p1.draw_moves()
                        for n, button in enumerate(blist):
                            if button.is_over():
                                if n == 0:
                                    switch = p1.special_attack(p2)
                                elif n == 1:
                                    switch = p1.rapid_attack(p2)
                                elif n == 2:
                                    switch = p1.normal_attack(p2)
                                else:
                                    switch = p1.effect_attack(p2)
                                if switch:
                                    over = p1.checker(p2, 'Player 1', 'Player 2')
                                change_turn(switch, p1, p2)
                                break
                    else:
                        blist = p2.draw_moves()
                        for n, button in enumerate(blist):
                            if button.is_over():
                                if n == 0:
                                    switch = p2.special_attack(p1)
                                elif n == 1:
                                    switch = p2.rapid_attack(p1)
                                elif n == 2:
                                    switch = p2.normal_attack(p1)
                                else:
                                    switch = p2.effect_attack(p1)
                                if switch:
                                    over = p2.checker(p1, 'Player 2', 'Player 1')
                                change_turn(switch, p1, p2)
                                break

                    # if the back button is pressed, game goes back to main screen
                    if pygame.Rect(50, 530, 100, 50).collidepoint(pos):
                        screen = 0

                # checking if buttons on stats screen are pressed
                elif screen == 2:

                    # if the back button is pressed, game goes back to main screen
                    if pygame.Rect(50, 530, 100, 50).collidepoint(pos):
                        screen = 0

                # checking if heal screen buttons are pressed
                # once heal is used, the Monsters switch turns
                elif screen == 4:
                    if p1.turn:
                        if health.is_over():
                            switch = p1.restore_health()
                            if switch:
                                over = p1.checker(p2, 'Player 1', 'Player 2')
                            change_turn(switch, p1, p2)
                        elif stamina.is_over():
                            switch = p1.restore_stamina()
                            if switch:
                                over = p1.checker(p2, 'Player 1', 'Player 2')
                            change_turn(switch, p1, p2)
                    else:
                        if health.is_over():
                            switch = p2.restore_health()
                            if switch:
                                over = p1.checker(p1, 'Player 2', 'Player 1')
                            change_turn(switch, p1, p2)
                        elif stamina.is_over():
                            switch = p2.restore_stamina()
                            if switch:
                                over = p1.checker(p1, 'Player 2', 'Player 1')
                            change_turn(switch, p1, p2)

                    # if the back button is pressed, game goes back to main screen
                    if pygame.Rect(50, 530, 100, 50).collidepoint(pos):
                        screen = 0

            # if we are in game over screen, check if the quit button is pressed. Game will quit if it is pressed.
            elif over or tie:
                if quit_game.is_over():
                    in_play = False

    # if we are in game over screen, stop the main game music and play the game end music
    if (over or tie) and (not played):
        theme.stop()
        end_theme.play(-1)
        played = True

    # game refreshes at 60 FPS
    clock.tick(60)

# if we escape the loop, pygame will quit
pygame.quit()
