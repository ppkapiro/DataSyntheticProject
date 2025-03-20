from pathlib import Path
from datetime import datetime  # Añadida importación
from utils.file_naming import FileNamingConvention
from utils.data_formats import DataFormatHandler

class ExportadorBase:
    """Clase base para todos los exportadores de datos"""
    
    def exportar(self, df, clinic_initials, output_dir, module_name):
        """
        Exporta datos en múltiples formatos
        
        Args:
            df: DataFrame con los datos
            clinic_initials: Iniciales de la clínica
            output_dir: Directorio de salida
            module_name: Nombre del módulo (farc, bio, mtp, etc)
        """
        # Primero exportar como TXT (formato obligatorio)
        self._exportar_txt(df, clinic_initials, output_dir, module_name)
        
        # Luego ofrecer otros formatos
        while True:
            formato = DataFormatHandler.prompt_format_selection()
            if not formato:
                break
                
            nombre_archivo = FileNamingConvention.generate_filename(
                clinic_initials=clinic_initials,
                module=module_name,
                extension=DataFormatHandler.SUPPORTED_FORMATS[formato]['ext'].lstrip('.')
            )
            
            ruta_salida = Path(output_dir) / nombre_archivo
            
            if DataFormatHandler.save_data(df, ruta_salida, formato):
                print(f"\nDatos exportados a: {ruta_salida}")
            else:
                print(f"Error al exportar en formato {formato}")

            if input("\n¿Desea exportar en otro formato? (S/N): ").upper() != 'S':
                break

    def _exportar_txt(self, df, clinic_initials, output_dir, module_name):
        """Exporta siempre una versión en TXT"""
        nombre_archivo = FileNamingConvention.generate_filename(
            clinic_initials=clinic_initials,
            module=module_name,
            extension='txt'
        )
        
        ruta_salida = Path(output_dir) / nombre_archivo
        
        # Crear texto estructurado
        texto = "=== INFORME DE DATOS ===\n\n"
        texto += f"Módulo: {module_name.upper()}\n"
        texto += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        texto += f"Registros: {len(df)}\n\n"
        
        # Añadir datos
        for idx, row in df.iterrows():
            texto += f"=== Registro #{idx + 1} ===\n"
            for columna in df.columns:
                texto += f"{columna}: {row[columna]}\n"
            texto += "\n"
            
        texto += "=== FIN DEL INFORME ===\n"
        
        # Guardar archivo
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            f.write(texto)
            
        print(f"\nInforme TXT guardado en: {ruta_salida}")
