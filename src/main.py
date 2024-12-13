import threading
import struct
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.style import Style
from rich.text import Text
from rich.color import ANSI_COLOR_NAMES
import traceback
import time

class Screen:
    def __init__(self):
        self.console = Console()
        self.width = None
        self.height = None
        self.color_mode = None
        self.buffer = []
        self.colors = []
        self.cursor_x = 0
        self.cursor_y = 0
        self.cursor_visible = True
        self.running = True  # State to keep the terminal active
        
    def setup(self, width, height, color_mode):
        self.width = width
        self.height = height
        self.color_mode = color_mode
        self.cursor_x = 0
        self.cursor_y = 0
        # Determine color system and set console color mode accordingly.
        if color_mode == 0:  # Monochrome
            self.console = Console(color_system="standard")
        elif color_mode == 1:  # 16 Colors
            self.console = Console(color_system="256")
        elif color_mode == 2:  # 256 Colors
            self.console = Console(color_system="256")
        else:  # Default to TrueColor for modern systems.
            self.console = Console(color_system="TRUECOLOR")
        self.buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.colors = self.generate_colors(color_mode)
        
    def generate_colors(self, color_mode):
        #Generate color palette based on the color mode.
        
        if color_mode == 0:  # Monochrome
            return ["white"]
        elif color_mode == 1:  # 16 Colors
            # return ["red", "green", "blue", "yellow", "cyan", "magenta", "white", "black"] # 8 Basic colors
            return [
                "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
                "bright_black", "bright_red", "bright_green", "bright_yellow", 
                "bright_blue", "bright_magenta", "bright_cyan", "bright_white"
            ] # 16 Colors including the bright variants
        elif color_mode == 2:  # 256 Colors
            return list(ANSI_COLOR_NAMES.keys())
        else:
            return ["white"]
        
    def draw_char(self, x, y, color, char):
        if 0 <= x < self.width and 0 <= y < self.height:
            try:
                color_name = self.colors[color] if color < len(self.colors) else "white"
                # self.buffer[y][x] = f'[{color_name}]{char}[/{color_name}]'
                self.buffer[y][x] = Text(char, style=f'{color_name}')
            except IndexError:
                self.console.print(Text(f"Invalid color index: {color}. Colors: {self.colors}", style="bold red"))
        else:
            self.console.print(Text('Invalid coordinates', style='bold red'))
            
    def draw_line(self, x1, y1, x2, y2, color, char):
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        if steps == 0:
            self.draw_char(x1, y1, color, char)
        else:
            for i in range(steps + 1):
                x = x1 + i * dx // steps
                y = y1 + i * dy // steps
                self.draw_char(x, y, color, char)
                time.sleep(0.1)
                
    def draw_text(self, x, y, color, text):
        for i, char in enumerate(text):
            self.draw_char(x + i, y, color, char)
            time.sleep(0.1)
            
    def move_cursor(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cursor_x = x
            self.cursor_y = y
        else:
            self.console.print(Text("Cursor move out of bounds.", style="bold red"))
        
    def draw_char_at_cursor(self, char, color):
        self.draw_char(self.cursor_x, self.cursor_y, color, char)
            
    def draw_rect(self, x, y, width, height, color):
        for i in range(y, y + height):
            for j in range(x, x + width):
                self.draw_char(j, i, color, '#')
                time.sleep(0.1)
                
    def clear(self):
        self.buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.cursor_x = 0
        self.cursor_y = 0
        
    def render_screen(self, last_command=None):
        # Converts the buffer into a rich.Text object for rendering.
        text = Text(f'Cursor: ({self.cursor_x}, {self.cursor_y})\n', style="bold blue")
        text.append(Text(f'Last Command: {last_command}\n', style="bold blue"))
        for y, row in enumerate(self.buffer):
            for x, cell in enumerate(row):
                if self.cursor_visible and x == self.cursor_x and y == self.cursor_y:
                    text.append(Text("|", style="white"))
                else:
                    text.append(cell)
            text.append("\n")  # Add a newline at the end of each row
        return text
    
def cursor_blinker(screen, LiveConsole):
    while screen.running:
        screen.cursor_visible = not screen.cursor_visible
        LiveConsole.update(Panel(screen.render_screen(last_command=""), title="Screen Renderer"))
        time.sleep(0.2)

def parse_binary_stream(file_path, screen, LiveConsole):
    try:
        with open(file_path, 'rb') as f:
            while True:
                # read the command byte
                command = f.read(1)
                if not command:
                    break
                command = struct.unpack('B', command)[0]
                
                # read the length byte
                length = f.read(1)
                if not length:
                    break
                length = struct.unpack('B', length)[0]
                
                # Read the data bytes
                data = f.read(length)
                if len(data) < length:
                    screen.console.print(Text("Incomplete data for command.", style="bold red"))
                    break

                if command == 0x1: #screen setup
                    width, height, color_mode = struct.unpack('BBB', data)
                    screen.setup(width, height, color_mode)
                elif command == 0x2: #draw a character
                    x, y, color, char = struct.unpack('BBBB', data)
                    screen.draw_char(x, y, color, chr(char))
                elif command == 0x3: #draw a line
                    x1, y1, x2, y2, color, char = struct.unpack('BBBBBB', data)
                    screen.draw_line(x1, y1, x2, y2, color, chr(char))
                elif command == 0x4: #draw text
                    x, y, color = struct.unpack('BBB', data[:3])
                    text = data[3:].decode('utf-8')
                    screen.draw_text(x, y, color, text)
                elif command == 0x5: #cursor move
                    x, y = struct.unpack('BB', data)
                    screen.move_cursor(x, y)
                elif command == 0x6: #draw char at cursor
                    char, color = struct.unpack('BB', data)
                    screen.draw_char_at_cursor(chr(char), color)
                elif command == 0x7: #draw rectangle
                    x, y, width, height, color = struct.unpack('BBBBB', data)
                    screen.draw_rect(x, y, width, height, color)
                elif command == 0x8: #clear
                    screen.clear()
                elif command == 0xFF: #end of stream
                    break
            
                # Render the screen only after the entire command is processed
                # screen.render_screen()
                
                # update the terminal screen
                LiveConsole.update(Panel(screen.render_screen(last_command = f'Command: {command}'), title="Screen Renderer"))
                screen.cursor_visible = not screen.cursor_visible # For the blinking effect
                time.sleep(0.5)
            
        # After processing is complete, ensure cursor is visible and render final screen
        screen.cursor_visible = True
        LiveConsole.update(Panel(screen.render_screen(last_command="Processing Complete"), title="Screen Renderer"))
        screen.running = False
        
        
        
    except FileNotFoundError as e:
        screen.console.print(Text('Binary file not found', style='bold red'))
        screen.running = False
    except Exception as e:
        screen.console.print(Text(f'An error occurred: {e}', style='bold red'))
        traceback.print_exc()
        screen.running = False
   
def main():
    screen = Screen()
    with Live(screen.render_screen(), refresh_per_second=10) as LiveConsole:
        # Start the cursor blinker thread
        cursor_thread = threading.Thread(target=cursor_blinker, args=(screen, LiveConsole))
        cursor_thread.start()
        # Parse the binary stream
        parse_binary_stream('sample.bin', screen, LiveConsole)
         
# Test the parsing function
if __name__ == '__main__':
    main()