from guizero import App, Box, Text, PushButton, CheckBox, Combo, Picture, info, warn, error, question
import configparser as cp
import random
import pyperclip as pc
import time
import os

# First part of selecting agents function
# This part generates the checkboxes for player names
def select_agents(app, box, players_checked_vars=[]):
    box.destroy()
    app.height = 100 + 25 * len(player_conf.sections())
    box = Box(app)
    if len(players_checked_vars) == len(player_conf.sections()): # If the checkboxes were passed in by the second part
        ii = 0
        for player in player_conf.sections():
            player_check_value = players_checked_vars[ii].value
            players_checked_vars[ii] = CheckBox(box, text=player)
            players_checked_vars[ii].text_color = 'white'
            players_checked_vars[ii].value = player_check_value
            ii += 1
    else:
        for player in player_conf.sections(): # Generating all checkboxes fresh
            player_check = CheckBox(box, text=player)
            player_check.text_color = 'white'
            players_checked_vars.append(player_check)
    generate_button = PushButton(box, text='Generate', command=generate_agents, args=[app, box, players_checked_vars])
    generate_button.bg = '#900000'
    global first_generation
    if not first_generation:
        app.height += 35
        previous_button = PushButton(box, text='Show Previous Agents', command=previous_agents, args=[app, box, players_checked_vars])
        previous_button.bg = '#900000'
    back_button = PushButton(box, text='Back', command=main, args=[app, box])
    back_button.bg = '#900000'

# Second part of selecting agents function
# This part does the random number generation to select agents and allows the user to copy them with a button
def generate_agents(app, box, players_checked_vars):
    box.destroy()
    box = Box(app)
    players_checked = []
    counter = 0
    for player in player_conf.sections():
        if players_checked_vars[counter].value:
            players_checked.append(player)
        counter += 1
    if len(players_checked) < 1:
        error('Error', 'Please select at least one player.')
        select_agents(app, box, players_checked_vars)
    app.height = 100 + 25 * len(players_checked)
    used_agents = []
    output = []
    longest_output = 0
    for player in players_checked: # Selects and displays a random agent for each player
        random.seed(round(time.time() * 1000))
        picked = random.randint(1, len(player_conf.options(player))) - 1
        anti_loop = 0
        global agents
        global prev_agents
        check_prev_agent = str(player) + ': ' + str(agents[picked]) + '\n'
        try:
            if prev_agents:
                while agents[picked] in used_agents or not player_conf.has_option(player, agents[picked].lower()) or check_prev_agent in prev_agents:
                    picked = random.randint(1, len(agent_conf.sections())) - 1
                    check_prev_agent = str(player) + ': ' + str(agents[picked]) + '\n'
                    anti_loop += 1
                    if anti_loop > 1000000: # Prevents an infinite loop
                        error('Error', 'Failed to pick agents. Please try again.')
                        main(app, box)
        except:
            while agents[picked] in used_agents or not player_conf.has_option(player, agents[picked].lower()):
                picked = random.randint(1, len(agent_conf.sections())) - 1
                check_prev_agent = str(player) + ': ' + str(agents[picked])
                anti_loop += 1
                if anti_loop > 1000000: # Prevents an infinite loop
                    error('Error', 'Failed to pick agents. Please try again.')
                    main(app, box)
        used_agents.append(agents[picked])
        new_output = str(player) + ': ' + str(agents[picked]) + '\n'
        if len(new_output) + 2 > longest_output: # Updates longest output; + 2 is for brackets
            longest_output = len(new_output) + 2
        output.append(new_output)
        picked = -1
    text = Text(box, width=longest_output, height=len(output)+1)
    text.text_color = 'white'
    text.append('\n')
    for ii in range(len(output)):
        output_step = output[ii].strip('{').strip('}')
        text.append(output_step)
    global first_generation
    first_generation = False
    prev_agents = output
    copy_button = PushButton(box, text='Copy', command=pc.copy, args=[text.value])
    copy_button.bg = '#900000'
    close_button = PushButton(box, text='Close', command=select_agents, args=[app, box, players_checked_vars])
    close_button.bg = '#900000'

# Shows the agents selected in the previous generation
def previous_agents(app, box, players_checked_vars):
    box.destroy()
    app.height = 100 + 25 * len(prev_agents)
    box = Box(app)
    text = Text(box, height=len(prev_agents)+1)
    text.text_color = 'white'
    text.append('\n')
    for ii in range(len(prev_agents)):
        output_step = prev_agents[ii].strip('{').strip('}')
        text.append(output_step)
    copy_button = PushButton(box, text='Copy', command=pc.copy, args=[text.value])
    copy_button.bg = '#900000'
    close_button = PushButton(box, text='Close', command=select_agents, args=[app, box, players_checked_vars])
    close_button.bg = '#900000'

# Randomly selects a map
def select_map(app, box):
    box.destroy()
    app.height = 175
    box = Box(app)
    random.seed(round(time.time() * 1000))
    map_num = random.randint(0, len(maps)-1)
    global prev_map_num
    while map_num == prev_map_num:
        map_num = random.randint(0, len(maps)-1)
    prev_map_num = map_num
    map = maps[map_num]
    text = Text(box, height=3)
    text.text_color = 'white'
    text.append('\n' + map)
    copy_button = PushButton(box, text='Copy', command=pc.copy, args=[text.value])
    copy_button.bg = '#900000'
    close_button = PushButton(box, text='Close', command=main, args=[app, box])
    close_button.bg = '#900000'

# First part of saving a player's unlocked agents
def add_agent_to_player(app, box):
    box.destroy()
    app.height = 200
    box = Box(app)
    text = Text(box, text='Select a Player:', height=3)
    text.text_color = 'white'
    text.append('\n')
    players = player_conf.sections()
    player_combo = Combo(box, options=players)
    player_combo.text_color = 'white'
    player_combo.focus()
    player_button = PushButton(box, text='Edit Agents', command=list_agents_for_player, args=[app, box, player_combo])
    player_button.bg = '#900000'
    back_button = PushButton(box, text='Back', command=main, args=[app, box])
    back_button.bg = '#900000'

# Second part of saving a player's unlocked agents
def list_agents_for_player(app, box, player_combo):
    box.destroy()
    app.height = 200 + 25 * len(agent_conf)
    box = Box(app)
    text = Text(box, text='Select a Player:', height=3)
    text.text_color = 'white'
    text.append('\n')
    players = player_conf.sections()
    player_combo_visual = Combo(box, options=players)
    player_combo_visual.value = player_combo.value
    player_combo_visual.text_color = 'white'
    player_combo_visual.disable()
    player_button = PushButton(box, text='Edit Agents')
    player_button.bg = '#900000'
    player_button.disable()
    agent_checkboxes = []
    for agent in agent_conf.sections():
        agent_checkbox = CheckBox(box, text=agent)
        agent_checkbox.text_color = 'white'
        try:
            agent_checkbox.value = player_conf.getboolean(player_combo.value, agent)
        except:
            agent_checkbox.value = False
        agent_checkboxes.append(agent_checkbox)
    save_button = PushButton(box, text='Save', command=save_agents_to_player, args=[app, box, player_combo.value, agent_checkboxes])
    save_button.bg = '#900000'
    back_button = PushButton(box, text='Back', command=main, args=[app, box])
    back_button.bg = '#900000'

# Saves agent checkbox values to a player
def save_agents_to_player(app, box, player, agent_checkboxes):
    for agent, agent_checkbox in zip(agents, agent_checkboxes):
        if not player_conf.has_option(player, agent) and agent_checkbox.value:
            player_conf.set(player, agent, '1')
    with open('conf/players.ini', 'w') as conf:
        player_conf.write(conf)
    default_players()
    info(title='Updated Successfully', text=f'{player}\'s agents were successfully updated.')
    main(app, box)

# For adding a new player and their unlocked agents to the config file
def add_new_player(app, box):
    new_player_name = question('Add New Player', 'What is the new player\'s name?')
    if new_player_name:
        if new_player_name not in player_conf.sections():
            player_conf.add_section(new_player_name)
            player_conf.set(new_player_name, 'brimstone', '1')
            player_conf.set(new_player_name, 'jett', '1')
            player_conf.set(new_player_name, 'phoenix', '1')
            player_conf.set(new_player_name, 'sage', '1')
            player_conf.set(new_player_name, 'sova', '1')
            player_combo = Combo(box, options=[new_player_name])
            player_combo.value = new_player_name
            player_combo.visible = False
            list_agents_for_player(app, box, player_combo)
        else:
            error('Player Exists', 'Player already exists.')

# For adding a new agent to the config file
def add_new_agent():
    new_agent_name = question('Add New Agent', 'What is the new agent\'s name?')
    if new_agent_name:
        if new_agent_name in agent_conf.sections():
            error('Error', 'Agent already exists!')
        else:
            new_agent_name = new_agent_name.capitalize()
            agent_conf.add_section(new_agent_name)
            with open('conf/agents.ini', 'w') as conf:
                agent_conf.write(conf)
            default_agents()
            info('Agent Added', 'Agent successfully added!')

# For adding a new map to the config file
def add_new_map():
    new_map_name = question('Add New Map', 'What is the new map\'s name?')
    if new_map_name:
        if new_map_name in map_conf.sections():
            error('Error', 'Map already exists!')
        else:
            new_map_name = new_map_name.capitalize()
            map_conf.add_section(new_map_name)
            with open('conf/maps.ini', 'w') as conf:
                map_conf.write(conf)
            default_maps()
            info('Map Added', 'Map successfully added!')

# Default window configuration
def main(app, box):
    box.destroy()
    app.width = 450
    app.height = 425
    box = Box(app)
    val_logo = Picture(box, image='img/valorant_logo.png')
    val_logo.align = 'top'
    val_logo.width = 375
    val_logo.height = 60
    title_text = Text(box, text='Random Agent Selector', size=22, height=1)
    title_text.text_color = 'white'
    global player_conf
    global agent_conf
    if player_conf.sections() and agent_conf.sections():
        generate_button = PushButton(box, text='Select Random Agents', command=select_agents, args=[app, box])
        generate_button.bg = '#900000'
    global map_conf
    if map_conf.sections():
        map_select_button = PushButton(box, text='Select Random Map', command=select_map, args=[app, box])
        map_select_button.bg = '#900000'
    if player_conf.sections() and agent_conf.sections():
        add_agent_to_player_button = PushButton(box, text='Add Agent to Player', command=add_agent_to_player, args=[app, box])
        add_agent_to_player_button.bg = '#900000'
    add_new_player_button = PushButton(box, text='Add New Player', command=add_new_player, args=[app, box])
    add_new_player_button.bg = '#900000'
    add_new_agent_button = PushButton(box, text='Add New Agent', command=add_new_agent)
    add_new_agent_button.bg = '#900000'
    add_new_map_button = PushButton(box, text='Add New Map', command=add_new_map)
    add_new_map_button.bg = '#900000'
    close_button = PushButton(box, text='Exit', command=exit, args=[0])
    close_button.bg = '#900000'


def default():
    global first_generation
    first_generation = True # Used for Previous Agents button
    global prev_map_num
    prev_map_num = -1
    cur_dir = os.getcwd()
    new_dir = 'conf'
    conf_dir = os.path.join(cur_dir, new_dir)
    if not os.path.isdir(conf_dir):
        os.mkdir(conf_dir)
    new_dir = 'img'
    img_dir = os.path.join(cur_dir, new_dir)
    if not os.path.isdir(img_dir):
        os.mkdir(img_dir)


def default_agents():
    # Agents config setup
    global agent_conf
    agent_conf = cp.ConfigParser()
    agent_conf_raw = cp.ConfigParser()
    try:
        agent_conf_raw.read_file(open('conf/agents.ini'))
    except:
        warn('Warning', 'conf/agents.ini not found. Please add agents or download from Github.')
        with open('conf/agents.ini', 'w') as conf:
            agent_conf.read('conf/agents.ini')
            return False
    global agents
    agents = []
    for agent in agent_conf_raw.sections():
        agents.append(agent)
    agents.sort()
    for agent in agents:
        agent_conf.add_section(agent)
    with open('conf/agents.ini', 'w') as conf:
        agent_conf.write(conf)
    return True


def default_players():
    # Players config setup
    global player_conf
    player_conf = cp.ConfigParser()
    try:
        player_conf.read_file(open('conf/players.ini'))
    except:
        warn('Warning', 'conf/players.ini not found. Please add players.')
        with open('conf/players.ini', 'w') as conf:
            player_conf.read('conf/players.ini')
        return False
    changed = False
    sorting_list = []
    for player in player_conf.sections():
        for option in player_conf.options(player):
            if not player_conf.getint(player, option):
                player_conf.remove_option(player, option)
                changed = True
        sorting_list.append([len(player_conf.options(player)), player, player_conf.options(player)])
    sorting_list.sort()
    if changed:
        with open('conf/players.ini', 'w') as conf:
            player_conf.write(conf)
    sort_player_conf = cp.ConfigParser()
    for item in sorting_list:
        sort_player_conf.add_section(item[1])
        item[2].sort()
        for option in item[2]:
            sort_player_conf.set(item[1], str(option), '1')
    with open('conf/players.ini', 'w') as conf:
        sort_player_conf.write(conf)
    return True


def default_maps():
    # Maps config setup
    global map_conf
    map_conf = cp.ConfigParser()
    try:
        map_conf.read_file(open('conf/maps.ini'))
    except:
        warn('Warning', 'conf/maps.ini not found. Please add maps or download from Github.')
        with open('conf/maps.ini', 'w') as conf:
            map_conf.read('conf/maps.ini')
        return False
    map_list = map_conf.sections()
    map_list.sort()
    with open('conf/maps.ini', 'w') as conf:
        map_conf.write(conf)
    global maps
    maps = map_conf.sections()
    return True


if __name__ == '__main__':
    default()
    default_agents()
    default_players()
    default_maps()
    app = App(title='Random Agent Selector', bg='#191919')
    box = Box(app, visible=False)
    main(app, box)
    app.display()