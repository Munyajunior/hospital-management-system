# from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
# from typing import Dict
# from schemas.auth import TokenData
# from backend.utils.dependencies import get_current_user

# router = APIRouter()

# # Store active WebSocket connections
# active_connections: Dict[int, WebSocket] = {}

# @router.websocket("/ws/{user_id}")
# async def websocket_endpoint(websocket: WebSocket, user_id: int, token: TokenData = Depends(get_current_user)):
#     """
#     WebSocket endpoint for real-time communication.
#     - Clients (users) connect via WebSocket with their user ID.
#     - Messages can be exchanged between users (doctor-patient communication).
#     """
#     await websocket.accept()
#     active_connections[user_id] = websocket

#     try:
#         while True:
#             message = await websocket.receive_text()
#             print(f"Received message from User {user_id}: {message}")
            
#             # Broadcast the message to all connected users
#             for connection in active_connections.values():
#                 await connection.send_text(f"User {user_id}: {message}")

#     except WebSocketDisconnect:
#         print(f"User {user_id} disconnected.")
#         active_connections.pop(user_id, None)
