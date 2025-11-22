from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.crud import animal as crud_animal
from app.db.session import get_db
from app.models.user import User
from app.schemas.animal import AnimalFavoritoCreate, AnimalFavoritoOut

router = APIRouter()


@router.post(
    "/favorites/",
    response_model=AnimalFavoritoOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuario - Favoritos"],
)
def add_favorite(
    favorite_in: AnimalFavoritoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return crud_animal.add_animal_to_favorites(
            db, user_id=current_user.id, favorite_in=favorite_in
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/favorites/{animal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Usuario - Favoritos"],
)
def remove_favorite(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    success = crud_animal.remove_animal_from_favorites(
        db, user_id=current_user.id, animal_id=animal_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Este animal no se encuentra en tu lista de favoritos",
        )
    return None


@router.get(
    "/favorites/", response_model=Page[AnimalFavoritoOut], tags=["Usuario - Favoritos"]
)
def list_my_favorites(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return paginate(crud_animal.list_user_favorites(db, user_id=current_user.id))
