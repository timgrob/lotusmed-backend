import uvicorn
from fastapi import FastAPI

app = FastAPI(
    title="Lotusmed Backend",
    description="Backend for the Lotusmed application",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message": "Application is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
