# EchoChess-Bot
This is a Discord bot developed for Massey Hacks VIII intended to assist chess players with replaying, finding tactics, and analyzing previous chess games. 
This project was primarily created using discord.py, and various APIs such as Amazon Textract, Lichess, and Chess.com. 

The bot has three main functions that each serve a purpose to help players improve their skills by reflecting on previous games. 
The first command is !file-scanner which takes an input of a carbon-copy scoresheet image from the user and outputs a pgn file that translates the written coordinates 
which can be used on various websites to replay games. 

The second functionality is !find-tactics which takes a specified number of previous games, starting from the most recent, and returns a pgn file with tactics 
(and solutions) that the player can then input into Chessable or another chess database software to read the positions. 

For example:
-> !find-tactics
Please enter your Lichess username
-> KnightOutpostOP
Please enter the number of games you would like to review
-> 10
puzzles.pgn

The final feature is !analyze-game which evaluates the most recently played chess game from Chess.com and returns the evaluations compiled in a pgn file which can be 
imported into databases such as Scid. 

For example:
-> !analyze-game
Please enter your Chess.com username
-> KnightOutpostOP
moves2.pgn

NOTE: Currently this bot is not available for public access but the link to adding the bot to your Discord server is below,
Bot authorization link: https://discord.com/api/oauth2/authorize?client_id=975054109814190090&permissions=2048&scope=bot 

