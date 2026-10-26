import math, sys
import vtk
import linear_course_model as course

asm = course.build()

def actors(filter_fn=None, clip=None, opacity_map=None):
    out = []
    for ch in asm.children:
        if filter_fn and not filter_fn(ch.name):
            continue
        shp = ch.obj.val() if hasattr(ch.obj, "val") else ch.obj
        pd = shp.toVtkPolyData(0.2, 0.05)
        src = pd
        if clip is not None:
            c = vtk.vtkClipPolyData(); c.SetInputData(pd); c.SetClipFunction(clip); c.Update()
            src = c.GetOutput()
        m = vtk.vtkPolyDataMapper(); m.SetInputData(src)
        a = vtk.vtkActor(); a.SetMapper(m)
        r, g, b, _ = ch.color.toTuple() if ch.color else (0.7, 0.7, 0.7, 1)
        a.GetProperty().SetColor(r, g, b)
        a.GetProperty().SetInterpolationToPhong()
        a.GetProperty().SetSpecular(0.15)
        if opacity_map:
            op = opacity_map(ch.name)
            if op < 1: a.GetProperty().SetOpacity(op)
        out.append(a)
    return out

def render(acts, cam_pos, focal, view_up, fname, size=(1600, 1100), parallel=None, texts=()):
    ren = vtk.vtkRenderer(); ren.SetBackground(1, 1, 1)
    for a in acts: ren.AddActor(a)
    for (txt, x, y, sz) in texts:
        t = vtk.vtkTextActor(); t.SetInput(txt)
        tp = t.GetTextProperty(); tp.SetFontSize(sz); tp.SetColor(0.1, 0.1, 0.1)
        tp.SetFontFamily(vtk.VTK_FONT_FILE); tp.SetFontFile("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
        t.SetPosition(x, y); ren.AddActor2D(t)
    cam = ren.GetActiveCamera()
    cam.SetPosition(*cam_pos); cam.SetFocalPoint(*focal); cam.SetViewUp(*view_up)
    if parallel:
        cam.ParallelProjectionOn(); cam.SetParallelScale(parallel)
    ren.ResetCameraClippingRange()
    kit = vtk.vtkLightKit(); kit.SetKeyLightIntensity(1.0); kit.AddLightsToRenderer(ren)
    rw = vtk.vtkRenderWindow(); rw.SetOffScreenRendering(1); rw.SetSize(*size); rw.AddRenderer(ren)
    rw.SetMultiSamples(8); rw.Render()
    w = vtk.vtkWindowToImageFilter(); w.SetInput(rw); w.Update()
    p = vtk.vtkPNGWriter(); p.SetFileName(fname); p.SetInputConnection(w.GetOutputPort()); p.Write()
    print("wrote", fname)

ang = math.radians(course.CART_CENTER)
cx, cy = course.R_C * math.cos(ang), course.R_C * math.sin(ang)

# 1) 全体（斜め上から）
render(actors(), (950, -1100, 900), (0, 60, 20), (0, 0, 1), "view_overall.png",
       texts=[("コース全体（円周3.0m・コイル60個・10区間）", 30, 1050, 30)])

# 2) 台車付近の拡大（壁の手前側を切り取り、内側から見る）
render(actors(opacity_map=lambda n: 0.35 if n in ("cart_magnet_carrier","cart_body") else 1), (cx * 0.35 - 260, cy * 0.35 - 120, 260), (cx, cy, 55), (0, 0, 1), "view_cart_close.png",
       texts=[("台車付近（内側から見た図）  磁石：赤=N 青=S   コイル：橙=U 黄=V 緑=W", 30, 1050, 26)])

