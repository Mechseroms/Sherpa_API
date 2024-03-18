from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from AI import generate_text, generate_gif, generate_image
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from os import listdir
from os.path import isfile, join

app = FastAPI()

app.mount("/static", StaticFiles(directory=Path(__file__).parent.parent.absolute() / "Sherpa_API" / "static"), name="static")


templates = Jinja2Templates(directory="templates")

@app.get('/', response_class=HTMLResponse)
async def homepage(request: Request):
    pics = ["a", "b", "c"]
    context = {
        "request": request,
        "pics": pics
    }
    return templates.TemplateResponse("index.html", context)

@app.post("/text_generation")
async def print_prompt(request: Request):
    inp = await request.form()
    print(inp.get("prompt"))
    response = generate_text(inp.get("prompt"))
    return response

@app.post("/gif_generation")
async def gif_generation(request: Request):
    inp = await request.form()
    print(inp.get("prompt"))
    file_path = generate_gif(inp.get("prompt"))
    return FileResponse(file_path)

@app.post("/image_generation")
async def image_generation(request: Request):
    inp = await request.form()
    print(inp.get("prompt"))
    file_path = generate_image(inp.get("prompt"))
    print(file_path)
    return FileResponse(file_path)