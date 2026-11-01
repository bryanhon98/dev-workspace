"""Read Java statements for an explanatory viewer; never execute project code."""
import re
from pathlib import Path

def mask_java(text):
    pattern=r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
    return re.sub(pattern,lambda m:''.join('\n' if c=='\n' else ' ' for c in m.group()),text)

def display_path(path):
    return str(path).replace('\\','/')

def compact_java(text):
    # Whitespace within a Java string literal remains exactly as written.
    parts=re.split(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')',text)
    return ''.join(p if i%2 else re.sub(r'\s+',' ',p) for i,p in enumerate(parts)).strip()

def classify(code):
    if re.match(r'(?:\w*Log(?:ger|Util)?|log|logger|LOGGER|DEFAULT|SERVICE_LOGGER)\.(?:info|debug|trace|warn|error)\s*\(',code):return 'context'
    if re.match(r'(?:if|else|for|while|switch|case|default|catch|throw|assert)\b',code) or re.search(r'\b(?:\w*Assert\w*|Assert|Checks)\.',code):return 'decision'
    if re.match(r'return\b',code):return 'action'
    if re.search(r'\.(?:execute|executeProcess|publish\w*|insert\w*|update\w*|store|handle|process\w*|create\w*|append\w*|build\w*|query\w*|load\w*|find\w*|transmit|finish|apply\w*|convert\w*|fill\w*)\s*\(',code):return 'action'
    return 'setup'

def explain(code,kind):
    if kind=='context':return 'Record diagnostic context without selecting a processing route.'
    if kind=='decision':return 'Check the condition or validation arguments shown here before continuing.'
    if code.startswith('return '):return 'Return this value to the caller.'
    if kind=='action':return 'Run the shown processing operation with these arguments.'
    return 'Prepare values or processing context for the following steps.'

def extract_statements(text,start_line=1):
    mask=mask_java(text);rows=[];start=None;paren=bracket=expr_brace=depth=0;i=0;frames=[0]
    def emit(end):
        nonlocal start
        if start is None:return
        raw=text[start:end].strip();code=compact_java(raw)
        if code and code not in [';',')','};',');']:
            kind=classify(code)
            rows.append({'line':start_line+text[:start].count('\n'),'end_line':start_line+text[:end].rstrip().count('\n'),'code':code,'kind':kind,'meaning':explain(code,kind),'depth':depth})
        start=None
    while i<len(mask):
        ch=mask[i]
        if start is None:
            if ch.isspace() or ch in '};':
                if ch=='}':
                    depth=max(0,depth-1)
                    if len(frames)>1:frames.pop()
                i+=1;continue
            start=i
        if ch=='(':paren+=1
        elif ch==')':paren=max(0,paren-1)
        elif ch=='[':bracket+=1
        elif ch==']':bracket=max(0,bracket-1)
        elif ch=='{' and bracket==0 and (paren==frames[-1] or re.search(r'(?:\bnew\s+[\w.<>]+\s*\([^{}]*\)\s*|->\s*)$',mask[start:i])):
            prefix=mask[start:i]
            callback=bool(re.search(r'(?:\bnew\s+[\w.<>]+\s*\([^{}]*\)\s*|->\s*)$',prefix))
            control=bool(re.match(r'\s*(if|else|for|while|switch|catch|try|synchronized)\b',prefix))
            expression=not callback and (expr_brace>0 or (not control and (bool(re.search(r'\bnew\b',prefix)) or bool(re.search(r'(?<![=!<>])=(?!=)',prefix)))))
            if expression:expr_brace+=1
            else:emit(i+1);depth+=1;frames.append(paren)
        elif ch=='}' and paren==frames[-1] and bracket==0:
            if expr_brace:expr_brace-=1
            else:
                emit(i);depth=max(0,depth-1);start=None
                if len(frames)>1:frames.pop()
        elif ch==';' and paren==frames[-1] and bracket==0 and expr_brace==0:emit(i+1)
        elif ch==':' and paren==frames[-1] and bracket==0 and re.match(r'\s*(?:case\b|default\b)',mask[start:i]):emit(i+1)
        i+=1
    emit(len(text))
    return rows

