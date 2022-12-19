from endpoints.auth import router as auth_router
from endpoints.post import router as post_router
from endpoints.user import router as user_router
from fastapi import FastAPI
import uvicorn


app = FastAPI(title="Ryglogram")


app.include_router(post_router, prefix="/posts", tags=["posts"])
app.include_router(user_router, prefix="/users", tags=["user"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="127.0.0.1", reload=True)
