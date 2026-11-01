/* More explanatory source reader; keeps all data local and source text escaped. */
(function(){
  const originalTextView=window.textview;
  const esc=escape;
  const readableName=n=>n.title+(n.method?'.'+n.method+'()':'');
  const breakName=s=>esc(s).replace(/([a-z0-9])([A-Z])/g,'$1<wbr>$2').replace(/\./g,'.<wbr>');
  const pathMarkup=path=>esc(path).split('/').join('/<wbr>');
  const shortPath=path=>String(path).replace(/\\/g,'/');
  function sourceInfo(e){
    if(!e)return '<p class="notice">Source evidence is not available for this component; its boundary remains unverified.</p>';
    return `<h3>Source location</h3><code class="source-path">${pathMarkup(e.display_path||shortPath(e.path))}:${e.line}</code>${e.url?'<p><a href="'+esc(e.url)+'">Open source file</a></p>':''}`;
  }
  function codeMarkup(code){
    const token=/"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b[A-Za-z_$][\w$]*Enum\.[A-Z][A-Z0-9_]*\b/g;
    let out='',last=0;
    for(const match of code.matchAll(token)){
      out+=esc(code.slice(last,match.index));
      out+=match[0].includes('Enum.')?'<span class="code-enum">'+esc(match[0])+'</span>':esc(match[0]);
      last=match.index+match[0].length;
    }
    return out+esc(code.slice(last));
  }
  const kindLabels={context:'Context / log',decision:'Decision / validation',action:'Core processing',setup:'Preparation'};
  function rowMarkup(row){
    const meaningful=row.kind==='decision'||(row.kind==='action'&&!row.meaning.startsWith('Perform the named'));
    return `<div class="source-row ${esc(row.kind)}" data-line="${row.line}" data-end-line="${row.end_line}" title="Source lines ${row.line}–${row.end_line}"><span class="source-line">L${row.line}</span><div style="min-width:0;margin-left:${Math.min(row.depth||0,4)*9}px"><div class="source-kind">${esc(kindLabels[row.kind]||row.kind)}</div><code>${codeMarkup(row.code)}</code>${meaningful?'<div class="row-meaning">'+esc(row.meaning)+'</div>':''}</div></div>`;
  }
  function codeBlock(f,open=false){
    const rows=f.statements||[];
    return `<details class="source-block" ${open?'open':''}><summary>${esc(f.method)} · L${f.line}–${f.end_line} · ${rows.length} statements</summary><div class="code-signature">${codeMarkup(f.signature||f.class+'.'+f.method+'()')}</div><div class="code-rows">${rows.length?rows.map(rowMarkup).join(''):'<div class="empty-method">This method has no executable statements.</div>'}</div></details>`;
  }
  function relationText(edge,incoming){
    const label=edge.label||'';
    if(edge.explanation)return edge.explanation;
    const meanings={
      call:incoming?'This function calls the selected method.':'The selected method calls this function.',
      rpc:incoming?'This component reaches the selected method through a service call.':'This path makes a service call to the component shown here.',
      dispatch:incoming?'This router selects the method for the matching message or action.':'The router chooses this implementation for a matching message or action.',
      binding:incoming?'Configuration connects this component to the selected handler.':'Configuration connects the selected component to this handler.',
      control:incoming?'This is an earlier step, helper or template hook on the selected path.':'Processing can continue through this helper, branch or template hook.',
      data:incoming?'These components are connected by stored records or returned data.':'The connection carries returned data or goes through persisted records; it is not a direct function call.',
      message:incoming?'A message from this component can enter the selected processing path.':'A published or subscribed message connects these processing steps.',
      async:incoming?'A scheduled or asynchronous step can start this work later.':'This work continues later through scheduling or asynchronous processing.',
      unknown:'This boundary still needs source evidence; the exact connection is unverified.'
    };
    const expansion={businessAction:'The route uses the business action selected earlier.',eventCode:'The message event code is the lookup key.',SingleFunded:'The payload is a single-funded V2 message.',BatchFunded:'The payload is a batch-funded V2 message.','true':'This path is taken when the check succeeds.','false':'This path is taken when the check fails.'};
    return (meanings[edge.kind]||'These steps are connected on the selected path.')+(label?' '+(expansion[label]||'Step or condition: '+label+'.'):'');
  }
  function relationshipGroup(node,incoming){
    const edges=current.edges.filter(e=>incoming?e.to===node.id:e.from===node.id);
    if(!edges.length)return '';
    return `<div class="relationship-group"><div class="relationship-group-label">${incoming?'Where it comes from':'What happens next'}</div>${edges.map(edge=>{
      const other=current.nodes.find(n=>n.id===(incoming?edge.from:edge.to));
      return `<div class="relationship-card"><button class="relationship-link" data-reader-target="${esc(other.id)}">${breakName(readableName(other))}</button><p>${esc(relationText(edge,incoming))}</p></div>`;
    }).join('')}</div>`;
  }
  window.selectNode=function(id){
    const node=current.nodes.find(n=>n.id===id);const notes=node.reader||{overview:node.detail};
    document.querySelectorAll('.node').forEach(el=>el.classList.toggle('selected',el.dataset.node===id));
    const matches=functions.filter(f=>node.evidence&&f.path===node.evidence.path&&(!node.method||f.method===node.method));
    const steps=(notes.steps||[]).map(step=>typeof step==='string'?'<li>'+esc(step)+'</li>':`<li>${esc(step.text)}<span class="reader-step-source">L${step.line} · ${esc(step.code)}</span></li>`).join('');
    const actions=notes.actions||[];
    $('panel').innerHTML=`<div class="reader-header"><span class="tag">${esc(current.id)} · ${node.method?'Function':'Component'}</span><button aria-label="Close details" data-reader-close>×</button></div><div class="reader-content"><h2>${breakName(node.title)}${node.method?'<br><span style="color:#466886">'+breakName(node.method)+'()</span>':''}</h2><h3>What it does</h3><p class="reader-overview">${esc(notes.overview)}</p>${notes.inputs?'<h3>What it receives</h3><p>'+esc(notes.inputs)+'</p>':''}${notes.signature?(notes.signatures||[notes.signature]).map(signature=>'<code class="reader-signature">'+esc(signature)+'</code>').join(''):''}${steps?'<h3>Inside this method</h3><ol class="reader-steps">'+steps+'</ol>':''}${notes.outcome?'<h3>Result</h3><div class="reader-outcome"><p>'+esc(notes.outcome)+'</p></div>':''}${sourceInfo(node.evidence)}<h3>How it connects</h3>${relationshipGroup(node,true)}${relationshipGroup(node,false)}${actions.length?'<details><summary>Actions selected here ('+actions.length+')</summary><p class="reader-subtle">Each value below is recorded at a call site. Open the code to see its surrounding conditions.</p><table class="action-routes">'+actions.map(a=>'<tr><td>L'+a.line+'</td><td><code>'+esc(a.action)+'</code></td></tr>').join('')+'</table></details>':''}${matches.length?'<h3>Read the code</h3><p class="source-hint">Each row groups one complete statement, branch or callback header. Wrapped source lines keep their first line number. Arguments and enum values are preserved; source code is shown verbatim.</p><div class="code-legend"><span class="legend-context">Context / logs</span><span class="legend-setup">Preparation</span><span class="legend-decision">Decisions / checks</span><span class="legend-action">Core processing</span></div>'+matches.map((f,i)=>codeBlock(f,i===0)).join(''):''}</div>`;
    $('panel').style.display='block';$('panel').scrollTop=0;
    $('panel').querySelector('[data-reader-close]').onclick=()=>{$('panel').style.display='none'};
    $('panel').querySelectorAll('[data-reader-target]').forEach(button=>button.onclick=()=>selectNode(button.dataset.readerTarget));
  };
  window.textview=function(view){
    if(view!=='functions'){originalTextView(view);return}
    mode=view;nav();$('canvas').style.display='none';$('textview').style.display='block';$('panel').style.display='none';$('viewport').scrollTop=0;
    $('textview').innerHTML='<h2>Function index</h2><p>Search '+functions.length+' methods. Expand a method to read complete statements, their arguments and source line numbers. This is a source reader, not a compiler-resolved execution trace.</p><input id="fsearch" placeholder="Filter class or method" aria-label="Filter functions" style="padding:10px;width:100%"><div id="flist"></div>';
    function render(query){
      const entries=functions.map((f,i)=>({f,i})).filter(({f})=>(f.class+'.'+f.method).toLowerCase().includes(query.toLowerCase()));
      $('flist').innerHTML=entries.map(({f,i})=>`<details class="function-entry" data-function-index="${i}"><summary><b>${esc(f.class)}.${esc(f.method)}()</b> · ${esc(f.repo)} · L${f.line}</summary><div class="function-source"></div></details>`).join('')||'<p class="function-empty">No matching functions.</p>';
      $('flist').querySelectorAll('.function-entry').forEach(entry=>entry.ontoggle=()=>{const content=entry.querySelector('.function-source');if(entry.open&&!content.innerHTML){const f=functions[+entry.dataset.functionIndex];content.innerHTML='<code class="source-path">'+esc(f.display_path||shortPath(f.path))+':'+f.line+'</code>'+codeBlock(f,true)}});
    }
    render('');$('fsearch').oninput=e=>render(e.target.value);
  };
  const requestedNode=new URLSearchParams(location.search).get('node');
  if(requestedNode&&current.nodes.some(node=>node.id===requestedNode))selectNode(requestedNode);
})();
