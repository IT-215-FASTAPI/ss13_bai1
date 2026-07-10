from datetime import datetime, timezone

from fastapi import FastAPI, Depends, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import MenuItem
from schemas import MenuItemCreate, MenuItemUpdate, MenuItemResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Catering Menu Management API")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_response(status_code: int, message: str, error, data, path: str):
    return {
        "statusCode": status_code,
        "message": message,
        "error": error,
        "data": data,
        "path": path,
        "timestamp": now_iso(),
    }


def success_response(status_code: int, message: str, data, path: str):
    return JSONResponse(
        status_code=status_code,
        content=build_response(status_code, message, None, data, path),
    )


def error_response(status_code: int, message: str, error: str, path: str):
    return JSONResponse(
        status_code=status_code,
        content=build_response(status_code, message, error, None, path),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    messages = "; ".join(str(e.get("msg", "")) for e in exc.errors())
    return error_response(
        status.HTTP_400_BAD_REQUEST,
        messages or "Dữ liệu đầu vào không hợp lệ",
        "Bad Request",
        str(request.url.path),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Đã xảy ra lỗi hệ thống",
        "Internal Server Error",
        str(request.url.path),
    )


@app.post("/menu-items", status_code=status.HTTP_201_CREATED)
def create_menu_item(payload: MenuItemCreate, request: Request, db: Session = Depends(get_db)):
    path = str(request.url.path)
    existing = db.query(MenuItem).filter(MenuItem.dish_code == payload.dish_code).first()
    if existing:
        return error_response(
            status.HTTP_400_BAD_REQUEST,
            "dish_code đã tồn tại trong hệ thống",
            "Bad Request",
            path,
        )

    try:
        new_item = MenuItem(
            dish_code=payload.dish_code,
            dish_name=payload.dish_name,
            calorie_count=payload.calorie_count,
            price=payload.price,
            status=payload.status or "AVAILABLE",
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except IntegrityError:
        db.rollback()
        return error_response(
            status.HTTP_400_BAD_REQUEST,
            "dish_code đã tồn tại trong hệ thống",
            "Bad Request",
            path,
        )
    except SQLAlchemyError:
        db.rollback()
        return error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Đã xảy ra lỗi hệ thống khi thêm món ăn",
            "Internal Server Error",
            path,
        )

    data = MenuItemResponse.model_validate(new_item).model_dump()
    return success_response(status.HTTP_201_CREATED, "Thêm món ăn thành công", data, path)


@app.get("/menu-items")
def get_menu_items(request: Request, db: Session = Depends(get_db)):
    path = str(request.url.path)
    items = db.query(MenuItem).all()
    data = [MenuItemResponse.model_validate(item).model_dump() for item in items]
    return success_response(status.HTTP_200_OK, "Lấy danh sách món ăn thành công", data, path)


@app.get("/menu-items/{item_id}")
def get_menu_item(item_id: int, request: Request, db: Session = Depends(get_db)):
    path = str(request.url.path)
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        return error_response(
            status.HTTP_404_NOT_FOUND,
            "Menu item not found",
            "Not Found",
            path,
        )
    data = MenuItemResponse.model_validate(item).model_dump()
    return success_response(status.HTTP_200_OK, "Lấy thông tin món ăn thành công", data, path)


@app.put("/menu-items/{item_id}")
def update_menu_item(item_id: int, payload: MenuItemUpdate, request: Request, db: Session = Depends(get_db)):
    path = str(request.url.path)
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        return error_response(
            status.HTTP_404_NOT_FOUND,
            "Menu item not found",
            "Not Found",
            path,
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "dish_code" in update_data and update_data["dish_code"] != item.dish_code:
        duplicate = (
            db.query(MenuItem)
            .filter(MenuItem.dish_code == update_data["dish_code"], MenuItem.id != item_id)
            .first()
        )
        if duplicate:
            return error_response(
                status.HTTP_400_BAD_REQUEST,
                "dish_code đã tồn tại trong hệ thống",
                "Bad Request",
                path,
            )

    try:
        for key, value in update_data.items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
    except IntegrityError:
        db.rollback()
        return error_response(
            status.HTTP_400_BAD_REQUEST,
            "dish_code đã tồn tại trong hệ thống",
            "Bad Request",
            path,
        )
    except SQLAlchemyError:
        db.rollback()
        return error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Đã xảy ra lỗi hệ thống khi cập nhật món ăn",
            "Internal Server Error",
            path,
        )

    data = MenuItemResponse.model_validate(item).model_dump()
    return success_response(status.HTTP_200_OK, "Cập nhật món ăn thành công", data, path)


@app.delete("/menu-items/{item_id}")
def delete_menu_item(item_id: int, request: Request, db: Session = Depends(get_db)):
    path = str(request.url.path)
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        return error_response(
            status.HTTP_404_NOT_FOUND,
            "Menu item not found",
            "Not Found",
            path,
        )

    try:
        db.delete(item)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Đã xảy ra lỗi hệ thống khi xóa món ăn",
            "Internal Server Error",
            path,
        )

    return success_response(status.HTTP_200_OK, "Xóa món ăn thành công", None, path)
