"""Generic SVG/Excalidraw geometry helpers."""
import html,hashlib,heapq
W,H,STEP=440,200,20
COLORS={'method':('#eef4ff','#4263a2'),'decision':('#fff4e6','#d97706'),'database':('#ebfbee','#2b8a3e'),'config':('#f3f0ff','#7950b2'),'queue':('#fff9db','#b98900'),'boundary':('#f8f9fa','#868e96')}
def esc(s):return html.escape(str(s),quote=True)
def wrap(s,limit):
    lines=[]
    for paragraph in s.split('\n'):
        current='';width=0
        for ch in paragraph:
            cw=2 if ord(ch)>255 else 1
            if width+cw>limit:lines.append(current);current='';width=0
            current+=ch;width+=cw
        lines.append(current)
    return lines
def simplify(points):
    out=[]
    for p in points:
        if out and p==out[-1]:continue
        if len(out)>1 and ((out[-2][0]==out[-1][0]==p[0]) or (out[-2][1]==out[-1][1]==p[1])):out[-1]=p
        else:out.append(p)
    return out
def route(a,b,boxes,maxx,maxy,used,ports):
    ax,ay=a;bx,by=b
    def port(x,y,side):
        key=(x,y,side);count=ports.get(key,0);ports[key]=count+1
        offset=[0,-40,40,-60,60,-80,80][count%7]
        if side=='right':return (x+W,y+H//2+offset)
        if side=='left':return (x,y+H//2+offset)
        if side=='bottom':return (x+W//2+offset,y+H)
        return (x+W//2+offset,y)
    if bx>ax: start=port(ax,ay,'right');goal=port(bx,by,'left');s=(start[0]+STEP,start[1]);t=(goal[0]-STEP,goal[1])
    elif bx<ax:start=port(ax,ay,'left');goal=port(bx,by,'right');s=(start[0]-STEP,start[1]);t=(goal[0]+STEP,goal[1])
    elif by>ay:start=port(ax,ay,'bottom');goal=port(bx,by,'top');s=(start[0],start[1]+STEP);t=(goal[0],goal[1]-STEP)
    else:start=port(ax,ay,'top');goal=port(bx,by,'bottom');s=(start[0],start[1]-STEP);t=(goal[0],goal[1]+STEP)
    def blocked(x,y):return any(px-5<x<px+W+5 and py-5<y<py+H+5 for px,py in boxes)
    q=[(0,0,s,None)];dist={(s,None):0};prev={};end=None
    while q:
        _,cost,v,direction=heapq.heappop(q)
        if v==t:end=(v,direction);break
        if cost!=dist.get((v,direction)):continue
        for dx,dy in [(STEP,0),(-STEP,0),(0,STEP),(0,-STEP)]:
            z=(v[0]+dx,v[1]+dy);nd=(dx,dy)
            if z[0]<20 or z[1]<180 or z[0]>maxx-20 or z[1]>maxy-20 or blocked(*z):continue
            c=cost+1+(0.7 if direction and nd!=direction else 0)+used.get(z,0)*0.15
            key=(z,nd)
            if c<dist.get(key,1e9):
                dist[key]=c;prev[key]=(v,direction);h=(abs(z[0]-t[0])+abs(z[1]-t[1]))/STEP
                heapq.heappush(q,(c+h,c,z,nd))
    if not end:raise ValueError(('No obstacle-free route',a,b))
    points=[];key=end
    while key in prev:points.append(key[0]);key=prev[key]
    points.append(s);points.reverse()
    for point in points:used[point]=used.get(point,0)+1
    return simplify([start]+points+[goal])

def element(id,type,x,y,w,h,stroke='#4263a2',bg='transparent'):
    return dict(id=id,type=type,x=x,y=y,width=w,height=h,angle=0,strokeColor=stroke,backgroundColor=bg,fillStyle='solid',strokeWidth=1.5,strokeStyle='solid',roughness=0,opacity=100,groupIds=[],frameId=None,roundness=None,seed=int(hashlib.sha256(id.encode()).hexdigest()[:7],16),version=1,versionNonce=1,isDeleted=False,boundElements=None,updated=1,link=None,locked=False)
def text_element(id,text,x,y,w,h,size=16,container=None):
    r=element(id,'text',x,y,w,h,'#243247');r.update(text=text,originalText=text,fontSize=size,fontFamily=2,textAlign='left',verticalAlign='middle',containerId=container,lineHeight=1.25,autoResize=False);return r

