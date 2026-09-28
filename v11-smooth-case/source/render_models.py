"""Render high-contrast, source-faithful views of the smooth outer case CAD.

All depicted parts are exported CAD surfaces or the actual current-piece STLs.
Coordinates are assembly millimeters; this is a digital study, not a physical
fit claim. Run after build_models.py and verification have written their files.
"""
from pathlib import Path
import sys

import cadquery as cq
import vtk

import tak_drawers as design

OUT = Path(__file__).resolve().parent.parent
PREVIEWS = OUT / "previews"
PREVIEWS.mkdir(exist_ok=True)
MODELS = OUT / "models"
REFERENCES = Path(__file__).resolve().parent / "references"

SHELL = (.85, .9, .96)
GRID = (.08, .11, .16)
TRAY = (.72, .78, .84)
CAT = (1., .65, .23)
WITCH = (.76, .57, 1.)
STOP = (.08, .85, .91)
BACKGROUND = (.025, .035, .055)
PARTS = {}


def part(name):
    if name not in PARTS:
        path = MODELS / f"{name}.step"
        if not path.exists():
            raise FileNotFoundError(f"Render needs exported CAD: {path}")
        PARTS[name] = cq.importers.importStep(str(path)).val()
    return PARTS[name]


def polygon_actor(poly, color, opacity=1):
    normal = vtk.vtkPolyDataNormals()
    normal.SetInputData(poly)
    normal.ConsistencyOn()
    normal.AutoOrientNormalsOn()
    normal.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normal.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color)
    actor.GetProperty().SetAmbient(.35)
    actor.GetProperty().SetDiffuse(.65)
    actor.GetProperty().SetOpacity(opacity)
    return actor


def solid_actor(shape, color, opacity=1):
    vertices, triangles = shape.tessellate(.07, .18)
    points = vtk.vtkPoints()
    faces = vtk.vtkCellArray()
    for point in vertices:
        points.InsertNextPoint(point.x, point.y, point.z)
    for triangle in triangles:
        faces.InsertNextCell(3)
        for index in triangle:
            faces.InsertCellPoint(index)
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(faces)
    return polygon_actor(poly, color, opacity)


def stl_actor(name, matrix, color):
    source = Path(name)
    if not source.is_absolute():
        source = REFERENCES / source
    if not source.exists():
        raise FileNotFoundError(source)
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(source))
    reader.Update()
    vtk_matrix = vtk.vtkMatrix4x4()
    for row, values in enumerate(matrix):
        for col, value in enumerate(values):
            vtk_matrix.SetElement(row, col, value)
    transform = vtk.vtkTransform()
    transform.SetMatrix(vtk_matrix)
    applied = vtk.vtkTransformPolyDataFilter()
    applied.SetInputConnection(reader.GetOutputPort())
    applied.SetTransform(transform)
    applied.Update()
    return polygon_actor(applied.GetOutput(), color)


def label(renderer, message, x, y, size, *, bold=False):
    actor = vtk.vtkTextActor()
    actor.SetInput(message)
    actor.SetPosition(x, y)
    prop = actor.GetTextProperty()
    prop.SetFontFamilyToArial()
    prop.SetFontSize(size)
    prop.SetColor(.98, .99, 1.)
    if bold:
        prop.BoldOn()
    renderer.AddActor2D(actor)


def render(filename, title, caption, solids, camera, focal, scale, *, up=(0, 0, 1), meshes=()):
    if len(sys.argv) > 1 and filename not in sys.argv[1:]:
        return
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(1500, 1000)
    window.SetMultiSamples(8)
    window.SetAlphaBitPlanes(1)
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(*BACKGROUND)
    renderer.SetUseDepthPeeling(1)
    window.AddRenderer(renderer)
    for shape, color, opacity in solids:
        renderer.AddActor(solid_actor(shape, color, opacity))
    for mesh in meshes:
        renderer.AddActor(mesh)
    view = renderer.GetActiveCamera()
    view.ParallelProjectionOn()
    view.SetPosition(*camera)
    view.SetFocalPoint(*focal)
    view.SetViewUp(*up)
    view.SetParallelScale(scale)
    renderer.ResetCameraClippingRange()
    label(renderer, title, 38, 923, 41, bold=True)
    label(renderer, caption, 40, 68, 26)
    label(renderer, "DIGITAL CAD / ACTUAL SOURCE GEOMETRY / PHYSICAL FIT PENDING", 40, 25, 20)
    window.Render()
    image = vtk.vtkWindowToImageFilter()
    image.SetInput(window)
    image.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(PREVIEWS / filename))
    writer.SetInputConnection(image.GetOutputPort())
    writer.Write()
    window.Finalize()
    print(filename, flush=True)


def render_pair(filename, views):
    """One large comparison sheet with independent opposing CAD cameras."""
    if len(sys.argv) > 1 and filename not in sys.argv[1:]:
        return
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(1500, 1000)
    window.SetMultiSamples(8)
    window.SetAlphaBitPlanes(1)
    for index, (title, caption, solids, position, focal, scale) in enumerate(views):
        renderer = vtk.vtkRenderer()
        renderer.SetViewport(index*.5, 0, (index+1)*.5, 1)
        renderer.SetBackground(*BACKGROUND)
        renderer.SetUseDepthPeeling(1)
        window.AddRenderer(renderer)
        for shape, color, opacity in solids:
            renderer.AddActor(solid_actor(shape, color, opacity))
        camera = renderer.GetActiveCamera()
        camera.ParallelProjectionOn()
        camera.SetPosition(*position)
        camera.SetFocalPoint(*focal)
        camera.SetViewUp(0, 0, 1)
        camera.SetParallelScale(scale)
        renderer.ResetCameraClippingRange()
        label(renderer, title, 25, 922, 29, bold=True)
        label(renderer, caption, 25, 70, 22)
        label(renderer, "DIGITAL CAD / PHYSICAL FIT PENDING", 25, 28, 17)
    window.Render()
    image = vtk.vtkWindowToImageFilter()
    image.SetInput(window)
    image.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(PREVIEWS / filename))
    writer.SetInputConnection(image.GetOutputPort())
    writer.Write()
    window.Finalize()
    print(filename, flush=True)


def case_parts(angle=-90, *, shell_opacity=1, tray_opacity=1,
               trays=True, lift_a=0, lift_b=0, grid=True):
    """Color-separated instances of the exported CAD in its true assembly pose."""
    shapes = []
    for name in ("stop-shoe-left", "stop-shoe-right"):
        shapes.append((part(name), STOP, shell_opacity))
    for index, name in enumerate(("wing-a", "center", "wing-b")):
        shapes.append((design.posed(part(name), index, angle), SHELL, shell_opacity))
        if grid:
            grid_name = ("grid-a", "grid-center", "grid-b")[index]
            shapes.append((design.posed(part(grid_name), index, angle), GRID, shell_opacity))
    if trays:
        for index, name, lift in ((0, "tray-a", lift_a), (2, "tray-b", lift_b)):
            shape = design.lift_tray(part(name), index, lift)
            shapes.append((design.posed(shape, index, angle), TRAY, tray_opacity))
    return shapes


if not hasattr(design, "PRESS_Y") or not hasattr(design, "CASE_X"):
    raise RuntimeError("Smooth cheek and recessed release source is required")


# Both x ends are shown from opposing oblique cameras. This exposes the
# protective cheek, width edge, and hinge termination at each end.
FOLDED = case_parts()
render_pair("01-folded-both-ends.png", (
    ("LEFT END / X MIN", "Rounded cheek + hinge edge", FOLDED,
     (-270, -145, 160), (102.5, 102.5, 43), 144),
    ("RIGHT END / X MAX", "Recessed press / guarded edge", FOLDED,
     (475, -145, 160), (102.5, 102.5, 43), 144),
))


# Crop the exact folded solids to the press region so both sides of the detail
# sheet have legible margins. Then remove only the outside skin in one copy.
detail_roi = design.box(204, 230, 70, 119, 19, 70)
detail_opaque = []
for name, index in (("wing-a", 0), ("wing-b", 2)):
    shape = design.posed(part(name), index, -90)
    cropped = shape.intersect(detail_roi)
    if cropped.Volume() > 1e-5:
        detail_opaque.append((cropped, SHELL, 1))
folded_a = design.posed(part("wing-a"), 0, -90)
expose_release = design.box(223.0, 230, 79, 113, 25, 65)
release_cutaway = folded_a.intersect(detail_roi).cut(expose_release)
press_tongue = design.posed(design.closure_tongue("right"), 0, -90)
press_stop = design.posed(design.box(*design.PRESS_STOP_X, 37, 49, 4, 17), 0, -90)
render_pair("02-release-recess-detail.png", (
    ("RIGHT END / PRESS RECESS", "Wide inset press, no pull tab",
     detail_opaque, (390, 35, 85), (217, 95, 44), 62),
    ("SOURCE CAD / SKIN CUT AWAY", "Inset tongue behind protective wall",
     [(release_cutaway, SHELL, .55),
      (press_tongue, STOP, 1), (press_stop, CAT, 1)],
     (390, 35, 85), (217, 95, 44), 62),
))


render(
    "03-open-tray-lift.png", "V11 / UNFOLD, THEN LIFT",
    "CAT tray raised vertically from keyed posts  |  playing face stays clear",
    case_parts(0, lift_a=58), (350, -295, 360), (102.5, 102.5, 27), 160,
)


def coupon_sheet():
    rows = (
        (("fit-protected-hinge-frame", SHELL), ("fit-stop-shoe-left", STOP)),
        (("fit-key-wing", SHELL), ("fit-key-tray-B", TRAY)),
        (("fit-recessed-catch-A", CAT), ("fit-recessed-catch-B", WITCH),
         ("fit-recessed-catch-C", STOP), ("fit-recessed-receiver", TRAY)),
    )
    meshes = []
    y = 0
    total_width = 0
    for row in rows:
        x = 0
        row_height = 0
        for name, color in row:
            path = MODELS / f"{name}.stl"
            if not path.exists():
                raise FileNotFoundError(path)
            reader = vtk.vtkSTLReader()
            reader.SetFileName(str(path))
            reader.Update()
            poly = reader.GetOutput()
            if poly.GetNumberOfPoints() == 0:
                raise ValueError(f"Empty trial mesh: {path}")
            xmin, xmax, ymin, ymax, _, _ = poly.GetBounds()
            place = ((1, 0, 0, x-xmin), (0, 1, 0, y-ymin),
                     (0, 0, 1, 0), (0, 0, 0, 1))
            meshes.append(stl_actor(str(path), place, color))
            x += xmax-xmin+15
            row_height = max(row_height, ymax-ymin)
        total_width = max(total_width, x-15)
        y += row_height+17
    return meshes, total_width, y-17


coupons, coupon_width, coupon_height = coupon_sheet()
coupon_focal = (coupon_width/2, coupon_height/2, 7)
coupon_scale = max(coupon_height/2+40, coupon_width/3+40, 110)
render(
    "04-protected-fit-coupons.png", "V11 / EXTERIOR FIT COUPONS",
    "Print-pose CAD meshes  |  guarded hinge, tray key, inset catch A/B/C + receiver",
    [], (coupon_focal[0]+250, coupon_focal[1]-235, 310),
    coupon_focal, coupon_scale, meshes=coupons,
)
