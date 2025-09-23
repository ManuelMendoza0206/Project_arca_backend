from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from fastapi import File, Form, UploadFile
from app.core.uploader import upload_to_cloudinary, delete_from_cloudinary


from app.db.session import get_db
from app.core.dependencies import require_admin_user, get_current_active_user, require_animal_management_permission

from app.crud import animal as crud_animal
from app.schemas.animal import (
    EspecieCreate, EspecieUpdate, EspecieOut,
    HabitatCreate, HabitatUpdate, HabitatOut,
    AnimalCreate, AnimalUpdate, AnimalOut, MediaOut
)
from app.models.user import User 


router = APIRouter()

# ---Especies ---

@router.post("/species/", response_model=EspecieOut, tags=["Especies"], status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_user)])
def create_especie(especie_in: EspecieCreate, db: Session = Depends(get_db)):
    db_especie = crud_animal.get_especie_by_nombre_cientifico(db, nombre_cientifico=especie_in.nombre_cientifico)
    if db_especie:
        raise HTTPException(status_code=400, detail="Ya existe una especie con este nombre cientifico")
    return crud_animal.create_especie(db, especie_in)

@router.get("/species/", response_model=List[EspecieOut], tags=["Especies"])
def list_especies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_animal.list_especies(db, skip=skip, limit=limit)

@router.get("/species/{especie_id}", response_model=EspecieOut, tags=["Especies"])
def get_especie(especie_id: int, db: Session = Depends(get_db)):
    db_especie = crud_animal.get_especie(db, especie_id)
    if not db_especie:
        raise HTTPException(status_code=404, detail="Especie no encontrada")
    return db_especie

@router.put("/species/{especie_id}", response_model=EspecieOut, tags=["Especies"], dependencies=[Depends(require_admin_user)])
def update_especie(especie_id: int, especie_in: EspecieUpdate, db: Session = Depends(get_db)):
    db_especie = crud_animal.get_especie(db, especie_id)
    if not db_especie:
        raise HTTPException(status_code=404, detail="Especie no encontrada")
    return crud_animal.update_especie(db, especie=db_especie, especie_in=especie_in)

@router.delete("/species/{especie_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Especies"], dependencies=[Depends(require_admin_user)])
def delete_especie(especie_id: int, db: Session = Depends(get_db)):
    deleted_especie = crud_animal.delete_especie(db, especie_id)
    if not deleted_especie:
        raise HTTPException(status_code=404, detail="Especie no encontrada")
    return None

# --- Habitats ---

@router.post("/habitats/", response_model=HabitatOut, tags=["Habitats"], status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_user)])
def create_habitat(habitat_in: HabitatCreate, db: Session = Depends(get_db)):
    db_habitat = crud_animal.get_habitat_by_nombre(db, nombre=habitat_in.nombre_habitat)
    if db_habitat:
        raise HTTPException(status_code=400, detail="Ya existe un habitat con este nombre")
    return crud_animal.create_habitat(db, habitat_in)

@router.get("/habitats/", response_model=List[HabitatOut], tags=["Habitats"])
def list_habitats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_animal.list_habitats(db, skip=skip, limit=limit)

@router.get("/habitats/{habitat_id}", response_model=HabitatOut, tags=["Habitats"])
def get_habitat(habitat_id: int, db: Session = Depends(get_db)):
    db_habitat = crud_animal.get_habitat(db, habitat_id)
    if not db_habitat:
        raise HTTPException(status_code=404, detail="Habitat no encontrado")
    return db_habitat

@router.put("/habitats/{habitat_id}", response_model=HabitatOut, tags=["Habitats"], dependencies=[Depends(require_admin_user)])
def update_habitat(habitat_id: int, habitat_in: HabitatUpdate, db: Session = Depends(get_db)):
    db_habitat = crud_animal.get_habitat(db, habitat_id)
    if not db_habitat:
        raise HTTPException(status_code=404, detail="Habitat no encontrado")
    return crud_animal.update_habitat(db, habitat=db_habitat, habitat_in=habitat_in)

@router.delete("/habitats/{habitat_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Habitats"], dependencies=[Depends(require_admin_user)])
def delete_habitat(habitat_id: int, db: Session = Depends(get_db)):
    deleted_habitat = crud_animal.delete_habitat(db, habitat_id)
    if not deleted_habitat:
        raise HTTPException(status_code=404, detail="Habitat no encontrado")
    return None

#animals
@router.post("/animals/", response_model=AnimalOut, tags=["Animales"], status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_animal_management_permission)])
def create_animal(animal_in: AnimalCreate, db: Session = Depends(get_db)):
    try:
        return crud_animal.create_animal(db, animal_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/animals/", response_model=List[AnimalOut], tags=["Animales"])
def list_animals(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: Optional[User] = Depends(get_current_active_user)
):

    user_role = getattr(getattr(current_user, 'role', None), 'nombre_rol', 'visitante').lower()
    allowed_roles = {"administrador", "veterinario", "cuidador"}

    if user_role in allowed_roles:
        return crud_animal.list_animals(db, es_publico=None, skip=skip, limit=limit)
    else:
        return crud_animal.list_animals(db, es_publico=True, skip=skip, limit=limit)

@router.get("/animals/{animal_id}", response_model=AnimalOut, tags=["Animales"])
def get_animal(animal_id: int, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_active_user)):
    db_animal = crud_animal.get_animal(db, animal_id)
    if not db_animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")

    user_role = getattr(getattr(current_user, 'role', None), 'nombre_rol', 'visitante').lower()
    allowed_roles = {"administrador", "veterinario", "cuidador"}
    
    if not db_animal.es_publico and user_role not in allowed_roles:
        raise HTTPException(status_code=403, detail="No tiene permiso para ver este animal")
        
    return db_animal

@router.put("/animals/{animal_id}", response_model=AnimalOut, tags=["Animales"], dependencies=[Depends(require_animal_management_permission)])
def update_animal(animal_id: int, animal_in: AnimalUpdate, db: Session = Depends(get_db)):
    db_animal = crud_animal.get_animal(db, animal_id)
    if not db_animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    try:
        return crud_animal.update_animal(db, animal=db_animal, animal_in=animal_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/animals/{animal_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Animales"], dependencies=[Depends(require_animal_management_permission)])
def delete_animal(animal_id: int, db: Session = Depends(get_db)):
    deleted_animal = crud_animal.delete_animal(db, animal_id)
    if not deleted_animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    return None

# --- Media ---

@router.post("/animals/{animal_id}/media", response_model=MediaOut, tags=["Animales", "Media"], status_code=status.HTTP_201_CREATED)
def upload_animal_media(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_animal_management_permission),
    file: UploadFile = File(...),
    titulo: str = Form(...),
    descripcion: Optional[str] = Form(None)
):

    db_animal = crud_animal.get_animal(db, animal_id)
    if not db_animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")

    # 1 Subir a Cloudinary
    upload_result = upload_to_cloudinary(file, folder="animals")
    
    # 2 Añadir metadatos adicionales para guardar en la BD
    media_data = {
        **upload_result,
        "titulo": titulo,
        "descripcion": descripcion
    }
    
    # 3 Guardar en la base de datos
    return crud_animal.add_media_to_animal(db, animal_id=animal_id, media_data=media_data)

@router.delete("/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Media"])
def delete_media_file(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_animal_management_permission)
):

    db_media = crud_animal.get_media(db, media_id)
    if not db_media:
        raise HTTPException(status_code=404, detail="Archivo multimedia no encontrado")
        
    # 1 Eliminar de Cloudinary
    if db_media.public_id:
        delete_from_cloudinary(db_media.public_id)
        
    # 2 Eliminar de la base de datos
    crud_animal.delete_media(db, media_id)
    
    return None

@router.get("/animals/{animal_id}/media", response_model=List[MediaOut], tags=["Animales", "Media"])
def get_all_media_for_animal(
    animal_id: int,
    db: Session = Depends(get_db)
):
    db_animal = crud_animal.get_animal(db, animal_id)
    if not db_animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
        
    media_list = crud_animal.get_media_by_animal_id(db, animal_id=animal_id)
    return media_list

@router.get("/media/", response_model=List[MediaOut], tags=["Media"])
def get_all_media_files(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    media_list = crud_animal.get_all_media(db, skip=skip, limit=limit)
    return media_list