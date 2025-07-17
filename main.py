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
def post_list_events(event_data: EventModel):
    initial_size = len(events_store)
    if event_data is not None:
        events_store.append(event_data)
        if len(events_store) > initial_size:
            return {"events" : serialized_stored_events()}
    return Response(content=json.dumps({"message": "Event not created!"}))

@app.put("/events")
def update_events(updated_events: List[EventModel] = Body(...)):
    updated_count = 0

    for updated_event in updated_events:
        for i, stored_event in enumerate(events_store):
            if stored_event.name == updated_event.name:
                events_store[i] = updated_event
                updated_count += 1
                break

    if updated_count > 0:
        return {"events": serialized_stored_events()}
    else:
        return Response(
            content=json.dumps({"message": "No matching events found to update!"}),
            media_type="application/json",
            status_code=404
        )

@app.get("/{full_path:path}")
def catch_all(full_path: str):
    with open("not-found.html","r",encoding="utf-8") as file:
        html_content = file.read()
        return Response(content=html_content, status_code=404, media_type="text/html")


