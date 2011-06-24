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

import httplib2
httplib2.debuglevel = 1

import xml.etree.ElementTree as etree

import base64

USER_AGENT = 'WordsWithFriendsAndroid/3.51'
DEVICE_OS = '2.3.3'
DEVICE_ID = 'ADR6300'
WWF_URL = 'https://wordswithfriends.zyngawithfriends.com/'

class Fiend(object):
    def __init__(self, login, password, userAgent=USER_AGENT, deviceOs=DEVICE_OS, deviceId=DEVICE_ID):
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
        """Data about your games"""
        if not self._games:
            self.refreshGames()

        return self._games

    def refreshGames(self):
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
            self.moves = self._processMoves(xmlElem.find('moves'))

        def _processMoves(self, moves):
            moveList = []

            for move in moves:
                moveObj = Fiend.Move(move)
                moveList.insert(moveObj.moveIndex, moveObj)
            
            return moveList

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
