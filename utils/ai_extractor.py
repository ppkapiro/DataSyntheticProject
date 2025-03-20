import os
from pathlib import Path
try:
    from google.cloud import vision
except ImportError:
    print("Advertencia: No se encontró google-cloud-vision. Algunas funciones de IA podrían no estar disponibles.")
    vision = None
import boto3
from utils.config_manager import ConfigManager
import tempfile
from PIL import Image
import pandas as pd

class AIExtractor:
    """Clase base para extracción de contenido usando IA"""
    
    def __init__(self):
        if vision is None:
            raise ImportError("google-cloud-vision no está instalado. Instálalo con: pip install google-cloud-vision")
        self.config = ConfigManager.load_config()
        
    def mejorar_extraccion(self, file_path, contenido_actual, tipo_archivo):
        """Mejora la extracción usando IA si el usuario lo desea"""
        print("\nSeleccione la API a usar:")
        print("1) Google Cloud Vision")
        print("2) Amazon Textract")
        
        while True:
            try:
                opcion = int(input("\nIngrese opción (0 para cancelar): "))
                if opcion == 0:
                    return contenido_actual, 0
                if opcion in [1, 2]:
                    break
                print("Opción no válida")
            except ValueError:
                print("Por favor ingrese un número válido")

        if opcion == 1:
            return self.usar_cloud_vision(file_path, tipo_archivo)
        else:
            return self.usar_textract(file_path, tipo_archivo)

    def usar_cloud_vision(self, file_path, tipo_archivo):
        """Usa Google Cloud Vision para mejorar la extracción"""
        if not self.config or not self.config['ai_services']['google_cloud_vision']['enabled']:
            print("\nError: Google Cloud Vision no está habilitado")
            return None, 0

        try:
            # Configurar credenciales
            credentials_file = self.config['ai_services']['google_cloud_vision']['credentials_file']
            credentials_path = Path(__file__).parent.parent / credentials_file
            
            if not credentials_path.exists():
                print(f"\nError: Archivo de credenciales no encontrado en: {credentials_path}")
                return None, 0

            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(credentials_path)
            client = vision.ImageAnnotatorClient()
            
            # Convertir archivo a imagen si es necesario
            if tipo_archivo not in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
                return self._procesar_documento(file_path, client)
            else:
                return self._procesar_imagen(file_path, client)

        except Exception as e:
            print(f"\nError en Google Cloud Vision: {str(e)}")
            return None, 0

    def usar_textract(self, file_path, tipo_archivo):
        """Placeholder para Amazon Textract"""
        print("\nIntegración con Amazon Textract - No implementada")
        print("Se requiere:")
        print("1. Configurar credenciales AWS")
        print("2. Implementar lógica de extracción")
        print("3. Manejar respuesta y calidad")
        return None, 0

    def _procesar_documento(self, file_path, client):
        """Procesa un documento usando Vision API"""
        # Implementación específica para cada tipo de documento
        # Por ahora, tratamos todo como imagen
        return self._procesar_imagen(file_path, client)

    def _procesar_imagen(self, file_path, client):
        """Procesa una imagen usando Vision API"""
        with open(file_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        text = response.full_text_annotation.text
        
        # Evaluar calidad
        quality = self._evaluar_calidad_extraccion(text)
        return text, quality

    def _evaluar_calidad_extraccion(self, contenido):
        """Evalúa la calidad de la extracción"""
        if not contenido:
            return 0

        # Análisis de contenido
        lines = contenido.split('\n')
        words = contenido.split()
        
        # Métricas básicas
        metrics = {
            'total_words': len(words),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'significant_words': len([w for w in words if len(w) > 3]),
            'lines': len(lines)
        }
        
        # Calcular calidad
        quality = min(100, (
            metrics['total_words'] * 0.3 +
            metrics['significant_words'] * 0.4 +
            metrics['lines'] * 0.3
        ))
        
        return int(quality)
