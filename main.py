from fastapi import FastAPI, Request, status, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

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

# API ROUTES
@app.get("/api/posts")
def get_posts():
    return posts

@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


# WEB ROUTES
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):
    return templates.TemplateResponse(
        request, 
        "home.html", 
        {"posts": posts, "title": "Home"},
    )

@app.get("/posts/{post_id}")
def post_page(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            title = post["title"][:50]
            return templates.TemplateResponse(
                    request, 
                    "post.html", 
                    {"post": post, "title": title},
                )
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.get("/account", name="account_page", include_in_schema=False)
def account(req: Request):
    pass

@app.get("/login", include_in_schema=False)
def login_page(req: Request):
    pass

@app.get("/register", include_in_schema=False)
def register_page(req: Request):
    pass