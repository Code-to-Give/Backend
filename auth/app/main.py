from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health():
    return {"message": "Authentication service is up and running!"}
