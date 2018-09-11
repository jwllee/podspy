#!/usr/bin/env python

"""This is the unit test module for the footprint module.

"""


from podspy.structure import FootprintMatrix


class TestFootprintMatrix:
    def test_build_from_causal_matrix(self, simple_causal_matrix):
        print(simple_causal_matrix)

        footprint = FootprintMatrix.build_from_causal_matrix(simple_causal_matrix)

        assert isinstance(footprint, FootprintMatrix)

        # expected footprint matrix
        # [
        #     (#, #, ->, #, #)
        #     (#, #, ->, #, #)
        #     (<-, <-, #, ->, ->)
        #     (#, #, <-, #, #)
        #     (#, #, <-, #, #)
        # ]

        w = FootprintMatrix.NEVER_FOLLOW
        x = FootprintMatrix.DIRECT_RIGHT
        y = FootprintMatrix.DIRECT_LEFT
        z = FootprintMatrix.PARALLEL

        expected = [
            (w, w, x, w, w),
            (w, w, x, w, w),
            (y, y, w, x, x),
            (w, w, y, w, w),
            (w, w, y, w, w)
        ]

        assert (footprint.matrix.values == expected).all()