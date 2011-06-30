# Fiend - A Python module for accessing Zynga's Words with Friends
# Copyright (C) 2011 Jahn Veach <v64@v64.net>
#
# This file is originally based on work by Sean Perry.
# Source: http://mail.python.org/pipermail/python-list/2002-October/775128.html
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

# This is a pure Python implementation of the Mersenne Twister,
# which Words with Friends uses as its random number generator.
#
# Mersenne Twister reference: http://en.wikipedia.org/wiki/Mersenne_twister

N = 624
M = 397
UPPER_MASK = 0x80000000L
LOWER_MASK = 0x7fffffffL
DEFAULT_SEED = 4357
MAG01 = [0x0L, 0x9908b0dfL]

class Mersenne(object):
    def __init__(self, seed=DEFAULT_SEED):
        self.seed(seed)

    def seed(self, seed):
        self.mt = []

        self.mt.append(seed & 0xffffffffL)
        for i in xrange(1, N+1):
            self.mt.append(1812433253L * (self.mt[i-1] ^ (self.mt[i-1] >> 30)) + i)
            self.mt[i] &= 0xffffffffL

        self.mti = i

    def rand(self):
        y = 0

        if self.mti >= N:
            if self.mti == N+1:
                self.seed(DEFAULT_SEED)

            for kk in xrange((N-M) + 1):
                y = (self.mt[kk]&UPPER_MASK)|(self.mt[kk+1]&LOWER_MASK)
                self.mt[kk] = self.mt[kk+M] ^ (y >> 1) ^ MAG01[y & 0x1]

            for kk in xrange(kk, N):
                y = (self.mt[kk]&UPPER_MASK)|(self.mt[kk+1]&LOWER_MASK)
                self.mt[kk] = self.mt[kk+(M-N)] ^ (y >> 1) ^ MAG01[y & 0x1]

            y = (self.mt[N-1]&UPPER_MASK)|(self.mt[0]&LOWER_MASK)
            self.mt[N-1] = self.mt[M-1] ^ (y >> 1) ^ MAG01[y & 0x1]

            self.mti = 0

        y = self.mt[self.mti]
        self.mti += 1

        y ^= (y >> 11)
        y ^= (y << 7) & 0x9d2c5680L 
        y ^= (y << 15) & 0xefc60000L 
        y ^= (y >> 18)

        return y
