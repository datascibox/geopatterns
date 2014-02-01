# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import hashlib
import math

from colour import Color

from .svg import SVG
from .utils import promap


class GeoPattern(object):
    def __init__(self, string, generator=None):
        self.hash = hashlib.sha1(string).hexdigest()
        self.svg = SVG()

        available_generators = [
            'hexagons',
            'overlappingcircles',
            'rings',
            'sinewaves',
            'squares',
            'xes'
        ]
        if generator not in available_generators:
            raise ValueError('{} is not a valid generator. Valid choices are {}.'.format(
                generator, ', '.join(['"{}"'.format(g) for g in available_generators])
            ))
        self.generate_background()
        getattr(self, 'geo_%s' % generator)()

    @property
    def svg_string(self):
        return self.svg.to_string()

    @property
    def base64_string(self):
        return base64.encodestring(self.svg.to_string()).replace('\n', '')

    def generate_background(self):
        hue_offset = promap(int(self.hash[14:][:3], 16), 0, 4095, 0, 359)
        sat_offset = int(self.hash[17:][:1], 16)
        base_color = Color(hsl=(0, .42, .41))
        base_color.hue = base_color.hue - hue_offset

        if sat_offset % 2:
            base_color.saturation = base_color.saturation + sat_offset / 100
        else:
            base_color.saturation = base_color.saturation - sat_offset / 100

        rgb = base_color.rgb
        r = int(round(rgb[0] * 255))
        g = int(round(rgb[1] * 255))
        b = int(round(rgb[2] * 255))
        return self.svg.rect(0, 0, '100%', '100%', **{
            'fill': 'rgb({}, {}, {})'.format(r, g, b)
        })

    def geo_hexagons(self):
        scale = int(self.hash[1:][:1], 16)
        side_length = promap(scale, 0, 15, 5, 120)
        hex_height = side_length * math.sqrt(3)
        hex_width = side_length * 2
        hex = self.build_hexagon_shape(side_length)

        self.svg.width = (hex_width * 3) + (side_length * 3)
        self.svg.height = hex_height * 6

        i = 0
        for y in range(5):
            for x in range(5):
                val = int(self.hash[i:][:1], 16)
                dy = (y * hex_height) if x % 2 else (y * hex_height + hex_height / 2)
                opacity = promap(val, 0, 15, 0.02, 0.18)
                fill = '#ddd' if val % 2 == 0 else '#222'
                tmp_hex = str(hex)

                self.svg.polyline(hex, **{
                    'opacity': opacity,
                    'fill': fill,
                    'stroke': '#000000',
                    'transform': 'translate({}, {})'.format(
                        x * side_length * 1.5 - hex_width / 2,
                        dy - hex_height / 2
                    )
                })

                # Add an extra one at top-right, for tiling.
                if x == 0:
                    self.svg.polyline(hex, **{
                        'opacity': opacity,
                        'fill': fill,
                        'stroke': '#000000',
                        'transform': 'translate({}, {})'.format(
                            6 * side_length * 1.5 - hex_width / 2,
                            dy - hex_height / 2
                        )
                    })

                # Add an extra row at the end that matches the first row, for tiling.
                if y == 0:
                    dy = (6 * hex_height) if x % 2 == 0 else (6 * hex_height + hex_height / 2)
                    self.svg.polyline(hex, **{
                        'opacity': opacity,
                        'fill': fill,
                        'stroke': '#000000',
                        'transform': 'translate({}, {})'.format(
                            x * side_length * 1.5 - hex_width / 2,
                            dy - hex_height / 2
                        )
                    })

                # Add an extra one at bottom-right, for tiling.
                if x == 0 and y == 0:
                    self.svg.polyline(hex, **{
                        'opacity': opacity,
                        'fill': fill,
                        'stroke': '#000000',
                        'transform': 'translate({}, {})'.format(
                            6 * side_length * 1.5 - hex_width / 2,
                            5 * hex_height + hex_height / 2
                        )
                    })

                i += 1

    def geo_sinewaves(self):
        period = math.floor(promap(int(self.hash[1:][:1], 16), 0, 15, 100, 400))
        amplitude = math.floor(promap(int(self.hash[2:][:1], 16), 0, 15, 30, 100))
        wave_width = math.floor(promap(int(self.hash[3:][:1], 16), 0, 15, 3, 30))

        self.svg.width = period
        self.svg.height = wave_width * 36

        for i in range(35):
            val = int(self.hash[i:][1], 16)
            fill = '#ddd' if val % 2 == 0 else '#222'
            opacity = promap(val, 0, 15, 0.02, 0.15)
            x_offset = period / 4 * 0.7

            str = 'M0 {} C {} 0, {} 0, {} {} S {} {}, {} {} S {} 0, {}, {}'.format(
                amplitude, x_offset, (period / 2 - x_offset), (period / 2),
                amplitude, (period - x_offset), (amplitude * 2), period,
                amplitude, (period * 1.5 - x_offset), (period * 1.5), amplitude
            )

            self.svg.path(str, **{
                'fill': 'none',
                'stroke': fill,
                'transform': 'translate({}, {})'.format(
                    (period / 4), (wave_width * i - amplitude * 1.5)
                ),
                'style': {
                    'opacity': opacity,
                    'stroke_width': '{}px'.format(wave_width)
                }
            })

            self.svg.path(str, **{
                'fill': 'none',
                'stroke': fill,
                'transform': 'translate({}, {})'.format(
                    (period / 4), (wave_width * i - amplitude * 1.5 + wave_width * 36)
                ),
                'style': {
                    'opacity': opacity,
                    'stroke_width': '{}px'.format(wave_width)
                }
            })

    def geo_xes(self):
        square_size = promap(int(self.hash[0:][:1], 16), 0, 15, 10, 25)
        x_shape = self.build_x_shape(square_size)
        x_size = square_size * 3 * 0.943

        self.svg.width = x_size * 3
        self.svg.height = x_size * 3

        i = 0
        for y in range(5):
            for x in range(5):
                val = int(self.hash[i:][:1], 16)
                opacity = promap(val, 0, 15, 0.02, 0.15)
                dy = (y * x_size - x_size * 0.5) if x % 2 == 0 else (y * x_size - x_size * 0.5 + x_size / 4)
                fill = '#ddd' if val % 2 == 0 else '#222'

                self.svg.group(x_shape, **{
                    'fill': fill,
                    'transform': 'translate({}, {}) rotate(45, {}, {})'.format(
                        (x * x_size / 2 - x_size / 2), (dy - y * x_size / 2),
                        (x_size / 2), (x_size / 2)
                    ),
                    'style': {
                        'opacity': opacity
                    }
                })

                # Add an extra column on the right for tiling.
                if x == 0:
                    self.svg.group(x_shape, **{
                        'fill': fill,
                        'transform': 'translate({}, {}) rotate(45, {}, {})'.format(
                            (6 * x_size / 2 - x_size / 2), (dy - y * x_size / 2),
                            (x_size / 2), (x_size / 2)
                        ),
                        'style': {
                            'opacity': opacity
                        }
                    })

                # Add an extra row on the bottom that matches the first row, for tiling.
                if y == 0:
                    dy = (6 * x_size - x_size / 2) if x % 2 == 0 else (6 * x_size - x_size / 2 + x_size / 4)
                    self.svg.group(x_shape, **{
                        'fill': fill,
                        'transform': 'translate({}, {}) rotate(45, {}, {})'.format(
                            (x * x_size / 2 - x_size / 2), (dy - 6 * x_size / 2),
                            (x_size / 2), (x_size / 2)
                        ),
                        'style': {
                            'opacity': opacity
                        }
                    })

                # These can hang off the bottom, so put a row at the top for tiling.
                if y == 5:
                    self.svg.group(x_shape, **{
                        'fill': fill,
                        'transform': 'translate({}, {}) rotate(45, {}, {})'.format(
                            (x * x_size / 2 - x_size / 2), (dy - 11 * x_size / 2),
                            (x_size / 2), (x_size / 2)
                        ),
                        'style': {
                            'opacity': opacity
                        }
                    })

                # Add an extra one at top-right and bottom-right, for tiling.
                if x == 0 and y == 0:
                    self.svg.group(x_shape, **{
                        'fill': fill,
                        'transform': 'translate({}, {}) rotate(45, {}, {})'.format(
                            (6 * x_size / 2 - x_size / 2), (dy - 6 * x_size / 2),
                            (x_size / 2), (x_size / 2)
                        ),
                        'style': {
                            'opacity': opacity
                        }
                    })

                i += 1

    def geo_overlappingcircles(self):
        scale = int(self.hash[1:][:1], 16)
        diameter = promap(scale, 0, 15, 20, 200)
        radius = diameter / 2

        self.svg.width = radius * 6
        self.svg.height = radius * 6

        i = 0
        for y in range(5):
            for x in range(5):
                val = int(self.hash[i:][:1], 16)
                opacity = promap(val, 0, 15, 0.02, 0.1)
                fill = '#ddd' if val % 2 == 0 else '#222'

                self.svg.circle(x * radius, y * radius, radius, **{
                    'fill': fill,
                    'style': {
                        'opacity': opacity
                    }
                })

                # Add an extra one at top-right, for tiling.
                if x == 0:
                    self.svg.circle(6 * radius, y * radius, radius, **{
                        'fill': fill,
                        'style': {
                            'opacity': opacity
                        }
                    })

                # Add an extra row at the end that matches the first row, for tiling.
                if y == 0:
                    self.svg.circle(x * radius, 6 * radius, radius, **{
                        'fill': fill,
                        'style': {
                            'opacity': opacity
                        }
                    })

                # Add an extra one at bottom-right, for tiling.
                if x == 0 and y == 0:
                    self.svg.circle(6 * radius, 6 * radius, radius, **{
                        'fill': fill,
                        'style': {
                            'opacity': opacity
                        }
                    })

                i += 1

    def geo_squares(self):
        square_size = promap(int(self.hash[0:][:1], 16), 0, 15, 10, 70)

        self.svg.width = square_size * 6
        self.svg.height = square_size * 6

        i = 0
        for y in range(5):
            for x in range(5):
                val = int(self.hash[i:][:1], 16)
                opacity = promap(val, 0, 15, 0.02, 0.2)
                fill = '#ddd' if val % 2 == 0 else '#222'

                self.svg.rect(x * square_size, y * square_size, square_size, square_size, **{
                    'fill': fill,
                    'style': {
                        'opacity': opacity
                    }
                })

                i += 1

    def geo_rings(self):
        scale = int(self.hash[1:][:1], 16)
        ring_size = promap(scale, 0, 15, 5, 80)
        stroke_width = ring_size / 4

        self.svg.width = (ring_size + stroke_width) * 6
        self.svg.height = (ring_size + stroke_width) * 6

        i = 0
        for y in range(5):
            for x in range(5):
                val = int(self.hash[i:][:1], 16)
                opacity = promap(val, 0, 15, 0.02, 0.16)

                self.svg.circle(
                    x * ring_size + x * stroke_width + (ring_size + stroke_width) / 2,
                    y * ring_size + y * stroke_width + (ring_size + stroke_width) / 2,
                    ring_size / 2, **{
                        'fill': 'none',
                        'stroke': '#000',
                        'style': {
                            'opacity': opacity,
                            'stroke-width': '{}px'.format(stroke_width)
                        }
                    }
                )

                i += 1

    def build_hexagon_shape(self, side_length):
        c = side_length
        a = c / 2
        b = math.sin(60 * math.pi / 180) * c
        return '0, {}, {}, 0, {}, 0, {}, {}, {}, {}, {}, {}, 0, {}'.format(
            b, a, a + c, 2 * c, b, a + c, 2 * b, a, 2 * b, b
        )

    def build_x_shape(self, square_size):
        return [
            'self.rect({}, 0, {}, {})'.format(square_size, square_size, square_size * 3),
            'self.rect(0, {}, {}, {})'.format(square_size, square_size * 3, square_size)
        ]
