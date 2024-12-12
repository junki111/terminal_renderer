import struct
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.style import Style
from rich.text import Text
from rich.color import ANSI_COLOR_NAMES
import traceback

class Screen:
    def __init__(self):
        self.console = Console()
        self.width = None
        self.height = None
        self.color_mode = None
        self.buffer = []
        self.colors = []
        
    def setup(self, width, height, color_mode):
        self.width = width
        self.height = height
        self.color_mode = color_mode
        # Determine color system and set console color mode accordingly.
        if color_mode == 0:  # Monochrome
            self.console = Console(color_system="MONOCHROME")
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
            self.draw_char(x1, y1, color, chr(char))
        else:
            for i in range(steps + 1):
                x = x1 + i * dx // steps
                y = y1 + i * dy // steps
                self.draw_char(x, y, color, chr(char))
                
    def draw_text(self, x, y, color, text):
        for i, char in enumerate(text):
            self.draw_char(x + i, y, color, chr(char))
            
    # def cursor_move(self, x, y): #mvoe the cursor to the specified position without drawing anything
    #     self.stdscr.move(y, x)  
        
    # def draw_char_at_cursor(self, color, char):
    #     self.cursor_move(self.stdscr.getyx()[1], self.stdscr.getyx()[0])
    #     self.stdscr.addch(char, curses.color_pair(color))
            
    def draw_rect(self, x, y, width, height, color):
        for i in range(y, y + height):
            for j in range(x, x + width):
                self.draw_char(j, i, color, '#')
                
    def clear(self):
        self.buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
    def render_screen(self):
        # Converts the buffer into a rich.Text object for rendering.
        text = Text()
        for row in self.buffer:
            for cell in row:
                if "[" in cell and "]" in cell:  # Handle rich tags
                    text.append(cell, style=None)
                else:
                    text.append(cell)
            text.append("\n")  # Add a newline at the end of each row
        return text
        
    # def render_screen(self):
    #     rendered_screen = "\n".join("".join(row) for row in self.buffer)
    #     return rendered_screen
    #     # self.console.clear()
    #     # self.console.print(Panel(rendered_screen))

def parse_binary_stream(file_path, screen):
    try:
        with open(file_path, 'rb') as f, Live(screen.render_screen(), refresh_per_second=10) as LiveConsole:
            while True:
                # read the command byte
                command = f.read(1)
                if not command:
                    break
                command = struct.unpack('B', command)[0]
                screen.console.print(Text(f'Command: {command}.', style="bold green"))
                
                # read the length byte
                length = f.read(1)
                if not length:
                    break
                length = struct.unpack('B', length)[0]
                screen.console.print(Text(f'Length: {length}.', style="bold green"))
                
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
                    screen.cursor_move(x, y)
                elif command == 0x6: #draw char at cursor
                    color, char = struct.unpack('cB', data)
                    screen.draw_char_at_cursor(color, chr(char))
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
                LiveConsole.update(Panel(screen.render_screen(), title="Screen Renderer"))
        
    except FileNotFoundError as e:
        screen.console.print(Text('Binary file not found', style='bold red'))
    except Exception as e:
        screen.console.print(Text(f'An error occurred: {e}', style='bold red'))
        traceback.print_exc()
   
def main():
    screen = Screen()
    parse_binary_stream('sample.bin', screen)
            
# Test the parsing function
if __name__ == '__main__':
    main()