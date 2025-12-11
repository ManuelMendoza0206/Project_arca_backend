from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import require_inventory_read_permission

from app.crud import dashboard as crud_dashboard
from app.schemas import dashboard as schemas_dashboard

router = APIRouter()

@router.get("/kpis", response_model=schemas_dashboard.DashboardKPIsOut)
def get_dashboard_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inventory_read_permission)
):
    return crud_dashboard.get_dashboard_kpis(db)


@router.get("/charts/animals-by-species", response_model=List[schemas_dashboard.ChartDataPoint])
def get_animals_by_species_chart(
    group_by: str = Query("clase", description="Campo para agrupar: 'clase', 'familia', 'orden', 'filo'"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inventory_read_permission)
):
    return crud_dashboard.get_animales_por_grupo(db, agrupar_por=group_by)


@router.get("/charts/tasks-today-status", response_model=schemas_dashboard.TasksSummaryOut)
def get_tasks_today_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inventory_read_permission)
):
    return crud_dashboard.get_tareas_status_hoy(db)