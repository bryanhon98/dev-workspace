"""Build the reusable, offline flow atlas from an explicit evidence manifest."""
import argparse,copy,hashlib,json,re
from pathlib import Path
from java_reader import extract_statements,mask_java,compact_java
from render_graphics import render_graphics

KINDS={'method','decision','database','config','queue','boundary'}
EDGES={'call','rpc','dispatch','binding','control','data','message','async','unknown'}
ASSETS=Path(__file__).resolve().parents[1]/'assets'

def source_path(root,relative):
    relative=Path(relative)
    if relative.is_absolute():raise ValueError('Source paths must be repository-relative')
    path=(root/relative).resolve()
    try:path.relative_to(root)
    except ValueError:raise ValueError('Source reference escapes its repository')
    forbidden={'.git','.ssh','.aws','.azure','.kube','.npmrc','.gitconfig','credentials.json','database.yml'}
    if any(part in forbidden or part.startswith('.env') for part in relative.parts) or path.suffix in {'.key','.pem','.p12','.db','.sqlite','.log'}:
        raise ValueError('Credential/log/database material is outside atlas source scope')
    if not path.is_file():raise ValueError('Missing source evidence: '+str(relative))
    return path

def prepare(manifest,base):
    data=copy.deepcopy(manifest);roots={};repos=[];hashes={}
    for repo in data.get('repositories',[]):
        if repo['id'] in roots:raise ValueError('Duplicate repository id')
        root=(base/repo['root']).resolve();roots[repo['id']]=root
        repos.append({'id':repo['id'],'label':repo.get('label',repo['id'])})
    data['repositories']=repos
    def evidence(ev):
        if ev['repo'] not in roots:raise ValueError('Unknown repository id')
        path=source_path(roots[ev['repo']],ev['path']);text=path.read_text()
        if not 1<=ev['line']<=len(text.splitlines()):raise ValueError('Source line outside file')
        package=next((r.get('package_prefix','') for r in manifest['repositories'] if r['id']==ev['repo']),'')
        relative=ev['path'].replace('\\','/')
        shown=relative.split('/src/main/java/',1)[-1] if '/src/main/java/' in relative else relative
        if shown.startswith('src/main/java/'):shown=shown[len('src/main/java/'):]
        if package and shown.startswith(package):shown=shown[len(package):]
        short=ev['repo']+'/'+shown
        safe={'repo':ev['repo'],'path':ev['repo']+'/'+relative,'display_path':short,'line':ev['line']}
        if data.get('local_source_links',True):safe['url']=path.as_uri()
        hashes[ev['repo']+'/'+relative]=hashlib.sha256(text.encode()).hexdigest()
        return safe,path,text
    functions=[];by_id={}
    for function in data.get('functions',[]):
        if function['id'] in by_id:raise ValueError('Duplicate function id')
        ev,path,text=evidence(function);lines=text.splitlines(keepends=True)
        end=function['end_line']
        if end<function['line'] or end>len(lines):raise ValueError('Function end line outside file')
        excerpt=''.join(lines[function['line']-1:end]);method=function['method']
        if not re.search(r'\b'+re.escape(method)+r'\s*\(',excerpt):raise ValueError('Function name is absent from its source range')
        out=dict(function);out.update(ev);out['class']=function.get('class',path.stem)
        if path.suffix=='.java':
            masked=mask_java(excerpt);brace=masked.find('{');close=masked.rfind('}')
            if brace<0 or close<brace:raise ValueError('Java function needs a complete body range')
            if not re.search(r'\b'+re.escape(method)+r'\s*\(',masked[:brace]):raise ValueError('Java source range must begin at the method declaration')
            out['signature']=compact_java(excerpt[:brace])
            out['statements']=extract_statements(excerpt[brace+1:close],function['line']+excerpt[:brace+1].count('\n'))
        else:
            # Other languages retain agent-selected source units, verified against source.
            for row in out.get('statements',[]):
                if not function['line']<=row['line']<=row['end_line']<=end:raise ValueError('Code unit outside function evidence')
                source=''.join(lines[row['line']-1:row['end_line']])
                if compact_java(source)!=compact_java(row['code']):raise ValueError('Code unit is not an exact source excerpt')
            if 'statements' not in out:raise ValueError('Non-Java functions need source-verified statement units')
        by_id[out['id']]=out;functions.append(out)
    ids=set()
    if not data.get('pages'):raise ValueError('At least one flow page is required')
    for page in data['pages']:
        if not re.fullmatch(r'[A-Za-z0-9_-]+',page['id']) or page['id'] in ids:raise ValueError('Invalid or duplicate page id')
        ids.add(page['id']);nodes={};occupied=set()
        for i,node in enumerate(page['nodes']):
            if not re.fullmatch(r'[A-Za-z0-9_-]+',node['id']) or node['id'] in nodes:raise ValueError('Invalid or duplicate node id')
            node.setdefault('col',i%3);node.setdefault('row',i//3)
            if not all(isinstance(node[k],int) and node[k]>=0 for k in ['col','row']):raise ValueError('Grid coordinates must be nonnegative integers')
            if (node['col'],node['row']) in occupied:raise ValueError('Nodes overlap on grid')
            occupied.add((node['col'],node['row']));nodes[node['id']]=node
            if node['kind'] not in KINDS:raise ValueError('Unsupported node kind')
            if not node.get('reader',{}).get('overview'):raise ValueError('Every node needs an explanatory overview')
            node.setdefault('method',None);node.setdefault('evidence',None)
            if node.get('function_id'):
                function=by_id[node['function_id']]
                node['method']=function['method'];node['evidence']={k:function[k] for k in ['repo','path','display_path','line']}
                if function.get('url'):node['evidence']['url']=function['url']
                reader=node['reader'];reader['signature']=function['signature'];reader['signatures']=[function['signature']]
                if not reader.get('inputs') or not reader.get('steps') or not reader.get('outcome'):raise ValueError('Function explanations need inputs, concrete steps and an outcome')
            elif node.get('evidence'):
                node['evidence']=evidence(node['evidence'])[0]
        for edge in page['edges']:
            if edge['from'] not in nodes or edge['to'] not in nodes:raise ValueError('Dangling relationship')
            if edge['kind'] not in EDGES:raise ValueError('Unsupported relationship kind')
            if not edge.get('explanation'):raise ValueError('Relationships need readable explanation, not just node ids')
            edge.setdefault('label','')
    data['functions']=functions;data['source_hashes']=hashes;data.setdefault('routes',[])
    data.setdefault('scope','Static source-based explanation; not a runtime trace.')
    return data

def build(manifest_path,output,overwrite=False):
    manifest_path=Path(manifest_path).resolve();output=Path(output).resolve()
    if output.exists() and any(output.iterdir()) and not overwrite:raise ValueError('Output is nonempty; choose another directory or explicitly use --overwrite')
    data=prepare(json.loads(manifest_path.read_text()),manifest_path.parent)
    output.mkdir(parents=True,exist_ok=True)
    svgs,combined=render_graphics(data,output)
    def embedded(value):return json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    template=(ASSETS/'viewer.html').read_text()
    replacements={'__DATA__':embedded(data),'__SVGS__':embedded(svgs),'__FUNCTIONS__':embedded(data['functions']),'__ROUTES__':embedded(data['routes']),'__STYLE__':(ASSETS/'viewer.css').read_text(),'__READER_JS__':(ASSETS/'reader.js').read_text()}
    template=re.sub(r'__(?:DATA|SVGS|FUNCTIONS|ROUTES|STYLE|READER_JS)__',lambda match:replacements[match.group()],template)
    (output/'index.html').write_text(template)
    (output/'atlas-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    (output/'atlas-flows.excalidraw').write_text(json.dumps({'type':'excalidraw','version':2,'source':'repo-flow-atlas','elements':combined,'appState':{'gridSize':20,'viewBackgroundColor':'#fff'},'files':{}},ensure_ascii=False))
    report={'generator':'repo-flow-atlas','version':'1.0.0','pages':len(data['pages']),'nodes':sum(len(p['nodes']) for p in data['pages']),'functions':len(data['functions']),'source_files':len(data['source_hashes']),'runtime_executed':False,'sharing':'Generated data may contain repository source and internal information; local output is not a sanitized public export.'}
    (output/'atlas-artifact.json').write_text(json.dumps(report,indent=2))
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('manifest');parser.add_argument('--output',required=True);parser.add_argument('--overwrite',action='store_true');args=parser.parse_args()
    print(json.dumps(build(args.manifest,args.output,args.overwrite),indent=2))
if __name__=='__main__':main()
