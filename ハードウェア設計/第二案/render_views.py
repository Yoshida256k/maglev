import math, vtk, maglev_floor_drive_model as c
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
ang=math.radians(c.CART_CENTER); cx,cy=c.R_C*math.cos(ang), c.R_C*math.sin(ang)
render(actors(c.build()),(950,-1150,820),(0,60,-5),"f_overall.png",[("床下駆動版（展示状態）：床はミラー/黒のカバー、壁は透明フェンス、台車付近のLED帯が点灯",30,1050,24)])
render(actors(c.build(see_through=True)),(950,-1150,820),(0,60,-5),"f_overall_inside.png",[("床下駆動版（床カバーを透かした図）：床下にコイル60個と浮上磁石2列",30,1050,24)])
show=actors(c.build_showcase())
# 目線の高さ：コースの外から透明フェンス越しに真横
out=c.R_C+380
a2=math.radians(c.CART_CENTER-3)
render(show,(out*math.cos(a2), out*math.sin(a2), 14),(cx,cy,12),"f_eye_level.png",
       [("目線の高さ（外側の透明フェンス越し）：床から6mm浮いて、下が光る",30,1050,26)], bg=(0.93,0.94,0.96))
fa=math.radians(c.CART_CENTER+30)
render(show,(260*math.cos(fa), 260*math.sin(fa), 170),(cx,cy,10),"f_cart_3q.png",
       [("台車：高さ約40mm、空のホイールハウスが光る、2段ローラー×4",30,1050,26)])
