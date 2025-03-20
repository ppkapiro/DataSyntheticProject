from datetime import datetime
from pathlib import Path

class FileNamingConvention:
    """Clase para manejar la convención de nombres de archivos"""
    
    @staticmethod
    def get_timestamp():
        """Genera el timestamp en formato HHMM_DDMM"""
        now = datetime.now()
        return f"{now.hour:02d}{now.minute:02d}_{now.day:02d}{now.month:02d}"
    
    @staticmethod
    def generate_filename(clinic_initials, module, extension, suffix="DataMasterData", num_records=None, patient_name=None):
        """
        Genera un nombre de archivo según la convención establecida
        
        Args:
            clinic_initials: Iniciales de la clínica (ej: 'ABC')
            module: Nombre del módulo (ej: 'pacientes')
            extension: Extensión del archivo sin el punto (ej: 'csv')
            suffix: Sufijo adicional (por defecto: 'DataMasterData')
            num_records: Número de registros (para múltiples pacientes)
            patient_name: Nombre del paciente (para archivo individual)
            
        Returns:
            str: Nombre del archivo
        """
        timestamp = FileNamingConvention.get_timestamp()
        
        # Determinar el identificador de paciente(s)
        if num_records and num_records > 1:
            patient_identifier = f"{num_records}p"  # p de pacientes
        elif patient_name:
            patient_identifier = patient_name.replace(" ", "_")[:20]  # limitar longitud
        else:
            patient_identifier = "registro"
            
        return f"{clinic_initials}_{patient_identifier}_{module}_{suffix}_{timestamp}.{extension}"
    
    @staticmethod
    def get_export_path(output_dir, filename):
        """Genera la ruta completa de exportación"""
        return Path(output_dir) / filename
