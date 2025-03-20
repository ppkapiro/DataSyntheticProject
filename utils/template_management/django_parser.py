import ast
from typing import Dict, Any, Optional
import re
from pathlib import Path

class DjangoModelParser:
    """Parser especializado para modelos Django"""

    def parse_model(self, content: str) -> Dict[str, Any]:
        """Analiza un modelo Django y extrae sus campos"""
        try:
            tree = ast.parse(content)
            model_fields = {}

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    fields = self._extract_model_fields(node)
                    model_fields.update(fields)

            return model_fields
        except Exception as e:
            print(f"Error analizando modelo: {str(e)}")
            return {}

    def parse_model_file(self, file_path: Path) -> Dict[str, Any]:
        """Analiza un archivo de modelo Django y extrae su estructura"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extraer nombre del modelo y campos
        model_match = re.search(r'class\s+(\w+)\(models\.Model\):', content)
        if not model_match:
            raise ValueError("No se encontró una clase modelo válida")

        model_name = model_match.group(1)
        fields = self._extract_fields(content)

        return {
            'name': model_name,
            'fields': fields
        }

    def _extract_model_fields(self, class_node: ast.ClassDef) -> Dict[str, Any]:
        """Extrae campos de una clase modelo"""
        fields = {}

        for node in class_node.body:
            if isinstance(node, ast.Assign):
                field_info = self._extract_field_info(node)
                if field_info:
                    name, info = field_info
                    fields[name] = info

        return fields

    def _extract_field_info(self, node: ast.Assign) -> Optional[tuple]:
        """Extrae información de un campo del modelo"""
        try:
            if len(node.targets) != 1:
                return None

            target = node.targets[0]
            if not isinstance(target, ast.Name):
                return None

            field_name = target.id
            if not isinstance(node.value, ast.Call):
                return None

            # Extraer tipo y opciones del campo
            field_info = self._analyze_field_call(node.value)
            if field_info:
                return field_name, field_info

        except Exception:
            pass

        return None

    def _analyze_field_call(self, call_node: ast.Call) -> Optional[Dict[str, Any]]:
        """Analiza la llamada a un campo del modelo"""
        try:
            if not isinstance(call_node.func, ast.Attribute):
                return None

            # Obtener tipo de campo
            field_type = call_node.func.attr.replace('Field', '').lower()

            # Analizar argumentos y opciones
            options = {
                'type': field_type,
                'required': True,
                'validators': []
            }

            # Procesar keywords
            for kw in call_node.keywords:
                self._process_field_keyword(kw, options)

            return options

        except Exception:
            return None

    def _process_field_keyword(self, keyword: ast.keyword, options: Dict[str, Any]) -> None:
        """Procesa un keyword de un campo"""
        key = keyword.arg
        value = keyword.value

        if key == 'null' and isinstance(value, ast.Constant):
            options['required'] = not value.value
        elif key == 'blank' and isinstance(value, ast.Constant):
            options['blank'] = value.value
        elif key == 'help_text' and isinstance(value, ast.Constant):
            options['description'] = value.value
        elif key == 'validators' and isinstance(value, ast.List):
            options['validators'].extend(self._extract_validators(value))

    def _extract_validators(self, validators_list: ast.List) -> list:
        """Extrae validadores de una lista de validadores"""
        validators = []
        for validator in validators_list.elts:
            if isinstance(validator, ast.Call):
                validator_info = self._analyze_validator(validator)
                if validator_info:
                    validators.append(validator_info)
        return validators

    def _analyze_validator(self, validator: ast.Call) -> Optional[Dict[str, Any]]:
        """Analiza un validador individual"""
        if not isinstance(validator.func, ast.Name):
            return None

        validator_name = validator.func.id
        validator_info = {
            'type': validator_name.replace('Validator', '').lower()
        }

        # Procesar argumentos del validador
        for kw in validator.keywords:
            if isinstance(kw.value, ast.Constant):
                validator_info[kw.arg] = kw.value.value

        return validator_info

    def _extract_fields(self, content: str) -> Dict[str, Any]:
        """Extrae y analiza los campos del modelo"""
        fields = {}
        field_pattern = r'(\w+)\s*=\s*models\.(\w+)Field\((.*?)\)'
        
        for match in re.finditer(field_pattern, content, re.DOTALL):
            field_name = match.group(1)
            field_type = match.group(2)
            options = self._parse_field_options(match.group(3))
            
            fields[field_name] = {
                'type': self._map_django_type(field_type),
                'required': not options.get('null', False),
                'validators': self._extract_validators(options),
                'description': options.get('help_text', f"Campo {field_name}"),
                'choices': self._parse_choices(options.get('choices'))
            }

        return fields

    def _map_django_type(self, django_type: str) -> str:
        """Mapea tipos de Django a tipos de plantilla"""
        type_mapping = {
            'Char': 'string',
            'Text': 'string',
            'Integer': 'number',
            'Float': 'number',
            'Boolean': 'boolean',
            'Date': 'date',
            'DateTime': 'date',
            'Email': 'email'
        }
        return type_mapping.get(django_type, 'string')
