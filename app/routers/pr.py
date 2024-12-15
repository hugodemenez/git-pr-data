import asyncio
import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import APIRouter, Header, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import logging

import jwt
from utils import pr_analyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/pull-request",
    tags=["pull-request"],
    responses={404: {"description": "Not found"}},
)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action='' onsubmit='createConnection(event)'>
            <input type="text" id="pullRequestUrl" placeholder="Your PR url"/>
            <button>Connect</button>
        </form>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws;
            function createConnection(event) {
                var input = document.getElementById("pullRequestUrl")
                ws = new WebSocket(`ws://localhost:8000/pull-request/analysis?git_pr_url=${input.value}`);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
            var messages = document.getElementById('messages')
            var message = document.createElement('li')
            var content = document.createTextNode('Connected')
            message.appendChild(content)
            messages.appendChild(message)
            event.preventDefault()
            }

            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.get("/test")
async def get():
    logger.info("GET request received")
    return HTMLResponse(html)


@router.get("/")
async def read_root():
    return {"message": "Endpoint to get data from a pull request"}


@router.websocket("/analysis")
async def ws_pr_analysis(websocket: WebSocket, supabase_token: Optional[str] = Header(None)):
    """
    Websocket endpoint for testing purposes.
    """

    load_dotenv()
    JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET",'')

    if supabase_token != "supabase=token":
        # Policy violaion
        await websocket.close(code=1008)
    try:
        logger.error(f"Token : {supabase_token}" f"JWT_SECRET : {JWT_SECRET}")
        payload = jwt.decode(
            supabase_token, JWT_SECRET, algorithms=["HS256"], audience="authenticated"
        )
        logger.debug(f"Decoded payload : {payload}")
        user_id = payload.get("sub")
        # Check user_id correspond to the user who created the offer for selected repo
    except Exception as error:
        await websocket.send_error(message= f"An error has occured while decoding the token : {error}")
        websocket.close(code=1008)

    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        git_pr_url = data.get("git_pr_url")
        logger.info(f"Websocket connection established for PR: {git_pr_url}")

        try:
            await websocket.send_json({"status": "pending", "added_lines": [], "removed_lines": []})
            await asyncio.sleep(0)
            try:
                added_lines, removed_lines = pr_analyzer.get_data(git_pr_url)
            except Exception as e:
                await websocket.send_json({"status": "error", "error": str(e)})
                await asyncio.sleep(0)
                await websocket.close()
            #TODO: SAVE DATA IN DATABASE
            # Instead of added_lines and removed_lines, we should check if error is handeled properly
            await websocket.send_json({"status": "success", "added_lines": added_lines, "removed_lines": removed_lines})
            await asyncio.sleep(0)
            await websocket.close()
        except WebSocketDisconnect:
            # If the client disconnects, close the websocket connection
            # We should continue the process in the background ?
            print("Client disconnected")
