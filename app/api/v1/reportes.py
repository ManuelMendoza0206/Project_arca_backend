from fastapi import APIRouter, Depends, Query, Response, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import (
    require_inventory_read_permission,
    require_task_management_permission,
    require_animal_management_permission
)

from app.core.report_service import ReportService

router = APIRouter()

@router.get("/diario", response_class=Response)
def download_diario_operativo(
    fecha: date = Query(default_factory=date.today, description="Fecha del reporte"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_management_permission)
):
    try:
        pdf_bytes = ReportService.generate_diario_operativo(db, fecha, current_user)
        
        filename = f"Diario_Operativo_{fecha.strftime('%Y%m%d')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        print(f"Error generando reporte diario: {e}")
        raise HTTPException(status_code=500, detail="Error al generar el PDF")


@router.get("/fichas-clinicas/{historial_id}", response_class=Response)
def download_ficha_clinica(
    historial_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_animal_management_permission)
):
    try:
        pdf_bytes = ReportService.generate_ficha_clinica(db, historial_id, current_user)
        
        filename = f"Historia_Clinica_{historial_id}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Historial medico no encontrado")
    except Exception as e:
        print(f"Error generando ficha clinica: {e}")
        raise HTTPException(status_code=500, detail="Error al generar el PDF")


@router.get("/kardex", response_class=Response)
def download_kardex_inventario(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inventory_read_permission)
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="La fecha de inicio no puede ser mayor a la fecha fin")

    try:
        pdf_bytes = ReportService.generate_kardex(db, start_date, end_date, current_user)
        
        filename = f"Kardex_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        print(f"Error generando kardex: {e}")
        raise HTTPException(status_code=500, detail="Error al generar el PDF")