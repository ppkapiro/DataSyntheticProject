import argparse
import sys
from pathlib import Path
from typing import List, Optional
from core.import_consolidator import ImportConsolidator

def parse_arguments() -> argparse.Namespace:
    """Parsea los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Sistema de Consolidación de Datos para Notefy"
    )
    
    # Modos de operación
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Comando: consolidar
    consolidar_parser = subparsers.add_parser('consolidar', help='Consolidar datos de un paciente')
    consolidar_parser.add_argument('--paciente', '-p', type=str, required=True,
                                  help='Nombre del paciente a procesar')
    consolidar_parser.add_argument('--clinica', '-c', type=str, 
                                  help='Código de clínica (opcional)')
    
    # Comando: importar
    importar_parser = subparsers.add_parser('importar', help='Importar documento específico')