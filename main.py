from fastapi import FastAPI
from fastapi.responses import HTMLResponse

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

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/posts", response_class=HTMLResponse, include_in_schema=False)
def home():
    return f"<h1>{posts[0]['title']}</h1>"

@app.get("/api/posts")
def get_posts():
    return posts