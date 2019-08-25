import tcod as libtcod

from render_functions import render_all, clear_all, RenderOrder
from entity import Entity, get_blocking_entities_at_location
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from game_messages import Message, MessageLog

def main():

    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 8
    max_rooms = 10

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10
    fov_recompute = True
    max_monsters_per_room = 3



    colors = {
        'dark_wall': libtcod.Color(0, 0, 100),
        'dark_ground': libtcod.Color(50, 50, 150),
        'light_wall': libtcod.Color(130, 110, 50),
        'light_ground': libtcod.Color(200, 180, 50)
    }

    print ("Creating Player Entity...")
    fighter_component = Fighter(hp=30, defence=2, power=5)
    player = Entity(0, 0, '@', libtcod.white, 'Player', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component)

    entities = [player]

    print("Setting up custom font...")
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

    print("Initializing Console with SDL2 renderer")
    libtcod.console_init_root(screen_width, screen_height,'libtcod Tutorial Revised', False, libtcod.RENDERER_SDL2)

    print("Creating console...")
    con = libtcod.console_new(screen_width, screen_height)

    print("Setting up view...")
    panel = libtcod.console_new(screen_width, panel_height)

    print("Setting up the message log...")
    message_log = MessageLog(message_x, message_width, message_height)

    print("Generating map...")
    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room)

    fov_map = initialize_fov(game_map)

    key = libtcod.Key()
    mouse = libtcod.Mouse()
    game_state = GameStates.PLAYERS_TURN

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute,
                   screen_width, screen_height,
                   bar_width, panel_height, panel_y, colors)

        fov_recompute = False

        libtcod.console_flush()
        clear_all(con, entities)

        # key = libtcod.console_check_for_keypress()
        action = handle_keys(key)

        move = action.get('move')
        exit = action.get('exit')
        # fullscreen = action.get('fullscreen')

        player_turn_results = []

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy
            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                if target:
                    player.fighter.attack(target)
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        if exit:
            return True

        for player_turn_results in player_turn_results:
            message = player_turn_results.get('message')
            dead_entity = player_turn_results.get('dead')
            if message:
                print (message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)
                print(message)

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for result in enemy_turn_results:
                        message = result.get('message')
                        dead_entity = result.get('dead')

                        if message:
                            print (message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)
                            print(message)
                            if game_state == GameStates.PLAYER_DEAD:
                                break
                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                game_state = GameStates.PLAYERS_TURN

if __name__ == '__main__':
    main()