from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health():
    return {"message": "Algorithm service is up and running!"}
