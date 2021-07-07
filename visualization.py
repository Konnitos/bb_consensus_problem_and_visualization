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
DEFULT_VALUE = 1


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

    def __init__(self, starting_point, is_traitor = False, is_consensus_time = False, original_order = 0):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[is_traitor] 
        self.is_traitor = is_traitor
        self.is_consensus_time = is_consensus_time
        self.orignal_order = original_order
        self.rect = self.image.get_rect(topleft=starting_point)

    def update(self):
        if(self.is_consensus_time and not self.is_traitor):
            Text_field((self.rect.left - 32, self.rect.top - 32), "We should Attack!!" if self.orignal_order else "We should Retreat!!", 35)

class General(pygame.sprite.Sprite):
    images = []

    def __init__(self, starting_point, is_traitor = False):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[is_traitor] 
        self.is_traitor = is_traitor
        self.decision = None
        self.rect = self.image.get_rect(topleft=starting_point)
        self.extracted_set = set()

    def update(self):
        if(not self.is_traitor and self.decision != None):
            Text_field((self.rect.right +30, self.rect.top + 15), "ATTACK!!!!" if self.decision else "RETREAT!!!!", 35) 

class Message(pygame.sprite.Sprite):
    images = []
    speed = 5

    def __init__(self, starting_point, payload, y_distance, is_up, enter_left, is_valid, signatures = []):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=starting_point)
        self.payload = payload
        self.leave_start_x = self.rect.right + 140
        self.leave_start_x_done = False
        self.y_distance = abs(y_distance)
        self.y_moved = 0
        self.is_up = is_up
        self.y_distance_done = False
        self.enter_x_value = 180
        self.enter_x_moved = 0
        self.enter_left = enter_left
        self.enter_x_done = False
        self.step = 0
        self.is_valid = is_valid
        self.text_field = Text_field((self.rect.left, self.rect.top), str(self.payload), 35)
        self.life_time = 0
        self.signature_text_field = Text_field((self.rect.left, self.rect.bottom + 5), f"Sign:{signatures}", 30)

    def update(self):
        if(self.step == 0):
            self.exit()

        if(self.step == 1):
            self.y_change()

        if(self.step == 2):
            self.enter()
        
        if(self.step == 3):
            self.backup_die()

        self.text_field.rect = self.rect
        self.signature_text_field.rect.x = self.rect.x
        self.signature_text_field.rect.y = self.rect.bottom + 5

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
            self.life_time += 1
            if(self.life_time > 60):
                self.life_time = 0
                self.step = 2

    def enter(self):
        if(self.enter_x_moved <= self.enter_x_value):
            self.enter_x_moved += self.speed
            self.rect.move_ip((self.speed * self.enter_left), 0 )
        else:
            self.enter_x_done = True
            

    def backup_die(self):
        if(self.life_time < 10):
            self.life_time += 1
            self.rect.move_ip((self.speed * (0 - self.enter_left)), 0 )
        else:
            self.kill()

            
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
    pause = load_image("pause.png")
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
    general_group = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()

    Leader.containers = node_group, all
    General.containers = node_group, general_group, all
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
    
    bb_replay(clock, screen,background, all, node_group, message_group, button_group, general_group, arrow, pause)
    
def start_screen(clock, screen, background, arrow, all, button_group):
    
    Text_field((20,20), "BB Consensus In Action", 100)

    number_of_nodes_text_field = Text_field((20,100), "Number of Nodes:", 30)
    node_count_text_field_x = (number_of_nodes_text_field.rect.right - number_of_nodes_text_field.rect.left)/2
    node_count_text_field = Node_count_text_field((node_count_text_field_x, 120), 100)
    node_count_up_button = Button((node_count_text_field.rect.right, node_count_text_field.rect.top), arrow, num_of_node_increase_callback)
    node_count_down_button = Button((node_count_text_field.rect.right,node_count_up_button.rect.bottom), pygame.transform.rotate(arrow, 180), num_of_node_decrease_callback)
    
    number_of_traitors_text_field = Text_field((20,200), "Number of Traitors:", 30)
    traitor_count_text_field_x = (number_of_traitors_text_field.rect.right - number_of_traitors_text_field.rect.left)/2
    triator_count_text_field = Traitor_count_text_field((traitor_count_text_field_x, 220), 100)
    traitor_count_up_button = Button((triator_count_text_field.rect.right, triator_count_text_field.rect.top), arrow, num_of_traitors_increase_callback)
    traitor_count_down_button = Button((triator_count_text_field.rect.right, traitor_count_up_button.rect.bottom), pygame.transform.rotate(arrow, 180), num_of_traitors_decrease_callback)
    
    force_traitor_leader_button = CheckButton((20, 300), force_traitor_leader_checkbox_callback)
    Text_field((force_traitor_leader_button.rect.right + 10, force_traitor_leader_button.rect.y + 5), "Force the leader to be a traitor?", 30)
    
    Text_field((20, 350), "0 is Retreat and 1 is Attack, defult general behavior is 1", 40)

    start_simulation_text_field = Text_field((20, 500), "Start Simulation !", 40)
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

def bb_replay(clock , screen , background, all, node_group, message_group, button_group, general_group, arrow, pause):
    
    Text_field((20,20), "Simulating BB Consensus", 75)

    all.update()
    pygame.display.update(all.draw(screen))

    network = run_bb_simulation(NUM_OF_NODES, NUM_OF_TRAITORS, FORCE_TRAITOR_LEADER)
    round_dict = process_bb_simulation_output(network)
    round_count = 1

    pop = load_sound("pop.mp3")
    dink = load_sound("dink.wav")
    message_out = load_sound("message_out.mp3")
    valid_message = load_sound("valid_message.ogg")
    
    pygame.time.wait(1000)
    all.clear(screen, background)
    all.empty()
    pygame.display.update()
    
    restart_text_field = Text_field((20,550), "Back to Start? ", 40)
    Button((restart_text_field.rect.right + 10, 550), pygame.transform.rotate(arrow,90), restart_callback)

    pause_text_field = Text_field((restart_text_field.rect.right + 60,550), "Pause? ", 40)
    pause_button = Button((pause_text_field.rect.right + 10 , 550), pause, blank_callback)

    nodes = []
    general_sets = {}

    leader = Leader((64, (SCREENRECT.bottom/2) -32), network[0].is_traitor)
    Text_field((leader.rect.left, leader.rect.bottom +5), "Id: 0 Leader", 40)
    pygame.display.update(all.draw(screen))
    pop.play()
    nodes.append(leader)

    for i in range(1, NUM_OF_NODES):
        pygame.time.wait(500)
        general = General((360, (i*120)), network[i].is_traitor)
        general_extracted_set = Text_field((general.rect.left, general.rect.top - 40), f"Id:{i} Orders:", 40)

        pygame.display.update(all.draw(screen))
        pop.play()

        nodes.append(general)
        general_sets[i] = general_extracted_set

    pygame.time.wait(500)


    round_text_field = Text_field((0,0), "Round: ", 70)
    round_count_text_field = Text_field((round_text_field.rect.right,0), str(round_count) ,70)

    for message in message_group.sprites():
        if(message.y_distance_done):
            pygame.time.wait(250)
            message.step = 2

    pause = False
    messages_sent = 0
    messages_in_round = len(round_dict[round_count])
    coms_over = False

    while REPLAY_SCREEN:

        for event in pygame.event.get():
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                if pause_button.rect.collidepoint(x,y):
                    pause = not pause

            if event.type == pygame.QUIT:
                pygame.quit()

            if(pause): break

            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                for button in button_group.sprites():
                    if button.rect.collidepoint(x,y):
                        button.callback()

        if(pause): continue

        all.clear(screen,background)
        all.update()

        for (id, set_text_field) in general_sets.items():
            if(len(nodes[id].extracted_set) > 0):
                set_text_field.text = f"Id:{id} Orders:{nodes[id].extracted_set}"

        if(len(message_group.sprites()) < 1 and not coms_over):
            if(messages_sent < messages_in_round):
                pygame.time.wait(200)
                draw_message(nodes,round_dict[round_count][messages_sent], message_out)
            
            elif(round_count < NUM_OF_TRAITORS + 1):
                round_count += 1
                messages_sent = 0
                messages_in_round = len(round_dict[round_count])

            else:
                coms_over = True

        round_count_text_field.text = str(round_count)

        for (node, message_list) in pygame.sprite.groupcollide(node_group, message_group, 0, 0).items():
            if(message_list[0].is_valid):
                valid_message.play()
                node.extracted_set.add(message_list[0].payload)
                message_list[0].kill()
            else:
                message_list[0].step = 3
                dink.play()

            message_list[0].text_field.kill()
            message_list[0].signature_text_field.kill()
            messages_sent += 1

        if(coms_over and messages_sent == messages_in_round):
            if( not leader.is_traitor):
                leader.orignal_order = round_dict[1][0].payload
                leader.is_consensus_time = True

            for general in general_group:
                if(not general.is_traitor and general.decision == None):
                    general.decision = general.extracted_set.pop() if len(general.extracted_set) == 1 else DEFULT_VALUE



        dirty = all.draw(screen)
        pygame.display.update(dirty)

        clock.tick(FPS)

    pygame.quit()

def draw_message(nodes, message, message_out):

    starting_node = nodes[message.sender_id]
    ending_node = nodes[message.reciver_id]         
    signature_ids = [] if message.signatures == None else [x.signer_id for x in message.signatures if x != None]
    y_distance = (ending_node.rect.top - starting_node.rect.top)
    is_up = -1 if (y_distance < 0 ) else 1
    enter_left = 1 if (message.sender_id == 0) else -1
    Message((starting_node.rect.right + 3, starting_node.rect.top), message.payload, y_distance, is_up, enter_left, message.is_valid, signature_ids)
    message_out.play()
        

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
    START_SCREEN = not START_SCREEN
    REPLAY_SCREEN = not REPLAY_SCREEN

def blank_callback():
    pass

def restart_callback():
    start_simulation_callback()
    main()

def process_bb_simulation_output(network: dict[Node]):

    round_dict = {}

    for i in range(0, NUM_OF_TRAITORS + 1):
        round_dict[i + 1] = []

    for id, node in network.items():
        for message in node.all_messages:
            message.reciver_id = id
            message.is_valid = message in node.valid_messages
            round_dict[message.round_sent].append(message)

    for i in range(0, NUM_OF_TRAITORS + 1):
        round_dict[i + 1].sort(key=sender_id)

    return round_dict   

def sender_id(message):
    return message.sender_id

if __name__ == "__main__":
    main()