# Terminal Renderer from Binary Commands

A Python program designed to render a terminal screen based on binary communication commands. 
This project demonstrates an efficient approach to interpreting and displaying binary data as a terminal interface, 
supporting features such as cursor blinking, command update visualization, and extensibility for color modes.

## Table of Contents
- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Features](#features)
- [Installation](#installation)
- [Running the program](#running-the-program)
- [Usage](#usage)
- [Future Enhancements](#future-enhancements)

## Problem Statement

Rendering a terminal screen from a stream of binary commands presents challenges in decoding structured binary data, 
managing updates, and efficiently handling features like blinking cursors and color rendering. 
This project aims to address these challenges while building a robust and extensible solution.

## Solution Overview

The solution involves a Python-based renderer that decodes binary commands and dynamic updates the terminal screen 
with visualization of each of the commands being processed. The renderer is designed to be extensible, 
allowing for additional features such as color modes and cursor blinking to always show cursor location.
The solution uses different threads to handle tasks other than command processing such as cursor blinking.

## Features

- **Dynamic Rendering**: Real-time updates to the terminal screen based on binary commands.
- **Cursor Blinking**: Support for blinking cursors to enhance user experience.
- **Color Modes**: Extensible support for different color modes.
- **Efficient Decoding**: Optimized decoding of structured binary data.

## Installation
### Prerequisites
- Python 3.8 or higher
- Install the required libraries:
```sh
pip install rich

```
## Running the program
- Clone the repository
```sh
git clone https://github.com/junki111/terminal-renderer.git
cd terminal_screen_renderer/src
```
- Run the program using Python
```sh
python main.py
```
The program will use the sample.bin file in the src folder 
In case you would want to create your own commands. Kindly refer to the usage section and the sample.bin to guide you on what to do.

NOTE: In case you have generated a different binary file based on the usage specification section then place it
in the src folder and make sure to rename it to sample.bin

## Usage

### Command Usage Table

The following table outlines the available commands in the binary protocol, their functionality, and the required parameters:

| Command (Hex) | Function           | Parameters                                           |
|---------------|--------------------|------------------------------------------------------|
| 0x01          | Screen Setup       | width (1 byte), height (1 byte), color_mode (1 byte) |
| 0x02          | Draw a Character   | x (1 byte), y (1 byte), color (1 byte), char (1 byte)|
| 0x03          | Draw a Line        | x1 (1 byte), y1 (1 byte), x2 (1 byte), y2 (1 byte), color (1 byte), char (1 byte) |
| 0x04          | Draw Text          | x (1 byte), y (1 byte), color (1 byte), text (variable length) |
| 0x05          | Cursor Move        | x (1 byte), y (1 byte)                               |
| 0x06          | Draw Char at Cursor| char (1 byte), color (1 byte)                        |
| 0x07          | Draw Rectangle     | x (1 byte), y (1 byte), width (1 byte), height (1 byte), color (1 byte) |
| 0x08          | Clear Screen       | None                                                 |
| 0xFF          | End of Stream      | None                                                 |

### Binary File Format

Each command in the binary stream has the following format:

- **Command Byte (1 byte)**: Indicates the operation to perform.

- **Length Byte (1 byte)**: Specifies the number of additional data bytes for the command.

- **Data Bytes**: Parameters required for the command.

## Future Enhancements

- **Cursor Update on print**: To make the cursor follow along with the text instead of remaining on the same position while text is printed elsewhere (**Completed**)
- **Support for more commands**: To add more commands to the protocol for more functionalities