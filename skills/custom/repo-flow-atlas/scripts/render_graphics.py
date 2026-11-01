"""Render an explicit atlas data model without inspecting any repository."""
import json
from pathlib import Path
from graphics import *

def render_graphics(data,output):
    SVG={};EXCAL=[];OVERVIEW=[]
    for pi,p in enumerate(data['pages']):
        coords={n['id']:(40+n['col']*560,220+n['row']*320) for n in p['nodes']}
        maxx=max(x for x,y in coords.values())+W+80;maxy=max(y for x,y in coords.values())+H+100
        used={};ports={};elements=[];sv=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{maxx}" height="{maxy}" viewBox="0 0 {maxx} {maxy}" data-page="{p["id"]}">', '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#64748b"/></marker></defs>',f'<rect width="{maxx}" height="{maxy}" fill="#fff"/>',f'<text x="40" y="50" font-size="28" fill="#172f4f" font-family="sans-serif" font-weight="700">{esc(p["title"])}</text>']
        for j,line in enumerate(wrap(p['summary'],160)):sv.append(f'<text x="40" y="{88+j*22}" font-size="16" fill="#52637a" font-family="sans-serif">{esc(line)}</text>')
        sv.append('<text x="40" y="160" font-size="13" fill="#64748b" font-family="sans-serif">Solid: call/data relationship. Dashed: dispatch, condition, async or unverified boundary. Static source analysis.</text>')
        title=text_element(p['id']+'-title',p['title'],40,30,maxx-80,40,28);elements.append(title)
        elements.append(text_element(p['id']+'-summary',p['summary'],40,85,maxx-80,70,16))
        shapes={}
        for n in p['nodes']:
            x,y=coords[n['id']];bg,stroke=COLORS[n['kind']];sid=p['id']+'-'+n['id'];sh=element(sid,'rectangle',x,y,W,H,stroke,bg);sh['roundness']={'type':3}
            if n['kind'] in ['boundary','decision']:sh['strokeStyle']='dashed'
            sh['boundElements']=[{'type':'text','id':sid+'-text'}];shapes[n['id']]=sh
            label=n['title']+(('.'+n['method']+'()') if n['method'] else '')+'\n\n'+n['detail']
            t='\n'.join(wrap(label,52));te=text_element(sid+'-text',t,x+14,y+12,W-28,H-24,14,sid)
            if n['evidence']:sh['link']=n['evidence'].get('url')
            elements.extend([sh,te])
        for i,edge in enumerate(p['edges']):
            points=route(coords[edge['from']],coords[edge['to']],list(coords.values()),maxx,maxy,used,ports)
            edge['points']=points;d='M'+' L'.join(f'{x},{y}' for x,y in points)
            dash='' if edge['kind'] in ['call','rpc','data'] else 'stroke-dasharray="6 5"'
            sv.append(f'<path d="{d}" fill="none" stroke="#64748b" stroke-width="1.6" {dash} marker-end="url(#arrow)"><title>{esc(edge["kind"]+": "+edge["label"])}</title></path>')
            label=edge['label']
            if label:
                segments=sorted(zip(points,points[1:]),key=lambda ab:abs(ab[0][0]-ab[1][0])+abs(ab[0][1]-ab[1][1]),reverse=True)
                a,b=segments[0];lx=(a[0]+b[0])/2;ly=(a[1]+b[1])/2-7
                sv.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#475569" stroke="#fff" stroke-width="4" paint-order="stroke">{esc(label)}</text>')
            eid=p['id']+'-edge-'+str(i);x,y=points[0];offset=[[px-x,py-y] for px,py in points]
            ar=element(eid,'arrow',x,y,max(abs(dx) for dx,dy in offset),max(abs(dy) for dx,dy in offset),'#64748b')
            ar.update(points=offset,startArrowhead=None,endArrowhead='arrow',elbowed=True,startBinding={'elementId':shapes[edge['from']]['id'],'focus':0,'gap':0},endBinding={'elementId':shapes[edge['to']]['id'],'focus':0,'gap':0},lastCommittedPoint=None)
            for binding,node_id,endpoint in [('startBinding',edge['from'],points[0]),('endBinding',edge['to'],points[-1])]:
                nx,ny=coords[node_id];ar[binding]['fixedPoint']=[(endpoint[0]-nx)/W,(endpoint[1]-ny)/H]
            if edge['kind'] not in ['call','rpc','data']:ar['strokeStyle']='dashed'
            for k in ['from','to']:shapes[edge[k]]['boundElements'].append({'type':'arrow','id':eid})
            elements.insert(2,ar)
            if label:elements.append(text_element(eid+'-label',label,lx-140,ly-12,280,20,12))
        for n in p['nodes']:
            x,y=coords[n['id']];bg,stroke=COLORS[n['kind']];dash='stroke-dasharray="7 4"' if n['kind'] in ['boundary','decision'] else ''
            sv.append(f'<g class="node" data-node="{n["id"]}" tabindex="0" role="button" aria-label="{esc(n["title"])}"><rect x="{x}" y="{y}" width="{W}" height="{H}" rx="12" fill="{bg}" stroke="{stroke}" stroke-width="1.5" {dash}/><title>{esc(n["detail"])}</title>')
            titlelines=wrap(n['title'],49)
            for j,line in enumerate(titlelines):sv.append(f'<text x="{x+16}" y="{y+24+j*18}" font-family="sans-serif" font-size="14" font-weight="700" fill="#243247">{esc(line)}</text>')
            yy=y+27+len(titlelines)*18
            if n['method']:
                for line in wrap(n['method']+'()',45):sv.append(f'<text x="{x+16}" y="{yy}" font-family="monospace" font-size="14" font-weight="700" fill="{stroke}">{esc(line)}</text>');yy+=18
            yy+=7
            for j,line in enumerate(wrap(n['detail'],57)):
                sv.append(f'<text x="{x+16}" y="{yy+j*17}" font-family="sans-serif" font-size="12" fill="#40516b">{esc(line)}</text>')
            ev=n['evidence'];loc=(ev['repo']+' · '+Path(ev.get('display_path',ev['path'])).name+':'+str(ev['line'])) if ev else 'Upstream source unverified'
            sv.append(f'<text x="{x+16}" y="{y+H-13}" font-size="10" fill="#66768b" font-family="monospace">{esc(loc)}</text></g>')
        sv.append('</svg>');svg=''.join(sv);SVG[p['id']]=svg
        (output/(p['id']+'.svg')).write_text(svg)
        ex={'type':'excalidraw','version':2,'source':'local-evidence-statement-atlas','elements':elements,'appState':{'gridSize':20,'viewBackgroundColor':'#ffffff'},'files':{}}
        (output/(p['id']+'.excalidraw')).write_text(json.dumps(ex,ensure_ascii=False,indent=2))
        # Combined editable board: each page occupies its own row to keep navigation stable.
        shift=pi*2700
        for el in elements:
            el=dict(el);el['y']+=shift;EXCAL.append(el)
        OVERVIEW.append({'id':p['id'],'title':p['title'],'nodes':len(p['nodes']),'edges':len(p['edges'])})
    
    return SVG,EXCAL
