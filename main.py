# IMPORTING
import discord
import uuid
import requests
import shutil
import os
import boto3
import chess
import chess.engine
import chess.svg
import random
from datetime import date
import io

# IMPORT FUNCTIONS 
from dotenv import load_dotenv
from discord.ext import commands

# LOADS THE .ENV FILE THAT RESIDES ON THE SAME LEVEL AS THE SCRIPT.
load_dotenv()

# GRAB THE API TOKEN FROM THE .ENV FILE.
# DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_TOKEN = input("WHAT IS THE DISCORD TOKEN?")
ACCESS_KEY = input("WHAT IS THE ACCESS KEY?")
SECRET = input("WHAT IS THE SECRET KEY?")

# GETS THE CLIENT OBJECT FROM DISCORD.PY. CLIENT IS SYNONYMOUS WITH BOT.
bot = discord.Client()
bot = commands.Bot(command_prefix = "!")

def translate(notation):
    replacements = [["9", "a"], ["y", "4"], ["0-0-0", "O-O-O"], ["0-0", "O-O"], ["S", "5"], ["s", "5"], ["l", "1"], ["I", "1"], ["H", "4"], ["o", "a"]]

    for orig, repl in replacements:
        notation = notation.replace(orig, repl)

    return notation

#AWS STUFF


s3 = boto3.resource('s3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key= SECRET)

AWS_S3_CREDS = {
    'aws_access_key_id':ACCESS_KEY, 
    'aws_secret_access_key':SECRET 
}
s3_client = boto3.client('s3',**AWS_S3_CREDS)

lis = []

def process_text_detection(bucket, document, region):
    s3_connection = boto3.resource('s3')
                          
    s3_object = s3_connection.Object(bucket,document)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())

    client = boto3.client('textract', region_name=region)

    response = client.detect_document_text(
        Document={'S3Object': {'Bucket': bucket, 'Name': document}})

    
    blocks=response['Blocks']
   
    for block in blocks:
        if block['BlockType'] != 'PAGE':
            lis.append(block['Text'])

    return len(blocks)

# FILE SCANNER
@bot.command(name="file-scanner", help = 'scans image with written moves and inputs them into pgn')
async def scan(ctx):
        
        try:
                url = ctx.message.attachments[0].url            
        except IndexError:
                await ctx.send("No attachments detected!")
        else:
                if url[0:26] == "https://cdn.discordapp.com":   
                    r = requests.get(url, stream=True)
                    imageName = 'moves.jpg'      
                    with open(imageName, 'wb') as out_file:
                        shutil.copyfileobj(r.raw, out_file)

        await ctx.channel.send("Please enter the last move number")

        def check(num):
                return num.author == ctx.author and num.channel == ctx.channel
        num = (await bot.wait_for("message", check=check)).content
                        
 
        fname = "moves2.pgn"
        highest = int(num)
        bucket = 'chess-test-transcribe'
        document = 'newEchoChess3.jpg'
        region='us-east-1'

        s3.Bucket(bucket).upload_file(imageName, "newEchoChess3.jpg")

        
        newLis = []

        block_count=process_text_detection(bucket,document,region)

        for i in range(1, highest+1):
                ind1 = lis.index(str(i))
                newLis.append(lis[ind1:ind1+3])
        
        FILE = open(fname, "a")
        
        FILE.write('[Event ""]\n')
        FILE.write('[Site ""]\n')
        FILE.write('[Date "????.??.??"]\n')
        FILE.write('[Round ""]\n')
        FILE.write('[White ""]\n')
        FILE.write('[Black ""]\n')
        FILE.write('[Result "*"]\n')
        FILE.write('[FEN "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"]\n')

        ret = ""

        for i in newLis:
                for k in i:
                        move = translate(k)
                        if len(move) > 2 and "-" not in move:
                                if move[0] == "x":
                                        ret += move.lower()+" "
                                else:
                                        ret += move.capitalize()+" "
                        else:
                                ret += move.lower()+" "

        FILE.write(ret+"\n")


        await ctx.channel.send(file=discord.File("moves2.pgn"))

class puzzleFinder():
    def __init__():
        1

    def square(coord):
        return (int(coord[1])-1)*8 + ord(coord[0])-97

    def hasMateInOne(board, color):
        if color == "WHITE":
            result = "1-0"
        else:
            result = "0-1"
            
        ret = []
        
        for possibleMove in board.legal_moves:        
            move = chess.Move.from_uci(chess.Move.uci(possibleMove))
            board.push(move)
            if board.is_checkmate():
                ret.append([move, result])
                board.pop()
                return ret
            
            board.pop()
        return ret

    def findAllMateInOne(game, FEN):
        ret = []
        game = game.split(" ")
        #print(game)
        board = chess.Board(FEN)

        color = "WHITE"

        for move in game:
            if move[0] in "0123456789":
                continue
            if color == "WHITE":
                color = "BLACK"
            else:
                color = "WHITE"
           
            board.push_san(move)

            lis = puzzleFinder.hasMateInOne(board, color)
            if lis != []:
                ret.append([board.copy(), lis]) #  [BOARD, [answer, result]]

        return ret

    def forcedMate(board):
        if board.legal_moves.count() == 0:
            return False
        for opponentMove in board.legal_moves:
            oppMove = chess.Move.from_uci(chess.Move.uci(opponentMove))
            board.push(oppMove)

            checkmate = puzzleFinder.hasMateInOne(board, "WHITE")

            board.pop()

            if checkmate == []: #not checkmate
                return False

        return True

    def randomMove(board):
        R = random.randint(0, board.legal_moves.count()-1)
        cnt = 0
        for move in board.legal_moves:
            if cnt == R:
                return move
            cnt += 1

    def findAllMateInTwo(game, FEN):
        ret = []
        game = game.split(" ")
        board = chess.Board(FEN)

        color = "WHITE"

        for move in game:
            if move[0] in "0123456789":
                continue

            if color == "WHITE":
                color = "BLACK"
            else:
                color = "WHITE"

            board.push_san(move)

            if puzzleFinder.hasMateInOne(board, color) != []:
                continue
            

            for possibleMove in board.legal_moves:
                posMove = chess.Move.from_uci(chess.Move.uci(possibleMove))
                origBoard = board.copy()
                board.push(posMove)

                if puzzleFinder.forcedMate(board):
                    # [BOARD, [answer, result]]
                    ans = [posMove]
                    oppMove = chess.Move.from_uci(chess.Move.uci(puzzleFinder.randomMove(board)))
                    ans.append(oppMove)
                    board.push(oppMove)

                    checkmate = puzzleFinder.hasMateInOne(board, color)
                    
                    ans.append(checkmate[0][0])

                    ret.append([origBoard, [ans, checkmate[0][1]]])

                    board.pop()

                board.pop()

        return ret
                

    def sendToFile(game, stuff):
        mateinOnes = puzzleFinder.findAllMateInOne(game, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        mateinTwos = puzzleFinder.findAllMateInTwo(game, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

        fname = "puzzles.pgn"
        FILE = open(fname, "a")
        
        for BOARD, lis in mateinOnes:
            ans = str(lis[0][0])
            res = lis[0][1]
    
            piece = str(BOARD.piece_at(puzzleFinder.square(ans[0:2])))
            for i in stuff:
                FILE.write(i+"\n")
            line = str(BOARD.board_fen)
            FEN = line[line.index("(")+2:line.index(")")-1]
            FILE.write('[FEN "'+FEN+'"]'+"\n")
            FILE.write("\n")
            if ord(piece) >= 97:
                piece = piece.upper()
                FILE.write("1... "+piece+ans[:]+"\n")
            else:
                FILE.write("1. "+piece+ans[:]+"\n")
            FILE.write(res+"\n\n")

        for BOARD, lis in mateinTwos:

            allAns = str(lis[0]).split()
            res = lis[1]
            ans = []

            for i in stuff:
                FILE.write(i+"\n")

            line = str(BOARD.board_fen)
            FEN = line[line.index("(")+2:line.index(")")-1]
            FILE.write('[FEN "'+FEN+'"]'+"\n\n")

            for m in allAns:
                move = m[m.index("'")+1: m.rfind("'")]
                piece = str(BOARD.piece_at(puzzleFinder.square(move[0:2])))
                BOARD.push_san(move)
                if piece != "p" and piece != "P":
                    ans.append(piece+move)
                else:
                    ans.append(move)

            if ord(ans[0][0]) >= 97:
                FILE.write("1... "+ans[0]+" ")
                FILE.write("2. "+ans[1]+" ")
                FILE.write("2..."+ans[2]+"\n")
            else:
                FILE.write("1. "+ans[0]+" ")
                FILE.write("1... "+ans[1]+" ")
                FILE.write("2. "+ans[2]+"\n")

            FILE.write(res+"\n\n")

        return FILE



# FIND TATICS
@bot.command(name="find-tactics", help = 'finds possible strategies and possible moves')
async def analyze(ctx):
        global username, games
        await ctx.channel.send("Please enter your Lichess username")
        
        def check(username):
                return username.author == ctx.author and username.channel == ctx.channel
        username = (await bot.wait_for("message", check=check)).content

        #GET RID OF THIS PART VVV
        # await ctx.channel.send(username.content)
        
        await ctx.channel.send("Please enter the number of games you would like to review")

        def check(games):
                return games.author == ctx.author and games.channel == ctx.channel
        games = (await bot.wait_for("message", check=check)).content

        URL = "https://lichess.org/api/games/user/"+username
        Params = {"max": games}

        x = requests.get(URL, Params)

        stuff = str(x.content)
        stuff = stuff[2:]
        stuff = stuff.split("\\n")

        lis = []
        ret = []
        variant = "Standard"
        for line in stuff:
                if line[0:2] == "1.":
                        if variant == "Standard":
                                ret = puzzleFinder.sendToFile(line, lis)
                                lis = []
                                variant = "Standard"
                        
                elif len(line)> 1 and "Termination" not in line:
                        lis.append(line)

                if "Variant" in line:
                        if "Standard" not in line:
                                variant = "NOT STANDARD"

        #GET RID OF THIS PART VVV
        # await ctx.channel.send(games.content)
        
        await ctx.channel.send(file=discord.File("puzzles.pgn"))



# ANALYZE GAME
@bot.command(name="analyze-game", help = 'provides an analysis of most recent game')
async def analyze(ctx):
        global username2
        await ctx.channel.send("Please enter your Chess.com username")
        
        def check(username2):
                return username2.author == ctx.author and username2.channel == ctx.channel
        username2 = (await bot.wait_for("message", check=check)).content

        # #GET RID OF THIS PART VVV
        # await ctx.channel.send(username2)

        DATE = str(date.today())
        # year = DATE[0:4]
        # month = DATE[6:8]
        year = "2022"
        month = "05"

        URL = "https://api.chess.com/pub/player/"+username2+"/games/"+year+"/"+month
        x = requests.get(URL)

        stuff = str(x.content)
        stuff = stuff[2:]
        stuff = stuff.split("\\n")

        lis = []

        for i in range(len(stuff)):
                if len(stuff[i]) > 2:
                        if stuff[i][0:2] == "1.":
                                lis.append(stuff[i])

        game = lis[-1]

        inBracket = False

        parsedGame = ""

        for i in range(len(game)):
                if game[i] == "{":
                        inBracket = True
                if game[i] == "}":
                        inBracket = False
                        continue

                if not inBracket:
                        parsedGame += game[i]

        parsedGame = parsedGame.split()

        finalGame = []

        for i in parsedGame:
                if i[0] in "1234567890":
                        continue
                finalGame.append(i)

        board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

        engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\alanb\Downloads\stockfish_15_win_x64_avx2\stockfish_15_win_x64_avx2\stockfish_15_x64_avx2.exe")

        fname = "games.pgn"
        FILE = open(fname, "a")

        moveNum = 1
        player = "WHITE"

        FILE.write('[Event ""]\n')
        FILE.write('[Site ""]\n')
        FILE.write('[Date "????.??.??"]\n')
        FILE.write('[Round ""]\n')
        FILE.write('[White ""]\n')
        FILE.write('[Black ""]\n')
        FILE.write('[Result "*"]\n')
        FILE.write('[FEN "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"]\n')

        for move in finalGame:
                info = engine.analyse(board, chess.engine.Limit(depth = 20))
                board.push_san(move)
                evaluation = str(info['score'].white())

                if player == "WHITE":
                        #print(str(moveNum)+". "+move+ "{ [%eval"+ str(evaluation)+"]}")
                        FILE.write(str(moveNum)+". "+move+ "{ [%eval"+ str(evaluation)+"]}")
                        player = "BLACK"
                else:
                        #print(str(moveNum)+"... "+move+"{ [%eval"+ str(evaluation)+"]}")
                        FILE.write(str(moveNum)+"... "+move+"{ [%eval"+ str(evaluation)+"]}")
                        player = "WHITE"
                        moveNum += 1

        await ctx.channel.send(file=discord.File("games.pgn"))

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.

bot.run(DISCORD_TOKEN)
