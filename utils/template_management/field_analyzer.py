from pathlib import Path
from typing import Dict, Any, Tuple, List
from datetime import datetime
import re
import ast
from .logging_config import setup_logging
from .validators import FieldValidator

class FieldAnalyzer:
    """Analizador de campos desde diferentes fuentes"""

    def __init__(self):
        self.logger = setup_logging()
        self.validator = FieldValidator()
        self.analyzers = {
            'basic_text': self._analyze_text_file,
            'json': self._analyze_json,
            'yaml': self._analyze_yaml,
            'django': self._analyze_django_model,
            'ast': self._analyze_ast,
            'regex': self._analyze_regex,
            'excel': self._analyze_excel
        }

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analiza un archivo probando todos los métodos disponibles"""
        self.logger.info(f"Iniciando análisis del archivo: {file_path}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"No se encuentra el archivo: {file_path}")

        # Leer contenido del archivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Probar cada analizador y guardar resultados
        analysis_results = []
        
        for method_name, analyzer in self.analyzers.items():
            try:
                self.logger.info(f"Probando método: {method_name}")
                fields = analyzer(content)
                quality = self._calculate_analysis_quality(fields, method_name)
                
                analysis_results.append({
                    'method': method_name,
                    'fields': fields,
                    'quality': quality,
                    'field_count': len(fields)
                })
                
                self.logger.info(f"✓ {len(fields)} campos encontrados (calidad: {quality}%)")
                
            except Exception as e:
                self.logger.error(f"Error en análisis {method_name}: {str(e)}")
                continue

        # Seleccionar el mejor resultado
        if not analysis_results:
            raise ValueError("Ningún método de análisis fue exitoso")

        best_result = max(analysis_results, key=lambda x: (x['quality'], x['field_count']))
        
        self.logger.info(f"✅ Método más efectivo: {best_result['method']} ({best_result['quality']}%)")
        
        return {
            'fields': best_result['fields'],
            'metadata': {
                'analysis_method': best_result['method'],
                'quality_score': best_result['quality'],
                'total_fields': best_result['field_count'],
                'alternative_methods': [
                    {
                        'method': r['method'],
                        'quality': r['quality'],
                        'fields': len(r['fields'])
                    }
                    for r in analysis_results
                    if r['method'] != best_result['method']
                ]
            }
        }

    def _generate_analysis_feedback(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Genera retroalimentación detallada del análisis"""
        feedback = {
            'quality_metrics': self._calculate_quality(fields),
            'suggestions': [],
            'warnings': [],
            'improvement_areas': []
        }

        # Análisis general
        if len(fields) < 3:
            feedback['warnings'].append("Pocos campos detectados - verificar archivo fuente")
        
        # Análisis por campo
        for field_name, field_data in fields.items():
            field_feedback = self._analyze_field_quality(field_name, field_data)
            feedback['suggestions'].extend(field_feedback['suggestions'])
            feedback['warnings'].extend(field_feedback['warnings'])
            
            if field_feedback.get('needs_improvement'):
                feedback['improvement_areas'].append(field_name)

        self.logger.info(f"Generada retroalimentación con {len(feedback['suggestions'])} sugerencias")
        return feedback

    def _analyze_field_quality(self, name: str, field: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza la calidad de un campo individual"""
        feedback = {
            'suggestions': [],
            'warnings': [],
            'needs_improvement': False,
            'validation_status': self._validate_field_configuration(name, field)
        }

        # Agregar validación mejorada
        validation_result = self._validate_field_configuration(name, field)
        if not validation_result['is_valid']:
            feedback['warnings'].extend(validation_result['errors'])
            feedback['needs_improvement'] = True

        return feedback

    def _validate_field_configuration(self, name: str, field: Dict[str, Any]) -> Dict[str, Any]:
        """Valida la configuración completa de un campo"""
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        # Validar tipo
        if not field.get('type'):
            result['is_valid'] = False
            result['errors'].append(f"Campo '{name}': Tipo no especificado")

        # Validar reglas básicas
        if field.get('required') and not field.get('validators'):
            result['warnings'].append(f"Campo '{name}': Campo requerido sin validadores")

        # Validar coherencia de configuración
        if field.get('type') == 'number':
            self._validate_number_config(field, result)
        elif field.get('type') == 'string':
            self._validate_string_config(field, result)

        return result

    def _validate_number_config(self, field: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Valida configuración específica para números"""
        if 'min_value' in field and 'max_value' in field:
            if field['min_value'] > field['max_value']:
                result['is_valid'] = False
                result['errors'].append("Rango de valores inválido")

    def _validate_string_config(self, field: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Valida configuración específica para strings"""
        if 'min_length' in field and 'max_length' in field:
            if field['min_length'] > field['max_length']:
                result['is_valid'] = False
                result['errors'].append("Longitud mínima mayor que máxima")

    def _analyze_django_model(self, file_path: Path) -> Dict[str, Any]:
        """Analiza un modelo Django"""
        self.logger.debug(f"Iniciando análisis de modelo Django: {file_path}")
        fields = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extraer definiciones de campo
        field_pattern = r'(\w+)\s*=\s*models\.(\w+)Field\((.*?)\)'
        matches = re.finditer(field_pattern, content, re.DOTALL)

        for match in matches:
            name = match.group(1)
            field_type = match.group(2)
            options = match.group(3)

            # Analizar opciones del campo
            fields[name] = {
                'type': self._map_django_type(field_type),
                'required': 'null=True' not in options,
                'validators': self._extract_validators(options),
                'description': self._extract_help_text(options)
            }

        self.logger.debug(f"Análisis Django completado: {len(fields)} campos")
        return fields

    def _map_django_type(self, django_type: str) -> str:
        """Mapea tipos de Django a tipos genéricos"""
        return {
            'Char': 'string',
            'Text': 'text',
            'Integer': 'number',
            'Float': 'float',
            'Boolean': 'boolean',
            'Date': 'date',
            'DateTime': 'datetime',
            'ForeignKey': 'relation',
            'OneToOne': 'relation',
            'ManyToMany': 'relation'
        }.get(django_type, 'string')

    def _extract_validators(self, options: str) -> list:
        """Extrae validadores de un campo Django"""
        validators = super()._extract_validators(options)
        
        # Convertir validadores Django a reglas de validación
        validation_rules = {}
        for validator in validators:
            if validator['type'] == 'regex':
                validation_rules['pattern'] = validator['pattern']
            elif validator['type'] in ['minlength', 'maxlength', 'minvalue', 'maxvalue']:
                validation_rules[validator['type']] = validator.get('limit')
        
        return {
            'validators': validators,
            'rules': validation_rules
        }

    def _extract_help_text(self, options: str) -> str:
        """Extrae el texto de ayuda de un campo"""
        match = re.search(r'help_text=_?\([\'"](.+?)[\'"]\)', options)
        return match.group(1) if match else None

    def _calculate_quality(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula la calidad del análisis con métricas detalladas"""
        metrics = {
            'total_score': 0,
            'field_scores': {},
            'issues': [],
            'suggestions': []
        }
        
        weights = {
            'type_detection': 0.4,
            'validation_rules': 0.3,
            'documentation': 0.3
        }

        for field_name, field_data in fields.items():
            field_score = self._calculate_field_score(field_name, field_data, weights)
            metrics['field_scores'][field_name] = field_score
            metrics['total_score'] += field_score['weighted_score']

        metrics['total_score'] = round(metrics['total_score'] / len(fields), 2)
        metrics['quality_level'] = self._get_quality_level(metrics['total_score'])
        
        self.logger.info(f"Calidad final: {metrics['total_score']}% ({metrics['quality_level']})")
        return metrics

    def _calculate_field_score(self, name: str, field: Dict[str, Any], weights: Dict[str, float]) -> Dict[str, Any]:
        """Calcula la puntuación detallada para un campo individual"""
        scores = {
            'type_detection': 100 if field.get('type') else 0,
            'validation_rules': self._calculate_validation_score(field),
            'documentation': self._calculate_documentation_score(field)
        }

        weighted_score = sum(score * weights[category] 
                           for category, score in scores.items())

        return {
            'scores': scores,
            'weighted_score': weighted_score,
            'issues': self._identify_field_issues(name, field)
        }

    def _calculate_validation_score(self, field: Dict[str, Any]) -> float:
        """Calcula la puntuación de validación"""
        score = 0
        if field.get('validators'):
            score += 50
            if any(v.get('type') == 'regex' for v in field['validators']):
                score += 25
            if len(field['validators']) > 1:
                score += 25
        return score

    def _calculate_documentation_score(self, field: Dict[str, Any]) -> float:
        """Calcula la puntuación de documentación"""
        score = 0
        if field.get('description'):
            score += 50
            if len(field['description']) > 10:
                score += 25
            if len(field['description']) > 50:
                score += 25
        return score

    def _get_quality_level(self, score: float) -> str:
        """Determina el nivel de calidad basado en la puntuación"""
        if score >= 90:
            return 'Excelente'
        elif score >= 75:
            return 'Bueno'
        elif score >= 60:
            return 'Aceptable'
        elif score >= 40:
            return 'Necesita Mejoras'
        return 'Crítico'

    def _identify_field_issues(self, name: str, field: Dict[str, Any]) -> List[str]:
        """Identifica problemas específicos en un campo"""
        issues = []
        if not field.get('type'):
            issues.append(f"Tipo no detectado en '{name}'")
        if not field.get('validators'):
            issues.append(f"Sin validadores en '{name}'")
        if not field.get('description'):
            issues.append(f"Sin descripción en '{name}'")
        return issues

    def _analyze_ast(self, file_path: Path) -> Dict[str, Any]:
        """Analiza un archivo usando AST con mejor manejo de errores"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificar si el contenido parece código Python
            if not self._looks_like_python(content):
                self.logger.warning(f"El contenido no parece ser código Python válido: {file_path}")
                return {}

            # Intentar parsear como Python
            tree = ast.parse(content)
            fields = {}

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_fields = self._extract_class_fields(node)
                    fields.update(class_fields)

            return fields

        except SyntaxError as e:
            self.logger.error(f"Error de sintaxis Python en {file_path}: {str(e)}")
            return {}
        except Exception as e:
            self.logger.error(f"Error en análisis AST de {file_path}: {str(e)}")
            return {}

    def _looks_like_python(self, content: str) -> bool:
        """Verifica si el contenido parece código Python"""
        python_indicators = [
            'class ',
            'def ',
            'import ',
            'from ',
            '    ',  # Indentación Python
            'self.',
            '__init__',
        ]
        
        first_lines = content.split('\n')[:10]  # Revisar primeras 10 líneas
        return any(any(indicator in line for indicator in python_indicators) 
                  for line in first_lines)

    def _extract_class_fields(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extrae campos de una clase con mejor manejo de errores"""
        fields = {}
        
        try:
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            field_name = target.id
                            field_info = self._analyze_field_assignment(item.value)
                            if field_info:
                                fields[field_name] = field_info
        except Exception as e:
            self.logger.error(f"Error extrayendo campos de clase: {str(e)}")
            
        return fields

    def _analyze_field_assignment(self, value_node: ast.AST) -> Dict[str, Any]:
        """Analiza la asignación de un campo con validación mejorada"""
        try:
            if isinstance(value_node, ast.Call):
                if isinstance(value_node.func, ast.Attribute):
                    # Extraer tipo de campo
                    field_type = value_node.func.attr
                    if field_type.endswith('Field'):
                        field_type = field_type[:-5].lower()
                        
                    return {
                        'type': field_type,
                        'required': True,  # Valor por defecto
                        'validators': self._extract_field_validators(value_node)
                    }
        except Exception as e:
            self.logger.debug(f"Error analizando asignación de campo: {str(e)}")
            
        return None

    def _calculate_analysis_quality(self, fields: Dict[str, Any], method: str) -> float:
        """Calcula la calidad del análisis basado en múltiples factores"""
        if not fields:
            return 0.0

        scores = []
        
        # Verificar estructura de campos
        for field_name, field_data in fields.items():
            field_score = 0
            
            # Tiene tipo definido
            if isinstance(field_data, dict) and 'type' in field_data:
                field_score += 40
                
                # Tiene validaciones
                if 'validators' in field_data:
                    field_score += 20
                    
                # Tiene descripción
                if 'description' in field_data:
                    field_score += 20
                    
                # Tiene otros metadatos
                if len(field_data) > 3:
                    field_score += 20
                    
            scores.append(field_score)

        # Calcular promedio
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Ajustar según el método
        method_multipliers = {
            'django': 1.2,    # Mayor confianza en análisis Django
            'ast': 1.1,       # AST es bastante confiable
            'json': 1.0,      # JSON es confiable si funciona
            'yaml': 1.0,      # YAML es confiable si funciona
            'basic_text': 0.8  # Texto básico es menos confiable
        }
        
        return round(avg_score * method_multipliers.get(method, 1.0), 2)
