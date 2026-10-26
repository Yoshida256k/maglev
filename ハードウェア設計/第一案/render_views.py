import math, vtk, maglev_course_model as c
FONT="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
def actors(asm, clip=None):
    out=[]
    for ch in asm.children:
        shp = ch.obj.val() if hasattr(ch.obj,"val") else ch.obj
        pd = shp.toVtkPolyData(0.2, 0.05)
        m=vtk.vtkPolyDataMapper(); m.SetInputData(pd)
        a=vtk.vtkActor(); a.SetMapper(m)
        r,g,b,al = ch.color.toTuple() if ch.color else (0.7,0.7,0.7,1)
        p=a.GetProperty(); p.SetColor(r,g,b); p.SetInterpolationToPhong(); p.SetSpecular(0.25); p.SetSpecularPower(30)
        if al<1: p.SetOpacity(al)
        out.append(a)
    return out
def render(acts, pos, foc, fname, texts=(), size=(1600,1100), bg=(1,1,1)):
    ren=vtk.vtkRenderer(); ren.SetBackground(*bg); ren.SetUseDepthPeeling(1); ren.SetMaximumNumberOfPeels(8)
    for a in acts: ren.AddActor(a)
    for (t,x,y,s) in texts:
        ta=vtk.vtkTextActor(); ta.SetInput(t); tp=ta.GetTextProperty(); tp.SetFontSize(s); tp.SetColor(0.1,0.1,0.1)
        tp.SetFontFamily(vtk.VTK_FONT_FILE); tp.SetFontFile(FONT); ta.SetPosition(x,y); ren.AddActor2D(ta)
    cam=ren.GetActiveCamera(); cam.SetPosition(*pos); cam.SetFocalPoint(*foc); cam.SetViewUp(0,0,1); ren.ResetCameraClippingRange()
    kit=vtk.vtkLightKit(); kit.AddLightsToRenderer(ren)
    rw=vtk.vtkRenderWindow(); rw.SetOffScreenRendering(1); rw.SetAlphaBitPlanes(1); rw.SetMultiSamples(0); rw.SetSize(*size); rw.AddRenderer(ren); rw.Render()
    w=vtk.vtkWindowToImageFilter(); w.SetInput(rw); w.Update()
    pw=vtk.vtkPNGWriter(); pw.SetFileName(fname); pw.SetInputConnection(w.GetOutputPort()); pw.Write(); print("wrote",fname)
full=actors(c.build())
ang=math.radians(c.CART_CENTER); rm=(c.R_INWALL_OUT+c.R_SHEET_IN)/2
cx,cy=rm*math.cos(ang), rm*math.sin(ang)
render(full,(950,-1150,850),(0,60,10),"m_overall.png",[("浮上式コース全体（円周3.0m・外側：透明シート＋コイル枠、内側：透明板）",30,1050,26)])
render(full,(cx*0.25-140, cy*0.25-260, 330),(cx,cy,40),"m_cart_close.png",[("台車付近（床の赤＝浮上用磁石、N極上向き）",30,1050,26)])
show=actors(c.build_showcase())
fa=math.radians(c.CART_CENTER+38)
render(show,(230*math.cos(fa), 230*math.sin(fa), 200),(cx,cy,35),"m_cart_only.png",
       [("台車（浮いてるミニ四駆）：床の赤＝浮上磁石、黄＝2段ローラー、外側ポッドに駆動磁石5極",30,1050,24)])
