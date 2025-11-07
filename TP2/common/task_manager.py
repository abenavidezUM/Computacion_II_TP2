"""
Sistema de gestión de tareas asíncronas.
Permite procesamiento en background con consulta de estado.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional
from enum import Enum


class TaskStatus(Enum):
    """Estados posibles de una tarea"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Task:
    """
    Representa una tarea de scraping.
    """
    def __init__(self, task_id: str, url: str, process: bool = False):
        self.task_id = task_id
        self.url = url
        self.process = process
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now().isoformat()
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.result: Optional[Dict] = None
        self.error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """
        Convierte la tarea a diccionario.
        
        Returns:
            Diccionario con información de la tarea
        """
        return {
            'task_id': self.task_id,
            'url': self.url,
            'status': self.status.value,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'has_result': self.result is not None,
            'error': self.error
        }


class TaskManager:
    """
    Gestor de tareas asíncronas.
    Almacena tareas en memoria y permite consultas.
    """
    def __init__(self, max_tasks: int = 1000):
        """
        Inicializa el gestor de tareas.
        
        Args:
            max_tasks: Número máximo de tareas a mantener en memoria
        """
        self.tasks: Dict[str, Task] = {}
        self.max_tasks = max_tasks
        self.queue = asyncio.Queue()
    
    def create_task(self, url: str, process: bool = False) -> str:
        """
        Crea una nueva tarea.
        
        Args:
            url: URL a procesar
            process: Si True, incluye procesamiento adicional
            
        Returns:
            ID único de la tarea
        """
        task_id = str(uuid.uuid4())
        task = Task(task_id, url, process)
        
        # Limitar tareas en memoria (FIFO)
        if len(self.tasks) >= self.max_tasks:
            # Eliminar la tarea más antigua completada o fallida
            oldest_completed = None
            for tid, t in self.tasks.items():
                if t.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                    oldest_completed = tid
                    break
            
            if oldest_completed:
                del self.tasks[oldest_completed]
        
        self.tasks[task_id] = task
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Obtiene una tarea por su ID.
        
        Args:
            task_id: ID de la tarea
            
        Returns:
            Objeto Task o None si no existe
        """
        return self.tasks.get(task_id)
    
    def update_status(self, task_id: str, status: TaskStatus):
        """
        Actualiza el estado de una tarea.
        
        Args:
            task_id: ID de la tarea
            status: Nuevo estado
        """
        task = self.tasks.get(task_id)
        if task:
            task.status = status
            
            if status == TaskStatus.PROCESSING and not task.started_at:
                task.started_at = datetime.now().isoformat()
            
            if status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                task.completed_at = datetime.now().isoformat()
    
    def set_result(self, task_id: str, result: Dict):
        """
        Establece el resultado de una tarea.
        
        Args:
            task_id: ID de la tarea
            result: Resultado del procesamiento
        """
        task = self.tasks.get(task_id)
        if task:
            task.result = result
            self.update_status(task_id, TaskStatus.COMPLETED)
    
    def set_error(self, task_id: str, error: str):
        """
        Establece un error en una tarea.
        
        Args:
            task_id: ID de la tarea
            error: Mensaje de error
        """
        task = self.tasks.get(task_id)
        if task:
            task.error = error
            self.update_status(task_id, TaskStatus.FAILED)
    
    def get_status(self, task_id: str) -> Optional[Dict]:
        """
        Obtiene el estado de una tarea.
        
        Args:
            task_id: ID de la tarea
            
        Returns:
            Diccionario con estado o None
        """
        task = self.get_task(task_id)
        if task:
            return task.to_dict()
        return None
    
    def get_result(self, task_id: str) -> Optional[Dict]:
        """
        Obtiene el resultado de una tarea.
        
        Args:
            task_id: ID de la tarea
            
        Returns:
            Diccionario con resultado o None
        """
        task = self.get_task(task_id)
        if task and task.status == TaskStatus.COMPLETED:
            return task.result
        return None
    
    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas del gestor.
        
        Returns:
            Diccionario con estadísticas
        """
        pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
        processing = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PROCESSING)
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        
        return {
            'total_tasks': len(self.tasks),
            'pending': pending,
            'processing': processing,
            'completed': completed,
            'failed': failed,
            'max_tasks': self.max_tasks
        }

