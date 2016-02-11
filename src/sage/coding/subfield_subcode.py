r"""
Subfield subcode

Let `C` be a `[n, k]` code over `\GF(q^t)`.
Let `Cs = \{c \in C | \forall i, c_i \in \GF(q)\}`, `c_i` being the `i`-th
coordinate of `c`.

`Cs` is called the subfield subcode of `C` over `\GF(q)`
"""

#*****************************************************************************
#       Copyright (C) 2016 David Lucas <david.lucas@inria.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from linear_code import (AbstractLinearCode,
                         LinearCodeParityCheckEncoder,
                         LinearCodeSyndromeDecoder,
                         LinearCodeNearestNeighborDecoder)
from sage.misc.cachefunc import cached_method
from sage.rings.integer import Integer
from sage.rings.finite_rings.finite_field_constructor import GF
from sage.functions.all import log

class SubfieldSubcode(AbstractLinearCode):
    r"""
    Representation of a subfield subcode.

    INPUT:

    - ``original_code``  -- the code ``self`` comes from.

    - ``subfield`` -- the base field of ``self``.

    EXAMPLES::

        sage: C = codes.RandomLinearCode(7, 3, GF(16, 'aa'))
        sage: codes.SubfieldSubcode(C, GF(4, 'a'))
        Subfield subcode over Finite Field in a of size 2^2 coming from Linear code of length 7, dimension 3 over Finite Field in aa of size 2^4
    """
    _registered_encoders = {}
    _registered_decoders = {}

    def __init__(self, original_code, subfield, embedding=None):
        r"""
        TESTS:

        ``subfield`` has to be a finite field, otherwise an error is raised::

            sage: C = codes.RandomLinearCode(7, 3, GF(16, 'aa'))
            sage: Cs = codes.SubfieldSubcode(C, RR)
            Traceback (most recent call last):
            ...
            ValueError: subfield has to be a finite field

        ``subfield`` has to be a subfield of ``original_code``'s base field,
        otherwise an error is raised::

            sage: C = codes.RandomLinearCode(7, 3, GF(16, 'aa'))
            sage: Cs = codes.SubfieldSubcode(C, GF(8, 'a'))
            Traceback (most recent call last):
            ...
            ValueError: subfield has to be a subfield of the base field of the original code

        """
        if not isinstance(original_code, AbstractLinearCode):
            raise ValueError("original_code must be a linear code")
        if not subfield.is_finite():
            raise ValueError("subfield has to be a finite field")
        p = subfield.characteristic()
        s = log(subfield.order(), p)
        sm = log(original_code.base_field().order(), p)
        if not s.divides(sm):
            raise ValueError("subfield has to be a subfield of the base field of the original code")
        self._original_code = original_code
        super(SubfieldSubcode, self).__init__(subfield, original_code.length(), "ParityCheck", "Syndrome")

    def __eq__(self, other):
        r"""
        Tests equality between Subfield Subcode objects.

        EXAMPLES::

            sage: C = codes.RandomLinearCode(7, 3, GF(16, 'aa'))
            sage: Cs1 = codes.SubfieldSubcode(C, GF(4, 'a'))
            sage: Cs2 = codes.SubfieldSubcode(C, GF(4, 'a'))
            sage: Cs1 == Cs2
            True
        """
        return isinstance(other, SubfieldSubcode) \
                and self.original_code() == other.original_code()\
                and self.base_field().order() == other.base_field().order()

    def _repr_(self):
        r"""
        Returns a string representation of ``self``.

        EXAMPLES::

            sage: C = codes.RandomLinearCode(7, 3, GF(16, 'aa'))
            sage: Cs = codes.SubfieldSubcode(C, GF(4, 'a'))
            sage: Cs
            Subfield subcode over Finite Field in a of size 2^2 coming from Linear code of length 7, dimension 3 over Finite Field in aa of size 2^4
        """
        return "Subfield subcode over %s coming from %s"\
                % (self.base_field(), self.original_code())

    def _latex_(self):
        r"""
        Returns a latex representation of ``self``.

        EXAMPLES::

            sage: C = codes.RandomLinearCode(7, 3, GF(16, 'aa'))
            sage: Cs = codes.SubfieldSubcode(C, GF(4, 'a'))
            sage: latex(Cs)
            \textnormal{Subfield subcode over \Bold{F}_{2^{2}} coming from }[7, 3]\textnormal{ Linear code over }\Bold{F}_{2^{4}}
        """
        return "\\textnormal{Subfield subcode over %s coming from }%s"\
                % (self.base_field()._latex_(), self.original_code()._latex_())

    def dimension(self):
        r"""
        Returns the dimension of ``self``.

        """
        return self.generator_matrix().nrows()

    def dimension_upper_bound(self):
        r"""
        Returns an upper bound for the dimension of ``self``.

        EXAMPLES::

            sage: C = codes.RandomLinearCode(7, 3, GF(16, 'aa'))
            sage: Cs = codes.SubfieldSubcode(C, GF(4, 'a'))
            sage: Cs.dimension_upper_bound()
            3
        """
        return self.original_code().dimension()

    def dimension_lower_bound(self):
        r"""
        Returns a lower bound for the dimension of ``self``.

        EXAMPLES::

            sage: C = codes.RandomLinearCode(7, 3, GF(16, 'aa'))
            sage: Cs = codes.SubfieldSubcode(C, GF(4, 'a'))
            sage: Cs.dimension_lower_bound()
            -1 #???????????
        """
        C = self.original_code()
        n = C.length()
        k = C.dimension()
        F = C.base_field()
        t = log(F.order() // self.base_field().order(), F.characteristic())
        return n - t*(n-k)

    def original_code(self):
        r"""
        Returns the original code of ``self``.

        EXAMPLES::

            sage: C = codes.RandomLinearCode(7, 3, GF(16, 'aa'))
            sage: Cs = codes.SubfieldSubcode(C, GF(4, 'a'))
            sage: Cs.original_code()
            Linear code of length 7, dimension 3 over Finite Field in aa of size 2^4
        """
        return self._original_code

    @cached_method
    def parity_check_matrix(self):
        r"""
        Returns a parity check matrix of ``self``.

        """
        raise NotImplementedError


####################### registration ###############################

SubfieldSubcode._registered_encoders["ParityCheck"] = LinearCodeParityCheckEncoder
SubfieldSubcode._registered_decoders["Syndrome"] = LinearCodeSyndromeDecoder
SubfieldSubcode._registered_decoders["NearestNeighbor"] = LinearCodeNearestNeighborDecoder
