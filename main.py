from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse, Response
from typing import Optional, List, Dict
import uvicorn
import yaml
import xml.etree.ElementTree as ET
import html

app = FastAPI()

quotations = [
    {"id": 1, "text": "The only thing we have to fear is fear itself.", "author": "Franklin D. Roosevelt"},
    {"id": 2, "text": "I think, therefore I am.", "author": "René Descartes"},
    {"id": 3, "text": "That's one small step for man, one giant leap for mankind.", "author": "Neil Armstrong"},
    {"id": 4, "text": "To be, or not to be, that is the question.", "author": "William Shakespeare"},
    {"id": 5, "text": "I have a dream.", "author": "Martin Luther King Jr."},
    {"id": 6, "text": "The unexamined life is not worth living.", "author": "Socrates"},
    {"id": 7, "text": "If you want to go fast, go alone. If you want to go far, go together.", "author": "African Proverb"},
    {"id": 8, "text": "In the beginning, God created the heavens and the earth.", "author": "Genesis"},
    {"id": 9, "text": "Float like a butterfly, sting like a bee.", "author": "Muhammad Ali"},
    {"id": 10, "text": "That's one small step for [a] man, one giant leap for mankind.", "author": "Neil Armstrong (reiterated)"},
]

def escape_csv(value):
    if value is None:
        return ''
    value = str(value).replace('"', '""')
    return f'"{value}"' if any(c in value for c in '",\n') else value

def to_csv(data):
    data = data if isinstance(data, list) else [data]
    if not data:
        return ''
    headers = data[0].keys()
    rows = [','.join(headers)]
    for item in data:
        rows.append(','.join(escape_csv(item.get(h, '')) for h in headers))
    return '\n'.join(rows)

def to_html(data):
    def row(d):
        return '<tr>' + ''.join(f'<td>{html.escape(str(v))}</td>' for v in d.values()) + '</tr>'
    if isinstance(data, list):
        header = '<tr>' + ''.join(f'<th>{html.escape(h)}</th>' for h in data[0].keys()) + '</tr>'
        return f'<table>{header}{"".join(row(d) for d in data)}</table>'
    return '<table>' + ''.join(f'<tr><th>{html.escape(k)}</th><td>{html.escape(str(v))}</td></tr>' for k, v in data.items()) + '</table>'

def to_xml(data):
    def dict_to_xml(tag, d):
        elem = ET.Element(tag)
        for k, v in d.items():
            child = ET.SubElement(elem, k)
            child.text = str(v)
        return elem
    if isinstance(data, list):
        root = ET.Element('items')
        for item in data:
            root.append(dict_to_xml('item', item))
    else:
        root = dict_to_xml('item', data)
    return ET.tostring(root, encoding='unicode')

def to_yaml(data):
    return yaml.dump(data)

def format_response(data, accept: str):
    if 'text/csv' in accept:
        return PlainTextResponse(content=to_csv(data), media_type='text/csv')
    elif 'application/xml' in accept:
        return Response(content=to_xml(data), media_type='application/xml')
    elif 'text/html' in accept:
        return HTMLResponse(content=to_html(data))
    elif 'application/x-yaml' in accept:
        return PlainTextResponse(content=to_yaml(data), media_type='application/x-yaml')
    elif 'application/json' in accept or '*/*' in accept:
        return JSONResponse(content=data)
    else:
        raise HTTPException(status_code=406, detail='Not Acceptable')

@app.get("/quotations")
def get_quotations(request: Request, quotationOnly: Optional[bool] = False, x_client_type: Optional[str] = Header('laptop')):
    client_type = x_client_type.lower()
    if client_type not in ['mobile', 'laptop']:
        raise HTTPException(status_code=400, detail="Invalid X-Client-Type header")

    base_data = [{"text": q["text"]} for q in quotations] if quotationOnly else quotations
    data = base_data[:3] if client_type == 'mobile' else base_data
    return format_response(data, request.headers.get('accept', 'application/json'))

@app.post("/quotations", status_code=201)
def add_quotation(request: Request, payload: Dict):
    text = payload.get("text")
    author = payload.get("author")
    if not text or not author:
        raise HTTPException(status_code=400, detail="Both text and author are required")
    new_id = max(q['id'] for q in quotations) + 1 if quotations else 1
    new_quote = {"id": new_id, "text": text, "author": author}
    quotations.append(new_quote)
    return format_response(new_quote, request.headers.get('accept', 'application/json'))

@app.get("/quotations/{quote_id}")
def get_quotation(quote_id: int, request: Request, quotationOnly: Optional[bool] = False):
    quote = next((q for q in quotations if q['id'] == quote_id), None)
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    data = {"text": quote["text"]} if quotationOnly else quote
    return format_response(data, request.headers.get('accept', 'application/json'))

@app.delete("/quotations/{quote_id}")
def delete_quotation(quote_id: int, request: Request):
    index = next((i for i, q in enumerate(quotations) if q['id'] == quote_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Quotation not found")
    deleted = quotations.pop(index)
    return format_response(deleted, request.headers.get('accept', 'application/json'))

@app.put("/quotations/{quote_id}")
def update_quotation(quote_id: int, request: Request, payload: Dict):
    index = next((i for i, q in enumerate(quotations) if q['id'] == quote_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Quotation not found")
    text = payload.get("text")
    author = payload.get("author")
    if not text or not author:
        raise HTTPException(status_code=400, detail="Both text and author are required")
    quotations[index].update({"text": text, "author": author})
    return format_response(quotations[index], request.headers.get('accept', 'application/json'))

# Uncomment the following lines to run locally
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)

