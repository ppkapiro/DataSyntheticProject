from typing import Dict, List, Callable, Any, Protocol, runtime_checkable
from enum import Enum, auto
import logging
import inspect
from dataclasses import dataclass, field
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class SystemEvent(Enum):
    """
    Eventos del sistema.
    
    Cada evento representa una acción importante del sistema que puede ser monitoreada.
    Los componentes pueden suscribirse a estos eventos para reaccionar ante ellos.
    """
    # Eventos de clínicas
    CLINIC_CREATED = auto()
    CLINIC_SELECTED = auto()
    CLINIC_UPDATED = auto()
    CLINIC_DELETED = auto()
    
    # Eventos de pacientes
    PATIENT_ADDED = auto()
    PATIENT_UPDATED = auto()
    PATIENT_DELETED = auto()
    
    # Eventos de documentos
    DOCUMENT_PROCESSED = auto()
    DOCUMENT_IMPORTED = auto()
    DOCUMENT_EXPORTED = auto()
    DOCUMENT_CONSOLIDATED = auto()
    
    # Eventos de análisis
    ANALYSIS_COMPLETED = auto()
    DATA_GENERATED = auto()
    
    # Eventos del sistema
    ERROR_OCCURRED = auto()
    WARNING_ISSUED = auto()
    SYSTEM_READY = auto()

@dataclass
class EventData:
    """Estructura estándar para datos de eventos."""
    event_type: SystemEvent
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    source: str = field(default_factory=lambda: inspect.stack()[2].function)

    def time_str(self) -> str:
        """Devuelve el timestamp como string formateado"""
        return datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')

@runtime_checkable
class EventObserver(Protocol):
    """
    Protocolo para observadores de eventos.

    Los observadores deben implementar un método 'on_event' que será llamado
    cuando ocurra un evento al que estén suscritos.
    """
    def on_event(self, event_data: EventData) -> None:
        """
        Método llamado cuando ocurre un evento.
        
        Args:
            event_data: Datos del evento ocurrido
        """
        ...

class EventBus:
    """
    Bus de eventos centralizado.

    Implementa el patrón Observer para desacoplar componentes del sistema.
    Permite que diferentes partes del sistema se comuniquen sin depender
    directamente unas de otras.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.subscribers = {
                event: [] for event in SystemEvent
            }
            cls._instance.event_history = []
            cls._instance.max_history_size = 100
        return cls._instance

    def subscribe(self, event: SystemEvent, callback: Callable[[EventData], None]) -> None:
        """
        Suscribe un callback a un evento específico.
        
        Args:
            event: Evento al que suscribirse
            callback: Función a llamar cuando ocurra el evento
        """
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(callback)
        logger.debug(f"Suscrito al evento {event.name}: {callback.__qualname__}")

    def unsubscribe(self, event: SystemEvent, callback: Callable) -> None:
        """
        Desuscribe un callback de un evento.
        
        Args:
            event: Evento del que desuscribirse
            callback: Función a desuscribir
        """
        if event in self.subscribers and callback in self.subscribers[event]:
            self.subscribers[event].remove(callback)
            logger.debug(f"Desuscrito del evento {event.name}: {callback.__qualname__}")

    def emit(self, event: SystemEvent, data: Dict[str, Any] = None) -> None:
        """
        Emite un evento con datos opcionales.
        
        Args:
            event: Evento a emitir
            data: Datos asociados al evento
        """
        event_data = EventData(event_type=event, data=data or {})
        logger.debug(f"Emitiendo evento {event.name} con datos: {data}")
        
        # Guardar evento en historial
        self.event_history.append(event_data)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)

        # Notificar a los suscriptores
        if event in self.subscribers:
            for callback in self.subscribers[event]:
                try:
                    callback(event_data)
                except Exception as e:
                    logger.error(f"Error en callback {callback.__qualname__}: {str(e)}")

    def get_event_history(self, limit: int = None) -> List[EventData]:
        """
        Obtiene el historial de eventos.
        
        Args:
            limit: Número máximo de eventos a retornar (los más recientes)
        
        Returns:
            Lista de eventos registrados
        """
        if limit is not None:
            return self.event_history[-limit:]
        return self.event_history.copy()

    def clear_history(self) -> None:
        """Limpia el historial de eventos."""
        self.event_history.clear()