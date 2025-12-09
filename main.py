# main.py
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from services.azure_storage import AzureStorage
from services.cosmos_db import CosmosDB
import uuid

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

storage = AzureStorage()
db = CosmosDB()

# ----- ROUTES -----
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    # error message support
    error = request.query_params.get("error", "")
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = db.get_user(username, password)
    if user:
        response = RedirectResponse(url="/feed", status_code=302)
        # set cookie to user's id
        response.set_cookie(key="user_id", value=user["id"], httponly=True)
        return response
    # redirect to login with error
    return RedirectResponse(url="/?error=Invalid+credentials", status_code=302)

@app.post("/signup")
def signup(request: Request, username: str = Form(...), password: str = Form(...)):
    created = db.create_user(username, password)
    if created:
        response = RedirectResponse(url="/feed", status_code=302)
        response.set_cookie(key="user_id", value=created["id"], httponly=True)
        return response
    return RedirectResponse(url="/?error=Username+already+exists", status_code=302)

@app.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/", status_code=302)
    return response

@app.get("/feed", response_class=HTMLResponse)
def feed(request: Request):
    videos = db.get_videos()
    # attach comments and commenter username for each video
    for v in videos:
        v['comments'] = db.get_comments_for_video(v['id'])
    # get current user's username (if logged in) for UI display
    user = None
    user_id = request.cookies.get("user_id")
    if user_id:
        user = db.get_user_by_id(user_id)
    return templates.TemplateResponse("feed.html", {"request": request, "videos": videos, "current_user": user})

@app.post("/upload")
async def upload_video(request: Request, title: str = Form(...), file: UploadFile = File(...)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/", status_code=302)

    # Get full user including username
    user = db.get_user_by_id(user_id)
    username = user.get("username") if user else "Unknown"

    # Validate format
    if not file.filename.lower().endswith((".mp4", ".mov", ".avi", ".webm")):
        return templates.TemplateResponse(
            "feed.html",
            {"request": request, "videos": db.get_videos(), "error": "Invalid video format"}
        )

    # read content
    content = await file.read()

    # unique filename
    unique_name = f"{uuid.uuid4().hex}_{file.filename}"

    # upload to azure
    url = storage.upload_file(content, unique_name)

    # save both user_id AND username
    db.create_video(title, url, user_id, username)

    return RedirectResponse(url="/feed", status_code=302)

@app.post("/like/{video_id}")
def like_video(video_id: str, request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return JSONResponse({"error": "Not logged in"}, status_code=401)
    try:
        video = db.update_video_likes(video_id)
        return {"likes": video.get("likes", 0)}
    except Exception as e:
        return JSONResponse({"error": "Video not found"}, status_code=404)

@app.post("/comment/{video_id}")
def comment_video(video_id: str, content: str = Form(...), request: Request = None):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return JSONResponse({"error": "Not logged in"}, status_code=401)
    content = content.strip()
    if not content:
        return JSONResponse({"error": "Empty comment"}, status_code=400)
    # fetch username
    user = db.get_user_by_id(user_id)
    username = user.get("username") if user else "Unknown"
    comment = db.create_comment(video_id, user_id, username, content)
    return comment
