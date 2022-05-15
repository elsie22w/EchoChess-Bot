# EchoChess-Bot
This is a Discord bot developed for Massey Hacks VIII intended to assist chess players with replaying, finding tactics, and analyzing previous chess games. This project was primarily created using discord.py, and various APIs such as Amazon Textract, Lichess, and Chess.com. 

The bot has three main functions that each serve a purpose to help players improve their skills by reflecting on previous games. The first command is !file-scanner which takes an input of a carbon-copy scoresheet image from the user and outputs a pgn file that translates the written coordinates which can be used on various websites to replay games. The second functionality is !find-tactics which takes a specified number of previous games, starting from the most recent, and returns a pgn file with tactics (and solutions) that the player can then input into Chessable or another chess database software to read the positions. The final feature is !analyze-game which evaluates the most recently played chess game from Chess.com and returns the evaluations compiled in a pgn file which can be imported into databases such as Scid. 

NOTE: Currently this bot is not available for public access 
