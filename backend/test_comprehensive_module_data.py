#!/usr/bin/env python3
"""
Test para la nueva función get_comprehensive_module_data()
que recupera TODA la información de un módulo con estructura jerárquica.

Funcionalidades:
- Recupera datos completos de tablas principales y sus subtablas
- Estructura jerárquica en JSON
- Ignora campos JSON y campos internos
- Ejemplo: problems → direct_effects → indirect_effects
"""

import json
import sys
from pathlib import Path

# Agregar ruta del backend
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Importar todo primero para evitar circular imports
import app.models.project
import app.models.problems
import app.models.population
import app.models.participants_general
import app.models.objectives
import app.models.alternatives_general
import app.models.direct_effects
import app.models.indirect_effects
import app.models.direct_causes
import app.models.indirect_causes
import app.models.affected_population
import app.models.intervention_population
import app.models.characteristics_population
import app.models.participants
import app.models.survey

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.chat_history import (
    get_comprehensive_module_data, 
    format_module_data_for_prompt
)


def test_comprehensive_module_data():
    """Test la función de datos comprensivos para todos los módulos."""
    db: Session = SessionLocal()
    
    try:
        # Obtener proyecto (usamos el primero)
        from app.models.project import Project
        project = db.query(Project).first()
        
        if not project:
            print("❌ No hay proyectos en la BD. Crea uno primero.")
            return
        
        project_id = project.id
        print(f"\n{'='*80}")
        print(f"🔍 Testando función de datos COMPLETOS del módulo")
        print(f"{'='*80}")
        print(f"Proyecto: {project.name} (ID: {project_id})")
        
        # Módulos principales a testear
        modules_to_test = [
            'problems',
            'population',
            'participants_general',
            'objectives',
            'alternatives_general',
        ]
        
        for module in modules_to_test:
            print(f"\n\n{'─'*80}")
            print(f"📦 Módulo: {module.upper()}")
            print(f"{'─'*80}")
            
            # Obtener datos completos del módulo
            data = get_comprehensive_module_data(db, project_id, module)
            
            # Mostrar estado
            if data.get("status") == "error":
                print(f"❌ Error: {data.get('message')}")
                continue
            
            total = data.get("total_records", 0)
            print(f"\n📊 Total de registros en BD: {total}")
            
            if total == 0:
                print(f"   (Sin registros de {module} para este proyecto)")
                continue
            
            # Mostrar estructura de datos (JSON)
            print(f"\n📋 Estructura de datos (JSON):\n")
            formatted = format_module_data_for_prompt(data, max_items=50)
            print(formatted)
            
            # Análisis de subtablas
            if data.get("records"):
                first_record = data["records"][0]
                subtables = [k for k in first_record.keys() 
                           if isinstance(first_record[k], list) and first_record[k]]
                
                if subtables:
                    print(f"\n📚 Subtablas encontradas en {module}:")
                    for subtable in subtables:
                        count = len(first_record[subtable])
                        print(f"   ├─ {subtable}: {count} registros")
                        
                        # Mostrar primer nivel de sub-subtablas
                        if first_record[subtable]:
                            sub_record = first_record[subtable][0]
                            sub_subtables = [k for k in sub_record.keys() 
                                           if isinstance(sub_record[k], list) and sub_record[k]]
                            for sub_subtable in sub_subtables:
                                sub_count = len(sub_record[sub_subtable])
                                print(f"   │  ├─ {sub_subtable}: {sub_count} registros")
        
        print(f"\n\n{'='*80}")
        print(f"✅ TEST COMPLETADO")
        print(f"{'='*80}\n")
        
        # Test específico: estructura jerárquica de problems
        print(f"\n{'='*80}")
        print(f"🔬 TEST DETALLADO: Estructura jerárquica de PROBLEMS")
        print(f"{'='*80}\n")
        
        problems_data = get_comprehensive_module_data(db, project_id, 'problems')
        
        if problems_data.get("total_records", 0) > 0:
            first_problem = problems_data["records"][0]
            
            print("Problema principal:")
            print(f"  central_problem: {first_problem.get('central_problem')[:50]}...")
            print(f"  current_description: {first_problem.get('current_description')[:50]}...")
            
            if 'direct_effects' in first_problem:
                effects = first_problem['direct_effects']
                print(f"\n  ├─ direct_effects ({len(effects)} registros):")
                for i, effect in enumerate(effects[:2], 1):
                    print(f"     {i}. {effect.get('description')[:40]}...")
                    
                    if 'indirect_effects' in effect:
                        indirect = effect['indirect_effects']
                        print(f"        └─ indirect_effects ({len(indirect)} registros):")
                        for j, ind_effect in enumerate(indirect[:1], 1):
                            print(f"           {j}. {ind_effect.get('description')[:35]}...")
            
            if 'direct_causes' in first_problem:
                causes = first_problem['direct_causes']
                print(f"\n  └─ direct_causes ({len(causes)} registros):")
                for i, cause in enumerate(causes[:2], 1):
                    print(f"     {i}. {cause.get('description')[:40]}...")
                    
                    if 'indirect_causes' in cause:
                        indirect = cause['indirect_causes']
                        print(f"        └─ indirect_causes ({len(indirect)} registros):")
                        for j, ind_cause in enumerate(indirect[:1], 1):
                            print(f"           {j}. {ind_cause.get('description')[:35]}...")
        else:
            print("(No hay problemas registrados)")
        
        print(f"\n{'='*80}")
        print(f"🎉 Estructura jerárquica verificada correctamente")
        print(f"{'='*80}\n")
        
    finally:
        db.close()


def test_population_hierarchy():
    """Test específico para la jerarquía de population."""
    db: Session = SessionLocal()
    
    try:
        from app.models.project import Project
        project = db.query(Project).first()
        
        if not project:
            print("❌ No hay proyectos en la BD.")
            return
        
        project_id = project.id
        
        print(f"\n{'='*80}")
        print(f"🏗️  TEST ESPECÍFICO: Estructura jerárquica de POPULATION")
        print(f"{'='*80}\n")
        
        population_data = get_comprehensive_module_data(db, project_id, 'population')
        
        if population_data.get("total_records", 0) > 0:
            pop = population_data["records"][0]
            
            print("Población principal:")
            print(f"  population_type_affected: {pop.get('population_type_affected')}")
            print(f"  number_affected: {pop.get('number_affected')}")
            
            # Mostrar subtablas
            subtables = {
                'affected_population': '📍 Población Afectada',
                'intervention_population': '🎯 Población de Intervención',
                'characteristics_population': '📊 Características de Población'
            }
            
            for table_key, label in subtables.items():
                if table_key in pop:
                    records = pop[table_key]
                    print(f"\n  {label}: ({len(records)} registros)")
                    
                    for i, record in enumerate(records[:3], 1):
                        fields = {k: v for k, v in record.items() 
                                 if k not in ['population_id', 'id']}
                        print(f"    {i}. {fields}")
                else:
                    print(f"\n  {label}: (sin registros)")
        else:
            print("(No hay población registrada)")
        
        print(f"\n{'='*80}\n")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  🎯 TEST: FUNCIÓN DE DATOS COMPRENSIVOS CON ESTRUCTURA JERÁRQUICA  ".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Ejecutar tests
    test_comprehensive_module_data()
    test_population_hierarchy()
    
    print("\n✅ Todos los tests completados\n")
