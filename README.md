# 🐍 MacroPy
MacroPy is a python macro that allows you to type short triggers and replace them with a full sentence by pressing a keybind.

# ⚙️ How to use
## Requirements
- [ydotool](https://github.com/ReimuNotMoe/ydotool)

## Setup
1. Clone the repository
2. Rename the `.env.example` to `.env` and replace with the correct value.
3. Rename the `abbreviations.json.example` to `abbreviations.json` and replace with your macros like in the example.

## Usage
As soon as the script runs, it'll copy the last block of text and check for matches in the `abbreviations.json` file. If it finds one, the script will paste the assigned value.

I personnaly made a custom shortcut in GNOME's settings to make it launch the script by pressing `ctrl + _`.

# ⚠️ Warning
This script has only be tested on GNOME (Wayland).

*Made with ❤️ by NovaXi*