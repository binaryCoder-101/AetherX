from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas import PostCreate, PostResponse 

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
@app.get(
        "/api/posts", 
        response_model=list[PostResponse]
)
def get_posts():
    return posts

@app.get(
        "/api/posts/{post_id}", 
        response_model=PostResponse
)
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post(
        "/api/posts",
        response_model=PostResponse,
        status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate):
    new_id = max(p["id"] for p in posts) + 1 if posts else 1
    new_post = {
        "id": new_id,
        "author": post.author,
        "title": post.title,
        "content": post.content,
        "date_posted": "September 02, 2026"
    }
    posts.append(new_post)
    return new_post

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
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.get("/account", name="account_page", include_in_schema=False)
def account(req: Request):
    pass

@app.get("/login", include_in_schema=False)
def login_page(req: Request):
    pass

@app.get("/register", include_in_schema=False)
def register_page(req: Request):
    pass

@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occured. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message}
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                content={"detail": exception.errors()},
            )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )

