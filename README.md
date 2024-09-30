# Pong CLI Documentation

## Introduction

This Pong CLI allows users to play a text-based Pong game in the terminal against web users connected through a WebSocket server. It supports user login, joining an online Pong match, and real-time game interaction using keyboard input.

The game runs entirely in a command-line interface (CLI) environment, making it suitable for those who prefer terminal-based applications. This documentation will guide you through the installation, usage, and available commands of the Pong CLI.

---

## System Requirements

- **Operating System**: Linux, macOS, Windows
- **Dependencies**:
  - Python 3.8+
  - Required Python libraries:
    - `requests`
    - `curses`
    - `asyncio`
    - `websockets`
    - `ssl`
  - Internet connection to connect to the web server

---

## Installation

### Step 1: Clone the repository

Clone the repository containing the Pong CLI code from GitHub or your preferred source.

```bash
git clone https://github.com/stanislas1200/ft_transcendence_cli.git
cd ft_transcendence_cli
```

## Step 2: Install Dependencies

Install the necessary Python dependencies using `pip`.

```bash
pip install requests websockets asyncio
```

## Step 3: Run the Pong CLI

Run the Pong CLI in the terminal:

```bash
python pong_cli.py
```

## Usage

### Command-Line Arguments

You can pass arguments when starting the program to avoid interactive prompts for username and password. Below are the available commands and options:
| Command                    | Description                                                 |
|-----------------------------|-------------------------------------------------------------|
| `--help`                    | Displays help and usage instructions.                       |
| `--username <username>`      | Logs in with the specified username.                        |
| `--password <password>`      | Logs in with the specified password.                        |
| `--register`                | Registers the user after logging in.                        |
### Example

This command logs in the user `player1` with the password `mypassword` and starts the Pong game.

```bash
python pong_cli.py --username player1 --password mypassword --start
```
## Interactive Mode

If you do not pass any command-line arguments, the Pong CLI will run in interactive mode, asking you to enter the following:

- **Username**: Your username for logging in.
- **Password**: Your password for authentication.

The game will automatically join a Pong match after successful login and will start displaying the Pong game in the terminal.

---

## Pong Game Controls

Once the game has started, you will use the keyboard to control your paddle in the Pong match.

| Key         | Action               |
|-------------|----------------------|
| `w` / Up    | Move paddle up        |
| `s` / Down  | Move paddle down      |
| `Ctrl + C`  | Quit the game         |

---

## Game Elements

- **Paddles**: The paddles are controlled by the player and the opponent.
- **Ball**: The ball moves automatically, and players must use their paddles to hit the ball back to the opponent.
- **Score**: The score is displayed at the top of the screen. It updates as the game progresses.

---

## Commands and Options

### `--username` and `--password`

These options allow you to specify the login credentials directly when starting the game, bypassing the interactive prompts.

```bash
python pong_cli.py --username player1 --password secret
```

If the login fails (e.g., wrong password), the game will display an error message and exit.

## --start
This option starts the Pong game immediately after login.

```bash
python pong_cli.py --username player1 --password secret --start 
```

## --difficulty
You can set the difficulty level of the game. Options are:
- easy
- medium (default)
- hard

```bash
python pong_cli.py --username player1 --password secret --start --difficulty hard
```

---

## Example Workflow
Here’s an example of how to use the Pong CLI from login to game execution:

### Login and Start
Run the following command to log in and start the game:

```bash
python pong_cli.py --username JohnDoe --password pass123 --start
```

### Control Your Paddle
Use the `w` key to move the paddle up and the `s` key to move the paddle down.

### Quit the Game
To quit the game at any time, press `Ctrl + C` to exit.

---

## Troubleshooting

### Common Issues

- **Login Failed**:  
  If you receive a "Failed to login" error, make sure your username and password are correct, and check your internet connection.

- **Connection Issues**:  
  If the WebSocket connection fails, ensure the WebSocket server is running and accessible at `wss://localhost:8001`.

- **Screen Flickering**:  
  If the terminal flickers, adjust the screen size to fit the game window (80x30), or reduce the refresh rate by modifying the `await asyncio.sleep()` value.
