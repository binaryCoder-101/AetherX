from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello world! This is the entry point of out API!"}
