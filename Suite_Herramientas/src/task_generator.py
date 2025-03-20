from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import json
from pathlib import Path
import logging

@dataclass
class Task:
    """Estructura de datos para representar una tarea"""
    description: str
    priority: int = 0
    created_at: datetime = datetime.now()
    due_date: Optional[datetime] = None
    tags: List[str] = None
    assignee: Optional[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class TaskGenerator:
    """Generador de tareas basado en análisis de texto"""
    
    def __init__(self, config_path: str = "../config/task_rules.json"):
        self.logger = logging.getLogger(__name__)
        self.rules = self._load_rules(config_path)

    def _load_rules(self, config_path: str) -> Dict:
        """Carga reglas de generación de tareas desde archivo de configuración"""
        try:
            with open(Path(__file__).parent.joinpath(config_path).resolve()) as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error cargando reglas: {e}")
            return {
                "keywords": {
                    "error": {"priority": 1, "tags": ["bug"]},
                    "análisis": {"priority": 2, "tags": ["analysis"]},
                    "documentación": {"priority": 3, "tags": ["docs"]}
                }
            }

    def generate_tasks(self, document_text: str) -> List[Task]:
        """
        Genera tareas basadas en el análisis del texto sin asignar fecha de vencimiento.
        
        Args:
            document_text: Texto del documento a analizar
            
        Returns:
            Lista de tareas ordenadas por prioridad
        """
        tasks = []
        text_lower = document_text.lower()

        # Procesa reglas basadas en palabras clave
        for keyword, rule in self.rules["keywords"].items():
            if keyword in text_lower:
                task = Task(
                    description=self._generate_description(keyword),
                    priority=rule.get("priority", 0),
                    tags=rule.get("tags", [])
                )
                tasks.append(task)

        # Agrega tarea por defecto si no se generaron tareas
        if not tasks:
            tasks.append(Task(
                description="Revisar el documento y definir tareas específicas",
                priority=0,
                tags=["review"]
            ))

        return sorted(tasks, key=lambda x: x.priority, reverse=True)

    def _generate_description(self, keyword: str) -> str:
        """Genera una descripción de tarea basada en la palabra clave"""
        descriptions = {
            "error": "Revisar y corregir errores identificados en el código",
            "análisis": "Validar resultados del análisis de documentos",
            "documentación": "Actualizar la documentación del proyecto"
        }
        return descriptions.get(keyword, f"Investigar aspectos relacionados con '{keyword}'")

def main():
    # Ejemplo de uso
    generator = TaskGenerator()
    sample_text = """
    El proyecto presenta un error en la fase de análisis.
    Se requiere actualizar la documentación y revisar el código.
    """
    
    tasks = generator.generate_tasks(sample_text)
    
    print("\nTareas Generadas:")
    for task in tasks:
        print(f"\n[Prioridad: {task.priority}] {task.description}")
        print(f"Tags: {', '.join(task.tags)}")
        # Verificar si due_date existe antes de intentar formatearlo
        if task.due_date:
            print(f"Fecha límite: {task.due_date.strftime('%Y-%m-%d')}")
        else:
            print("Fecha límite: No establecida")

if __name__ == "__main__":
    main()
