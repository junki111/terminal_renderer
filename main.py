import struct
from rich.console import Console
from rich.panel import Panel

class Screen:
    def __init__(self):
        self.console = Console()
        self.width = None
        self.height = None
        self.color_mode = None
        self.buffer = []
        
    def setup(self, width, height, color_mode):
        self.width = width
        self.height = height
        self.color_mode = color_mode
        self.buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
    def draw_char(self, x, y, color, char):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.buffer[y][x] = char
        else:
            self.console.print('Invalid coordinates')
            
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
                
    def draw_text(self, x, y, color, text):
        for i, char in enumerate(text):
            self.draw_char(x + i, y, color, char)
            
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
        rendered_screen = "\n".join("".join(row) for row in self.buffer)
        self.console.clear()
        self.console.print(Panel(rendered_screen))

def parse_binary_stream(file_path, screen):
    try:
        with open(file_path, 'rb') as f:
            while True:
                # read the command byte
                command = f.read(1)
                if not command:
                    break
                command = struct.unpack('B', command)[0]
                screen.console.print(f'Command: {command}.', style="bold green")
                
                # read the length byte
                length = f.read(1)
                if not length:
                    break
                length = struct.unpack('B', length)[0]
                screen.console.print(f'Length: {length}.', style="bold green")
                
                # Read the data bytes
                data = f.read(length)
                if len(data) < length:
                    screen.console.print("Incomplete data for command.", style="bold red")
                    break

                if command == 0x1: #screen setup
                    width, height, color_mode = struct.unpack('BBB', data)
                    screen.setup(width, height, color_mode)
                elif command == 0x2: #draw a character
                    x, y, color, char = struct.unpack('BBBB', data)
                    screen.draw_char(x, y, color, chr(char))
                elif command == 0x3: #draw a line
                    x1, y1, x2, y2, color, char = struct.unpack('BBBBBB', data)
                    screen.draw_line(x1, y1, x2, y2, color, char)
                elif command == 0x4: #draw text
                    x, y, color = struct.unpack('BBB', data[:3])
                    text = data[3:].decode('utf-8')
                    screen.draw_text(x, y, color, text)
                elif command == 0x5: #cursor move
                    x, y = struct.unpack('BB', data)
                    screen.cursor_move(x, y)
                elif command == 0x6: #draw char at cursor
                    color, char = struct.unpack('cB', data)
                    screen.draw_char_at_cursor(color, char)
                elif command == 0x7: #draw rectangle
                    x, y, width, height, color = struct.unpack('BBBBB', data)
                    screen.draw_rect(x, y, width, height, color)
                elif command == 0x8: #clear
                    screen.clear()
                elif command == 0xFF: #end of stream
                    break
            
                # Render the screen only after the entire command is processed
                screen.render_screen()
        
    except FileNotFoundError as e:
        screen.console.print('Binary file not found', style='bold red')
    except Exception as e:
        screen.console.print(f'An error occurred: {e}', style='bold red')
   
def main():
    screen = Screen()
    parse_binary_stream('sample.bin', screen)
            
# Test the parsing function
if __name__ == '__main__':
    main()