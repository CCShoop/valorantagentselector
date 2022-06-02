from guizero import App, Text, PushButton, CheckBox, warn, error, question
import configparser as cp
import random
import pyperclip as pc
import time

# First part of selecting agents function
# This part generates the checkboxes for player names
def select_agents(app, players_checked_vars=[]):
    app.destroy()
    app = App(title='Select Random Agents', bg='#191919')
    if len(players_checked_vars) == len(player_conf.sections()): # If the checkboxes were passed in by the second part
        ii = 0
        for player in player_conf.sections():
            player_check = CheckBox(app, text=player)
            player_check.text_color = 'white'
            player_check.value = players_checked_vars[ii].value
            ii += 1
    else:
        for player in player_conf.sections(): # Generating all checkboxes fresh
            player_check = CheckBox(app, text=player)
            player_check.text_color = 'white'
            players_checked_vars.append(player_check)
    generate_button = PushButton(app, text='Generate', command=generate_agents, args=[app, players_checked_vars])
    generate_button.bg = '#900000'
    global first_generation
    if not first_generation:
        previous_button = PushButton(app, text='Show Previous Agents', command=previous_agents, args=[app, players_checked_vars])
        previous_button.bg = '#900000'
    back_button = PushButton(app, text='Back', command=main, args=[app])
    back_button.bg = '#900000'
    
# Second part of selecting agents function
# This part does the random number generation to select agents and allows the user to copy them with a button
def generate_agents(app, players_checked_vars):
    app.destroy()
    app = App(title='Agents Selected', bg='#191919')
    players_checked = []
    counter = 0
    for player in player_conf.sections():
        if players_checked_vars[counter].value:
            players_checked.append(player)
        counter += 1
    if len(players_checked) < 1:
        error('Error', 'Please select at least one player.')
        main(app)
    used_agents = []
    output = []
    longest_output = 0
    for player in players_checked: # Selects and displays a random agent for each player
        random.seed(round(time.time() * 1000))
        picked = random.randint(1, len(player_conf.options(player))) - 1
        anti_loop = 0
        while agents[picked] in used_agents or not player_conf.has_option(player, agents[picked].lower()):
            picked = random.randint(1, len(agent_conf.sections()))-1
            anti_loop += 1
            if anti_loop > 1000000: # Prevents an infinite loop
                error('Error', 'Failed to pick agents. Please try again.')
                main(app)
        used_agents.append(agents[picked])
        new_output = str(player) + ': ' + str(agents[picked]) + '\n'
        if len(new_output) + 2 > longest_output: # Updates longest output; + 2 is for brackets
            longest_output = len(new_output) + 2
        output.append(new_output)
        picked = -1
    text = Text(app, width=longest_output, height=len(output)+1)
    text.text_color = 'white'
    text.append('\n')
    for ii in range(len(output)):
        output_step = output[ii].strip('{').strip('}')
        text.append(output_step)
    text.disable()
    global prev_agents
    global first_generation
    first_generation = False
    prev_agents = output
    copy_button = PushButton(app, text='Copy', command=pc.copy, args=[text.value])
    copy_button.bg = '#900000'
    close_button = PushButton(app, text='Close', command=select_agents, args=[app, players_checked_vars])
    close_button.bg = '#900000'

# Shows the agents selected in the previous generation
def previous_agents(app, players_checked_vars):
    app.destroy()
    app = App(title='Previous Agents', bg='#191919')
    text = Text(app, height=len(prev_agents)+1)
    text.text_color = 'white'
    text.append('\n')
    for ii in range(len(prev_agents)):
        output_step = prev_agents[ii].strip('{').strip('}')
        text.append(output_step)
    text.disable()
    copy_button = PushButton(app, text='Copy', command=pc.copy, args=[text.value])
    copy_button.bg = '#900000'
    close_button = PushButton(app, text='Close', command=select_agents, args=[app, players_checked_vars])
    close_button.bg = '#900000'

# Randomly selects a map
def select_map(app):
    app.destroy()
    app = App(title='Map Selected', bg='#191919')
    random.seed(round(time.time() * 1000))
    global maps
    map = maps[random.randint(0, len(maps)-1)]
    text = Text(app, height=3)
    text.text_color = 'white'
    text.append('\n' + map)
    text.disable()
    copy_button = PushButton(app, text='Copy', command=pc.copy, args=[text.value])
    copy_button.bg = '#900000'
    close_button = PushButton(app, text='Close', command=main, args=[app])
    close_button.bg = '#900000'

# Default window configuration
def main(app):
    app.destroy()
    app = App(title='Random Agent Selector', bg='#191919')
    if player_conf.sections() and agent_conf.sections():
        generate_button = PushButton(app, text='Select Random Agents', command=select_agents, args=[app])
        generate_button.bg = '#900000'
    if map_conf.sections():
        map_select_button = PushButton(app, text='Select Random Map', command=select_map, args=[app])
        map_select_button.bg = '#900000'

    close_button = PushButton(app, text='Exit', command=exit, args=[0])
    close_button.bg = '#900000'


app = App(visible=False)
first_generation = True # Used for Previous Agents button
# Agents config setup
agent_conf = cp.ConfigParser()
try:
    agent_conf.read_file(open('agents.ini'))
except:
    warn('Warning', 'agents.ini not found. Please add agents.')
    agent_conf.read('agents.ini')
    main(app)
agents = []
for agent in agent_conf.sections():
    agents.append(agent)

# Players config setup
player_conf = cp.ConfigParser()
try:
    player_conf.read_file(open('players.ini'))
except:
    warn('Warning', 'players.ini not found. Please add players.')
    player_conf.read('players.ini')
    main(app)
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
    with open('players.ini', 'w') as conf:
        player_conf.write(conf)

new_player_conf = cp.ConfigParser()
for item in sorting_list:
    new_player_conf.add_section(item[1])
    item[2].sort()
    for option in item[2]:
        new_player_conf.set(item[1], str(option), '1')
with open('players.ini', 'w') as conf:
    new_player_conf.write(conf)

# Maps config setup
map_conf = cp.ConfigParser()
try:
    map_conf.read_file(open('maps.ini'))
except:
    warn('Warning', 'maps.ini not found. Please add maps.')
    map_conf.read('maps.ini')
    main(app)
map_list = map_conf.sections()
map_list.sort()
with open('maps.ini', 'w') as conf:
    map_conf.write(conf)
global maps
maps = []
for map in map_conf.sections():
    maps.append(map)
app.destroy()

if __name__ == '__main__':
    app = App(visible=False)
    main(app)
    app.display()