from sqlalchemy.orm import Session, joinedload
from typing import Dict, List, Optional

from app.models.animal import Especie, Habitat, Animal, AnimalFavorito
from app.schemas.animal import EspecieCreate, EspecieUpdate, HabitatCreate, HabitatUpdate, AnimalCreate, AnimalUpdate, AnimalFavoritoCreate

from app.models.animal import MediaAnimal
from app.schemas.animal import MediaCreate
# --- Especies ---

def create_especie(db: Session, especie_in: EspecieCreate) -> Especie:
    db_especie = Especie(**especie_in.model_dump())
    db.add(db_especie)
    db.commit()
    db.refresh(db_especie)
    return db_especie

def get_especie(db: Session, especie_id: int) -> Optional[Especie]:
    return db.query(Especie).filter(Especie.id_especie == especie_id, Especie.is_active == True).first()

def get_especie_by_nombre_cientifico(db: Session, nombre_cientifico: str) -> Optional[Especie]:
    return db.query(Especie).filter(Especie.nombre_cientifico == nombre_cientifico).first()

def list_especies(db: Session, skip: int = 0, limit: int = 100) -> List[Especie]:
    return db.query(Especie).filter(Especie.is_active == True).offset(skip).limit(limit).all()

def update_especie(db: Session, especie: Especie, especie_in: EspecieUpdate) -> Especie:
    update_data = especie_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(especie, field, value)
    db.commit()
    db.refresh(especie)
    return especie

def delete_especie(db: Session, especie_id: int) -> Optional[Especie]:
    db_especie = get_especie(db, especie_id)
    if db_especie:
        db_especie.is_active = False
        db.commit()
        db.refresh(db_especie)
    return db_especie

# --- Habitat ---

def create_habitat(db: Session, habitat_in: HabitatCreate) -> Habitat:
    db_habitat = Habitat(**habitat_in.model_dump())
    db.add(db_habitat)
    db.commit()
    db.refresh(db_habitat)
    return db_habitat

def get_habitat(db: Session, habitat_id: int) -> Optional[Habitat]:
    return db.query(Habitat).filter(Habitat.id_habitat == habitat_id, Habitat.is_active == True).first()

def get_habitat_by_nombre(db: Session, nombre: str) -> Optional[Habitat]:
    return db.query(Habitat).filter(Habitat.nombre_habitat == nombre).first()
    
def list_habitats(db: Session, skip: int = 0, limit: int = 100) -> List[Habitat]:
    return db.query(Habitat).filter(Habitat.is_active == True).offset(skip).limit(limit).all()

def update_habitat(db: Session, habitat: Habitat, habitat_in: HabitatUpdate) -> Habitat:
    update_data = habitat_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habitat, field, value)
    db.commit()
    db.refresh(habitat)
    return habitat

def delete_habitat(db: Session, habitat_id: int) -> Optional[Habitat]:
    db_habitat = get_habitat(db, habitat_id)
    if db_habitat:
        db_habitat.is_active = False
        db.commit()
        db.refresh(db_habitat)
    return db_habitat

#Animals
def create_animal(db: Session, animal_in: AnimalCreate) -> Animal:
    especie = db.query(Especie).filter(Especie.id_especie == animal_in.especie_id, Especie.is_active == True).first()
    if not especie:
        raise ValueError("La especie especificada no existe o no esta activa")
        
    habitat = db.query(Habitat).filter(Habitat.id_habitat == animal_in.habitat_id, Habitat.is_active == True).first()
    if not habitat:
        raise ValueError("El habitat especificado no existe o no esta activo")

    db_animal = Animal(**animal_in.model_dump())
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    return db_animal

def get_animal(db: Session, animal_id: int) -> Optional[Animal]:
    return (
        db.query(Animal)
        .options(joinedload(Animal.especie), joinedload(Animal.habitat))
        .filter(Animal.id_animal == animal_id)
        .first()
    )

def list_animals(db: Session, es_publico: Optional[bool] = None, skip: int = 0, limit: int = 100) -> List[Animal]:

    query = db.query(Animal).options(joinedload(Animal.especie), joinedload(Animal.habitat))
    if es_publico is not None:
        query = query.filter(Animal.es_publico == es_publico)
    
    return query.offset(skip).limit(limit).all()

def update_animal(db: Session, animal: Animal, animal_in: AnimalUpdate) -> Animal:
    update_data = animal_in.model_dump(exclude_unset=True)

    if "especie_id" in update_data:
        especie = db.query(Especie).filter(Especie.id_especie == update_data["especie_id"], Especie.is_active == True).first()
        if not especie:
            raise ValueError("La nueva especie especificada no existe o no está activa")
    
    if "habitat_id" in update_data:
        habitat = db.query(Habitat).filter(Habitat.id_habitat == update_data["habitat_id"], Habitat.is_active == True).first()
        if not habitat:
            raise ValueError("El nuevo habitat especificado no existe o no esta activo")

    for field, value in update_data.items():
        setattr(animal, field, value)
        
    db.commit()
    db.refresh(animal)
    return animal

def delete_animal(db: Session, animal_id: int) -> Optional[Animal]:
    db_animal = get_animal(db, animal_id)
    if db_animal:
        db.delete(db_animal)
        db.commit()
    return db_animal

# --- Media de Animales ---

def add_media_to_animal(db: Session, animal_id: int, media_data: Dict) -> MediaAnimal:

    db_media = MediaAnimal(
        animal_id=animal_id,
        url=media_data.get("secure_url"),
        public_id=media_data.get("public_id"), 
        tipo_medio=media_data.get("resource_type"), 
        titulo=media_data.get("titulo"),
        descripcion=media_data.get("descripcion")
    )
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media
    
def get_media(db: Session, media_id: int) -> Optional[MediaAnimal]:
    return db.query(MediaAnimal).filter(MediaAnimal.id_media == media_id).first()
    
def delete_media(db: Session, media_id: int) -> Optional[MediaAnimal]:
    db_media = get_media(db, media_id)
    if db_media:
        db.delete(db_media)
        db.commit()
    return db_media

def get_media_by_animal_id(db: Session, animal_id: int) -> List[MediaAnimal]:
    return db.query(MediaAnimal).filter(MediaAnimal.animal_id == animal_id).all()

def get_all_media(db: Session, skip: int = 0, limit: int = 100) -> List[MediaAnimal]:
    return db.query(MediaAnimal).offset(skip).limit(limit).all()


# --- Animales Favoritos ---

def get_favorite(db: Session, user_id: int, animal_id: int) -> Optional[AnimalFavorito]:
    return db.query(AnimalFavorito).filter(
        AnimalFavorito.usuario_id == user_id,
        AnimalFavorito.animal_id == animal_id
    ).first()

def add_animal_to_favorites(db: Session, user_id: int, favorite_in: AnimalFavoritoCreate) -> AnimalFavorito:

    animal = get_animal(db, favorite_in.animal_id)
    if not animal:
        raise ValueError("El animal especificado no existe")
        
    if get_favorite(db, user_id, favorite_in.animal_id):
        raise ValueError("Este animal ya esta en tu lista de favoritos")
    db_favorite = AnimalFavorito(
        usuario_id=user_id,
        animal_id=favorite_in.animal_id
    )
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

def remove_animal_from_favorites(db: Session, user_id: int, animal_id: int) -> bool:
    db_favorite = get_favorite(db, user_id, animal_id)
    if db_favorite:
        db.delete(db_favorite)
        db.commit()
        return True
    return False

def list_user_favorites(db: Session, user_id: int) -> List[AnimalFavorito]:
    return (
        db.query(AnimalFavorito)
        .options(joinedload(AnimalFavorito.animal).joinedload(Animal.especie)) 
        .filter(AnimalFavorito.usuario_id == user_id)
        .all()
    )