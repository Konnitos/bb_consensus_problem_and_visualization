from Node import Node
import pygame
import pygame.examples.aliens
import os
from bb_consensus_simulation import run_bb_simulation

SCREENRECT = pygame.Rect(0, 0, 900 , 600)
FPS = 60
NUM_OF_TRAITORS = 0
NUM_OF_NODES = 2
FORCE_TRAITOR_LEADER = False
START_SCREEN = True
REPLAY_SCREEN = False


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

    def __init__(self, starting_point, is_traitor = False):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[is_traitor] 
        self.rect = self.image.get_rect(topleft=starting_point)

class General(pygame.sprite.Sprite):
    images = []

    def __init__(self, starting_point, is_traitor = False):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[is_traitor] 
        self.rect = self.image.get_rect(topleft=starting_point)
        self.extracted_set = set()

class Message(pygame.sprite.Sprite):
    images = []
    speed = 5

    def __init__(self, starting_point, payload, y_distance, is_up, enter_left, is_valid):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=starting_point)
        self.payload = payload
        self.leave_start_x = self.rect.right + 100
        self.leave_start_x_done = False
        self.y_distance = abs(y_distance)
        self.y_moved = 0
        self.is_up = is_up
        self.y_distance_done = False
        self.enter_x_value = 100
        self.enter_x_moved = 0
        self.enter_left = enter_left
        self.enter_x_done = False
        self.step = 0
        self.is_valid = is_valid
        self.text_field = Text_field((self.rect.left, self.rect.top), str(self.payload), 30)

    def update(self):
        if(self.step == 0):
            self.exit()

        if(self.step == 1):
            self.y_change()

        if(self.step == 2):
            self.enter()

        self.text_field.rect = self.rect

    def exit(self):
        if(self.rect.right <= self.leave_start_x and not self.leave_start_x_done):
            self.rect.move_ip(self.speed,0)
        else: 
            self.leave_start_x_done = True
            self.step = 1

    def y_change(self):
        if(self.y_moved <= self.y_distance):
            self.y_moved += self.speed
            self.rect.move_ip(0,(self.speed * self.is_up))
        else:
            self.y_distance_done = True
            # self.step = 2

    def enter(self):
        if(self.enter_x_moved <= self.enter_x_value):
            self.enter_x_moved += self.speed
            self.rect.move_ip((self.speed * self.enter_left), 0 )
        else:
            self.enter_x_done = True
            
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
    Leader.images = [leader, load_image("tleader.png")]
    General.images = [load_image("general.png"), load_image("tgeneral.png")]
    Message.images = [load_image("letter.png")] 
    CheckButton.images = [load_image("uncheckedbox.png"), load_image("checkedbox.png")]

    # setting basic window view
    icon = pygame.transform.scale(leader,(32,32))
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Byzantine General Consensus Problem")

    node_group = pygame.sprite.Group()
    message_group = pygame.sprite.Group()
    button_group = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()

    Leader.containers = node_group, all
    General.containers = node_group, all
    Message.containers = message_group, all
    CheckButton.containers = button_group, all
    Button.containers = button_group, all
    Text_field.containers = all
    Node_count_text_field.containers = all
    Traitor_count_text_field.containers = all

    start_screen(clock, screen, background, arrow, all, button_group)
    
    all.clear(screen, background)
    all.empty()
    pygame.display.update()
    
    bb_replay(clock, screen,background, all, node_group, message_group)
    
def start_screen(clock, screen, background, arrow, all, button_group):
    
    Text_field((20,20), "BB Consensus In Action", 100)

    force_traitor_leader_button = CheckButton((20, 100), force_traitor_leader_checkbox_callback)
    

    Text_field((force_traitor_leader_button.rect.right + 10, force_traitor_leader_button.rect.y + 5), "Force the leader to be a traitor?", 30)

    number_of_nodes_text_field = Text_field((20,180), "Number of Nodes:", 30)
    node_count_text_field_x = (number_of_nodes_text_field.rect.right - number_of_nodes_text_field.rect.left)/2
    node_count_text_field = Node_count_text_field((node_count_text_field_x, 200), 100)
    node_count_up_button = Button((node_count_text_field.rect.right, node_count_text_field.rect.top), arrow, num_of_node_increase_callback)
    node_count_down_button = Button((node_count_text_field.rect.right,node_count_up_button.rect.bottom), pygame.transform.rotate(arrow, 180), num_of_node_decrease_callback)
    
    number_of_traitors_text_field = Text_field((20,280), "Number of Traitors:", 30)
    traitor_count_text_field_x = (number_of_traitors_text_field.rect.right - number_of_traitors_text_field.rect.left)/2
    triator_count_text_field = Traitor_count_text_field((traitor_count_text_field_x, 300), 100)
    traitor_count_up_button = Button((triator_count_text_field.rect.right, triator_count_text_field.rect.top), arrow, num_of_traitors_increase_callback)
    traitor_count_down_button = Button((triator_count_text_field.rect.right, traitor_count_up_button.rect.bottom), pygame.transform.rotate(arrow, 180), num_of_traitors_decrease_callback)
    
    start_simulation_text_field = Text_field((20, 400), "Start Simulation !", 40)
    start_simulation_button = Button((start_simulation_text_field.rect.right + 10, start_simulation_text_field.rect.top), pygame.transform.rotate(arrow, -90), start_simulation_callback)

    while START_SCREEN:

        for event in pygame.event.get():
        
            if event.type == pygame.QUIT:
                pygame.quit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                for button in button_group.sprites():
                    if button.rect.collidepoint(x,y):
                        button.callback()

        all.clear(screen,background)

        all.update()

        dirty = all.draw(screen)
        pygame.display.update(dirty)

        clock.tick(FPS)

def bb_replay(clock , screen , background, all, node_group, message_group):
    
    Text_field((20,20), "Simulating BB Consensus", 75)

    all.update()
    pygame.display.update(all.draw(screen))

    network = run_bb_simulation(NUM_OF_NODES, NUM_OF_TRAITORS, FORCE_TRAITOR_LEADER)
    round_dict = run_bb_simulation_and_process_output(network)

    pop = load_sound("pop.mp3")
    dink = load_sound("dink.wav")
    message_out = load_sound("message_out.mp3")
    valid_message = load_sound("valid_message.ogg")
    
    pygame.time.wait(1000)
    all.clear(screen, background)
    all.empty()
    pygame.display.update()
    
    buttons = []
    nodes = []
    general_sets = {}

    leader = Leader((64, (SCREENRECT.bottom/2) -32), network[0].is_traitor)
    pygame.display.update(all.draw(screen))
    pop.play()
    nodes.append(leader)

    for i in range(1, NUM_OF_NODES):
        pygame.time.wait(500)
        general = General((320, (i*104)), network[i].is_traitor)
        general_extracted_set = Text_field((general.rect.left, general.rect.bottom + 5), str(general.extracted_set), 40)

        pygame.display.update(all.draw(screen))
        pop.play()

        nodes.append(general)
        general_sets[i] = general_extracted_set

    pygame.time.wait(500)
    
    round_count= 1 
    node_sending = 0

    round_text_field = Text_field((0,0), "Round: ", 70)
    round_count_text_field = Text_field((round_text_field.rect.right,0), str(round_count) ,70)

    sent_messages = draw_messages(round_count, node_sending, nodes, round_dict, all , screen, message_out)

    pause = False
    while REPLAY_SCREEN:

        for event in pygame.event.get():

            if(pause): break

            if event.type == pygame.QUIT:
                pygame.quit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                for button in buttons:
                    if button.rect.collidepoint(x,y):
                        button.callback()

        if(pause): continue

        all.clear(screen,background)

        round_count_text_field.text = str(round_count)

        for (id, set_text_field) in general_sets.items():
            set_text_field.text = str(nodes[id].extracted_set)

        all.update()

        for (node, message_list) in pygame.sprite.groupcollide(node_group, message_group, 0, 1).items():
            if(message_list[0].is_valid):
                valid_message.play()
                node.extracted_set.add(message_list[0].payload)
            else:
                dink.play()

        dirty = all.draw(screen)
        pygame.display.update(dirty)

        clock.tick(FPS)

    pygame.quit()

def draw_messages(round_count, node_sending, nodes, round_dict, all, screen, message_out):
    messages_to_draw = round_dict[round_count][node_sending]
    messages = []

    print([x.__dict__ for x in messages_to_draw])

    for message in messages_to_draw:
        print(message.payload)
        starting_node = nodes[message.sender_id]
        ending_node = nodes[message.reciver_id]        

        y_distance = (ending_node.rect.top - starting_node.rect.top) + 24
        is_up = -1 if (y_distance < 0 ) else 1
        enter_left = 1 if (node_sending == 0) else -1
        sending_message = Message((starting_node.rect.right + 3, starting_node.rect.top + 16), message.payload, y_distance, is_up, enter_left, message.is_valid)

        messages.append(sending_message)
    
    message_out.play()
    return messages
        

def force_traitor_leader_checkbox_callback():
    global FORCE_TRAITOR_LEADER    
    if(NUM_OF_TRAITORS > 0):
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
    global REPLAY_SCREEN
    START_SCREEN = False
    REPLAY_SCREEN = True

def run_bb_simulation_and_process_output(network: dict[Node]):

    round_dict = {}

    for i in range(0, NUM_OF_TRAITORS + 1):
        round_dict[i + 1] = {}
        for j in range(0, NUM_OF_NODES):
            round_dict[i + 1][j] = []

    for id, node in network.items():
        for message in node.all_messages:
            message.reciver_id = id
            message.is_valid = message in node.valid_messages
            round_dict[message.round_sent][message.sender_id].append(message)

    return round_dict   

if __name__ == "__main__":
    main()
