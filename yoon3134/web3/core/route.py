from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from models.image import Image  # 이미지 모델 임포트

router = APIRouter()

class Item(BaseModel):
    name: str
    description: str

@router.post("/api/v1/items/")
async def create_item(item: Item):
    return {"item_name": item.name, "item_description": item.description}

@router.get("/api/v1/items/{item_id}")
async def read_item(item_id: int):
    if item_id < 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "item_name": "Sample Item"}

# 갤러리 라우트 추가
@router.get("/gallery", response_class=HTMLResponse)
async def read_gallery(request: Request, templates: Jinja2Templates = Depends(lambda: Jinja2Templates(directory="templates"))):
    images = [
        Image(filename="image1.jpg", title="이미지 1"),
        Image(filename="image2.jpg", title="이미지 2"),
        Image(filename="image3.jpg", title="이미지 3"),
    ]
    return templates.TemplateResponse("gallery.html", {"request": request, "images": images})

