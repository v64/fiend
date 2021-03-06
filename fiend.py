# Fiend - A Python module for accessing Zynga's Words with Friends
# Copyright (C) 2011 Jahn Veach <j@hnvea.ch>
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

VERSION = '0.3'

import base64
import copy
import xml.etree.ElementTree as etree
import httplib2
import mersenne

# Device data required in the headers.
USER_AGENT = 'WordsWithFriendsAndroid/3.51'
DEVICE_OS = '2.3.3'
DEVICE_ID = 'ADR6300'
PLATFORM = 'android'

# Main URL for all server requests.
WWF_URL = 'https://wordswithfriends.zyngawithfriends.com/'

GAME_OVER_BY_DECLINE = 97
GAME_OVER_BY_NO_PLAY = 99
GAME_OVER_BY_WIN = 100

# Letter distribution:
# A-9 B-2 C-2 D-5 E-13 F-2 G-3 H-4 I-8 J-1 K-1 L-4 M-2
# N-5 O-8 P-2 Q-1 R-6  S-5 T-7 U-4 V-2 W-2 X-1 Y-2 Z-1
# Blanks-2
LETTER_MAP = ['', '',
              'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E',
              'E', 'E', 'E', 'E',
              'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 
              'I', 'I', 'I', 'I', 'I', 'I', 'I', 'I', 
              'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 
              'N', 'N', 'N', 'N', 'N', 
              'R', 'R', 'R', 'R', 'R', 'R', 
              'T', 'T', 'T', 'T', 'T', 'T', 'T', 
              'D', 'D', 'D', 'D', 'D', 
              'L', 'L', 'L', 'L', 
              'S', 'S', 'S', 'S', 'S', 
              'U', 'U', 'U', 'U', 
              'G', 'G', 'G', 
              'B', 'B', 
              'C', 'C', 
              'F', 'F', 
              'H', 'H', 'H', 'H', 
              'M', 'M', 
              'P', 'P', 
              'V', 'V', 
              'W', 'W', 
              'Y', 'Y', 
              'J', 
              'K', 
              'Q', 
              'X', 
              'Z'] 

LETTER_VALUES = {
    '':  0,  'A': 1, 'B': 4,  'C': 4, 'D': 2,
    'E': 1,  'F': 4, 'G': 3,  'H': 3, 'I': 1,
    'J': 10, 'K': 5, 'L': 2,  'M': 4, 'N': 2,
    'O': 1,  'P': 4, 'Q': 10, 'R': 1, 'S': 1,
    'T': 1,  'U': 2, 'V': 5,  'W': 4, 'X': 8,
    'Y': 3,  'Z': 10,
}

TRIPLE_WORD = '$'
TRIPLE_LETTER = '!'
DOUBLE_WORD = '='
DOUBLE_LETTER = '+'
BONUS_SQUARES = [['-', '-', '-', '$', '-', '-', '!', '-', '!', '-', '-', '$', '-', '-', '-'],
                 ['-', '-', '+', '-', '-', '=', '-', '-', '-', '=', '-', '-', '+', '-', '-'],
                 ['-', '+', '-', '-', '+', '-', '-', '-', '-', '-', '+', '-', '-', '+', '-'],
                 ['$', '-', '-', '!', '-', '-', '-', '=', '-', '-', '-', '!', '-', '-', '$'],
                 ['-', '-', '+', '-', '-', '-', '+', '-', '+', '-', '-', '-', '+', '-', '-'],
                 ['-', '=', '-', '-', '-', '!', '-', '-', '-', '!', '-', '-', '-', '=', '-'],
                 ['!', '-', '-', '-', '+', '-', '-', '-', '-', '-', '+', '-', '-', '-', '!'],
                 ['-', '-', '-', '=', '-', '-', '-', '-', '-', '-', '-', '=', '-', '-', '-'],
                 ['!', '-', '-', '-', '+', '-', '-', '-', '-', '-', '+', '-', '-', '-', '!'],
                 ['-', '=', '-', '-', '-', '!', '-', '-', '-', '!', '-', '-', '-', '=', '-'],
                 ['-', '-', '+', '-', '-', '-', '+', '-', '+', '-', '-', '-', '+', '-', '-'],
                 ['$', '-', '-', '!', '-', '-', '-', '=', '-', '-', '-', '!', '-', '-', '$'],
                 ['-', '+', '-', '-', '+', '-', '-', '-', '-', '-', '+', '-', '-', '+', '-'],
                 ['-', '-', '+', '-', '-', '=', '-', '-', '-', '=', '-', '-', '+', '-', '-'],
                 ['-', '-', '-', '$', '-', '-', '!', '-', '!', '-', '-', '$', '-', '-', '-']]

class Fiend(object):
    def __init__(self, login, password, userAgent=USER_AGENT, deviceOs=DEVICE_OS, deviceId=DEVICE_ID, platform=PLATFORM):
        '''
        Params:
            login - Your Words with Friends login email address.
            password - Your phone's device ID. For Android, this can be found in Settings > About phone > Status > MEID.
            userAgent - The string sent in the User-Agent header.
            deviceOs - The string set in the Device-OS header.
            deviceId - The string set in the Device-Id header.
        '''

        self.login = login
        self.password = password
        self.userAgent = userAgent
        self.deviceOs = deviceOs
        self.deviceId = deviceId
        self.platform = platform

        self.userId = None
        self.userName = None
        self.userEmail = None

        self.authorization = base64.b64encode(self.login + ':' + self.password) 

        self._http = httplib2.Http();

        self._games = {}

    @property
    def games(self):
        '''
        A dictionary of your games, with game IDs as the keys, and
        Game objects as the values.

        This property is lazy loaded. If you want to force a refresh, call
        refreshGames().
        '''

        if not self._games:
            self.refreshGames()

        return self._games

    @property
    def activeGames(self):
        activeGames = {}

        for id, game in self.games.items():
            if not game.gameOver:
                activeGames[id] = game

        return activeGames

    def refreshGames(self):
        '''
        Makes a call to the server to retrieve a list of your games. It sets
        the games property to be a dictionary, with game IDs as the keys, and 
        Game objects as the values.
        '''

        self._games = {}

        params = {
            'game_type':           'WordGame',
            'include_invitations': 'true',
            'games_since':         '1970-0-1T0:0:0-00:00',
            'moves_since':         '0',
            'chat_messages_since': '0',
            'get_current_user':    'true'
        }

        gamesXml = etree.fromstring(self._serverGet('games', params))

        for gameXml in gamesXml:
            gameObj = Fiend.Game()
            gameObj.parent = self
            gameObj.setWithXml(gameXml)
            
            self._games[gameObj.id] = gameObj

    def _serverGet(self, call, params):
        url = self._makeUrl(call, params)
        headers = {
            'User-Agent':    USER_AGENT,
            'Content-Type':  'application/xml',
            'Authorization': self.authorization,
            'Device-OS':     self.deviceOs,
            'Device-Id':     self.deviceId,
            'Accept':        'text/xml',
            'Cache-Control': 'no-cache',
            'Pragma':        'no-cache'
        }

        # TODO: Check response to make sure all is well
        response, content = self._http.request(url, headers=headers)
        return content

    def _makeUrl(self, call, params):
        url = WWF_URL + call + '?'
        url += '&'.join([str(k) + '=' + str(v) for k, v in params.items()])
        return url

    class Game(object):
        def __init__(self):
            self.id = None
            self.parent = None
            self.currentMoveUserId = None
            self.createdByUserId = None
            self.chatSessionId = None
            self.isMatchmaking = None
            self.wasMatchmaking = None
            self.movesCount = None
            self.moveCount = None
            self.clientVersion = None
            self.observers = None
            self.createdAt = None
            self.boardChecksum = 0

            self._blanks = [None, None]
            self.letterBagCodes = [i for i in range(len(LETTER_MAP))]
            self._randomSeed = None
            self._random = None

            self.board = self._initBoard()
            self.creator = Fiend.User()
            self.opponent = Fiend.User()
            self.player = None
            self.moves = []
            self.gameOver = False

        def setWithXml(self, xmlElem):
            self.id = int(xmlElem.findtext('id'))

            if xmlElem.findtext('current-move-user-id'):
                self.currentMoveUserId = int(xmlElem.findtext('current-move-user-id'))

            self.createdByUserId = int(xmlElem.findtext('created-by-user-id'))
            self.chatSessionId = int(xmlElem.findtext('chat_session_id'))
            self.isMatchmaking = str(xmlElem.findtext('is-matchmaking'))
            self.wasMatchmaking = str(xmlElem.findtext('was-matchmaking'))
            self.movesCount = int(xmlElem.findtext('moves-count'))
            self.moveCount = int(xmlElem.findtext('move_count'))
            self.randomSeed = int(xmlElem.findtext('random-seed'))
            self.clientVersion = str(xmlElem.findtext('client-version'))
            self.observers = str(xmlElem.findtext('observers'))
            self.createdAt = str(xmlElem.findtext('created-at'))

            if self.parent.userId is None and xmlElem.find('current-user') is not None:
                currentUserXmlElem = xmlElem.find('current-user')
                self.parent.userId = int(currentUserXmlElem.findtext('id'))
                self.parent.userName = str(currentUserXmlElem.findtext('name'))
                self.parent.userEmail = str(currentUserXmlElem.findtext('email'))

            self._processUsers(xmlElem.find('users'))
            self._processMoves(xmlElem.find('moves'))

        @property
        def boardString(self):
            '''
            Returns a 15x15 text grid of the game board.
            '''

            board = '';

            for y in range(15):
                for x in range(15):
                    if self.board[x][y] == -1:
                        board += BONUS_SQUARES[x][y]
                    elif self.board[x][y] == 0 or self.board[x][y] == 1:
                        board += self._blanks[self.board[x][y]]
                    else:
                        board += LETTER_MAP[self.board[x][y]]

                board += '\n'

            return board

        @property
        def boardGrid(self):
            boldLetter = '\033[1;31m'
            outline = '\033[0;37m'
            reset = '\033[0;0m'
            
            board = outline + '   ' + ('+---'*15) + '+\n' + reset

            for y in range(15):
                if 14 - y < 10:
                    board += ' '

                board += str(14 - y) + ' ' + outline + '|' + reset

                for x in range(15):
                    board += ' '

                    if self.board[x][y] == -1:
                        if BONUS_SQUARES[x][y] == '-':
                            board += ' '
                        else:
                            board += BONUS_SQUARES[x][y]
                    elif self.board[x][y] == 0 or self.board[x][y] == 1:
                        board += boldLetter + self._blanks[self.board[x][y]] + reset
                    else:
                        board += boldLetter + LETTER_MAP[self.board[x][y]] + reset

                    board += ' ' + outline + '|' + reset

                if y == 0:
                    board += '    ' + TRIPLE_WORD + ' Triple Word'
                elif y == 1:
                    board += '    ' + TRIPLE_LETTER + ' Triple Letter'
                elif y == 2:
                    board += '    ' + DOUBLE_WORD + ' Double Word'
                elif y == 3:
                    board += '    ' + DOUBLE_LETTER + ' Double Letter'

                board += outline + '\n   ' + ('+---'*15) + '+\n' + reset

            board += '     ' + '   '.join([str(x) for x in range(10)])
            board += '   ' + '  '.join([str(x) for x in range(10,15)])
            board += '\n'

            return board

        @property
        def randomSeed(self):
            return self._randomSeed

        @randomSeed.setter
        def randomSeed(self, value):
            if self._randomSeed is not None:
                raise GameError('randomSeed is already set for game', self)

            if value is not None:
                self._randomSeed = value
                self._random = mersenne.Mersenne(self._randomSeed)
                self._assignInitialTiles()

        @property
        def remainingLetterCodes(self):
            random = copy.deepcopy(self._random)
            letterBagCodes = copy.deepcopy(self.letterBagCodes)
            return self._drawFromLetterBag(len(letterBagCodes), random, letterBagCodes)

        @property
        def remainingLetters(self):
            return [LETTER_MAP[code] for code in self.remainingLetterCodes]

        def addMove(self, move):
            '''
            Takes a Move object as an argument. Adds the Move to the Game and updates
            the Game's board.
            '''

            if self.gameOver:
                raise Fiend.MoveError('Moves cannot be added to an ended game', move, self)

            if self.randomSeed is None:
                raise Fiend.GameError('Game does not have a randomSeed', self)

            # moveIndex is 0-indexed
            nextMoveIndex = len(self.moves)
            if move.moveIndex is None:
                move.moveIndex = nextMoveIndex
            elif move.moveIndex != nextMoveIndex:
                raise Fiend.MoveError("The moveIndex is not next in this game's sequence", move, self)

            numLettersPlayed, wordPoints, wordsPlayed, passedTurn = self._updateBoard(move)

            currentPlayer = self.creator if move.userId == self.creator.id else self.opponent

            currentPlayer.score += wordPoints
            currentPlayer.rack.extend(self._drawFromLetterBag(numLettersPlayed))

            for tile in [a for a in move.textCodes if a != '*']:
                currentPlayer.rack.remove(tile)

                if passedTurn:
                    self.letterBagCodes.append(tile)

            if move.fromX == GAME_OVER_BY_WIN:
                if len(self.creator.rack) == 0:
                    giver = self.opponent
                    receiver = self.creator
                else:
                    giver = self.creator
                    receiver = self.opponent

                pointExchange = 0
                for tile in giver.rack:
                    pointExchange += LETTER_VALUES[LETTER_MAP[tile]]
                giver.score -= pointExchange
                receiver.score += pointExchange

            move.score = wordPoints
            move.words = wordsPlayed
            move.player = currentPlayer
            move.game = self
            self.moves.append(move)

        def _assignInitialTiles(self):
            self.creator.rack = self._drawFromLetterBag(7)
            self.opponent.rack = self._drawFromLetterBag(7)

        def _processUsers(self, usersXml):
            for userXml in usersXml:
                userObj = Fiend.User()
                userObj.setWithXml(userXml)

                if userObj.id == self.createdByUserId:
                    userObj.rack = self.creator.rack
                    self.creator = userObj
                else:
                    userObj.rack = self.opponent.rack
                    self.opponent = userObj

                self.player = self.creator if self.creator.id == self.parent.userId else self.opponent

        def _processMoves(self, movesXml):
            moveList = []

            # Order the moves before adding them to a Game. They should be
            # ordered in the XML, but this isn't required.
            for moveXml in movesXml:
                moveObj = Fiend.Move()
                moveObj.setWithXml(moveXml)
                moveList.insert(moveObj.moveIndex, moveObj)

            for moveObj in moveList:
                self.addMove(moveObj)

        def _initBoard(self):
            return [[-1 for y in range(15)] for x in range(15)]

        def _updateBoard(self, move):
            numLettersPlayed = 0
            wordPoints = 0
            wordsPlayed = []
            passedTurn = False
            promoted = 0

            if move.fromX > 14:
                # Out of bounds fromX is used to signify various game conditions:
                # 97 = User declined new game
                # 99 = User resigned game due to no play
                # 100 = User won game
                # 101 = Piece exchange
                numLettersPlayed = len(move.textCodes)
                passedTurn = True

                # Either a player won or the game ended due to someone not taking their
                # turn in a given amount of time.
                if GAME_OVER_BY_DECLINE <= move.fromX <= GAME_OVER_BY_WIN:
                    self.gameOver = move.fromX

            else:
                # Make a copy of the board so that if any exceptions are raised,
                # then the actual board isn't corrupted.
                workingBoard = copy.deepcopy(self.board)

                if move.fromX == move.toX and move.fromY == move.toY:
                    # Special case for one letter plays
                    promoted = 3

                    try:
                        above = workingBoard[move.fromX][move.toY+1]
                    except IndexError:
                        above = -1

                    try:
                        below = workingBoard[move.fromX][move.toY-1]
                    except IndexError:
                        below = -1

                    if above != -1 or below != -1:
                        direction = 'V'
                    else:
                        direction = 'H'
                elif move.fromX == move.toX:
                    direction = 'V'
                else:
                    direction = 'H'

                if direction == 'V':
                    if not promoted:
                        promoted = 2

                    moveCoords = [(move.fromX, y) for y in range(move.fromY, move.toY+1)]
                    extendCoordsLeft = [(move.fromX, j) for j in range(move.fromY - 1, -1, -1)]
                    extendCoordsRight = [(move.toX, j) for j in range(move.toY + 1, 15)]
                elif direction == 'H':
                    if not promoted:
                        promoted = 1

                    moveCoords = [(x, move.fromY) for x in range(move.fromX, move.toX+1)]
                    extendCoordsLeft = [(j, move.fromY) for j in range(move.fromX -1, -1, -1)]
                    extendCoordsRight = [(j, move.toY) for j in range(move.toX + 1, 15)]

                if move.promoted is None:
                    move.promoted = promoted
                elif move.promoted != promoted:
                    raise Fiend.MoveError('Promoted value mismatch', move, self)

                discoveredPoints = 0
                scoreMultiplier = 1
                mainWord = ''

                for i, (x,y) in enumerate(moveCoords):
                    if move.textCodes[i] == '*':
                        if workingBoard[x][y] == 0 or workingBoard[x][y] == 1:
                            addedLetter = self._blanks[workingBoard[x][y]]
                        else:
                            addedLetter = LETTER_MAP[workingBoard[x][y]]
                        mainWord += addedLetter

                        wordPoints += LETTER_VALUES[LETTER_MAP[workingBoard[x][y]]]

                        continue

                    else:
                        if move.textCodes[i] == 0 or move.textCodes[i] == 1:
                            addedLetter = move._blanks[move.textCodes[i]]
                        else:
                            addedLetter = LETTER_MAP[move.textCodes[i]]

                        mainWord += addedLetter

                    if workingBoard[x][y] != -1:
                        raise Fiend.MoveError('Move illegally overlaps an existing move', move, self)

                    workingBoard[x][y] = move.textCodes[i]
                    numLettersPlayed += 1

                    letterValue = LETTER_VALUES[LETTER_MAP[move.textCodes[i]]]
                    if BONUS_SQUARES[x][y] == DOUBLE_LETTER:
                        letterValue *= 2
                    elif BONUS_SQUARES[x][y] == TRIPLE_LETTER:
                        letterValue *= 3
                    wordPoints += letterValue

                    multOnLetter = False
                    if BONUS_SQUARES[x][y] == DOUBLE_WORD:
                        scoreMultiplier *= 2
                        multOnLetter = True
                    elif BONUS_SQUARES[x][y] == TRIPLE_WORD:
                        scoreMultiplier *= 3
                        multOnLetter = True

                    if direction == 'V':
                        checkCoordsLeft = [(j, y) for j in range(x-1, -1, -1)]
                        checkCoordsRight = [(j, y) for j in range(x+1, 15)]
                    elif direction == 'H':
                        checkCoordsLeft = [(x, j) for j in range(y-1, -1, -1)]
                        checkCoordsRight = [(x, j) for j in range(y+1, 15)]

                    countedLetter = False
                    onCheckCoordsLeft = True
                    if move.textCodes[i] == 0 or move.textCodes[i] == 1:
                        auxWord = move._blanks[move.textCodes[i]]
                    else:
                        auxWord = LETTER_MAP[move.textCodes[i]]

                    for coords in [checkCoordsLeft, checkCoordsRight]:
                        for (j,k) in coords:
                            if workingBoard[j][k] == -1:
                                if onCheckCoordsLeft:
                                    onCheckCoordsLeft = False
                                break

                            if workingBoard[j][k] == 0 or workingBoard[j][k] == 1:
                                addedLetter = self._blanks[workingBoard[j][k]]
                            else:
                                addedLetter = LETTER_MAP[workingBoard[j][k]]

                            if onCheckCoordsLeft:
                                auxWord = addedLetter + auxWord
                            else:
                                auxWord = auxWord + addedLetter

                            if multOnLetter:
                                wordPoints += LETTER_VALUES[LETTER_MAP[workingBoard[j][k]]]
                            else:
                                discoveredPoints += LETTER_VALUES[LETTER_MAP[workingBoard[j][k]]]

                            if not countedLetter:
                                if multOnLetter:
                                    wordPoints += letterValue
                                else:
                                    discoveredPoints += letterValue

                                countedLetter = True
                        else:
                            onCheckCoordsLeft = False

                    if len(auxWord) > 1:
                        wordsPlayed.append(auxWord)

                onExtendCoordsLeft = True
                for coords in [extendCoordsLeft, extendCoordsRight]:
                    for (j,k) in coords:
                        if workingBoard[j][k] == -1:
                            if onExtendCoordsLeft:
                                onExtendCoordsLeft = False
                            break

                        if workingBoard[j][k] == 0 or workingBoard[j][k] == 1:
                            addedLetter = self._blanks[workingBoard[j][k]]
                        else:
                            addedLetter = LETTER_MAP[workingBoard[j][k]]

                        if onExtendCoordsLeft:
                            mainWord = addedLetter + mainWord
                        else:
                            mainWord = mainWord + addedLetter

                        wordPoints += LETTER_VALUES[LETTER_MAP[workingBoard[j][k]]]
                    else:
                        onExtendCoordsLeft = False

                if mainWord:
                    # Put the main word at the front of the array
                    wordsPlayed.insert(0, mainWord)

                wordPoints *= scoreMultiplier
                wordPoints += discoveredPoints

                if numLettersPlayed == 7:
                    wordPoints += 35

                workingBoardChecksum = self._calculateBoardChecksum(workingBoard)
                if move.boardChecksum is None:
                    move.boardChecksum = workingBoardChecksum
                elif move.boardChecksum != 0 and move.boardChecksum != workingBoardChecksum:
                    raise Fiend.MoveError('Board checksum mismatch', move, self)

                # Move was successful, make working board the real board
                self.board = workingBoard
                self.boardChecksum = workingBoardChecksum

                for i in [0, 1]:
                    if move._blanks[i]:
                        self._blanks[i] = move._blanks[i]

            return (numLettersPlayed, wordPoints, wordsPlayed, passedTurn)

        def _drawFromLetterBag(self, num, random=None, letterBagCodes=None):
            if random is None:
                random = self._random

            if letterBagCodes is None:
                letterBagCodes = self.letterBagCodes

            output = []

            for dummy in range(num):
                if len(letterBagCodes) == 0:
                    break

                i = random.rand() % len(letterBagCodes)
                output.append(letterBagCodes[i])
                del letterBagCodes[i]

            return output

        def _calculateBoardChecksum(self, board=None):
            '''
            Calculates the board_checksum value for the board in its current state.
            Since _updateBoard() calls this, you shouldn't need to call it yourself and
            can just rely on game.boardChecksum.

            If anyone recognizes this as a known algorithm, let me know.
            '''

            if board is None:
                board = self.board

            checkSum = 0
            numTilesPlayed = 0

            for y in range(15):
                for x in range(15):

                    # Space doesn't have a tile on it
                    if board[x][y] == -1:
                        checkSum ^= 1

                    # Space has the first blank on it
                    elif board[x][y] == 0:
                        checkSum ^= 2 ** ((15 * y + x) % 32)
                        numTilesPlayed += 1

                    # Space has the second blank or some other letter on it
                    else:
                        checkSum ^= board[x][y]
                        numTilesPlayed += 1

            if numTilesPlayed % 2 == 1:
                checkSum = -checkSum

                if (checkSum ^ 2) % 2 == 0:
                    checkSum -= 2

            return checkSum

    class User(object):
        def __init__(self):
            self.id = None
            self.name = None

            self.rack = None
            self.score = 0
        
        def setWithXml(self, xmlElem):
            self.id = int(xmlElem.findtext('id'))
            self.name = str(xmlElem.findtext('name'))

        @property
        def rackLetters(self):
            return sorted([LETTER_MAP[num] for num in self.rack])

    class Move(object):
        def __init__(self):
            self.id = None
            self.game = None
            self.gameId = None
            self.userId = None
            self.fromX = None
            self.fromY = None
            self.toX = None
            self.toY = None
            self.moveIndex = None
            self.text = None
            self.createdAt = None
            self.promoted = None
            self.boardChecksum = None

            self.score = None
            self.words = []
            self.player = None

            self._textCodes = None

            self._text = None
            self._blanks = [None, None]

        def setWithXml(self, xmlElem):
            self.id = int(xmlElem.findtext('id'))
            self.gameId = int(xmlElem.findtext('game-id'))
            self.userId = int(xmlElem.findtext('user-id'))
            self.fromX = int(xmlElem.findtext('from-x'))
            self.fromY = int(xmlElem.findtext('from-y'))
            self.toX = int(xmlElem.findtext('to-x'))
            self.toY = int(xmlElem.findtext('to-y'))
            self.moveIndex = int(xmlElem.findtext('move-index'))
            self.text = str(xmlElem.findtext('text'))
            self.createdAt = str(xmlElem.findtext('created-at'))
            self.promoted = int(xmlElem.findtext('promoted'))
            self.boardChecksum = int(xmlElem.findtext('board-checksum'))

        @property
        def text(self):
            return self._text

        @text.setter
        def text(self, value):
            self._text = value

            if self._text:
                self._setBlanks()

        @property
        def textCodes(self):
            if self._textCodes is None:
                self._textCodes = []

                if self.text != '(null)':
                    self._textCodes = []
                    for code in self.text[:-1].split(','):
                        if code == '*':
                            self.textCodes.append('*')
                        else:
                            try:
                                self._textCodes.append(int(code))
                            except ValueError:
                                continue

            return self._textCodes

        @property
        def moveXml(self):
            moveXml = ''

            if len(self.words) > 0:
                moveXml += '<?xml version="1.0" encoding="UTF-8"?>\n'
                moveXml += '<move>\n'
                moveXml += '    <from_x>' + str(self.fromX) + '</from_x>\n'
                moveXml += '    <from_y>' + str(self.fromY) + '</from_y>\n'
                moveXml += '    <to_x>' + str(self.toX) + '</to_x>\n'
                moveXml += '    <to_y>' + str(self.toY) + '</to_y>\n'
                moveXml += '    <promoted>' + str(self.promoted) + '</promoted>\n'
                moveXml += '    <text>' + '</text>\n'
                moveXml += '    <game_id>' + str(self.gameId) + '</game_id>\n'
                moveXml += '    <primary_key>' + '</primary_key>\n'
                moveXml += '    <board_checksum>' + str(self.boardChecksum) + '</board_checksum>\n'
                moveXml += '    <move_index>' + str(self.moveIndex) + '</move_index>\n'
                moveXml += '</move>\n'
                moveXml += '&words=' + self.words[0].lower() + '&points=' + str(self.score) + '&platform=' + self.game.parent.platform

            return moveXml

        def _setBlanks(self):
            letterCodes = self.text[:-1].split(',')
            for i in ['0', '1']:
                if i in letterCodes:
                    self._blanks[int(i)] = letterCodes[letterCodes.index(i) + 1].upper()

    class Error(Exception):
        '''Base class for exceptions in this module.'''
        pass

    class GameError(Error):
        def __init__(self, msg, game):
            self.msg = msg
            self.game = game

        def __str__(self):
            return repr(self.msg)

    class MoveError(Error):
        '''
        Raised when an error occurs when adding a move to a board.

        Params:
            msg: Error message for the exception.
            move: The move that caused the error.
            game: The game that this move was trying to be added to.
        '''

        def __init__(self, msg, move, game):
            self.msg = msg
            self.move = move
            self.game = game

        def __str__(self):
            return repr(self.msg)
