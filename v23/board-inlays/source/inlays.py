"""V23 flush overlays; reuse v17 grid and retained v16 celestial CAD. Units mm."""
from functools import lru_cache
from pathlib import Path
import sys
import cadquery as cq

OUT = Path(__file__).resolve().parents[1]
REPO = OUT.parents[1]
sys.path.insert(0, str(OUT.parent / 'source'))
import case as case
sys.path.insert(0, str(REPO / 'v16-field-book/source'))
import tak_book as artwork

FACE = 15.3
DEPTH = .6
ROLES = {'body': (1, '#111111'), 'grid': (2, '#FFFFFF'),
         'stars': (2, '#FFFFFF'), 'art': (3, '#D6A54C')}


def union(shapes):
    return artwork.dc.union(shapes)


@lru_cache(None)
def grid(side):
    """The exact v17 four-leaf 0.8 mm grid, filled to the face."""
    lines = [case.box(7.6, 97.8, 10+36*i-.4, 10+36*i+.4, FACE-DEPTH, FACE)
             for i in range(6)]
    lines += [case.box(x-.4, x+.4, 9.6, 190.4, FACE-DEPTH, FACE)
              for x in (8, 44, 80)]
    shape = union(lines)
    return shape if side == 'left' else case.mirror(shape)


@lru_cache(None)
def overlays(side):
    old = 'A' if side == 'left' else 'B'
    shift = (0, 0, FACE-artwork.FACE)
    return {'grid': grid(side), 'stars': artwork.stars(old).translate(shift),
            'art': union([artwork.decor(old, colour).translate(shift)
                          for colour in ('orange', 'purple')])}


@lru_cache(None)
def parts(side, release=0):
    accents = overlays(side)
    body = case.board(side, release).cut(union(list(accents.values()))).clean()
    return {'body': body, **accents}


def complete(side, release=0):
    return union(list(parts(side, release).values()))


def coupon():
    """Two front-row cells plus the seam half-cell; grid, stars, moon and spiral."""
    clip = case.box(7.6, 97.8, 9.6, 46.4, FACE-DEPTH-1.2, FACE)
    p = parts('left')
    return {role: shape.intersect(clip).clean() for role, shape in p.items()}
