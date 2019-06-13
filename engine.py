import tcod as libtcod

from render_functions import render_all, clear_all
from entity import Entity, get_blocking_entities_at_location
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates

def main():
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45

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
    player = Entity(0, 0, '@', libtcod.white, 'Player', blocks=True)

    entities = [player]

    print("Setting up custom font...")
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

    print("Initializing Console with SDL2 renderer")
    libtcod.console_init_root(screen_width, screen_height,'libtcod Tutorial Revised', False, libtcod.RENDERER_SDL2)

    print("Creating console...")
    con = libtcod.console_new(screen_width, screen_height)

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

        render_all(con, entities, game_map, fov_map, fov_recompute, screen_width, screen_height, colors)
        fov_recompute = False

        libtcod.console_flush()
        clear_all(con, entities)

        # key = libtcod.console_check_for_keypress()
        action = handle_keys(key)

        move = action.get('move')
        exit = action.get('exit')
        # fullscreen = action.get('fullscreen')

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity != player:
                    print ('The ' + entity.name + ' ponders the meaning of its existence.')

            game_state = GameStates.PLAYERS_TURN

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy
            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                if target:
                    print ('You kick the ' + target.name + 'in the shins, much to its annoyance!')
                else:
                    player.move(dx, dy)
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        if exit:
            return True

if __name__ == '__main__':
    main()