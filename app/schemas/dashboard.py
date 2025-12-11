from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any

class DashboardKPIsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    total_animales: int
    total_usuarios: int
    alertas_stock: int
    tareas_pendientes: int

class ChartDataPoint(BaseModel):
    label: str
    value: int
    color: Optional[str] = None 

class TasksSummaryOut(BaseModel):
    total_hoy: int
    resumen: List[BaseModel]
    resumen: List[dict]