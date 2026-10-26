import itertools
L=3000; tau=37.5; cart=4*tau
def bits(x, gsp, offs, poles):
    # cart occupies [x, x+cart) mod L, poles N,S,N,S... ; sensor active if under S
    out=[]
    for g in range(int(L/gsp)):
        for o in offs:
            s=(g*gsp+o)
            r=(s-x)%L
            if r<cart:
                k=int(r//tau)
                # skip near boundaries (uncertain)
                out.append(1 if poles[k]=='S' else 0)
            else: out.append(0)
    return tuple(out)
def check(gsp, offs, poles, step=0.5, margin=3):
    seen={}
    amb=0
    x=0.0
    while x<L:
        # skip positions where any sensor within margin of a pole boundary
        b=bits(x,gsp,offs,poles)
        if b in seen and abs(((seen[b]-x+L/2)%L)-L/2)>margin*2:
            amb+=1; ex=(seen[b],x)
        else: seen.setdefault(b,x)
        x+=step
    return amb, len(seen)
for gsp in [150,112.5,75,37.5]:
    print(gsp, check(gsp,[0,25,50],'NSNS'))

def spread(gsp, offs, poles, step=0.25):
    d={}
    x=0.0
    while x<L:
        d.setdefault(bits(x,gsp,offs,poles),[]).append(x); x+=step
    worst=0
    for b,xs in d.items():
        xs=sorted(xs)
        # circular span: max gap complement
        gaps=[xs[i+1]-xs[i] for i in range(len(xs)-1)]+[xs[0]+L-xs[-1]]
        span=L-max(gaps)
        worst=max(worst,span)
    return len(d), worst
print('---')
for gsp in [150,112.5,75]:
    for poles in ['NSNS','NSNSN','SNSNS']:
        c=len(poles)*tau
        globals()['cart']=c
        print(gsp,poles,spread(gsp,[0,25,50],poles))
globals()['cart']=4*tau
