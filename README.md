# Pypke Bot

[![GitHub License](https://img.shields.io/github/license/pypke/pypke-bot?label=License&style=flat-square)](/LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/pypke/pypke-bot?label=Issues&style=flat-square)](https://github.com/pypke/pypke-bot/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/pypke/pypke-bot?label=Pull%20Requests&style=flat-square)](https://github.com/pypke/pypke-bot/pulls)

Pypke is a fast and feature-rich Discord bot, with a variety of commands for moderation, utility, giveaways, music, images, fun, and even chatbot functionality. The bot is designed to be easy to use, customizable, and scalable, making it suitable for small servers as well as large communities.

## Self-hosting

While the bot is designed to be self-hosted, the code in this repository is not recommended for production use. Instead, we recommend using the official version of the bot hosted by the Pypke team. If you wish to contribute to the project or customize the bot to your liking, you can fork the repository and run it locally. Keep in mind that self-hosting comes with additional responsibilities, such as ensuring the bot is always online, up-to-date, and secure.

## Installation

To run the bot locally, you will need to have Python 3.6 or higher installed on your system. You can download Python from the official website: https://www.python.org/downloads/

Once you have Python installed, you can install the bot's dependencies using pip. The dependencies are listed in the `requirements.txt` file. To install the dependencies, run the following command in your terminal:

`pip install -r requirements.txt`


## Configuration

Before running the bot, you will need to set up a Discord bot application and obtain a bot token. You can follow the instructions in the Discord Developer Portal to create a new application and bot: https://discord.com/developers/docs/intro

Once you have a bot token, create a new file called `.env` in the project directory, and add the following line to it:

`TOKEN=<your_bot_token_here>`

Replace `<your_bot_token_here>` with your actual bot token. Other Tokens also need to be set up

## Usage

To run the bot, use the following command in your terminal:

`python main.py`

The bot will start up and connect to your Discord server. You can use the bot's commands by typing the prefix followed by the command name. The default prefix is `?`, but you can change it in the `main.py` file.

## Contributing

We welcome contributions to the project! If you wish to contribute code, please create a pull request with your changes. Make sure to follow the existing code style and include tests if applicable. You can also contribute by reporting bugs, suggesting new features, or improving the documentation.

## License

This repository is licensed under the [GNU General Public License v3.0](/LICENSE). Please read the license before using or modifying the source code for personal or other use.
