#!/usr/bin/env python3
"""
.NET Model to Python Migration Generator
Converts Entity Framework models to SQLAlchemy/Django ORM models and generates database migrations
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class PropertyInfo:
    """Represents a .NET property"""
    name: str
    csharp_type: str
    python_type: str
    nullable: bool = False
    is_key: bool = False
    is_foreign_key: bool = False
    foreign_table: Optional[str] = None
    max_length: Optional[int] = None
    is_required: bool = False
    default_value: Optional[str] = None
    annotations: List[str] = field(default_factory=list)


@dataclass
class ModelInfo:
    """Represents a .NET model/entity"""
    name: str
    namespace: str
    properties: List[PropertyInfo]
    base_class: Optional[str] = None
    relationships: List[Dict] = field(default_factory=list)
    table_name: Optional[str] = None


class MigrationGenerator:
    """Generates Python ORM models and migrations from .NET Entity Framework models"""
    
    # Type mappings from C# to Python/SQLAlchemy
    TYPE_MAPPINGS = {
        'string': ('str', 'String'),
        'int': ('int', 'Integer'),
        'long': ('int', 'BigInteger'),
        'bool': ('bool', 'Boolean'),
        'datetime': ('datetime', 'DateTime'),
        'decimal': ('Decimal', 'Numeric'),
        'float': ('float', 'Float'),
        'double': ('float', 'Float'),
        'guid': ('str', 'String(36)'),
        'byte[]': ('bytes', 'LargeBinary'),
        'short': ('int', 'SmallInteger'),
        'byte': ('int', 'SmallInteger'),
    }
    
    def __init__(self, models_path: str, target_framework: str = 'sqlalchemy', output_dir: str = '.'):
        self.models_path = Path(models_path)
        self.target_framework = target_framework.lower()
        self.output_dir = Path(output_dir)
        self.models: List[ModelInfo] = []
        
        if self.target_framework not in ['sqlalchemy', 'django']:
            raise ValueError(f"Unsupported framework: {target_framework}. Use 'sqlalchemy' or 'django'")
    
    def generate(self):
        """Main generation workflow"""
        print(f"Scanning .NET models in: {self.models_path}")
        self._scan_models()
        
        print(f"Found {len(self.models)} models to migrate")
        
        if self.target_framework == 'sqlalchemy':
            self._generate_sqlalchemy_models()
        else:
            self._generate_django_models()
        
        self._generate_migration_script()
        
        print(f"\n✓ Migration files generated in: {self.output_dir}")
    
    def _scan_models(self):
        """Scan .NET model files and extract information"""
        cs_files = list(self.models_path.rglob('*.cs'))
        
        for cs_file in cs_files:
            content = cs_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check if file contains entity/model class
            if self._is_model_file(content):
                model = self._parse_model(content, cs_file)
                if model:
                    self.models.append(model)
    
    def _is_model_file(self, content: str) -> bool:
        """Check if file contains an entity model"""
        indicators = [
            r'public class \w+',
            r'\[Table\(',
            r': DbContext',
            r'DbSet<',
            r'\[Key\]',
            r'\[Required\]',
        ]
        return any(re.search(pattern, content) for pattern in indicators)
    
    def _parse_model(self, content: str, file_path: Path) -> Optional[ModelInfo]:
        """Parse a C# model file"""
        # Extract namespace
        namespace_match = re.search(r'namespace\s+([\w\.]+)', content)
        namespace = namespace_match.group(1) if namespace_match else 'Unknown'
        
        # Extract class name
        class_match = re.search(r'public\s+class\s+(\w+)(?:\s*:\s*(\w+))?', content)
        if not class_match:
            return None
        
        class_name = class_match.group(1)
        base_class = class_match.group(2)
        
        # Skip DbContext classes
        if base_class and 'DbContext' in base_class:
            return None
        
        # Extract table name from attribute
        table_name_match = re.search(r'\[Table\("(\w+)"\)\]', content)
        table_name = table_name_match.group(1) if table_name_match else None
        
        # Parse properties
        properties = self._parse_properties(content)
        
        # Parse relationships
        relationships = self._parse_relationships(content)
        
        return ModelInfo(
            name=class_name,
            namespace=namespace,
            properties=properties,
            base_class=base_class,
            relationships=relationships,
            table_name=table_name
        )
    
    def _parse_properties(self, content: str) -> List[PropertyInfo]:
        """Extract properties from C# class"""
        properties = []
        
        # Match property declarations with annotations
        prop_pattern = r'(?:\[([^\]]+)\]\s*)*public\s+([\w\[\]<>?]+)\s+(\w+)\s*{\s*get;\s*set;\s*}'
        
        for match in re.finditer(prop_pattern, content, re.MULTILINE):
            annotations_str = match.group(1) or ''
            csharp_type = match.group(2)
            prop_name = match.group(3)
            
            # Parse annotations
            annotations = [a.strip() for a in annotations_str.split('][') if a]
            
            # Determine if nullable
            nullable = '?' in csharp_type
            csharp_type = csharp_type.replace('?', '')
            
            # Map to Python type
            python_type, sqlalchemy_type = self._map_type(csharp_type)
            
            # Check for key
            is_key = any('Key' in a for a in annotations)
            
            # Check for foreign key
            is_fk = any('ForeignKey' in a for a in annotations)
            foreign_table = None
            if is_fk:
                fk_match = re.search(r'ForeignKey\("(\w+)"\)', annotations_str)
                if fk_match:
                    foreign_table = fk_match.group(1)
            
            # Check for required
            is_required = any('Required' in a for a in annotations)
            
            # Check for max length
            max_length = None
            max_length_match = re.search(r'MaxLength\((\d+)\)', annotations_str)
            if max_length_match:
                max_length = int(max_length_match.group(1))
            elif 'StringLength' in annotations_str:
                str_len_match = re.search(r'StringLength\((\d+)\)', annotations_str)
                if str_len_match:
                    max_length = int(str_len_match.group(1))
            
            properties.append(PropertyInfo(
                name=prop_name,
                csharp_type=csharp_type,
                python_type=python_type,
                nullable=nullable,
                is_key=is_key,
                is_foreign_key=is_fk,
                foreign_table=foreign_table,
                max_length=max_length,
                is_required=is_required,
                annotations=annotations
            ))
        
        return properties
    
    def _parse_relationships(self, content: str) -> List[Dict]:
        """Parse EF navigation properties and relationships"""
        relationships = []
        
        # One-to-many: ICollection<T> or List<T>
        one_to_many_pattern = r'public\s+(?:virtual\s+)?(?:ICollection|List)<(\w+)>\s+(\w+)\s*{'
        for match in re.finditer(one_to_many_pattern, content):
            relationships.append({
                'type': 'one_to_many',
                'related_model': match.group(1),
                'property_name': match.group(2)
            })
        
        # Many-to-one or one-to-one: single reference
        ref_pattern = r'public\s+(?:virtual\s+)?(\w+)\s+(\w+)\s*{\s*get;\s*set;\s*}'
        for match in re.finditer(ref_pattern, content):
            type_name = match.group(1)
            prop_name = match.group(2)
            
            # Skip if it's a collection or primitive type
            if type_name not in ['string', 'int', 'bool', 'DateTime', 'decimal', 'float', 'double']:
                # Check if it's likely a navigation property
                if prop_name.endswith('Id'):
                    continue  # Skip foreign key properties
                
                relationships.append({
                    'type': 'many_to_one',
                    'related_model': type_name,
                    'property_name': prop_name
                })
        
        return relationships
    
    def _map_type(self, csharp_type: str) -> Tuple[str, str]:
        """Map C# type to Python and SQLAlchemy types"""
        csharp_type_lower = csharp_type.lower()
        
        for cs_type, (py_type, sa_type) in self.TYPE_MAPPINGS.items():
            if cs_type in csharp_type_lower:
                return py_type, sa_type
        
        # Default to string if unknown
        return 'str', 'String'
    
    def _generate_sqlalchemy_models(self):
        """Generate SQLAlchemy model files"""
        output_file = self.output_dir / 'models.py'
        
        with open(output_file, 'w') as f:
            # Write imports
            f.write('"""SQLAlchemy models generated from .NET Entity Framework models"""\n\n')
            f.write('from datetime import datetime\n')
            f.write('from decimal import Decimal\n')
            f.write('from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Float, ForeignKey, Text, LargeBinary\n')
            f.write('from sqlalchemy.ext.declarative import declarative_base\n')
            f.write('from sqlalchemy.orm import relationship\n\n')
            f.write('Base = declarative_base()\n\n\n')
            
            # Write models
            for model in self.models:
                self._write_sqlalchemy_model(f, model)
        
        print(f"✓ Generated SQLAlchemy models: {output_file}")
    
    def _write_sqlalchemy_model(self, f, model: ModelInfo):
        """Write a single SQLAlchemy model"""
        table_name = model.table_name or self._to_snake_case(model.name)
        
        f.write(f'class {model.name}(Base):\n')
        f.write(f'    """Migrated from {model.namespace}.{model.name}"""\n')
        f.write(f'    __tablename__ = "{table_name}"\n\n')
        
        # Write columns
        for prop in model.properties:
            column_def = self._generate_sqlalchemy_column(prop)
            f.write(f'    {self._to_snake_case(prop.name)} = {column_def}\n')
        
        # Write relationships
        if model.relationships:
            f.write('\n')
            for rel in model.relationships:
                rel_def = self._generate_sqlalchemy_relationship(rel)
                f.write(f'    {self._to_snake_case(rel["property_name"])} = {rel_def}\n')
        
        f.write('\n\n')
    
    def _generate_sqlalchemy_column(self, prop: PropertyInfo) -> str:
        """Generate SQLAlchemy column definition"""
        # Map type
        _, sa_type = self._map_type(prop.csharp_type)
        
        # Build column definition
        parts = [sa_type]
        
        if prop.max_length:
            parts[0] = f'String({prop.max_length})'
        
        args = []
        
        if prop.is_key:
            args.append('primary_key=True')
        
        if prop.is_foreign_key and prop.foreign_table:
            fk_table = self._to_snake_case(prop.foreign_table)
            parts.insert(0, f'ForeignKey("{fk_table}.id")')
        
        if not prop.nullable and not prop.is_key:
            args.append('nullable=False')
        
        if prop.default_value:
            args.append(f'default={prop.default_value}')
        
        # Combine
        args_str = ', '.join(args)
        if args_str:
            return f'Column({", ".join(parts)}, {args_str})'
        else:
            return f'Column({", ".join(parts)})'
    
    def _generate_sqlalchemy_relationship(self, rel: Dict) -> str:
        """Generate SQLAlchemy relationship definition"""
        related_model = rel['related_model']
        
        if rel['type'] == 'one_to_many':
            return f'relationship("{related_model}", back_populates="{self._to_snake_case(rel["property_name"])}")'
        else:
            return f'relationship("{related_model}")'
    
    def _generate_django_models(self):
        """Generate Django model files"""
        output_file = self.output_dir / 'models.py'
        
        with open(output_file, 'w') as f:
            # Write imports
            f.write('"""Django models generated from .NET Entity Framework models"""\n\n')
            f.write('from django.db import models\n')
            f.write('from datetime import datetime\n')
            f.write('from decimal import Decimal\n\n\n')
            
            # Write models
            for model in self.models:
                self._write_django_model(f, model)
        
        print(f"✓ Generated Django models: {output_file}")
    
    def _write_django_model(self, f, model: ModelInfo):
        """Write a single Django model"""
        f.write(f'class {model.name}(models.Model):\n')
        f.write(f'    """Migrated from {model.namespace}.{model.name}"""\n\n')
        
        # Write fields
        for prop in model.properties:
            if not prop.is_key or prop.name.lower() != 'id':  # Django auto-creates 'id'
                field_def = self._generate_django_field(prop)
                f.write(f'    {self._to_snake_case(prop.name)} = {field_def}\n')
        
        # Write Meta class
        if model.table_name:
            f.write('\n    class Meta:\n')
            f.write(f'        db_table = "{model.table_name}"\n')
        
        f.write('\n\n')
    
    def _generate_django_field(self, prop: PropertyInfo) -> str:
        """Generate Django field definition"""
        # Map to Django field type
        field_mapping = {
            'str': 'CharField',
            'int': 'IntegerField',
            'bool': 'BooleanField',
            'datetime': 'DateTimeField',
            'Decimal': 'DecimalField',
            'float': 'FloatField',
            'bytes': 'BinaryField',
        }
        
        django_field = field_mapping.get(prop.python_type, 'CharField')
        
        args = []
        
        if prop.max_length and django_field == 'CharField':
            args.append(f'max_length={prop.max_length}')
        elif django_field == 'CharField' and not prop.max_length:
            args.append('max_length=255')
        
        if prop.python_type == 'Decimal':
            args.append('max_digits=18')
            args.append('decimal_places=2')
        
        if prop.nullable:
            args.append('null=True')
            args.append('blank=True')
        
        if prop.is_foreign_key and prop.foreign_table:
            django_field = 'ForeignKey'
            args.insert(0, f'"{prop.foreign_table}"')
            args.append('on_delete=models.CASCADE')
        
        args_str = ', '.join(args)
        return f'models.{django_field}({args_str})'
    
    def _generate_migration_script(self):
        """Generate migration instructions/script"""
        output_file = self.output_dir / 'MIGRATION_GUIDE.md'
        
        with open(output_file, 'w') as f:
            f.write('# Database Migration Guide\n\n')
            f.write('This guide explains how to apply the generated models to your database.\n\n')
            
            if self.target_framework == 'sqlalchemy':
                f.write('## SQLAlchemy Migration with Alembic\n\n')
                f.write('### 1. Install Alembic\n')
                f.write('```bash\n')
                f.write('pip install alembic\n')
                f.write('```\n\n')
                f.write('### 2. Initialize Alembic\n')
                f.write('```bash\n')
                f.write('alembic init alembic\n')
                f.write('```\n\n')
                f.write('### 3. Configure Alembic\n')
                f.write('Edit `alembic/env.py` and import your models:\n')
                f.write('```python\n')
                f.write('from models import Base\n')
                f.write('target_metadata = Base.metadata\n')
                f.write('```\n\n')
                f.write('### 4. Generate Migration\n')
                f.write('```bash\n')
                f.write('alembic revision --autogenerate -m "Initial migration from .NET"\n')
                f.write('```\n\n')
                f.write('### 5. Apply Migration\n')
                f.write('```bash\n')
                f.write('alembic upgrade head\n')
                f.write('```\n\n')
            else:
                f.write('## Django Migration\n\n')
                f.write('### 1. Copy models.py to your Django app\n')
                f.write('```bash\n')
                f.write('cp models.py your_app/models.py\n')
                f.write('```\n\n')
                f.write('### 2. Generate migrations\n')
                f.write('```bash\n')
                f.write('python manage.py makemigrations\n')
                f.write('```\n\n')
                f.write('### 3. Apply migrations\n')
                f.write('```bash\n')
                f.write('python manage.py migrate\n')
                f.write('```\n\n')
            
            f.write('## Models Summary\n\n')
            f.write(f'Total models migrated: {len(self.models)}\n\n')
            
            for model in self.models:
                f.write(f'### {model.name}\n')
                f.write(f'- Namespace: `{model.namespace}`\n')
                f.write(f'- Properties: {len(model.properties)}\n')
                f.write(f'- Relationships: {len(model.relationships)}\n')
                if model.table_name:
                    f.write(f'- Table: `{model.table_name}`\n')
                f.write('\n')
        
        print(f"✓ Generated migration guide: {output_file}")
    
    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert PascalCase to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def main():
    parser = argparse.ArgumentParser(
        description='Generate Python ORM models and migrations from .NET Entity Framework models'
    )
    parser.add_argument(
        'models_path',
        help='Path to directory containing .NET model files'
    )
    parser.add_argument(
        '--framework',
        choices=['sqlalchemy', 'django'],
        default='sqlalchemy',
        help='Target Python ORM framework (default: sqlalchemy)'
    )
    parser.add_argument(
        '--output',
        '-o',
        default='./migrations',
        help='Output directory for generated files (default: ./migrations)'
    )
    parser.add_argument(
        '--from-dotnet-models',
        dest='models_path',
        help='Alias for models_path (for compatibility with docs)'
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate migrations
    generator = MigrationGenerator(
        models_path=args.models_path,
        target_framework=args.framework,
        output_dir=output_dir
    )
    
    try:
        generator.generate()
        print("\n✓ Migration generation completed successfully!")
        print(f"\nNext steps:")
        print(f"1. Review generated models in: {output_dir}/models.py")
        print(f"2. Follow instructions in: {output_dir}/MIGRATION_GUIDE.md")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
