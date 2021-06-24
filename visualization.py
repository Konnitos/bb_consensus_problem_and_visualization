import pygame
import os
from bb_consensus_simulation import run_bb_simulation

SCREENRECT = pygame.Rect(0, 0, 900 , 600)
FPS = 60
NUM_OF_TRAITORS = 0
NUM_OF_NODES = 2
FORCE_TRAITOR_LEADER = False
START_SCREEN = True

def load_image(file):
    """ loads an image, prepares it for play
    """
    file = os.path.join("assets", file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pygame.get_error()))
    return surface.convert_alpha()

def load_sound(file):
    """ because pygame can be be compiled without mixer.
    """
    if not pygame.mixer:
        return None
    file = os.path.join("assets", file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print("Warning, unable to load, %s" % file)
    return None

class Leader(pygame.sprite.Sprite):
    images = []

    def __init__(self, starting_point):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=starting_point)

class General(pygame.sprite.Sprite):
    images = []

    def __init__(self, starting_point):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=starting_point)

class Message(pygame.sprite.Sprite):
    images = []

    def __init__(self, starting_point):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=starting_point)

class CheckButton(pygame.sprite.Sprite):
    images = []
    checked = FORCE_TRAITOR_LEADER

    def __init__(self, starting_point, callback):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[self.checked]
        self.rect = self.image.get_rect(topleft=starting_point)
        self.callback = callback

    def update(self):
        self.checked = FORCE_TRAITOR_LEADER
        self.image = self.images[self.checked]

class Button(pygame.sprite.Sprite):
    def __init__(self, starting_point, image, callback):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image
        self.rect = self.image.get_rect(topleft=starting_point)
        self.callback = callback

class Text_field(pygame.sprite.Sprite):
    def __init__(self, starting_point, text, font_size):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(None, font_size)
        self.color = pygame.Color("Black")
        self.text = text
        self.update()
        self.rect = self.image.get_rect(topleft=starting_point)    

    def update(self):
        self.image = self.font.render(self.text, 0, self.color)

class Node_count_text_field(pygame.sprite.Sprite):
    def __init__(self, starting_point, font_size):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(None, font_size)
        self.color = pygame.Color("Black")
        self.update()
        self.rect = self.image.get_rect(topleft=starting_point)    

    def update(self):
        self.image = self.font.render(str(NUM_OF_NODES), 0, self.color)        

class Traitor_count_text_field(pygame.sprite.Sprite):
    def __init__(self, starting_point, font_size):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(None, font_size)
        self.color = pygame.Color("Black")
        self.update()
        self.rect = self.image.get_rect(topleft=starting_point)    

    def update(self):
        self.image = self.font.render(str(NUM_OF_TRAITORS), 0, self.color)        

def main():
    # Used for set frames per second
    clock = pygame.time.Clock()
    
    # init sound system
    if pygame.get_sdl_version()[0] == 2:
        pygame.mixer.pre_init(44100, 32, 2, 1024)
    pygame.init()
    if pygame.mixer and not pygame.mixer.get_init():
        print("Warning, no sound")
        pygame.mixer = None

    screen = pygame.display.set_mode(SCREENRECT.size)

    # setting up background
    bg = load_image("bg.png")
    background = pygame.Surface(SCREENRECT.size)
    background.blit(bg, (0,0))
    screen.blit(background, (0,0))
    pygame.display.flip()

    # loading in assets
    leader = load_image("leader.png")
    arrow = load_image("arrow.png")
    Leader.images = [leader]
    General.images = [load_image("general.png")]
    Message.images = [load_image("letter.png")] 
    CheckButton.images = [load_image("uncheckedbox.png"), load_image("checkedbox.png")]
    pop = load_sound("pop.mp3")
    dink = load_sound("dink.wav")
    valid_message = load_sound("valid_message.ogg")

    # setting basic window view
    icon = pygame.transform.scale(leader,(32,32))
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Byzantine General Consensus Problem")

    nodes = pygame.sprite.Group()
    messages = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()

    Leader.containers = nodes, all
    General.containers = nodes, all
    Message.containers = messages, all
    CheckButton.containers = all
    Button.containers = all
    Text_field.containers = all
    Node_count_text_field.containers = all
    Traitor_count_text_field.containers = all

    buttons = []

       
    Text_field((20,20), "BB Consensus In Action", 100)

    force_traitor_leader_button = CheckButton((20, 100), force_traitor_leader_checkbox_callback)
    buttons.append(force_traitor_leader_button)

    Text_field((force_traitor_leader_button.rect.right + 10, force_traitor_leader_button.rect.y + 5), "Force the leader to be a traitor?", 30)

    number_of_nodes_text_field = Text_field((20,180), "Number of Nodes:", 30)
    node_count_text_field_x = (number_of_nodes_text_field.rect.right - number_of_nodes_text_field.rect.left)/2
    node_count_text_field = Node_count_text_field((node_count_text_field_x, 200), 100)
    node_count_up_button = Button((node_count_text_field.rect.right, node_count_text_field.rect.top), arrow, num_of_node_increase_callback)
    buttons.append(node_count_up_button)
    node_count_down_button = Button((node_count_text_field.rect.right,node_count_up_button.rect.bottom), pygame.transform.rotate(arrow, 180), num_of_node_decrease_callback)
    buttons.append(node_count_down_button)

    number_of_traitors_text_field = Text_field((20,280), "Number of Traitors:", 30)
    traitor_count_text_field_x = (number_of_traitors_text_field.rect.right - number_of_traitors_text_field.rect.left)/2
    triator_count_text_field = Traitor_count_text_field((traitor_count_text_field_x, 300), 100)
    traitor_count_up_button = Button((triator_count_text_field.rect.right, triator_count_text_field.rect.top), arrow, num_of_traitors_increase_callback)
    buttons.append(traitor_count_up_button)
    traitor_count_down_button = Button((triator_count_text_field.rect.right, traitor_count_up_button.rect.bottom), pygame.transform.rotate(arrow, 180), num_of_traitors_decrease_callback)
    buttons.append(traitor_count_down_button)

    start_simulation_text_field = Text_field((20, 400), "Start Simulation !", 40)
    start_simulation_button = Button((start_simulation_text_field.rect.right + 10, start_simulation_text_field.rect.top), pygame.transform.rotate(arrow, -90), start_simulation_callback)
    buttons.append(start_simulation_button)
    
    all.update()

    dirty = all.draw(screen)
    pygame.display.update(dirty)

    # messages_sent_by_nodes_per_round = run_bb_simulation_and_process_output()

    run = True
    pause = False
    while run:

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pause = not pause
                print(pause)

            if(pause): break

            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                for button in buttons:
                    if button.rect.collidepoint(x,y):
                        button.callback()

        if(pause): continue

        all.clear(screen,background)

        all.update()

        dirty = all.draw(screen)
        pygame.display.update(dirty)

        clock.tick(FPS)

    # pygame.quit()

def force_traitor_leader_checkbox_callback():
    global FORCE_TRAITOR_LEADER
    FORCE_TRAITOR_LEADER = not FORCE_TRAITOR_LEADER

def num_of_node_increase_callback():
    global NUM_OF_NODES
    if(NUM_OF_NODES < 5):
        NUM_OF_NODES += 1

def num_of_node_decrease_callback():
    global NUM_OF_NODES
    if(NUM_OF_NODES > 2):
        NUM_OF_NODES -= 1

def num_of_traitors_increase_callback():
    global NUM_OF_TRAITORS
    if(NUM_OF_NODES - 1 > NUM_OF_TRAITORS):
        NUM_OF_TRAITORS += 1

def num_of_traitors_decrease_callback():
    global NUM_OF_TRAITORS
    if(NUM_OF_TRAITORS > 0):
        NUM_OF_TRAITORS -= 1

def start_simulation_callback():
    global START_SCREEN 
    START_SCREEN = False

def run_bb_simulation_and_process_output():
    network = run_bb_simulation(NUM_OF_NODES, NUM_OF_TRAITORS, FORCE_TRAITOR_LEADER)
    return None   

if __name__ == "__main__":
    main()
