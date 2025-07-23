import json
from typing import List

from fastapi import FastAPI, Request, Body
from pydantic import BaseModel
from starlette.responses import Response

app = FastAPI()

@app.get("/")
async def root(request: Request):
    x_api_key_value = request.headers.get("x-api-key")
    content_type = request.headers.get("Accept")

    if x_api_key_value is None:
        return Response(content=json.dumps({"message": "API key not given!"}),
                        status_code=403, media_type="application/json")
    elif x_api_key_value != "123456789":
        return Response(content=json.dumps({"message": "API key is invalid!"}),status_code=403, media_type="application/json")

    if content_type not in ("text/html", "text/plain"):
        return Response(content=json.dumps({"message": "Type error"}),
                        status_code=400, media_type="application/json")

    with open("welcome.html", "r", encoding="utf-8") as file:
        html_content = file.read()
        return Response(content=html_content, status_code=200, media_type="text/html")


class EventModel(BaseModel):
    name : str
    description : str
    start_date : str
    end_date : str

events_store : List[EventModel] = []

def serialized_stored_events():
    events_converted = []
    for event in events_store:
        events_converted.append(event.dict())
    return events_converted

@app.get("/events")
def list_events():
    return {"events": serialized_stored_events()}

@app.post("/events")
def post_event(list_event : List[EventModel]):
    for event in list_event:
        exist = False
        for initial_event in events_store:
            if initial_event.name == event.name:
                exist = True
        if exist is False:
            events_store.append(event)
    return Response(content=json.dumps({"events": serialized_stored_events()}),status_code=200,media_type="application/json")

@app.put("/events")
def modify_event(list_event: List[EventModel]):
    for event in list_event:
        found = False
        for i,initial_event in enumerate(events_store):
            if initial_event.name == event.name:
                events_store[i] = event
                found = True
                break
        if found is False:
            events_store.append(event)
    return Response(content=json.dumps({"events": serialized_stored_events()}),status_code=200,media_type="application/json")


@app.get("/{full_path:path}")
def catch_all(full_path: str):
    with open("not-found.html","r",encoding="utf-8") as file:
        html_content = file.read()
        return Response(content=html_content, status_code=404, media_type="text/html")


