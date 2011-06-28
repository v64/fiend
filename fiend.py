# Fiend - A Python module for accessing Zynga's Words with Friends
# Copyright (C) 2011 Jahn Veach <v64@v64.net>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

VERSION = '0.1'

import base64
import copy
import xml.etree.ElementTree as etree
import httplib2
import random

# Device data required in the headers.
USER_AGENT = 'WordsWithFriendsAndroid/3.51'
DEVICE_OS = '2.3.3'
DEVICE_ID = 'ADR6300'

# Main URL for all server requests.
WWF_URL = 'https://wordswithfriends.zyngawithfriends.com/'

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

TRIPLE_WORD = 'T'
TRIPLE_LETTER = 'R'
DOUBLE_WORD = 'D'
DOUBLE_LETTER = 'O'
POINT_SQUARES = [['' , '' , '' , 'T', '' , '' , 'R', '' , 'R', '' , '' , 'T', '' , '' , '' ],
                 ['' , '' , 'O', '' , '' , 'D', '' , '' , '' , 'D', '' , '' , 'O', '' , '' ],
                 ['' , 'O', '' , '' , 'O', '' , '' , '' , '' , '' , 'O', '' , '' , 'O', '' ],
                 ['T', '' , '' , 'R', '' , '' , '' , 'D', '' , '' , '' , 'R', '' , '' , 'T'],
                 ['' , '' , 'O', '' , '' , '' , 'O', '' , 'O', '' , '' , '' , 'O', '' , '' ],
                 ['' , 'D', '' , '' , '' , 'R', '' , '' , '' , 'R', '' , '' , '' , 'D', '' ],
                 ['R', '' , '' , '' , 'O', '' , '' , '' , '' , '' , 'O', '' , '' , '' , 'R'],
                 ['' , '' , '' , 'D', '' , '' , '' , '' , '' , '' , '' , 'D', '' , '' , '' ],
                 ['R', '' , '' , '' , 'O', '' , '' , '' , '' , '' , 'O', '' , '' , '' , 'R'],
                 ['' , 'D', '' , '' , '' , 'R', '' , '' , '' , 'R', '' , '' , '' , 'D', '' ],
                 ['' , '' , 'O', '' , '' , '' , 'O', '' , 'O', '' , '' , '' , 'O', '' , '' ],
                 ['T', '' , '' , 'R', '' , '' , '' , 'D', '' , '' , '' , 'R', '' , '' , 'T'],
                 ['' , 'O', '' , '' , 'O', '' , '' , '' , '' , '' , 'O', '' , '' , 'O', '' ],
                 ['' , '' , 'O', '' , '' , 'D', '' , '' , '' , 'D', '' , '' , 'O', '' , '' ],
                 ['' , '' , '' , 'T', '' , '' , 'R', '' , 'R', '' , '' , 'T', '' , '' , '' ]]

class Fiend(object):
    def __init__(self, login, password, userAgent=USER_AGENT, deviceOs=DEVICE_OS, deviceId=DEVICE_ID):
        """
        Params:
            login - Your Words with Friends login email address.
            password - Your phone's device ID. For Android, this can be found in Settings > About phone > Status > MEID.
            userAgent - The string sent in the User-Agent header.
            deviceOs - The string set in the Device-OS header.
            deviceId - The string set in the Device-Id header.
        """

        self.login = login
        self.password = password
        self.userAgent = userAgent
        self.deviceOs = deviceOs
        self.deviceId = deviceId

        self.authorization = base64.b64encode(self.login + ':' + self.password) 

        self._http = httplib2.Http();

        self._games = {}

    @property
    def games(self):
        """
        A dictionary of your games, with game IDs as the keys, and
        Game objects as the values.

        This property is lazy loaded. If you want to force a refresh, call
        refreshGames().
        """

        if not self._games:
            self.refreshGames()

        return self._games

    def refreshGames(self):
        """
        Makes a call to the server to retrieve a list of your games. It sets
        the games property to be a dictionary, with game IDs as the keys, and 
        Game objects as the values.
        """

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
        url += '&'.join([str(k) + '=' + str(v) for k, v in params.iteritems()])
        return url

    class Game(object):
        def __init__(self):
            self.id = None
            self.currentMoveUserId = None
            self.createdByUserId = None
            self.chatSessionId = None
            self.isMatchmaking = None
            self.wasMatchmaking = None
            self.movesCount = None
            self.moveCount = None
            self.randomSeed = None
            self.clientVersion = None
            self.observers = None
            self.createdAt = None
            self.boardChecksum = 0

            self._blanks = [None, None]
            self._letterBag = list(LETTER_MAP)
            self._randomSeed = None
            self._random = None

            self.board = self._initBoard()
            self.moves = []

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

            self._processMoves(xmlElem.find('moves'))

        @property
        def letterBag(self):
            """
            A list of letters not yet used in the game.
            """

            return filter(lambda a: a != '-', self._letterBag)

        @property
        def boardString(self):
            """
            Returns a 15x15 text grid of the game board.
            """

            board = '';

            for y in range(15):
                for x in range(15):
                    if self.board[x][y] == -1:
                        board += '-'
                    elif self.board[x][y] == 0 or self.board[x][y] == 1:
                        board += self._blanks[self.board[x][y]]
                    else:
                        board += LETTER_MAP[self.board[x][y]]

                board += "\n"

            return board

        @property
        def randomSeed(self):
            return self._randomSeed

        @randomSeed.setter
        def randomSeed(self, value):
            self._randomSeed = value
            self._random = random.Random()
            self._random.seed(self._randomSeed)

        def addMove(self, move):
            """
            Takes a Move object as an argument. Adds the Move to the Game and updates
            the Game's board.
            """

            # moveIndex is 0-indexed
            nextMoveIndex = len(self.moves)
            if move.moveIndex is None:
                move.moveIndex = nextMoveIndex
            elif move.moveIndex != nextMoveIndex:
                raise Fiend.MoveError("The moveIndex is not next in this game's sequence", move, self)

            if move.moveIndex == 0:
                # draw tiles for both players
                pass

            newBoard = copy.deepcopy(self.board)
            numLettersPlayed, blanks = self._updateBoard(move, newBoard)
            newBoardChecksum = self._calculateBoardChecksum(newBoard)
            if move.boardChecksum is None:
                move.boardChecksum = newBoardChecksum
            elif move.boardChecksum != 0 and move.boardChecksum != newBoardChecksum:
                raise Fiend.MoveError("Board checksum mismatch", move, self)

            self.board = newBoard
            for i in [0, 1]:
                if blanks[i]:
                    self._blanks[i] = blanks[i]

            self.boardChecksum = newBoardChecksum
            self._updateLetterBag(move)
            move.game = self
            self.moves.append(move)

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

        def _updateBoard(self, move, board=None):
            if board is None:
                board = self.board

            numLettersPlayed = 0
            blanks = [None, None]

            # Out of bounds fromX is used to signify a pass, I think
            if move.fromX > 14:
                return (numLettersPlayed, blanks)

            if move.fromX == move.toX:
                for i, y in enumerate(range(move.fromY, move.toY+1)):
                    if move.textCodes[i] == '*':
                        continue

                    if board[move.fromX][y] != -1:
                        raise Fiend.MoveError('Move illegally overlaps an existing move', move, self)

                for i, y in enumerate(range(move.fromY, move.toY+1)):
                    if move.textCodes[i] == '*':
                        continue

                    board[move.fromX][y] = move.textCodes[i]
                    numLettersPlayed += 1

                    if move.textCodes[i] == 0 or move.textCodes[i] == 1:
                        blanks[move.textCodes[i]] = move._blanks[move.textCodes[i]]

            else:
                for i, x in enumerate(range(move.fromX, move.toX+1)):
                    if move.textCodes[i] == '*':
                        continue

                    if board[x][move.fromY] != -1:
                        raise Fiend.MoveError('Move illegally overlaps an existing move', move, self)

                for i, x in enumerate(range(move.fromX, move.toX+1)):
                    if move.textCodes[i] == '*':
                        continue

                    board[x][move.fromY] = move.textCodes[i]
                    numLettersPlayed += 1

                    if move.textCodes[i] == 0 or move.textCodes[i] == 1:
                        blanks[move.textCodes[i]] = move._blanks[move.textCodes[i]]

            return (numLettersPlayed, blanks)

        def _updateLetterBag(self, move):
            letterCodes = move.text[:-1].split(',')
            for letterCode in letterCodes:
                if letterCode == '*':
                    continue;
                else:
                    try:
                        self._letterBag[int(letterCode)] = '-'
                    except ValueError:
                        continue;

        def _drawFromLetterBag(self, num):
            output = []

            for tile in range(0, num):
                i = self._random.randint(0, 104)

                if self._letterBag[i] == '-':
                    raise Fiend.GameError('Random number generator fail', self)

                output.append(self._letterBag[i])
                self._letterBag[i] = '-'

            return output

        def _calculateBoardChecksum(self, board=None):
            """
            Calculates the board_checksum value for the board in its current state.
            Since addMove() calls this, you shouldn't need to call it yourself and
            can just rely on game.boardChecksum.

            If anyone recognizes this as a known algorithm, let me know.
            """

            if board is None:
                board = self.board

            i = 0
            j = 0
            k = 225

            for y in range(15):
                for x in range(15):
                    if board[x][y] == -1:
                        i ^= 1
                        k -= 1
                    elif board[x][y] == 0:
                        i ^= (2 ** j)
                    else:
                        i ^= board[x][y]

                    j += 1
                    if j == 32:
                        j = 0

            if k % 2 != 0:
                i = -i
                if (i ^ 2) % 2 == 0:
                    i -= 2

            return i

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

            self._textWord = None
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
        def textWord(self):
            """
            A Move's text field is either a comma separated series of numbers, asterisks,
            and letters, or the string '(null)'.
            
            The numbers correspond to letters as mapped out in LETTER_MAP.
            
            The asterisks signify a letter that's already on the board that this move
            overlaps.
            
            The letters signify that a blank has been played and that letter
            has been selected as its value.

            If the text field equals '(null)', then the turn was a pass.
            """

            if self._textWord is None:
                # This signifies the turn was a pass
                if self.text == '(null)':
                    return

                word = ''
                letterCodes = self.text[:-1].split(',')

                for letterCode in letterCodes:
                    if letterCode == '*':
                        # A * indicates the intersection point of this word
                        # and another word already on the board.
                        word += '*'
                    else:
                        try:
                            word += LETTER_MAP[int(letterCode)]
                        except ValueError:
                            # We have a letter, not a number, so this is
                            # defining a blank.
                            word += letterCode.upper()

                self._textWord = word

            return self._textWord

        def _setBlanks(self):
            letterCodes = self.text[:-1].split(',')
            for i in ['0', '1']:
                if i in letterCodes:
                    self._blanks[int(i)] = letterCodes[letterCodes.index(i) + 1].upper()

    class Error(Exception):
        """Base class for exceptions in this module."""
        pass

    class GameError(Error):
        def __init__(self, msg, game):
            self.msg = msg
            self.game = game

        def __str__(self):
            return repr(self.msg)

    class MoveError(Error):
        """
        Raised when an error occurs when adding a move to a board.

        Params:
            msg: Error message for the exception.
            move: The move that caused the error.
            game: The game that this move was trying to be added to.
        """

        def __init__(self, msg, move, game):
            self.msg = msg
            self.move = move
            self.game = game

        def __str__(self):
            return repr(self.msg)
