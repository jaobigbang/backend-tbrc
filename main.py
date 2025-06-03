import uvicorn
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from routers.api_router import router as api_router
# from routers import admin_router 
from auth import auth_router
app = FastAPI()


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# กำหนด origin ที่อนุญาต
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # หรือ ["*"] เพื่อเปิดกว้าง (ไม่แนะนำใน production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include main API router
app.include_router(api_router)
# app.include_router(admin_router.router)
app.include_router(auth_router.router)

if __name__ == "__main__":

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)