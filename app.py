import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from claude_client import generate_deep_dive, generate_ideas
from database import get_db, init_db
from models import Idea

load_dotenv()

app = FastAPI(title="VibeCode Idea Generator")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/generate")
async def generate(
    request: Request,
    euty_experience: str = Form(...),
    simon_experience: str = Form(...),
):
    try:
        ideas = await generate_ideas(euty_experience, simon_experience)
    except Exception as e:
        return templates.TemplateResponse(
            "home.html",
            {
                "request": request,
                "error": f"Failed to generate ideas: {e}",
                "euty_experience": euty_experience,
                "simon_experience": simon_experience,
            },
        )

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "ideas": ideas,
            "euty_experience": euty_experience,
            "simon_experience": simon_experience,
        },
    )


@app.post("/save")
async def save(
    title: str = Form(...),
    summary: str = Form(...),
    euty_experience: str = Form(...),
    simon_experience: str = Form(...),
    db: Session = Depends(get_db),
):
    idea = Idea(
        title=title,
        summary=summary,
        euty_experience=euty_experience,
        simon_experience=simon_experience,
    )
    db.add(idea)
    db.commit()
    return RedirectResponse(url="/saved?saved=1", status_code=303)


@app.get("/saved")
async def saved(request: Request, saved: int = 0, db: Session = Depends(get_db)):
    ideas = db.query(Idea).order_by(Idea.created_at.desc()).all()
    return templates.TemplateResponse(
        "saved.html",
        {"request": request, "ideas": ideas, "saved": saved},
    )


@app.get("/idea/{idea_id}")
async def idea_detail(
    request: Request, idea_id: int, db: Session = Depends(get_db)
):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return templates.TemplateResponse(
        "detail.html", {"request": request, "idea": idea}
    )


@app.post("/idea/{idea_id}/deep-dive")
async def deep_dive(idea_id: int, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    result = await generate_deep_dive(
        idea.title, idea.summary, idea.euty_experience, idea.simon_experience
    )
    idea.deep_dive = result
    db.commit()
    return RedirectResponse(url=f"/idea/{idea_id}", status_code=303)


@app.post("/idea/{idea_id}/delete")
async def delete_idea(idea_id: int, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    db.delete(idea)
    db.commit()
    return RedirectResponse(url="/saved", status_code=303)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
