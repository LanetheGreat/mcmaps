# Copyright 2020 Lane Shaw
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

''' Python3 equivalent of Java's Random library class '''

import ctypes, time
from math import log, sqrt

__all__ = ['Random']


class _DoubleBits(ctypes.Union):
    _fields_ = (
        ('double_value', ctypes.c_double),
        ('long_value', ctypes.c_long),
    )


class Random:
    '''
        An instance of this class is used to generate a stream of
        pseudorandom numbers. The class uses a 48-bit seed, which is
        modified using a linear congruential formula. (See Donald Knuth,
        _The Art of Computer Programming, Volume 2_, Section 3.2.1.)

        If two instances of `Random` are created with the same
        seed, and the same sequence of method calls is made for each, they
        will generate and return identical sequences of numbers. In order to
        guarantee this property, particular algorithms are specified for the
        class `Random`. Java implementations must use all the algorithms
        shown here for the class `Random`, for the sake of absolute
        portability of Java code. However, subclasses of class `Random`
        are permitted to use other algorithms, so long as they adhere to the
        general contracts for all the methods.

        The algorithms implemented by class `Random` use a
        `protected` utility method that on each invocation can supply
        up to 32 pseudorandomly generated bits.

        Many applications will find the method Math#random simpler to use.

        Instances of `java.util.Random` are threadsafe.
        However, the concurrent use of the same `java.util.Random`
        instance across threads may encounter contention and consequent
        poor performance. Consider instead using
        `java.util.concurrent.ThreadLocalRandom` in multithreaded designs.

        Instances of `java.util.Random` are not cryptographically
        secure.  Consider instead using `java.security.SecureRandom` to
        get a cryptographically secure pseudo-random number generator for use
        by security-sensitive applications.
    '''

    __slots__ = ('seed', 'nextNextGaussian', 'haveNextNextGaussian')

    multiplier = 0x5DEECE66D
    addend = 0xB
    mask = (1 << 48) - 1
    unique_seed = ctypes.c_uint64(8682522807148012)

    DOUBLE_UNIT = 1.0 / (1 << 53)

    @classmethod
    def seedUniquifier(self):
        next_seed = Random.unique_seed.value * 181783497276652981
        Random.unique_seed.value = next_seed
        return next_seed

    @classmethod
    def initialScramble(self, seed):
        return (seed ^ self.multiplier) & self.mask

    def __init__(self, seed=None):
        '''
            Creates a new random number generator using a single `long` seed.
            The seed is the initial value of the internal state of the
            pseudorandom number generator which is maintained by method `next`.

            The invocation `Random(seed)` is equivalent to:
            ```
            Random rnd = new Random();
            rnd.setSeed(seed);}
            ```

            :param seed the initial seed

            See setSeed().
        '''

        self.seed = 0
        self.nextNextGaussian = 0.0
        self.haveNextNextGaussian = False

        if seed is None:
            seed = self.seedUniquifier() ^ int(time.monotonic() * 1e9)
        self.setSeed(seed)

    def setSeed(self, seed):
        '''
            Sets the seed of this random number generator using a single
            `long` seed. The general contract of `setSeed` is that it alters
            the state of this random number generator object so as to be in
            exactly the same state as if it had just been created with the
            argument `seed` as a seed. The method `setSeed` is implemented by
            class `Random` by atomically updating the seed to
            `(seed ^ 0x5DEECE66DL) & ((1L << 48) - 1)`
            and clearing the `haveNextNextGaussian` flag used by `nextGaussian`.

            The implementation of `setSeed` by class `Random` happens to use
            only 48 bits of the given seed. In general, however, an overriding
            method may use all 64 bits of the `long` argument as a seed value.

            :param seed the initial seed
        '''
        self.seed = self.initialScramble(seed)
        self.haveNextNextGaussian = False

    def next(self, bits):
        '''
            Generates the next pseudorandom number. Subclasses should override
            this, as this is used by all other methods.

            The general contract of `next` is that it returns an `int` value
            and if the argument `bits` is between `1` and `32` (inclusive),
            then that many low-order bits of the returned value will be
            (approximately) independently chosen bit values, each of which is
            (approximately) equally likely to be `0` or `1`. The method `next`
            is implemented by class `Random` by atomically updating the seed to
            `(seed * 0x5DEECE66DL + 0xBL) & ((1L << 48) - 1)`
            and returning
            `(int)(seed >>> (48 - bits))`

            This is a linear congruential pseudorandom number generator, as
            defined by D. H. Lehmer and described by Donald E. Knuth in
            _The Art of Computer Programming,_ Volume 3:
            _Seminumerical Algorithms_, section 3.2.1.

            :param  bits random bits
            :return the next pseudorandom value from this random number
                    generator's sequence
        '''

        nextseed = (self.seed * self.multiplier + self.addend) & self.mask
        self.seed = nextseed
        return (nextseed >> (48 - bits))

    def nextBytes(self, buffer):
        '''
            Generates random bytes and places them into a user-supplied
            bytearray. The number of random bytes produced is equal to the
            length of the byte array.

            The method `nextBytes` is implemented by class `Random`
            as if by:
            ```java
            public void nextBytes(byte[] bytes) {
              for (int i = 0; i < bytes.length; )
                for (int rnd = nextInt(), n = Math.min(bytes.length - i, 4);
                     n-- > 0; rnd >>= 8)
                  bytes[i++] = (byte)rnd;
            }}
            ```

            :param  bytes the bytearray to fill with random bytes
        '''

        bLen = len(buffer)
        i = 0
        while i < bLen:
            rnd = self.nextInt()
            for _ in range(min(bLen - i, 4)):
                buffer[i] = rnd & 0xFF
                rnd >>= 8
                i += 1

    def nextInt(self, bound=None):
        '''
            Returns the next pseudorandom, uniformly distributed `int`
            value from this random number generator's sequence. The general
            contract of `nextInt` is that one `int` value is pseudorandomly
            generated and returned. All 2<sup>32</sup> possible `int` values
            are produced with (approximately) equal probability.

            The method `nextInt` is implemented by class `Random` as if by:
            ```
            public int nextInt() {
              return next(32);
            }}
            ```
            or if bound is specified:
            Returns a pseudorandom, uniformly distributed `int` value between 0
            (inclusive) and the specified value (exclusive), drawn from this
            random number generator's sequence.  The general contract of
            `nextInt` is that one `int` value in the specified range is
            pseudorandomly generated and returned.  All `bound` possible `int`
            values are produced with (approximately) equal probability. The
            method `nextInt(int bound)` is implemented by class `Random` as if
            by:
            ```
            public int nextInt(int bound) {
              if (bound <= 0)
                throw new IllegalArgumentException("bound must be positive");

              if ((bound & -bound) == bound)  // i.e., bound is a power of 2
                return (int)((bound * (long)next(31)) >> 31);

              int bits, val;
              do {
                  bits = next(31);
                  val = bits % bound;
              } while (bits - val + (bound-1) < 0);
              return val;
            }}
            ```

            The hedge "approximately" is used in the foregoing description only
            because the next method is only approximately an unbiased source of
            independently chosen bits.  If it were a perfect source of randomly
            chosen bits, then the algorithm shown would choose `int` values
            from the stated range with perfect uniformity.

            The algorithm is slightly tricky.  It rejects values that would
            result in an uneven distribution (due to the fact that 2^31 is not
            divisible by n). The probability of a value being rejected depends
            on n. The worst case is n=2^30+1, for which the probability of a
            reject is 1/2, and the expected number of iterations before the
            loop terminates is 2.

            The algorithm treats the case where n is a power of two specially:
            it returns the correct number of high-order bits from the
            underlying pseudo-random number generator. In the absence of
            special treatment, the correct number of _low-order_ bits would be
            returned. Linear congruential pseudo-random number generators such
            as the one implemented by this class are known to have short
            periods in the sequence of values of their low-order bits. Thus,
            this special case greatly increases the length of the sequence of
            values returned by successive calls to this method if n is a small
            power of two.

            :param bound the upper bound (exclusive). Must be positive or None.
            :return the next pseudorandom, uniformly distributed `int` value
                    between zero (inclusive) and `bound` (exclusive) if
                    specified, from this random number generator's sequence
            :throws ValueError if bound is not positive
        '''
        if bound is None:
            return self.next(32)

        if bound <= 0:
            raise ValueError('bound must be greater than 0')

        r = self.next(31)
        m = bound - 1
        if not bound & m:
            r = ((bound * r) >> 31) & 0xFFFFFFFF
        else:
            u = r
            r = u % bound
            while u - r + m < 0:
                u = self.next(31)
                r = u % bound

        return r

    def nextLong(self, bound=None):
        '''
            Returns the next pseudorandom, uniformly distributed `long` value
            from this random number generator's sequence. The general contract
            of `nextLong` is that one `long` value is pseudorandomly generated
            and returned.

            The method `nextLong` is implemented by class `Random` as if by:
            ```
            public long nextLong() {
              return ((long)next(32) << 32) + next(32);
            }}
            ```

            Because class `Random` uses a seed with only 48 bits,
            this algorithm will not return all possible `long` values.

            :param bound the upper bound (exclusive). Must be positive or None.
            :return the next pseudorandom, uniformly distributed `long` value
                    between zero (inclusive) and `bound` (exclusive) if
                    specified, from this random number generator's sequence
            :throws ValueError if bound is not positive
        '''

        if bound is None:
            return (self.next(32) << 32) + self.next(32)

        if bound <= 0:
            raise ValueError('bound must be greater than 0')

        r = (self.next(32) << 32) + self.next(32)
        m = bound - 1
        if not bound & m:
            r = (r & m)
        else:
            u = r >> 1
            r = u % bound
            while u + m - r < 0:
                u = ((self.next(32) << 32) + self.next(32)) >> 1
                r = u % bound

        return r

    def nextBoolean(self):
        '''
            Returns the next pseudorandom, uniformly distributed `boolean`
            value from this random number generator's sequence. The general
            contract of `nextBoolean` is that one `boolean` value is
            pseudorandomly generated and returned. The values `true` and
            `false` are produced with (approximately) equal probability.

            The method `nextBoolean` is implemented by class `Random` as if by:
            ```
            public boolean nextBoolean() {
              return next(1) != 0;
            }}
            ```

            :return the next pseudorandom, uniformly distributed `boolean`
                    value from this random number generator's sequence
        '''
        return bool(self.next(1))

    def nextFloat(self):
        '''
            Returns the next pseudorandom, uniformly distributed `float` value
            between `0.0` and `1.0` from this random number generator's
            sequence.

            The general contract of `nextFloat` is that one `float` value,
            chosen (approximately) uniformly from the range `0.0f` (inclusive)
            to `1.0f` (exclusive), is pseudorandomly generated and returned.
            All 2<sup>24</sup> possible `float` values of the form _m x 2^-24,
            where _m_ is a positive integer less than 2^24, are produced with
            (approximately) equal probability.

            The method `nextFloat` is implemented by class `Random`
            as if by:
            ```
            public float nextFloat() {
              return next(24) / ((float)(1 << 24));
            }}
            ```

            The hedge "approximately" is used in the foregoing description only
            because the next method is only approximately an unbiased source of
            independently chosen bits. If it were a perfect source of randomly
            chosen bits, then the algorithm shown would choose `float` values
            from the stated range with perfect uniformity.<p>
            [In early versions of Java, the result was incorrectly calculated
            as:
            `return next(30) / ((float)(1 << 30));}`

            This might seem to be equivalent, if not better, but in fact it
            introduced a slight nonuniformity because of the bias in the
            rounding of floating-point numbers: it was slightly more likely
            that the low-order bit of the significand would be 0 than that it
            would be 1.]

            :return the next pseudorandom, uniformly distributed `float` value
            between `0.0` and `1.0` from this
                    random number generator's sequence
        '''
        return self.next(24) / float(1 << 24)

    def nextDouble(self):
        '''
            Returns the next pseudorandom, uniformly distributed `double` value
            between `0.0` and `1.0` from this random number generator's
            sequence.

            The general contract of `nextDouble` is that one `double` value,
            chosen (approximately) uniformly from the range `0.0d` (inclusive)
            to `1.0d` (exclusive), is pseudorandomly generated and returned.

            The method `nextDouble` is implemented by class `Random` as if by:
            ```
            public double nextDouble() {
              return (((long)next(26) << 27) + next(27))
                / (double)(1L << 53);
            }}
            ```

            The hedge "approximately" is used in the foregoing description only
            because the `next` method is only approximately an unbiased source
            of independently chosen bits. If it were a perfect source of
            randomly chosen bits, then the algorithm shown would choose
            `double` values from the stated range with perfect uniformity.
            [In early versions of Java, the result was incorrectly calculated
            as:
            `return (((long)next(27) << 27) + next(27)) / (double)(1L << 54);`

            This might seem to be equivalent, if not better, but in fact it
            introduced a large nonuniformity because of the bias in the rounding
            of floating-point numbers: it was three times as likely that the
            low-order bit of the significand would be 0 than that it would be 1!
            This nonuniformity probably doesn't matter much in practice, but we
            strive for perfection.]

            :return the next pseudorandom, uniformly distributed `double` value
                    between `0.0` and `1.0` from this random number
                    generator's sequence
        '''
        return ((self.next(26) << 27) + self.next(27)) * self.DOUBLE_UNIT

    def nextGaussian(self):
        '''
            Returns the next pseudorandom, Gaussian ("normally") distributed
            `double` value with mean `0.0` and standard deviation `1.0` from
            this random number generator's sequence.

            The general contract of `nextGaussian` is that one `double` value,
            chosen from (approximately) the usual normal distribution with
            mean `0.0` and standard deviation `1.0`, is pseudorandomly
            generated and returned.

            The method `nextGaussian` is implemented by class `Random` as if by
            a threadsafe version of the following:
            ```
            private double nextNextGaussian;
            private boolean haveNextNextGaussian = false;

            public double nextGaussian() {
              if (haveNextNextGaussian) {
                haveNextNextGaussian = false;
                return nextNextGaussian;
              } else {
                double v1, v2, s;
                do {
                  v1 = 2 * nextDouble() - 1;   // between -1.0 and 1.0
                  v2 = 2 * nextDouble() - 1;   // between -1.0 and 1.0
                  s = v1 * v1 + v2 * v2;
                } while (s >= 1 || s == 0);
                double multiplier = StrictMath.sqrt(-2 * StrictMath.log(s)/s);
                nextNextGaussian = v2 * multiplier;
                haveNextNextGaussian = true;
                return v1 * multiplier;
              }
            }}
            ```
            This uses the _polar method_ of G. E. P. Box, M. E. Muller, and
            G. Marsaglia, as described by Donald E. Knuth in _The Art of
            Computer Programming_, Volume 3: _Seminumerical Algorithms_,
            section 3.4.1, subsection C, algorithm P. Note that it generates two
            independent values at the cost of only one call to `StrictMath.log`
            and one call to `StrictMath.sqrt`.

            :return the next pseudorandom, Gaussian ("normally") distributed
                    `double` value with mean `0.0` and standard deviation `1.0`
                    from this random number generator's sequence
        '''

        if self.haveNextNextGaussian:
            self.haveNextNextGaussian = False
            return self.nextNextGaussian

        v1 = 2.0 * self.nextDouble() - 1.0
        v2 = 2.0 * self.nextDouble() - 1.0
        s = v1 * v1 + v2 * v2

        while s >= 1.0 or s == 0.0:
            v1 = 2.0 * self.nextDouble() - 1.0
            v2 = 2.0 * self.nextDouble() - 1.0
            s = v1 * v1 + v2 * v2

        multiplier = sqrt(-2.0 * log(s) / s)
        self.nextNextGaussian = v2 * multiplier
        self.haveNextNextGaussian = True
        return v1 * multiplier

    def ints(self, streamSize=None, randomNumberOrigin=None, randomNumberBound=None):
        '''
            Returns a stream producing the given `streamSize` number of
            pseudorandom `int` values or an unlimited stream if `streamSize` is
            `None`, each conforming to the given origin (inclusive) and bound
            (exclusive) if `randomNumberOrigin` and `randomNumberBound` are
            specified.

            A pseudorandom `int` value is generated as if it's the result of
            calling the method `nextInt()`.

            :param streamSize the number of values to generate or `None`
            :param randomNumberOrigin the origin (inclusive) of each random value
            :param randomNumberBound the bound (exclusive) of each random value
            :return a stream of pseudorandom `int` values, each with the given
                    origin (inclusive) and bound (exclusive)
            :throws ValueError if `streamSize` is less than zero, or
                    `randomNumberOrigin` is greater than or equal to
                    `randomNumberBound`
        '''

        if streamSize is not None and streamSize < 0:
            raise ValueError('streamSize must be non-negative')

        if randomNumberOrigin is not None or randomNumberBound is not None:
            if randomNumberOrigin is None or randomNumberBound is None:
                raise ValueError('randomNumberOrigin and randomNumberBound must both be specified, if either is not None')

            if randomNumberOrigin >= randomNumberBound:
                raise ValueError('randomNumberOrigin must be less than randomNumberBound')

            n = randomNumberBound - randomNumberOrigin
            if streamSize is None:
                while True:
                    yield self.nextInt(n) + randomNumberOrigin
            else:
                for _ in range(streamSize):
                    yield self.nextInt(n) + randomNumberOrigin
        else:
            if streamSize is None:
                while True:
                    yield self.nextInt()
            else:
                for _ in range(streamSize):
                    yield self.nextInt()

    def longs(self, streamSize=None, randomNumberOrigin=None, randomNumberBound=None):
        '''
            Returns a stream producing the given `streamSize` number of
            pseudorandom `long` values or an unlimited stream if `streamSize`
            is `None`, each conforming to the given origin (inclusive) and
            bound (exclusive) if `randomNumberOrigin` and `randomNumberBound`
            are specified.

            A pseudorandom `long` value is generated as if it's the result of
            calling the method `nextLong()`.

            :param streamSize the number of values to generate or `None`
            :param randomNumberOrigin the origin (inclusive) of each random value
            :param randomNumberBound the bound (exclusive) of each random value
            :return a stream of pseudorandom `long` values, each with the given
                    origin (inclusive) and bound (exclusive)
            :throws ValueError if `streamSize` is less than zero, or
                    `randomNumberOrigin` is greater than or equal to
                    `randomNumberBound`
        '''

        if streamSize is not None and streamSize < 0:
            raise ValueError('streamSize must be non-negative')

        if randomNumberOrigin is not None or randomNumberBound is not None:
            if randomNumberOrigin is None or randomNumberBound is None:
                raise ValueError('randomNumberOrigin and randomNumberBound must both be specified, if either is not None')

            if randomNumberOrigin >= randomNumberBound:
                raise ValueError('randomNumberOrigin must be less than randomNumberBound')

            n = randomNumberBound - randomNumberOrigin
            if streamSize is None:
                while True:
                    yield self.nextLong(n) + randomNumberOrigin
            else:
                for _ in range(streamSize):
                    yield self.nextLong(n) + randomNumberOrigin
        else:
            if streamSize is None:
                while True:
                    yield self.nextLong()
            else:
                for _ in range(streamSize):
                    yield self.nextLong()

    def _internalNextDouble(self, origin, bound, n):
        r = self.nextDouble()
        r = r * n + origin
        if r >= bound:  # correct for rounding
            bits = _DoubleBits(double_value=r)
            bits.long_value -= 1
            return bits.double_value
        return r

    def doubles(self, streamSize=None, randomNumberOrigin=None, randomNumberBound=None):
        '''
            Returns a stream producing the given `streamSize` number of
            pseudorandom `double` values or an unlimited stream if `streamSize`
            is `None`, each conforming to the given origin (inclusive) and
            bound (exclusive) if `randomNumberOrigin` and `randomNumberBound`
            are specified.

            A pseudorandom `double` value is generated as if it's the result of
            calling the method `nextDouble()`.

            :param streamSize the number of values to generate or `None`
            :param randomNumberOrigin the origin (inclusive) of each random value
            :param randomNumberBound the bound (exclusive) of each random value
            :return a stream of pseudorandom `double` values, each with the
                    given origin (inclusive) and bound (exclusive)
            :throws ValueError if `streamSize` is less than zero, or
                    `randomNumberOrigin` is greater than or equal to
                    `randomNumberBound`
        '''

        if streamSize is not None and streamSize < 0:
            raise ValueError('streamSize must be non-negative')

        if randomNumberOrigin is not None or randomNumberBound is not None:
            if randomNumberOrigin is None or randomNumberBound is None:
                raise ValueError('randomNumberOrigin and randomNumberBound must both be specified, if either is not None')

            if randomNumberOrigin >= randomNumberBound:
                raise ValueError('randomNumberOrigin must be less than randomNumberBound')

            n = randomNumberBound - randomNumberOrigin
            if streamSize is None:
                while True:
                    yield self._internalNextDouble(randomNumberOrigin, randomNumberBound, n)
            else:
                for _ in range(streamSize):
                    yield self._internalNextDouble(randomNumberOrigin, randomNumberBound, n)
        else:
            if streamSize is None:
                while True:
                    yield self.nextDouble()
            else:
                for _ in range(streamSize):
                    yield self.nextDouble()
