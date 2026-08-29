from fastapi import FastAPI

app = FastAPI()

posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2026",
    },
    {
        "id": 2,
        "author": "Tony Stark",
        "title": "Python is great for my servers!",
        "content": "As you all might know, my personal servers at Stark tower are AI heavy. And hence, Python is particularly great language for running on my servers!",
        "date_posted": "April 21, 2026",
    },
]

@app.get("/")
def home():
    return {"message": "Hello world! This is the entry point of out API!"}

@app.get("/api/posts")
def get_posts():
    return posts