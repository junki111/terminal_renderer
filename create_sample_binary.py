import struct

#sample commands to test the binary parser
# commands = [
#     # command 0x1: Screen setup (Width: 40, Height: 40, Monochrome)
#     (0x1, [40, 40, 0x2]),
#     # command 0x2: Draw a character at position (10, 10) with color index 0 and ASCII 'A'
#     (0x2, [10, 10, 0x1, ord('A')]),
#     # command 0x3: Draw a line at position (15, 15) with length 5, direction 0, and color index 1
#     # (0x3, [20, 20, 5, 5, 1]),
#     # command 0x3: Draw a rectangle at position (20, 20) with width 5, height 5, and color index 1
#     (0x7, [20, 20, 5, 5, 0x2]),
#     # command 0xFF: End of the stream
#     (0xFF, [])
# ]

commands = [
    (0x1, [40, 20, 2]),  # Screen setup: 40x20, 256 colors
    (0x2, [10, 5, 1, ord('A')]),  # Draw char at (10, 5) with color 1, 'A'
    (0x3, [7, 7, 35, 7, 2, ord('#')]),  # Draw horizontal line with 'B'
    (0x4, [0, 0, 3] + list(b"Hello Darkness My Old Friend")),  # Draw text "Hello" at (0, 0) with color 3
    (0x5, [15, 10]),  # Move cursor to (15, 10)
    (0x6, [ord('X'), 4]),  # Draw 'X' at cursor with color 4
    (0x5, [17, 10]),  # Move cursor to (15, 10)
    (0x7, [20, 10, 5, 5, 5]),  # Draw rectangle at (20, 10) with width=5, height=5, color=5
    (0xFF, []),  # End of stream
]

# Create a sample binary file
with open('./sample.bin', 'wb') as f:
    for cmd,data in commands:
        # write the command byte
        f.write(struct.pack('B', cmd))
        # write the length byte
        f.write(struct.pack('B', len(data)))
        # write the data bytes
        if data:
            f.write(struct.pack(f'{len(data)}B', *data))
            
print('Sample binary file created: sample.bin')
    