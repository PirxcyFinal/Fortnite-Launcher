# Fortnite Launcher

A program that allows you to launch Fortnite with support for multiple accounts.
Allowing the possibility to start multiple independent clients at the same time if you wish.
You will need Fortnite and the Epic Games Launcher installed.

![Preview](https://media.discordapp.net/attachments/838192486547324938/871619987683573800/fnlauncher.png?width=881&height=461)

Note:
_Sometimes the game will not launch due to an error._

# Installation

> - Install [Python 3.8](https://www.python.org/downloads/)
> - Download this repository as a ZIP file.
> - Extract it to a comfortable place.
> - Put your Fortnite folder path and your command line arguments (optional) in the `config.json` file. [Example](#Configuration-example)
> - Then run `RUN.bat` to start it.

You can add a shortcut of `RUN.bat` file on your Desktop for easier access!

# Usage

After installation the `RUN.bat` file will open a console with some options.
Just type the letter/number of choice.

You can add your accounts typing `A`, or remove them with `R`

# Update

This project has an simple update system. When a new version comes out you will see an notification every time you start the program. 

To update simply do this:

- Open the program folder or click on the notification and double click `UPDATE.bat`
- Once the update window is open, wait for the update to finish.
In case the update script is updated you will have to start again `UPDATE.bat`.

- Once finished, if you see a text indicating that you must run `INSTALL.bat` do it before starting the launcher.

_Note:_
_You can avoid checking for updates by adding `--skip-update-check` to the `RUN.bat` file.
Example:_
```bat
@echo off
python main.py --skip-update-check
```

# Configuration example

```json
{
    "fortnite_path": "C:/Program Files/Epic Games/Fortnite",
    "command_line_arguments": "-USEALLAVAILABLECORES -NOSPLASH",
    "hide_emails": true
}
```


---

If you need help feel free to you add me on Discord `Bay#1111` or on twitter `@CodeBayGamerJJ`

Use code **BayGamerJJ** in the item shop if you want to support me #EpicPartner