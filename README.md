# Fortnite Launcher

A program that allows you to launch Fortnite with support for multiple accounts.
Allowing the possibility to start multiple independent clients at the same time if you wish.
You will need Fortnite installed.

_Note:_

_Multiple client are possible only if your choosen anticheat is EasyAntiCheat._


![Preview](https://media.discordapp.net/attachments/908236658812543006/918311697289187420/unknown.png)

# Installation

> - Install [Python 3.8/3.9](https://www.python.org/downloads/)
> - Download this repository as a ZIP file.
> - Extract it to a comfortable place.
> - Put your Fortnite folder path and your command line arguments (optional) in the `config.json` file.
> - Run `install.bat` to install the required packages
> - Then run `run.bat` to start it.

You can add a shortcut of `run.bat` file on your Desktop for easier access!

# Usage

After installation the `run.bat` file will open a console with some options.
Just type the letter/number of choice.

You can add your accounts typing `A`, or remove them with `R`

# Configuration

In the `config.json` file there are a few options:

- _`fortnite_path`_ > Path to the game's installation folder
- _`commandline_arguments`_ > Additional launch arguments to the game (for example `-NOTEXTURESTREAMING`)
- _`auth_type`_ > The auth type to use. You can use either `refresh` or `device`.

## Auth types

_Refresh token_ (`refresh`)

This method uses `refresh_token` to authenticate. It allows you to authenticate without the risk of getting a password reset. Its disadvantages is that if you use more accounts with this method the credentials can be invalidated. Also, if you do not use the saved credentials within 23 days they are invalidated (This credentials are refreshed every time you launch the game).

_Device auth_ (`device`)

 This method uses `device_auths` to authenticate. It allows to authenticate without any problem at any time, the credentials are invalidated when you change your password. But, at some point for security reasons epic will ask you to change your password (these are the famous password resets). This is the best option to use with multiple accounts.

_Note:_

_You can use different auth types per account. Just change the `auth_type` in config file before adding the account._

---

If you need help feel free to you add me on Discord `Bay#8293` or on twitter `@CodeBayGamerJJ`

Use code **BayGamerJJ** in the item shop if you want to support me #EpicPartner