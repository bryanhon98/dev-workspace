"""Verify a generated atlas with an already available Playwright/Chromium runtime."""
import argparse,json
from pathlib import Path

def check(output):
    from playwright.sync_api import sync_playwright
    output=Path(output).resolve();data=json.loads((output/'atlas-data.json').read_text());checks=[];errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1680,'height':1200})
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((output/'index.html').as_uri())
        for flow in data['pages']:
            page.locator('button[data-id="'+flow['id']+'"]').click()
            if page.locator('.node').count()!=len(flow['nodes']):raise AssertionError('Node count mismatch')
            for node in flow['nodes']:
                page.locator('.node[data-node="'+node['id']+'"]').click()
                if not page.locator('#panel').is_visible():raise AssertionError('Inspector is missing')
                if not page.locator('#panel .reader-overview').inner_text():raise AssertionError('Explanation is missing')
                page.locator('#panel [data-reader-close]').click()
            checks.append(flow['id']+' navigation and inspectors')
            overflow=page.evaluate('''() => [...document.querySelectorAll('.node')].flatMap(g=>{const r=g.querySelector('rect'),x=+r.getAttribute('x'),y=+r.getAttribute('y'),w=+r.getAttribute('width'),h=+r.getAttribute('height');return [...g.querySelectorAll('text')].filter(t=>{const b=t.getBBox();return b.x<x||b.y<y||b.x+b.width>x+w+1||b.y+b.height>y+h+1}).map(t=>t.textContent)})''')
            if overflow:raise AssertionError('Diagram text overflows: '+str(overflow))
        candidate=next(((flow,node) for flow in data['pages'] for node in flow['nodes'] if node.get('function_id')),None)
        if candidate:
            flow,node=candidate;page.locator('button[data-id="'+flow['id']+'"]').click();page.locator('.node[data-node="'+node['id']+'"]').click()
            if not page.locator('#panel .source-row').count():raise AssertionError('Source statements are missing')
            if page.locator('#panel .source-block').first.evaluate('(e)=>getComputedStyle(e).backgroundColor')!='rgb(16, 27, 43)':raise AssertionError('Code design drift')
            page.screenshot(path=str(output/'reader-preview.png'))
            page.locator('#panel [data-reader-close]').click();page.locator('button[data-view="functions"]').click()
            name=next(f['method'] for f in data['functions'] if f['id']==node['function_id']);page.locator('#fsearch').fill(name)
            entry=page.locator('#flist .function-entry').first;entry.locator('summary').click();entry.locator('.source-row').first.wait_for(state='visible')
            checks.append('Statement reader, dark code and lazy function index')
        if errors:raise AssertionError('Browser errors: '+str(errors))
        browser.close()
    report={'status':'passed','checks':checks,'javascript_errors':errors}
    (output/'browser-check.json').write_text(json.dumps(report,indent=2));return report

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output');args=parser.parse_args();print(json.dumps(check(args.output),indent=2))
if __name__=='__main__':main()
