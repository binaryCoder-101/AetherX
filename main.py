from typing import Annotated

from fastapi import Depends, FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

import models
from database import Base, engine, get_db
from schemas import PostCreate, PostResponse, UserCreate, UserResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")

# posts: list[dict] = [
#     {
#         "id": 1,
#         "author": "Corey Schafer",
#         "title": "FastAPI is Awesome",
#         "content": "This framework is really easy to use and super fast.",
#         "date_posted": "April 20, 2026",
#     },
#     {
#         "id": 2,
#         "author": "Tony Stark",
#         "title": "Python is great for my servers!",
#         "content": "As you all might know, my personal servers at Stark tower are AI heavy. And hence, Python is particularly great language for running on my servers!",
#         "date_posted": "April 21, 2026",
#     },
# ]

# API ROUTES

# User endpoints

# 1. create new user
@app.post(
        "/api/users",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]): #Dependency Injection
    result = db.execute(
        select(models.User).where(models.User.username == user.username),
    )
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Username already exists",
        )

    result = db.execute(
        select(models.User).where(models.User.email == user.email),
    )
    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Email already exists",
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# 2. get a single user by user id
@app.get(
        "/api/users/{user_id}",
        response_model=UserResponse
)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == user_id),
    )
    user = result.scalars().first()

    if user:
        return user
    
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "User not found"
    )

# 3. get all posts by a user
@app.get(
        "/api/users/{user_id}/posts",
        response_model=list[PostResponse]
)
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    pass
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts

# Post endpoints
# 1. Get all posts
@app.get(
    "/api/posts", 
    response_model=list[PostResponse]
)
def get_posts(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts

# 2. Get a single post by post id
@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.Post).where(models.Post.id == post_id)
    )
    post = result.scalars().first()

    if post:
        return post

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found",
    )

# 3. Create a new post
@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == post.user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

# WEB ROUTES

# 1. Home page - returns all posts
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request, 
        "home.html", 
        {"posts": posts, "title": "Home"},
    )

# 2. Single post page by post id
@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
            title = post.title[:50]
            return templates.TemplateResponse(
                    request, 
                    "post.html", 
                    {"post": post, "title": title},
                )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

# 3. All posts of a user
@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )


# 4. Account page
@app.get("/account", name="account_page", include_in_schema=False)
def account(req: Request):
    pass

# 5. Login page
@app.get("/login", include_in_schema=False)
def login_page(req: Request):
    pass

# 6. Register page
@app.get("/register", include_in_schema=False)
def register_page(req: Request):
    pass

# HTTP Exception Handler
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

# Validation Exception Handler
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

