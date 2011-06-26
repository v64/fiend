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

import httplib2
import xml.etree.ElementTree as etree
import base64

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

class Fiend(object):
    def __init__(self, login, password, userAgent=USER_AGENT, deviceOs=DEVICE_OS, deviceId=DEVICE_ID):
        """
        Params:
            login - Your Words with Friends login email address.
            password - Your phone's device ID. For Android, this can be found in Settings > About phone > Status > MEID.
            userAgent - The string sent in the User-Agent header.
            deviceOs - The string set in the Device-OS header.
            deviceId - The string set in the Device-ID header.
        """

        self.login = login
        self.password = password
        self.userAgent = userAgent
        self.deviceOs = deviceOs
        self.deviceId = deviceId

        self.authorization = self._makeAuthorization(self.login, self.password)

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

        games = etree.fromstring(self._serverGet('games', params))

        for game in games:
            gameObj = Fiend.Game(game)
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

    def _makeAuthorization(self, login, password):
        return base64.b64encode(login + ':' + password)

    class Game(object):
        def __init__(self, xmlElem):
            self.id = int(xmlElem.findtext('id'))

            if xmlElem.findtext('current-move-user-id'):
                self.currentMoveUserId = int(xmlElem.findtext('current-move-user-id'))
            else:
                self.currentMoveUserId = 0

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

            self._letterBag = list(LETTER_MAP)

            self.board = self._initBoard()
            self.moves = []
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
                row = ''
                for x in range(15):
                    row += self.board[x][y]
                board += row + "\n"

            return board

        def addMove(self, move):
            """
            Takes a Move object as an argument. Adds the Move to the Game and updates
            the Game's board.
            """

            if move.moveIndex is None:
                move.moveIndex = len(self.moves) - 1
            else:
                # TODO: If moveObj.moveIndex is set, make sure that it makes sense
                # to insert it into the game given its current state.
                pass

            self.moves.append(move)
            self._updateBoard(move)
            self._updateLetterBag(move)
            return move

        def _processMoves(self, moves):
            moveList = []

            # Order the moves before adding them to a Game. They should be
            # ordered in the XML, but this isn't required.
            for move in moves:
                moveObj = Fiend.Move(move)
                moveList.insert(moveObj.moveIndex, moveObj)

            for moveObj in moveList:
                self.addMove(moveObj)

        def _initBoard(self):
            return [['-' for y in range(15)] for x in range(15)]

        def _updateBoard(self, move):
            # Out of bounds fromX is used to signify a pass, I think
            if move.fromX > 14:
                return

            word = move.textCodeToWord()

            i = -1
            if move.fromX == move.toX:
                for y in range(move.fromY, move.toY+1):
                    i += 1

                    if word[i:i+1] == '*':
                        continue

                    self.board[move.fromX][y] = word[i:i+1]
            else:
                for x in range(move.fromX, move.toX+1):
                    i += 1

                    if word[i:i+1] == '*':
                        continue

                    self.board[x][move.fromY] = word[i:i+1]

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

    class Move(object):
        def __init__(self, xmlElem):
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

        def textCodeToWord(self):
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

            return word
