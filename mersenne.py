# Fiend - A Python module for accessing Zynga's Words with Friends
# Copyright (C) 2011 Jahn Veach <j@hnvea.ch>
#
# This file is originally based on work by Sean Perry <shalehperry@attbi.com>.
# Source: https://mail.python.org/pipermail/python-list/2002-October/160915.html
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

# This is a pure Python implementation of the Mersenne Twister,
# which Words with Friends uses as its random number generator.
#
# Mersenne Twister reference: http://en.wikipedia.org/wiki/Mersenne_twister

N = 624
M = 397
UPPER_MASK = 0x80000000
LOWER_MASK = 0x7fffffff
DEFAULT_SEED = 4357
MAG01 = [0x0, 0x9908b0df]

class Mersenne(object):
    def __init__(self, seed=DEFAULT_SEED):
        self.seed(seed)

    def seed(self, seed):
        self.mt = []

        self.mt.append(seed & 0xffffffff)
        for i in range(1, N+1):
            self.mt.append(1812433253 * (self.mt[i-1] ^ (self.mt[i-1] >> 30)) + i)
            self.mt[i] &= 0xffffffff

        self.mti = i

    def rand(self):
        y = 0

        if self.mti >= N:
            if self.mti == N+1:
                self.seed(DEFAULT_SEED)

            for kk in range((N-M) + 1):
                y = (self.mt[kk]&UPPER_MASK)|(self.mt[kk+1]&LOWER_MASK)
                self.mt[kk] = self.mt[kk+M] ^ (y >> 1) ^ MAG01[y & 0x1]

            for kk in range(kk, N):
                y = (self.mt[kk]&UPPER_MASK)|(self.mt[kk+1]&LOWER_MASK)
                self.mt[kk] = self.mt[kk+(M-N)] ^ (y >> 1) ^ MAG01[y & 0x1]

            y = (self.mt[N-1]&UPPER_MASK)|(self.mt[0]&LOWER_MASK)
            self.mt[N-1] = self.mt[M-1] ^ (y >> 1) ^ MAG01[y & 0x1]

            self.mti = 0

        y = self.mt[self.mti]
        self.mti += 1

        y ^= (y >> 11)
        y ^= (y << 7) & 0x9d2c5680 
        y ^= (y << 15) & 0xefc60000 
        y ^= (y >> 18)

        return y
