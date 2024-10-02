import curses
import time
import requests
import asyncio
import websockets
import ssl
import json
import argparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress only the single InsecureRequestWarning from urllib3 needed
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Constants
PADDLE_HEIGHT = 4
PADDLE_WIDTH = 1
BALL_SIZE = 1
SCREEN_HEIGHT = 30
SCREEN_WIDTH = 80

# Initialize game state
game_state = {
    'paddle1_y': SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
    'paddle2_y': SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
    'ball_x': SCREEN_WIDTH // 2,
    'ball_y': SCREEN_HEIGHT // 2,
    'score1': 0,
    'score2': 0
}

session = requests.Session()

def register(win):
    url = 'https://localhost:8000/register'
    first_name = get_user_input(win, "First Name: ")
    last_name = get_user_input(win, "Last Name: ")
    email = get_user_input(win, "Email: ")
    username = get_user_input(win, "Username: ")
    password = get_user_input(win, "Password: ")
    conf_password = get_user_input(win, "Confirm Password: ")
    data = {'first_name': first_name, 'last_name': last_name, 'email': email, 'username': username, 'password': password, 'c_password': conf_password}
    response = session.post(url, data=data, verify=False)
    if response.status_code == 200:
        return login(username, password)
    else:
        print('Failed to register:', response.status_code)
        print(response.text)
        return None

def login(username, password):
    url = 'https://localhost:8000/login'
    data = {'username': username, 'password': password}
    response = session.post(url, data=data, verify=False)
    if response.status_code == 201:
        return response.json()
    else:
        print('Failed to login:', response.status_code)
        return None

def join_game(mode):
    global user_id, party_id
    param = ''
    if mode == 1:
        param = '&nbPlayers=1'
    if mode == 2:
        param = '&nbPlayers=2&gameMode=ffa'
    if mode == 3:
        param = '&nbPlayers=4&gameMode=team'
    
    url = f'https://localhost:8001/game/join?gameName=pong{param}'
    response = session.post(url, verify=False)
    if response.status_code == 200:

        party_id = response.json()['game_id']
        user_id = session.cookies.get('userId')
        return
    else:
        print('Failed to join game:', response.status_code)
        return None

async def connect_to_websocket(party_id, user_id, game_state):
    global websocket
    uri = f'wss://localhost:8001/ws/pong/{party_id}/{user_id}'
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    cookies = session.cookies.get_dict()
    cookie_header = '; '.join([f'{name}={value}' for name, value in cookies.items()])

    headers = {'Cookie': cookie_header}

    try:
        async with websockets.connect(uri, ssl=ssl_context, extra_headers=headers) as websocket:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                if 'x' in data:
                    if data['state'] == 'playing':
                        game_state['ball_x'] = int(data['x'] * SCREEN_WIDTH / 800)
                        game_state['ball_y'] = int(data['y'] * SCREEN_HEIGHT / 600)
                        game_state['paddle1_y'] = int(data['positions'][0] * SCREEN_HEIGHT / 600)
                        game_state['paddle2_y'] = int(data['positions'][1] * SCREEN_HEIGHT / 600)
                        game_state['score1'] = data['scores'][0]
                        game_state['score2'] = data['scores'][1]
    except websockets.exceptions.ConnectionClosedOK:
        print('Connection closed')
    except websockets.exceptions.ConnectionClosedError:
        print('Connection closed with error')
    except websockets.exceptions.WebSocketException as e:
        print('WebSocket exception:', e)

def draw_paddle(win, y, x):
    for i in range(PADDLE_HEIGHT):
        win.addch(int(y + i - PADDLE_HEIGHT/2), x, '█')

def draw_ball(win, y, x):
    if 0 <= y < SCREEN_HEIGHT and 0 <= x < SCREEN_WIDTH:
        win.addch(y, x, 'O')

def get_user_input(win, prompt_string):
    curses.echo()
    win.addstr(prompt_string)
    win.refresh()
    input_str = win.getstr().decode('utf-8')
    curses.noecho()
    return input_str

def print_menu(win, selected_row_idx, menu):
    win.clear()
    win.addstr(0, 0, 'Under construct')
    h, w = win.getmaxyx()
    
    for idx, row in enumerate(menu):
        x = w//2 - len(row)//2
        y = h//2 - len(menu)//2 + idx
        if idx == selected_row_idx:
            win.attron(curses.color_pair(1))
            win.addstr(y, x, row)
            win.attroff(curses.color_pair(1))
        else:
            win.addstr(y, x, row)
    
    win.refresh()

def under_construct(win):
    menu_options = ['back']
    ret = handle_menu(win, menu_options)
    return 1

async def play(win):
    global user_id, party_id

    asyncio.create_task(connect_to_websocket(party_id, user_id, game_state))
    win.nodelay(1)
    win.timeout(0)  # Reduce timeout for more responsive input handling
    while True:
        win.erase()
        win.border(0)

        # Draw paddles and ball
        draw_paddle(win, game_state['paddle1_y'], 3)
        draw_paddle(win, game_state['paddle2_y'], SCREEN_WIDTH - 4)
        draw_ball(win, game_state['ball_y'], game_state['ball_x'])

        # Draw score
        if game_state['score1'] and game_state['score2']:
            win.addstr(0, SCREEN_WIDTH // 2 - 1, f"{game_state['score1']} - {game_state['score2']}")

        key = win.getch()
        if websocket:
            if key in [curses.KEY_UP, ord('w')]:
                await websocket.send(json.dumps({'direction': 'up'}))
            elif key in [curses.KEY_DOWN, ord('s')]:
                await websocket.send(json.dumps({'direction': 'down'}))

        win.refresh()
        await asyncio.sleep(0.01)  # Reduce sleep duration for more responsive updates

def handle_menu(win, menu_options):
    current_row = 0
    while True:
        print_menu(win, current_row, menu_options)

        key = win.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_options) - 1:
            current_row += 1
        elif key == ord('\n'):  # Enter key
            return current_row

def main_menu(win):
    menu_options = ['Play', 'History', 'Stats', 'Leaderboard']
    ret = handle_menu(win, menu_options)
    return ret + 2

def play_menu(win):
    menu_options = ['solo', 'ffa 2', 'team 4', 'back']
    ret = handle_menu(win, menu_options)
    mode = 0
    if ret == 0:
        #solo
        mode = 1
        ret = 6
    elif ret == 1:
        #ffa
        mode = 2
        ret = 6
    elif ret == 2:
        # team
        mode = 3
        ret = 6
    elif ret == 3:
        ret = 1
    return ret, mode

async def app(win):
    menu = 1
    mode = 0
    while True:
        if menu == 1:
            menu = main_menu(win)
        elif menu == 2:
            menu, mode = play_menu(win)
        elif menu == 3:
            under_construct(win)
            menu = 1
            # menu = history(win)
        elif menu == 4:
            under_construct(win)
            menu = 1
            # menu = stats(win)
        elif menu == 5:
            under_construct(win)
            menu = 1
            # menu = leaderboard(win)
        elif menu == 6:
            join_game(mode)
            menu = 7
        elif menu == 7:
            await play(win) 

async def main(stdscr,):
    global websocket
    websocket = None

    parser = argparse.ArgumentParser(description='Pong CLI for authentication')
    parser.add_argument('--username', type=str, required=False, help='Your username')
    parser.add_argument('--password', type=str, required=False, help='Your password')
    parser.add_argument('--register', action='store_true', help='Register a new account')
    
    # # Parse the arguments
    args = parser.parse_args()

    username = args.username
    password = args.password
    
    win = curses.newwin(SCREEN_HEIGHT, SCREEN_WIDTH, 0, 0)

    login_response = None
    if args.register:
            register(win)
    else:
        if not username and not password:
            username = get_user_input(win, 'Enter your username: ')
            password = get_user_input(win, 'Enter your password: ')
        while not login_response:
            login_response = login(username, password)
            if not login_response:
                win.erase()
                win.addstr(0, 0, 'Invalid username or password. Please try again.')
                win.refresh()
                time.sleep(2)
                win.erase()
                username = get_user_input(win, 'Enter your username: ')
                password = get_user_input(win, 'Enter your password: ')

    win.keypad(True)

    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Color pair 1: Black on White

    
    # Hide cursor
    curses.curs_set(0)
    await app(win)
  
if __name__ == "__main__":
    curses.wrapper(lambda stdscr: asyncio.run(main(stdscr)))