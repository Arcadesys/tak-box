"""V24 flush overlays; reuse v17 grid and retained v16 celestial CAD. Units mm."""
from functools import lru_cache
from pathlib import Path
import sys
import cadquery as cq

OUT = Path(__file__).resolve().parents[1]
REPO = OUT.parents[2]
sys.path.insert(0, str(OUT.parent / 'source'))
import case as case
sys.path.insert(0, str(OUT / 'source/vendor/artwork'))
import tak_book as artwork

FACE = 16.5
DEPTH = .6
ROLES = {'body': (1, '#111111'), 'grid': (2, '#FFFFFF'),
         'stars': (2, '#FFFFFF'), 'orange': (3, '#D6A54C'),
         'purple': (4, '#B887DD')}


def slot(role, silk=True):
    return ROLES[role][0] if silk else (1 if role == 'body' else 2)


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
            'orange': artwork.decor(old, 'orange').translate(shift),
            'purple': artwork.decor(old, 'purple').translate(shift)}


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
