import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import logging
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
async def ws_pr_analysis(websocket: WebSocket, git_pr_url: str):
    """
    Websocket endpoint for testing purposes.
    """
    logger.info(f"Websocket connection established for PR: {git_pr_url}")
    await websocket.accept()
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
        await websocket.send_json({"status": "success", "added_lines": added_lines, "removed_lines": removed_lines})
        await asyncio.sleep(0)
        await websocket.close()
    except WebSocketDisconnect:
        print("Client disconnected")
