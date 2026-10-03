"""Large labeled previews from exported geometry; no generated concept imagery."""
from pathlib import Path
import json
import numpy as np
import trimesh
import vtk
import design as d

PACKAGE = Path(__file__).resolve().parents[1]
visual = d.load_source('capstone_renderer', 'pieces/fox-cat-capstones-v4/source/render.py')
DARK = (.50,.60,.72)  # light shell against dark background for visible geometry
TRAY_COLOR = (.40,.49,.61)
WHITE = (.95,.95,.90)
FOX = (.96,.62,.24)


def mesh(name):
    return trimesh.load_mesh(PACKAGE/'models'/f'{name}.stl', process=True)


def moved(m, position):
    result = m.copy()
    result.apply_translation(position)
    return result


def box(extents, center):
    return trimesh.creation.box(extents, transform=trimesh.transformations.translation_matrix(center))


def board(position=(0,0,d.BOARD_Z)):
    parts = [(moved(mesh('board-felt-backing'),position),DARK)]
    # Felt and grid represent the exact SVG template, not printed mesh details.
    parts.append((box([232,224,1],[position[0],position[1],position[2]+6.5]),(.04,.07,.12)))
    for i in range(6):
        c = -105+i*42
        parts += [(box([1.4,211.4,.05],[position[0]+c,position[1],position[2]+7.025]),WHITE),
                  (box([211.4,1.4,.05],[position[0],position[1]+c,position[2]+7.025]),WHITE)]
    return parts


def loaded_tray(team, position):
    color = WHITE if team=='cat' else FOX
    parts = [(moved(mesh('tray'),position),TRAY_COLOR)]
    stone = mesh(team+'-body-assembly')
    floor = moved(mesh('stone-floor'),[0,0,d.FLOOR_Z])
    for p in d.flat_positions():
        pos = np.array(p)+np.array(position)
        parts.extend([(moved(stone,pos),color),(moved(floor,pos),color)])
    parts.append((moved(mesh(team+'-capstone-storage-reference'),position),color))
    return parts


def render(name, title, note, parts, focus, camera, scale, size=(1800,1300)):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(.025,.035,.055)
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(*size)
    window.SetMultiSamples(8)
    window.AddRenderer(renderer)
    for m,color in parts:
        renderer.AddActor(visual.actor(m,color))
    visual.text(renderer,title,35,size[1]-85,48)
    visual.text(renderer,note,35,35,32)
    c = renderer.GetActiveCamera()
    c.ParallelProjectionOn()
    c.SetFocalPoint(*focus)
    c.SetPosition(*camera)
    c.SetViewUp(0,0,1)
    c.SetParallelScale(scale)
    renderer.ResetCameraClippingRange()
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(PACKAGE/'previews'/f'{name}.png'))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
    print(name,flush=True)


def main():
    platform = [(mesh('platform'),DARK)]
    play = platform + board()
    cat = mesh('cat-body-assembly')
    fox = mesh('fox-body-assembly')
    # A crowded pair and a five-flat stack show real scale/finger spacing.
    for team,m,pos,color in [('cat',cat,(-84,-84,73),WHITE),('fox',fox,(-42,-84,73),FOX),
                              ('cat',cat,(0,-42,73),WHITE)]:
        play.append((moved(m,pos),color))
    for i in range(5):
        play.append((moved(fox,(42,0,73+i*10)),FOX))
    play.append((moved(mesh('cat-capstone'),(-42,42,73)),WHITE))
    play.append((moved(mesh('fox-capstone'),(84,42,73)),FOX))
    wall = cat.copy()
    wall.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
    wall.apply_translation([84,-84,73-wall.bounds[0,2]])
    play.append((wall,WHITE))
    render('01-play','Full-size Tak | board foundation',
        '25 x 25 x 10 mm flats | 42 mm pitch | Ornament still to come',play,
        (0,0,52),(350,-440,385),180)
    exploded = platform + loaded_tray('cat',(-60,-87,100))
    exploded += loaded_tray('fox',(-60,-87,160)) + board((0,0,225))
    render('02-storage','Lift the board, then remove both cassettes',
        'Two located cassettes | 21 flats + one capstone each',exploded,
        (0,0,115),(360,-450,405),205)
    setup = platform + board() + loaded_tray('cat',(-265,-87,0)) + loaded_tray('fox',(145,-87,0))
    render('03-trays-out','Ready for play | cassettes beside the board',
        'No roof over the field | Felt/grid shown from the size template',setup,
        (0,0,25),(400,-700,630),220,size=(2000,1250))
    render('04-packed','Packed | low stepped rectangular platform',
        '248 x 240 x 72 mm printed shell | Transport latch not yet designed',platform+board(),
        (0,0,36),(350,-440,320),175)
    underside = mesh('tray')
    underside.apply_transform(trimesh.transformations.rotation_matrix(np.pi,[1,0,0]))
    underside.apply_translation([20,87,-underside.bounds[0,2]])
    cassette_parts = loaded_tray('cat',(-140,-87,0))+[(underside,TRAY_COLOR)]
    render('05-cassettes','Piece cassettes | lift out for play',
        'Flat rows: 5 + 5 + 6 + 5 | Separate capstone compartment',cassette_parts,
        (0,0,10),(230,-390,490),145)
    (PACKAGE/'reports/rendering.json').write_text(json.dumps({
        'source':'exported STL meshes', 'views':5, 'renderer':vtk.vtkVersion.GetVTKVersion(),
        'felt_and_grid':'dimensioned diagram from felt-grid-100-percent.svg',
        'rendered_accessibility':'Large white labels on dark background; visible grid and separate motif geometry',
        'physical_result':False},indent=2)+'\n')


if __name__=='__main__':
    main()
