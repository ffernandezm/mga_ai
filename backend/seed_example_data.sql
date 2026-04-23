-- ============================================================
-- SCRIPT DE DATOS DE EJEMPLO PARA VALIDAR FLUJO DEL SISTEMA
-- 4 Proyectos de ejemplo en diferentes sectores
-- ============================================================
-- IMPORTANTE: Este script ELIMINA y RECREA todas las tablas.
-- Ejecutar completo en pgAdmin.
-- ============================================================

BEGIN;

-- ============================================================
-- PASO 1: ELIMINAR TODAS LAS TABLAS (orden inverso de dependencias)
-- ============================================================
DROP TABLE IF EXISTS pnds CASCADE;
DROP TABLE IF EXISTS development_plans CASCADE;
DROP TABLE IF EXISTS activities CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS chat_history CASCADE;
DROP TABLE IF EXISTS requirements CASCADE;
DROP TABLE IF EXISTS requirements_general CASCADE;
DROP TABLE IF EXISTS localization CASCADE;
DROP TABLE IF EXISTS localization_general CASCADE;
DROP TABLE IF EXISTS alternatives CASCADE;
DROP TABLE IF EXISTS alternatives_general CASCADE;
DROP TABLE IF EXISTS technical_analysis CASCADE;
DROP TABLE IF EXISTS characteristics_population CASCADE;
DROP TABLE IF EXISTS intervention_population CASCADE;
DROP TABLE IF EXISTS affected_population CASCADE;
DROP TABLE IF EXISTS population CASCADE;
DROP TABLE IF EXISTS objectives_indicator CASCADE;
DROP TABLE IF EXISTS objectives_causes CASCADE;
DROP TABLE IF EXISTS value_chain_objectives CASCADE;
DROP TABLE IF EXISTS value_chains CASCADE;
DROP TABLE IF EXISTS objectives CASCADE;
DROP TABLE IF EXISTS indirect_effects CASCADE;
DROP TABLE IF EXISTS direct_effects CASCADE;
DROP TABLE IF EXISTS indirect_causes CASCADE;
DROP TABLE IF EXISTS direct_causes CASCADE;
DROP TABLE IF EXISTS problems CASCADE;
DROP TABLE IF EXISTS participants CASCADE;
DROP TABLE IF EXISTS participants_general CASCADE;
DROP TABLE IF EXISTS survey CASCADE;
DROP TABLE IF EXISTS project_localizations CASCADE;
DROP TABLE IF EXISTS product_catalogs CASCADE;
DROP TABLE IF EXISTS projects CASCADE;

-- ============================================================
-- PASO 2: CREAR TODAS LAS TABLAS
-- ============================================================

-- PROJECTS
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    description VARCHAR,
    process VARCHAR,
    object_desc VARCHAR,
    region VARCHAR,
    department VARCHAR,
    municipality VARCHAR,
    intervention_type VARCHAR,
    project_typology VARCHAR,
    main_product VARCHAR,
    sector VARCHAR,
    indicator_code VARCHAR
);
CREATE INDEX ix_projects_id ON projects (id);
CREATE INDEX ix_projects_name ON projects (name);

-- PROJECT LOCALIZATIONS
CREATE TABLE project_localizations (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    region VARCHAR,
    department VARCHAR,
    municipality VARCHAR
);
CREATE INDEX ix_project_localizations_id ON project_localizations (id);

-- SURVEY
CREATE TABLE survey (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    survey_json JSON NOT NULL
);
CREATE INDEX ix_survey_id ON survey (id);

-- CHAT HISTORY
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    tab VARCHAR NOT NULL,
    session_id VARCHAR NOT NULL,
    sender VARCHAR NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX ix_chat_history_id ON chat_history (id);
CREATE INDEX ix_chat_history_session_id ON chat_history (session_id);

-- PARTICIPANTS GENERAL
CREATE TABLE participants_general (
    id SERIAL PRIMARY KEY,
    participants_analisis TEXT,
    project_id INTEGER NOT NULL UNIQUE REFERENCES projects(id),
    participants_json JSON
);
CREATE INDEX ix_participants_general_id ON participants_general (id);

-- PARTICIPANTS
CREATE TABLE participants (
    id SERIAL PRIMARY KEY,
    participant_actor TEXT,
    participant_entity TEXT,
    interest_expectative TEXT,
    rol TEXT,
    contribution_conflicts TEXT,
    participants_general_id INTEGER NOT NULL REFERENCES participants_general(id)
);

-- PROBLEMS
CREATE TABLE problems (
    id SERIAL PRIMARY KEY,
    central_problem TEXT NOT NULL DEFAULT '',
    current_description TEXT NOT NULL DEFAULT '',
    magnitude_problem TEXT NOT NULL DEFAULT '',
    problem_tree_json JSON,
    project_id INTEGER NOT NULL UNIQUE REFERENCES projects(id)
);
CREATE INDEX ix_problems_id ON problems (id);

-- DIRECT CAUSES
CREATE TABLE direct_causes (
    id SERIAL PRIMARY KEY,
    problem_id INTEGER REFERENCES problems(id) ON DELETE CASCADE,
    description TEXT
);
CREATE INDEX ix_direct_causes_id ON direct_causes (id);

-- INDIRECT CAUSES
CREATE TABLE indirect_causes (
    id SERIAL PRIMARY KEY,
    direct_cause_id INTEGER REFERENCES direct_causes(id) ON DELETE CASCADE,
    description TEXT
);
CREATE INDEX ix_indirect_causes_id ON indirect_causes (id);

-- DIRECT EFFECTS
CREATE TABLE direct_effects (
    id SERIAL PRIMARY KEY,
    problem_id INTEGER REFERENCES problems(id) ON DELETE CASCADE,
    description TEXT
);
CREATE INDEX ix_direct_effects_id ON direct_effects (id);

-- INDIRECT EFFECTS
CREATE TABLE indirect_effects (
    id SERIAL PRIMARY KEY,
    direct_effect_id INTEGER REFERENCES direct_effects(id) ON DELETE CASCADE,
    description TEXT
);
CREATE INDEX ix_indirect_effects_id ON indirect_effects (id);

-- OBJECTIVES
CREATE TABLE objectives (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL UNIQUE REFERENCES projects(id),
    general_problem TEXT NOT NULL DEFAULT '',
    general_objective TEXT NOT NULL DEFAULT ''
);
CREATE INDEX ix_objectives_id ON objectives (id);

-- VALUE CHAINS
CREATE TABLE value_chains (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    name VARCHAR
);
CREATE INDEX ix_value_chains_id ON value_chains (id);
CREATE INDEX ix_value_chains_name ON value_chains (name);

-- VALUE CHAIN OBJECTIVES
CREATE TABLE value_chain_objectives (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    value_chain_id INTEGER NOT NULL REFERENCES value_chains(id),
    name VARCHAR
);
CREATE INDEX ix_value_chain_objectives_id ON value_chain_objectives (id);
CREATE INDEX ix_value_chain_objectives_name ON value_chain_objectives (name);

-- OBJECTIVES CAUSES
CREATE TABLE objectives_causes (
    id SERIAL PRIMARY KEY,
    type TEXT,
    cause_related TEXT,
    specifics_objectives TEXT,
    cause_id INTEGER,
    value_chain_objective_id INTEGER REFERENCES value_chain_objectives(id),
    objective_id INTEGER REFERENCES objectives(id)
);
CREATE INDEX ix_objectives_causes_id ON objectives_causes (id);

-- OBJECTIVES INDICATOR
CREATE TABLE objectives_indicator (
    id SERIAL PRIMARY KEY,
    indicator TEXT NOT NULL,
    unit TEXT NOT NULL,
    meta FLOAT NOT NULL DEFAULT 0.0,
    source_type TEXT NOT NULL,
    source_validation TEXT NOT NULL,
    objective_id INTEGER REFERENCES objectives(id)
);
CREATE INDEX ix_objectives_indicator_id ON objectives_indicator (id);

-- POPULATION
CREATE TABLE population (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL UNIQUE REFERENCES projects(id),
    population_type_affected TEXT,
    number_affected INTEGER,
    source_information_affected TEXT,
    population_type_intervention TEXT NOT NULL DEFAULT 'No especificado',
    number_intervention INTEGER NOT NULL DEFAULT 0,
    source_information_intervention TEXT,
    population_json JSON
);
CREATE INDEX ix_population_id ON population (id);

-- AFFECTED POPULATION
CREATE TABLE affected_population (
    id SERIAL PRIMARY KEY,
    region TEXT NOT NULL,
    department VARCHAR NOT NULL,
    city TEXT,
    population_center TEXT,
    location_entity TEXT,
    population_id INTEGER NOT NULL REFERENCES population(id)
);
CREATE INDEX ix_affected_population_id ON affected_population (id);

-- INTERVENTION POPULATION
CREATE TABLE intervention_population (
    id SERIAL PRIMARY KEY,
    region TEXT NOT NULL,
    department VARCHAR NOT NULL,
    city TEXT,
    population_center TEXT,
    location_entity TEXT,
    population_id INTEGER NOT NULL REFERENCES population(id)
);
CREATE INDEX ix_intervention_population_id ON intervention_population (id);

-- CHARACTERISTICS POPULATION
CREATE TABLE characteristics_population (
    id SERIAL PRIMARY KEY,
    classification TEXT NOT NULL,
    detail VARCHAR NOT NULL,
    people_number INTEGER NOT NULL,
    information TEXT,
    population_id INTEGER NOT NULL REFERENCES population(id)
);
CREATE INDEX ix_characteristics_population_id ON characteristics_population (id);

-- ALTERNATIVES GENERAL
CREATE TABLE alternatives_general (
    id SERIAL PRIMARY KEY,
    solution_alternatives BOOLEAN NOT NULL DEFAULT FALSE,
    cost BOOLEAN NOT NULL DEFAULT FALSE,
    profitability BOOLEAN NOT NULL DEFAULT FALSE,
    project_id INTEGER NOT NULL UNIQUE REFERENCES projects(id)
);
CREATE INDEX ix_alternatives_general_id ON alternatives_general (id);

-- ALTERNATIVES
CREATE TABLE alternatives (
    id SERIAL PRIMARY KEY,
    name TEXT,
    active BOOLEAN NOT NULL DEFAULT FALSE,
    state TEXT,
    alternative_id INTEGER REFERENCES alternatives_general(id)
);
CREATE INDEX ix_alternatives_id ON alternatives (id);

-- TECHNICAL ANALYSIS
CREATE TABLE technical_analysis (
    id SERIAL PRIMARY KEY,
    analysis TEXT,
    project_id INTEGER NOT NULL UNIQUE REFERENCES projects(id)
);
CREATE INDEX ix_technical_analysis_id ON technical_analysis (id);

-- LOCALIZATION GENERAL
CREATE TABLE localization_general (
    id SERIAL PRIMARY KEY,
    administrative_political_factors BOOLEAN DEFAULT FALSE,
    proximity_to_target_population BOOLEAN DEFAULT FALSE,
    proximity_to_supply_sources BOOLEAN DEFAULT FALSE,
    communications BOOLEAN DEFAULT FALSE,
    land_cost_and_availability BOOLEAN DEFAULT FALSE,
    public_services_availability BOOLEAN DEFAULT FALSE,
    labor_availability_and_cost BOOLEAN DEFAULT FALSE,
    tax_and_legal_structure BOOLEAN DEFAULT FALSE,
    environmental_factors BOOLEAN DEFAULT FALSE,
    gender_equity_impact BOOLEAN DEFAULT FALSE,
    transport_means_and_costs BOOLEAN DEFAULT FALSE,
    public_order BOOLEAN DEFAULT FALSE,
    other_factors BOOLEAN DEFAULT FALSE,
    topography BOOLEAN DEFAULT FALSE,
    project_id INTEGER NOT NULL UNIQUE REFERENCES projects(id)
);
CREATE INDEX ix_localization_general_id ON localization_general (id);

-- LOCALIZATION
CREATE TABLE localization (
    id SERIAL PRIMARY KEY,
    region TEXT,
    department TEXT,
    city TEXT,
    type_group TEXT,
    "group" TEXT,
    entity TEXT,
    georeferencing BOOLEAN DEFAULT TRUE,
    latitude FLOAT,
    longitude FLOAT,
    localization_general_id INTEGER NOT NULL REFERENCES localization_general(id)
);

-- REQUIREMENTS GENERAL
CREATE TABLE requirements_general (
    id SERIAL PRIMARY KEY,
    requirements_analysis TEXT,
    project_id INTEGER NOT NULL UNIQUE REFERENCES projects(id)
);
CREATE INDEX ix_requirements_general_id ON requirements_general (id);

-- REQUIREMENTS
CREATE TABLE requirements (
    id SERIAL PRIMARY KEY,
    good_service_name TEXT,
    good_service_description TEXT,
    supply_description TEXT,
    demand_description TEXT,
    unit_of_measure TEXT,
    start_year INTEGER,
    end_year INTEGER,
    last_projected_year INTEGER,
    requirements_general_id INTEGER NOT NULL REFERENCES requirements_general(id)
);

-- PRODUCTS
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    value_chain_objective_id INTEGER NOT NULL REFERENCES value_chain_objectives(id),
    measured_through VARCHAR,
    quantity FLOAT,
    cost FLOAT,
    stage VARCHAR,
    description TEXT
);
CREATE INDEX ix_products_id ON products (id);

-- ACTIVITIES
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    cost FLOAT,
    stage VARCHAR,
    description TEXT
);
CREATE INDEX ix_activities_id ON activities (id);

-- DEVELOPMENT PLANS
CREATE TABLE development_plans (
    id SERIAL PRIMARY KEY,
    program VARCHAR,
    national_development_plan VARCHAR,
    departmental_or_sectoral_development_plan VARCHAR,
    strategy_departmental VARCHAR,
    program_departmental VARCHAR,
    district_or_municipal_development_plan VARCHAR,
    strategy_district VARCHAR,
    program_district VARCHAR,
    community_type VARCHAR,
    ethnic_group_planning_instruments VARCHAR,
    other_development_plan VARCHAR,
    strategy_other VARCHAR,
    program_other VARCHAR,
    project_id INTEGER NOT NULL UNIQUE REFERENCES projects(id)
);
CREATE INDEX ix_development_plans_id ON development_plans (id);

-- PNDS
CREATE TABLE pnds (
    id SERIAL PRIMARY KEY,
    transformation VARCHAR,
    pillar VARCHAR,
    catalyst VARCHAR,
    component VARCHAR,
    development_plan_id INTEGER NOT NULL REFERENCES development_plans(id)
);
CREATE INDEX ix_pnds_id ON pnds (id);

-- PRODUCT CATALOGS
CREATE TABLE product_catalogs (
    id SERIAL PRIMARY KEY,
    sector_code INTEGER,
    sector_name VARCHAR,
    program_code INTEGER,
    program_name VARCHAR,
    product_code INTEGER,
    product_name VARCHAR,
    description TEXT,
    measured_through VARCHAR,
    indicator_code INTEGER,
    product_indicator VARCHAR,
    measurement_unit VARCHAR,
    main_indicator VARCHAR,
    is_national VARCHAR,
    is_territorial VARCHAR,
    selected_to_project BOOLEAN
);
CREATE INDEX ix_product_catalogs_id ON product_catalogs (id);

-- ============================================================
-- PASO 3: RESETEAR SECUENCIAS DE IDS
-- ============================================================
-- (No es necesario porque usamos IDs explícitos, pero las secuencias
--  se actualizan al final para que los próximos INSERT autoincrementen bien)

-- ============================================================
-- PASO 4: INSERTAR DATOS DE EJEMPLO
-- ============================================================

-- ============================================================
-- 1. PROYECTO
-- ============================================================
INSERT INTO projects (id, name, description, process, object_desc, intervention_type, project_typology, main_product, sector, indicator_code)
VALUES (
    1,
    'Mejoramiento de la infraestructura educativa en Soacha',
    'Proyecto orientado a mejorar las condiciones físicas de las instituciones educativas del municipio de Soacha para garantizar ambientes de aprendizaje adecuados.',
    'Inversión',
    'Mejorar la infraestructura física de 5 instituciones educativas oficiales del municipio de Soacha, Cundinamarca, incluyendo aulas, laboratorios y espacios deportivos.',
    'Mejoramiento',
    'Proyecto de inversión',
    'Infraestructura educativa mejorada',
    'Educación',
    'EDU-001'
);

-- ============================================================
-- 2. LOCALIZACIÓN DEL PROYECTO
-- ============================================================
INSERT INTO project_localizations (id, project_id, region, department, municipality)
VALUES
    (1, 1, 'Centro Oriente', 'Cundinamarca', 'Soacha');

-- ============================================================
-- 3. ENCUESTA (Survey)
-- ============================================================
INSERT INTO survey (id, project_id, survey_json)
VALUES (
    1, 1,
    '{"respuesta_1": "Mejorar infraestructura educativa", "respuesta_2": "Municipio de Soacha", "respuesta_3": "Estudiantes de educación básica y media", "respuesta_4": "Condiciones deficientes de aulas y laboratorios"}'::json
);

-- ============================================================
-- 4. ANÁLISIS DE PARTICIPANTES
-- ============================================================
INSERT INTO participants_general (id, project_id, participants_analisis, participants_json)
VALUES (
    1, 1,
    'Se identificaron los actores clave del proyecto incluyendo la comunidad educativa, autoridades locales y entidades de cooperación. Cada actor tiene un rol definido en la formulación, ejecución y seguimiento del proyecto.',
    '{"total_participantes": 5, "tipo": "multiactor"}'::json
);

INSERT INTO participants (id, participants_general_id, participant_actor, participant_entity, interest_expectative, rol, contribution_conflicts)
VALUES
    (1, 1, 'Estudiantes', 'Instituciones Educativas de Soacha', 'Contar con espacios adecuados para el aprendizaje y la recreación', 'Beneficiario', 'Alta expectativa por mejoras. Posible resistencia temporal durante obras.'),
    (2, 1, 'Docentes', 'Secretaría de Educación de Cundinamarca', 'Mejorar condiciones laborales y pedagógicas', 'Beneficiario / Cooperante', 'Interés en participar en el diseño de espacios. Posibles diferencias en prioridades.'),
    (3, 1, 'Alcaldía Municipal de Soacha', 'Alcaldía de Soacha', 'Cumplir metas del Plan de Desarrollo Municipal en educación', 'Ejecutor', 'Disponibilidad presupuestal limitada. Compromiso político con el proyecto.'),
    (4, 1, 'Padres de familia', 'Asociaciones de padres', 'Garantizar seguridad y calidad educativa para sus hijos', 'Cooperante', 'Apoyo al proyecto. Posible preocupación por tiempos de ejecución.'),
    (5, 1, 'Ministerio de Educación Nacional', 'MEN', 'Mejorar indicadores de cobertura y calidad educativa', 'Financiador / Cooperante', 'Interés en alineación con política nacional. Requiere cumplimiento de estándares.');

-- ============================================================
-- 5. IDENTIFICACIÓN DEL PROBLEMA
-- ============================================================
INSERT INTO problems (id, project_id, central_problem, current_description, magnitude_problem, problem_tree_json)
VALUES (
    1, 1,
    'Deficientes condiciones de infraestructura física en las instituciones educativas oficiales del municipio de Soacha',
    'Actualmente, las 5 instituciones educativas priorizadas presentan deterioro en techos, paredes, pisos, instalaciones eléctricas e hidráulicas. Los laboratorios carecen de equipamiento adecuado y los espacios deportivos están en mal estado. Esto afecta a aproximadamente 8,500 estudiantes.',
    'El 70% de las aulas presentan filtraciones en techos. El 60% de los laboratorios no cuentan con equipamiento funcional. Solo el 30% de las áreas deportivas están en condiciones de uso. El índice de deserción escolar asociado a infraestructura es del 8.5%.',
    '{"nodos": {"problema_central": "Deficientes condiciones de infraestructura", "causas_directas": ["Falta de mantenimiento", "Insuficiente inversión"], "efectos_directos": ["Bajo rendimiento académico", "Alta deserción escolar"]}}'::json
);

-- 5.1 Causas Directas
INSERT INTO direct_causes (id, problem_id, description)
VALUES
    (1, 1, 'Falta de mantenimiento preventivo y correctivo en las instituciones educativas'),
    (2, 1, 'Insuficiente inversión en infraestructura educativa por parte del municipio');

-- 5.2 Causas Indirectas
INSERT INTO indirect_causes (id, direct_cause_id, description)
VALUES
    (1, 1, 'Ausencia de un plan de mantenimiento institucional con presupuesto asignado'),
    (2, 1, 'Falta de personal técnico capacitado para labores de mantenimiento'),
    (3, 2, 'Baja priorización de la inversión educativa en los planes de desarrollo anteriores'),
    (4, 2, 'Limitada gestión de recursos ante entidades del orden nacional y departamental');

-- 5.3 Efectos Directos
INSERT INTO direct_effects (id, problem_id, description)
VALUES
    (1, 1, 'Bajo rendimiento académico de los estudiantes por ambientes inadecuados'),
    (2, 1, 'Alta tasa de deserción escolar asociada a condiciones físicas deficientes');

-- 5.4 Efectos Indirectos
INSERT INTO indirect_effects (id, direct_effect_id, description)
VALUES
    (1, 1, 'Menores oportunidades de acceso a educación superior para los egresados'),
    (2, 1, 'Disminución del bienestar y la motivación del cuerpo docente'),
    (3, 2, 'Incremento de población joven sin formación expuesta a riesgos sociales'),
    (4, 2, 'Mayor brecha educativa entre Soacha y otros municipios de Cundinamarca');

-- ============================================================
-- 6. OBJETIVOS
-- ============================================================
INSERT INTO objectives (id, project_id, general_problem, general_objective)
VALUES (
    1, 1,
    'Deficientes condiciones de infraestructura física en las instituciones educativas oficiales del municipio de Soacha',
    'Mejorar las condiciones de infraestructura física en 5 instituciones educativas oficiales del municipio de Soacha para garantizar ambientes de aprendizaje adecuados'
);

-- 6.1 Cadena de Valor
INSERT INTO value_chains (id, project_id, name)
VALUES (1, 1, 'Cadena de valor - Infraestructura educativa Soacha');

-- 6.2 Objetivos de la Cadena de Valor
INSERT INTO value_chain_objectives (id, project_id, value_chain_id, name)
VALUES
    (1, 1, 1, 'Rehabilitar aulas y espacios pedagógicos'),
    (2, 1, 1, 'Dotar laboratorios con equipamiento funcional'),
    (3, 1, 1, 'Recuperar espacios deportivos y recreativos');

-- 6.3 Causas de Objetivos (vinculan causas con objetivos específicos)
INSERT INTO objectives_causes (id, objective_id, type, cause_related, specifics_objectives, cause_id, value_chain_objective_id)
VALUES
    (1, 1, 'directa', 'Falta de mantenimiento preventivo y correctivo en las instituciones educativas', 'Implementar un programa de rehabilitación y mantenimiento de aulas y espacios pedagógicos', 1, 1),
    (2, 1, 'directa', 'Insuficiente inversión en infraestructura educativa por parte del municipio', 'Dotar y equipar laboratorios escolares con equipamiento funcional y moderno', 2, 2),
    (3, 1, 'indirecta', 'Ausencia de un plan de mantenimiento institucional con presupuesto asignado', 'Recuperar y adecuar los espacios deportivos y recreativos de las instituciones', 1, 3),
    (4, 1, 'indirecta', 'Baja priorización de la inversión educativa en los planes de desarrollo anteriores', 'Fortalecer la gestión de recursos para infraestructura educativa', 3, NULL);

-- 6.4 Indicadores de Objetivos
INSERT INTO objectives_indicator (id, objective_id, indicator, unit, meta, source_type, source_validation)
VALUES
    (1, 1, 'Porcentaje de aulas en buen estado', 'Porcentaje', 90.0, 'Informe técnico', 'Interventoría del proyecto'),
    (2, 1, 'Número de laboratorios equipados', 'Unidad', 10.0, 'Inventario', 'Acta de entrega de equipos'),
    (3, 1, 'Tasa de deserción escolar por infraestructura', 'Porcentaje', 3.0, 'SIMAT', 'Reporte anual Secretaría de Educación');

-- ============================================================
-- 7. POBLACIÓN
-- ============================================================
INSERT INTO population (id, project_id, population_type_affected, number_affected, source_information_affected, population_type_intervention, number_intervention, source_information_intervention, population_json)
VALUES (
    1, 1,
    'Población escolar del municipio de Soacha',
    45000,
    'Secretaría de Educación de Cundinamarca - Matrícula 2025',
    'Estudiantes de las 5 instituciones educativas priorizadas',
    8500,
    'Censo institucional 2025 - Secretaría de Educación Municipal',
    '{"grupos_etarios": {"6-10": 3200, "11-14": 3100, "15-17": 2200}, "genero": {"masculino": 4300, "femenino": 4200}}'::json
);

-- 7.1 Población Afectada (ubicación)
INSERT INTO affected_population (id, population_id, region, department, city, population_center, location_entity)
VALUES
    (1, 1, 'Centro Oriente', 'Cundinamarca', 'Soacha', 'Comuna 1 - Compartir', 'I.E. Compartir'),
    (2, 1, 'Centro Oriente', 'Cundinamarca', 'Soacha', 'Comuna 3 - Despensa', 'I.E. La Despensa'),
    (3, 1, 'Centro Oriente', 'Cundinamarca', 'Soacha', 'Comuna 4 - Cazucá', 'I.E. Ciudadela Sucre');

-- 7.2 Población de Intervención (ubicación)
INSERT INTO intervention_population (id, population_id, region, department, city, population_center, location_entity)
VALUES
    (1, 1, 'Centro Oriente', 'Cundinamarca', 'Soacha', 'Comuna 1 - Compartir', 'I.E. Compartir'),
    (2, 1, 'Centro Oriente', 'Cundinamarca', 'Soacha', 'Comuna 3 - Despensa', 'I.E. La Despensa'),
    (3, 1, 'Centro Oriente', 'Cundinamarca', 'Soacha', 'Comuna 4 - Cazucá', 'I.E. Ciudadela Sucre');



-- ============================================================
-- 8. ANÁLISIS DE ALTERNATIVAS
-- ============================================================
INSERT INTO alternatives_general (id, project_id, solution_alternatives, cost, profitability)
VALUES (1, 1, TRUE, TRUE, TRUE);

INSERT INTO alternatives (id, alternative_id, name, active, state)
VALUES
    (1, 1, 'Alternativa 1: Rehabilitación integral de las 5 instituciones educativas con obras civiles, dotación de laboratorios y recuperación de espacios deportivos', TRUE, 'seleccionada'),
    (2, 1, 'Alternativa 2: Construcción de una nueva mega-institución educativa centralizada para reemplazar las 5 existentes', FALSE, 'descartada'),
    (3, 1, 'Alternativa 3: Rehabilitación parcial (solo aulas) y arrendamiento de espacios externos para laboratorios y deportes', FALSE, 'descartada');

-- ============================================================
-- 9. ANÁLISIS TÉCNICO
-- ============================================================
INSERT INTO technical_analysis (id, project_id, analysis)
VALUES (
    1, 1,
    'El análisis técnico determina que la alternativa seleccionada (rehabilitación integral) es viable considerando: 1) Las estructuras existentes son recuperables según diagnóstico de ingeniería estructural. 2) Los costos de rehabilitación representan el 40% del costo de construcción nueva. 3) Se mantiene la cobertura geográfica actual sin desplazar estudiantes. 4) El plazo de ejecución estimado es de 18 meses con intervención simultánea en las 5 instituciones. 5) Se requiere reubicación temporal de estudiantes durante las obras, con plan de contingencia definido.'
);

-- ============================================================
-- 10. LOCALIZACIÓN (Factores y sitios)
-- ============================================================
INSERT INTO localization_general (id, project_id, administrative_political_factors, proximity_to_target_population, proximity_to_supply_sources, communications, land_cost_and_availability, public_services_availability, labor_availability_and_cost, tax_and_legal_structure, environmental_factors, gender_equity_impact, transport_means_and_costs, public_order, other_factors, topography)
VALUES (
    1, 1,
    TRUE,   -- administrative_political_factors
    TRUE,   -- proximity_to_target_population
    TRUE,   -- proximity_to_supply_sources
    TRUE,   -- communications
    FALSE,  -- land_cost_and_availability (terrenos existentes)
    TRUE,   -- public_services_availability
    TRUE,   -- labor_availability_and_cost
    FALSE,  -- tax_and_legal_structure
    TRUE,   -- environmental_factors
    TRUE,   -- gender_equity_impact
    TRUE,   -- transport_means_and_costs
    TRUE,   -- public_order
    FALSE,  -- other_factors
    TRUE    -- topography
);

INSERT INTO localization (id, localization_general_id, region, department, city, type_group, "group", entity, georeferencing, latitude, longitude)
VALUES
    (1, 1, 'Centro Oriente', 'Cundinamarca', 'Soacha', 'Urbano', 'Comuna 1', 'I.E. Compartir', TRUE, 4.5796, -74.2167),
    (2, 1, 'Centro Oriente', 'Cundinamarca', 'Soacha', 'Urbano', 'Comuna 3', 'I.E. La Despensa', TRUE, 4.5854, -74.2089),
    (3, 1, 'Centro Oriente', 'Cundinamarca', 'Soacha', 'Urbano', 'Comuna 4', 'I.E. Ciudadela Sucre', TRUE, 4.5712, -74.1998);

-- ============================================================
-- 11. ESTUDIO DE NECESIDADES (Requirements)
-- ============================================================
INSERT INTO requirements_general (id, project_id, requirements_analysis)
VALUES (
    1, 1,
    'Se identificaron las necesidades de bienes y servicios requeridos para la rehabilitación integral de las 5 instituciones educativas. Se analizó la oferta disponible en la región y la demanda proyectada para los próximos 10 años considerando el crecimiento poblacional del municipio.'
);

INSERT INTO requirements (id, requirements_general_id, good_service_name, good_service_description, supply_description, demand_description, unit_of_measure, start_year, end_year, last_projected_year)
VALUES
    (1, 1, 'Aulas rehabilitadas', 'Rehabilitación integral de aulas incluyendo pisos, paredes, techos, instalaciones eléctricas e iluminación', 'Actualmente 120 aulas, de las cuales 84 (70%) presentan deterioro significativo', 'Se requieren 120 aulas en óptimas condiciones para atender 8,500 estudiantes', 'Unidad', 2026, 2027, 2036),
    (2, 1, 'Laboratorios equipados', 'Dotación y equipamiento de laboratorios de ciencias, informática e idiomas', 'Existen 15 laboratorios de los cuales 9 (60%) no son funcionales', 'Se requieren 15 laboratorios plenamente funcionales', 'Unidad', 2026, 2027, 2036),
    (3, 1, 'Espacios deportivos recuperados', 'Recuperación de canchas, gimnasios y áreas recreativas', 'Existen 10 espacios deportivos, solo 3 (30%) están en condiciones de uso', 'Se requieren 10 espacios deportivos en buen estado', 'Unidad', 2026, 2027, 2036);

-- ============================================================
-- 12. PRODUCTOS Y ACTIVIDADES (Cadena de Valor)
-- ============================================================
-- Productos vinculados a objetivos de cadena de valor
INSERT INTO products (id, project_id, value_chain_objective_id, measured_through, quantity, cost, stage, description)
VALUES
    (1, 1, 1, 'Número de aulas rehabilitadas', 84, 2520000000, 'Inversión', 'Rehabilitación integral de 84 aulas en las 5 instituciones educativas priorizadas'),
    (2, 1, 2, 'Número de laboratorios equipados', 9, 900000000, 'Inversión', 'Dotación y equipamiento de 9 laboratorios (ciencias, informática e idiomas)'),
    (3, 1, 3, 'Número de espacios deportivos recuperados', 7, 1050000000, 'Inversión', 'Recuperación de 7 espacios deportivos y recreativos');

-- Actividades por producto
INSERT INTO activities (id, project_id, product_id, cost, stage, description)
VALUES
    -- Actividades del Producto 1 (Aulas)
    (1, 1, 1, 500000000, 'Preinversión', 'Elaboración de estudios y diseños arquitectónicos y estructurales'),
    (2, 1, 1, 1800000000, 'Inversión', 'Ejecución de obras civiles de rehabilitación de aulas'),
    (3, 1, 1, 220000000, 'Inversión', 'Interventoría técnica, administrativa y financiera de obras de aulas'),
    -- Actividades del Producto 2 (Laboratorios)
    (4, 1, 2, 150000000, 'Preinversión', 'Diseño técnico de laboratorios y especificaciones de equipamiento'),
    (5, 1, 2, 600000000, 'Inversión', 'Adquisición e instalación de equipos de laboratorio'),
    (6, 1, 2, 150000000, 'Inversión', 'Adecuación física de espacios para laboratorios'),
    -- Actividades del Producto 3 (Espacios deportivos)
    (7, 1, 3, 200000000, 'Preinversión', 'Estudios técnicos y diseños de espacios deportivos'),
    (8, 1, 3, 750000000, 'Inversión', 'Ejecución de obras de recuperación de espacios deportivos'),
    (9, 1, 3, 100000000, 'Inversión', 'Interventoría de obras de espacios deportivos');

-- ============================================================
-- 13. PLANES DE DESARROLLO
-- ============================================================
INSERT INTO development_plans (id, project_id, program, national_development_plan, departmental_or_sectoral_development_plan, strategy_departmental, program_departmental, district_or_municipal_development_plan, strategy_district, program_district, community_type, ethnic_group_planning_instruments, other_development_plan, strategy_other, program_other)
VALUES (
    1, 1,
    'Educación de calidad para un futuro con oportunidades',
    'Plan Nacional de Desarrollo 2022-2026: Colombia Potencia Mundial de la Vida',
    'Plan Departamental de Desarrollo de Cundinamarca 2024-2027',
    'Cundinamarca educada y con oportunidades',
    'Mejoramiento de infraestructura educativa departamental',
    'Plan de Desarrollo Municipal de Soacha 2024-2027',
    'Soacha educada, incluyente y competitiva',
    'Infraestructura para la educación de calidad',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL
);

INSERT INTO pnds (id, development_plan_id, transformation, pillar, catalyst, component)
VALUES
    (1, 1, 'Transformación 3: Derecho humano a la alimentación', 'Pilar: Seguridad humana y justicia social', 'Educación de calidad', 'Infraestructura educativa'),
    (2, 1, 'Transformación 5: Convergencia regional', 'Pilar: Ordenamiento del territorio alrededor del agua', 'Infraestructura y equipamientos', 'Equipamientos educativos territoriales');

-- ============================================================
-- VERIFICACIÓN: Consultas para validar la inserción
-- ============================================================

-- Descomentar las siguientes líneas para verificar:

-- SELECT 'projects' AS tabla, COUNT(*) FROM projects WHERE id = 1
-- UNION ALL SELECT 'problems', COUNT(*) FROM problems WHERE project_id = 1
-- UNION ALL SELECT 'direct_causes', COUNT(*) FROM direct_causes WHERE problem_id = 1
-- UNION ALL SELECT 'indirect_causes', COUNT(*) FROM indirect_causes
-- UNION ALL SELECT 'direct_effects', COUNT(*) FROM direct_effects WHERE problem_id = 1
-- UNION ALL SELECT 'indirect_effects', COUNT(*) FROM indirect_effects
-- UNION ALL SELECT 'objectives', COUNT(*) FROM objectives WHERE project_id = 1
-- UNION ALL SELECT 'objectives_causes', COUNT(*) FROM objectives_causes WHERE objective_id = 1
-- UNION ALL SELECT 'objectives_indicator', COUNT(*) FROM objectives_indicator WHERE objective_id = 1
-- UNION ALL SELECT 'participants_general', COUNT(*) FROM participants_general WHERE project_id = 1
-- UNION ALL SELECT 'participants', COUNT(*) FROM participants
-- UNION ALL SELECT 'population', COUNT(*) FROM population WHERE project_id = 1
-- UNION ALL SELECT 'affected_population', COUNT(*) FROM affected_population
-- UNION ALL SELECT 'intervention_population', COUNT(*) FROM intervention_population
-- UNION ALL SELECT 'characteristics_population', COUNT(*) FROM characteristics_population
-- UNION ALL SELECT 'alternatives_general', COUNT(*) FROM alternatives_general WHERE project_id = 1
-- UNION ALL SELECT 'alternatives', COUNT(*) FROM alternatives
-- UNION ALL SELECT 'technical_analysis', COUNT(*) FROM technical_analysis WHERE project_id = 1
-- UNION ALL SELECT 'localization_general', COUNT(*) FROM localization_general WHERE project_id = 1
-- UNION ALL SELECT 'localization', COUNT(*) FROM localization
-- UNION ALL SELECT 'requirements_general', COUNT(*) FROM requirements_general WHERE project_id = 1
-- UNION ALL SELECT 'requirements', COUNT(*) FROM requirements
-- UNION ALL SELECT 'value_chains', COUNT(*) FROM value_chains WHERE project_id = 1
-- UNION ALL SELECT 'value_chain_objectives', COUNT(*) FROM value_chain_objectives WHERE project_id = 1
-- UNION ALL SELECT 'products', COUNT(*) FROM products WHERE project_id = 1
-- UNION ALL SELECT 'activities', COUNT(*) FROM activities WHERE project_id = 1
-- UNION ALL SELECT 'development_plans', COUNT(*) FROM development_plans WHERE project_id = 1
-- UNION ALL SELECT 'pnds', COUNT(*) FROM pnds
-- UNION ALL SELECT 'survey', COUNT(*) FROM survey WHERE project_id = 1
-- UNION ALL SELECT 'project_localizations', COUNT(*) FROM project_localizations WHERE project_id = 1;


-- ############################################################
-- ############################################################
-- PROYECTO 2: SALUD - Red hospitalaria de primer nivel
--             en el Bajo Cauca Antioqueño
-- ############################################################
-- ############################################################

-- ============================================================
-- 1. PROYECTO
-- ============================================================
INSERT INTO projects (id, name, description, process, object_desc, intervention_type, project_typology, main_product, sector, indicator_code)
VALUES (
    2,
    'Fortalecimiento de la red hospitalaria de primer nivel en el Bajo Cauca Antioqueño',
    'Proyecto para fortalecer la capacidad instalada de atención en salud de primer nivel en 3 municipios del Bajo Cauca Antioqueño mediante la dotación de equipos biomédicos, adecuación de infraestructura y formación de talento humano.',
    'Inversión',
    'Fortalecer la red hospitalaria de primer nivel en los municipios de Caucasia, Nechí y El Bagre mediante dotación de equipos, adecuación de infraestructura y capacitación del personal de salud.',
    'Dotación',
    'Proyecto de inversión',
    'Servicios de salud de primer nivel fortalecidos',
    'Salud y Protección Social',
    'SAL-002'
);

-- ============================================================
-- 2. LOCALIZACIÓN DEL PROYECTO
-- ============================================================
INSERT INTO project_localizations (id, project_id, region, department, municipality)
VALUES
    (2, 2, 'Caribe', 'Antioquia', 'Caucasia'),
    (3, 2, 'Caribe', 'Antioquia', 'Nechí'),
    (4, 2, 'Caribe', 'Antioquia', 'El Bagre');

-- ============================================================
-- 3. ENCUESTA (Survey)
-- ============================================================
INSERT INTO survey (id, project_id, survey_json)
VALUES (
    2, 2,
    '{"respuesta_1": "Fortalecer la red hospitalaria de primer nivel", "respuesta_2": "Bajo Cauca Antioqueño", "respuesta_3": "Población rural y urbana de Caucasia, Nechí y El Bagre", "respuesta_4": "Baja capacidad resolutiva de los hospitales de primer nivel"}'::json
);

-- ============================================================
-- 4. ANÁLISIS DE PARTICIPANTES
-- ============================================================
INSERT INTO participants_general (id, project_id, participants_analisis, participants_json)
VALUES (
    2, 2,
    'Se identificaron los actores principales del sector salud en la subregión del Bajo Cauca, incluyendo las ESE hospitalarias, la Secretaría Seccional de Salud de Antioquia, EPS del régimen subsidiado y la comunidad.',
    '{"total_participantes": 4, "tipo": "institucional"}'::json
);

INSERT INTO participants (id, participants_general_id, participant_actor, participant_entity, interest_expectative, rol, contribution_conflicts)
VALUES
    (6, 2, 'Hospitales locales (ESE)', 'E.S.E. Hospital César Uribe Piedrahíta, E.S.E. Hospital San Bartolomé, E.S.E. Hospital Nuestra Señora del Carmen', 'Mejorar la capacidad resolutiva y reducir remisiones a segundo nivel', 'Ejecutor / Beneficiario', 'Alta disposición. Limitaciones en talento humano especializado.'),
    (7, 2, 'Secretaría Seccional de Salud de Antioquia', 'Gobernación de Antioquia', 'Reducir brechas de acceso a salud en la subregión', 'Financiador / Cooperante', 'Interés en cumplimiento de indicadores de salud pública. Posibles demoras en desembolsos.'),
    (8, 2, 'EPS del régimen subsidiado', 'Nueva EPS, Savia Salud', 'Garantizar la prestación de servicios a sus afiliados', 'Cooperante', 'Interés en reducir costos de remisión. Tensión por cartera pendiente con ESE.'),
    (9, 2, 'Comunidad y líderes sociales', 'Juntas de Acción Comunal, veedurías ciudadanas', 'Acceder a servicios de salud oportunos y de calidad sin desplazarse', 'Beneficiario / Veedor', 'Fuerte apoyo comunitario. Exigencia de transparencia en la ejecución.');

-- ============================================================
-- 5. IDENTIFICACIÓN DEL PROBLEMA
-- ============================================================
INSERT INTO problems (id, project_id, central_problem, current_description, magnitude_problem, problem_tree_json)
VALUES (
    2, 2,
    'Baja capacidad resolutiva de la red hospitalaria de primer nivel en el Bajo Cauca Antioqueño',
    'Los hospitales de primer nivel de Caucasia, Nechí y El Bagre presentan equipos biomédicos obsoletos, infraestructura deteriorada y déficit de personal capacitado. Esto genera altas tasas de remisión a segundo y tercer nivel (Medellín y Montería), con costos adicionales para el sistema y riesgo para los pacientes.',
    'La tasa de remisión a segundo nivel es del 35%, frente al promedio departamental del 18%. El 50% de los equipos biomédicos tienen más de 15 años de uso. Solo el 40% de las camas hospitalarias cumplen con estándares de habilitación. El tiempo promedio de traslado a Medellín es de 6 horas.',
    '{"nodos": {"problema_central": "Baja capacidad resolutiva de hospitales de primer nivel", "causas_directas": ["Equipos biomédicos obsoletos", "Infraestructura deteriorada"], "efectos_directos": ["Alta tasa de remisiones", "Mortalidad evitable"]}}'::json
);

-- 5.1 Causas Directas
INSERT INTO direct_causes (id, problem_id, description)
VALUES
    (3, 2, 'Equipos biomédicos obsoletos e insuficientes en los tres hospitales'),
    (4, 2, 'Infraestructura hospitalaria deteriorada que no cumple estándares de habilitación');

-- 5.2 Causas Indirectas
INSERT INTO indirect_causes (id, direct_cause_id, description)
VALUES
    (5, 3, 'Ausencia de planes de reposición y mantenimiento de equipos biomédicos'),
    (6, 3, 'Limitada asignación presupuestal del SGP para dotación hospitalaria'),
    (7, 4, 'Falta de inversión en mantenimiento de infraestructura desde hace más de 10 años'),
    (8, 4, 'Deficiente gestión de proyectos ante el Sistema General de Regalías');

-- 5.3 Efectos Directos
INSERT INTO direct_effects (id, problem_id, description)
VALUES
    (3, 2, 'Alta tasa de remisión de pacientes a hospitales de segundo y tercer nivel'),
    (4, 2, 'Incremento de la mortalidad evitable por falta de atención oportuna');

-- 5.4 Efectos Indirectos
INSERT INTO indirect_effects (id, direct_effect_id, description)
VALUES
    (5, 3, 'Altos costos de transporte y estancia para pacientes y familias'),
    (6, 3, 'Sobrecarga de los hospitales de referencia en Medellín y Montería'),
    (7, 4, 'Deterioro de los indicadores de salud pública de la subregión'),
    (8, 4, 'Pérdida de confianza de la comunidad en el sistema de salud local');

-- ============================================================
-- 6. OBJETIVOS
-- ============================================================
INSERT INTO objectives (id, project_id, general_problem, general_objective)
VALUES (
    2, 2,
    'Baja capacidad resolutiva de la red hospitalaria de primer nivel en el Bajo Cauca Antioqueño',
    'Fortalecer la capacidad resolutiva de la red hospitalaria de primer nivel en Caucasia, Nechí y El Bagre para reducir las remisiones y mejorar la atención en salud'
);

INSERT INTO value_chains (id, project_id, name)
VALUES (2, 2, 'Cadena de valor - Fortalecimiento red hospitalaria Bajo Cauca');

INSERT INTO value_chain_objectives (id, project_id, value_chain_id, name)
VALUES
    (4, 2, 2, 'Dotar hospitales con equipos biomédicos modernos'),
    (5, 2, 2, 'Adecuar infraestructura hospitalaria según estándares'),
    (6, 2, 2, 'Capacitar al talento humano en salud');

INSERT INTO objectives_causes (id, objective_id, type, cause_related, specifics_objectives, cause_id, value_chain_objective_id)
VALUES
    (5, 2, 'directa', 'Equipos biomédicos obsoletos e insuficientes', 'Dotar a los tres hospitales con equipos biomédicos de última generación', 3, 4),
    (6, 2, 'directa', 'Infraestructura hospitalaria deteriorada', 'Adecuar la infraestructura hospitalaria cumpliendo estándares de habilitación', 4, 5),
    (7, 2, 'indirecta', 'Ausencia de planes de reposición y mantenimiento', 'Implementar programa de capacitación continua para el personal de salud', 5, 6),
    (8, 2, 'indirecta', 'Limitada asignación presupuestal para dotación hospitalaria', 'Fortalecer la gestión institucional para sostenibilidad del proyecto', 6, NULL);

INSERT INTO objectives_indicator (id, objective_id, indicator, unit, meta, source_type, source_validation)
VALUES
    (4, 2, 'Tasa de remisión a segundo nivel', 'Porcentaje', 18.0, 'REPS', 'Reporte trimestral Secretaría de Salud'),
    (5, 2, 'Porcentaje de equipos biomédicos en buen estado', 'Porcentaje', 95.0, 'Inventario hospitalario', 'Auditoría técnica anual'),
    (6, 2, 'Porcentaje de camas habilitadas', 'Porcentaje', 100.0, 'Sistema de habilitación', 'Visita de verificación Secretaría Seccional');

-- ============================================================
-- 7. POBLACIÓN
-- ============================================================
INSERT INTO population (id, project_id, population_type_affected, number_affected, source_information_affected, population_type_intervention, number_intervention, source_information_intervention, population_json)
VALUES (
    2, 2,
    'Población total de los 3 municipios del Bajo Cauca',
    185000,
    'DANE - Proyecciones de población 2025',
    'Población que acude a los hospitales de primer nivel',
    120000,
    'RIPS - Registro Individual de Prestación de Servicios 2025',
    '{"grupos_etarios": {"0-5": 18000, "6-17": 30000, "18-59": 55000, "60+": 17000}, "regimen": {"subsidiado": 95000, "contributivo": 15000, "no_afiliado": 10000}}'::json
);

INSERT INTO affected_population (id, population_id, region, department, city, population_center, location_entity)
VALUES
    (4, 2, 'Caribe', 'Antioquia', 'Caucasia', 'Cabecera municipal', 'E.S.E. Hospital César Uribe Piedrahíta'),
    (5, 2, 'Caribe', 'Antioquia', 'Nechí', 'Cabecera municipal', 'E.S.E. Hospital San Bartolomé'),
    (6, 2, 'Caribe', 'Antioquia', 'El Bagre', 'Cabecera municipal', 'E.S.E. Hospital Nuestra Señora del Carmen');

INSERT INTO intervention_population (id, population_id, region, department, city, population_center, location_entity)
VALUES
    (4, 2, 'Caribe', 'Antioquia', 'Caucasia', 'Cabecera municipal', 'E.S.E. Hospital César Uribe Piedrahíta'),
    (5, 2, 'Caribe', 'Antioquia', 'Nechí', 'Cabecera municipal', 'E.S.E. Hospital San Bartolomé'),
    (6, 2, 'Caribe', 'Antioquia', 'El Bagre', 'Cabecera municipal', 'E.S.E. Hospital Nuestra Señora del Carmen');


-- ============================================================
-- 8. ANÁLISIS DE ALTERNATIVAS
-- ============================================================
INSERT INTO alternatives_general (id, project_id, solution_alternatives, cost, profitability)
VALUES (2, 2, TRUE, TRUE, TRUE);

INSERT INTO alternatives (id, alternative_id, name, active, state)
VALUES
    (4, 2, 'Alternativa 1: Dotación integral de equipos biomédicos, adecuación de infraestructura y capacitación del personal en los 3 hospitales existentes', TRUE, 'seleccionada'),
    (5, 2, 'Alternativa 2: Construcción de un hospital subregional nuevo de segundo nivel en Caucasia', FALSE, 'descartada'),
    (6, 2, 'Alternativa 3: Convenio con hospitales privados para atención delegada de servicios deficitarios', FALSE, 'descartada');

-- ============================================================
-- 9. ANÁLISIS TÉCNICO
-- ============================================================
INSERT INTO technical_analysis (id, project_id, analysis)
VALUES (
    2, 2,
    'La alternativa seleccionada es técnicamente viable porque: 1) Los tres hospitales cuentan con infraestructura base que puede ser adecuada. 2) El mercado de equipos biomédicos tiene oferta nacional e internacional competitiva. 3) Se puede ejecutar en 12 meses con intervención simultánea en los 3 municipios. 4) Permite mantener la prestación del servicio durante la ejecución con plan de contingencia. 5) La capacitación fortalece la sostenibilidad del proyecto a largo plazo.'
);

-- ============================================================
-- 10. LOCALIZACIÓN
-- ============================================================
INSERT INTO localization_general (id, project_id, administrative_political_factors, proximity_to_target_population, proximity_to_supply_sources, communications, land_cost_and_availability, public_services_availability, labor_availability_and_cost, tax_and_legal_structure, environmental_factors, gender_equity_impact, transport_means_and_costs, public_order, other_factors, topography)
VALUES (
    2, 2, TRUE, TRUE, FALSE, TRUE, FALSE, TRUE, FALSE, FALSE, TRUE, TRUE, TRUE, TRUE, FALSE, FALSE
);

INSERT INTO localization (id, localization_general_id, region, department, city, type_group, "group", entity, georeferencing, latitude, longitude)
VALUES
    (4, 2, 'Caribe', 'Antioquia', 'Caucasia', 'Urbano', 'Cabecera', 'E.S.E. Hospital César Uribe Piedrahíta', TRUE, 7.9847, -75.1983),
    (5, 2, 'Caribe', 'Antioquia', 'Nechí', 'Urbano', 'Cabecera', 'E.S.E. Hospital San Bartolomé', TRUE, 8.0953, -74.7736),
    (6, 2, 'Caribe', 'Antioquia', 'El Bagre', 'Urbano', 'Cabecera', 'E.S.E. Hospital Nuestra Señora del Carmen', TRUE, 7.5967, -74.8069);

-- ============================================================
-- 11. ESTUDIO DE NECESIDADES (Requirements)
-- ============================================================
INSERT INTO requirements_general (id, project_id, requirements_analysis)
VALUES (
    2, 2,
    'Se evaluó la brecha entre la oferta actual de servicios de salud de primer nivel y la demanda real de la población. Se identificaron necesidades en dotación de equipos, adecuación de infraestructura y formación de personal.'
);

INSERT INTO requirements (id, requirements_general_id, good_service_name, good_service_description, supply_description, demand_description, unit_of_measure, start_year, end_year, last_projected_year)
VALUES
    (4, 2, 'Equipos biomédicos', 'Equipos de diagnóstico, laboratorio clínico, imagenología y urgencias', 'Actualmente el 50% de los equipos tienen más de 15 años y presentan fallas recurrentes', 'Se requiere la reposición de 45 equipos críticos en los 3 hospitales', 'Unidad', 2026, 2027, 2036),
    (5, 2, 'Infraestructura hospitalaria adecuada', 'Adecuación de áreas de urgencias, consulta externa y laboratorio', '3 hospitales con áreas que no cumplen estándares de habilitación', 'Se requiere adecuar 2,400 m² de infraestructura hospitalaria', 'Metro cuadrado', 2026, 2027, 2036),
    (6, 2, 'Personal de salud capacitado', 'Programas de formación en manejo de equipos y protocolos de atención', 'Solo el 30% del personal ha recibido actualización en los últimos 3 años', 'Se requiere capacitar a 150 profesionales de salud', 'Persona', 2026, 2027, 2036);

-- ============================================================
-- 12. PRODUCTOS Y ACTIVIDADES
-- ============================================================
INSERT INTO products (id, project_id, value_chain_objective_id, measured_through, quantity, cost, stage, description)
VALUES
    (4, 2, 4, 'Número de equipos biomédicos adquiridos e instalados', 45, 3500000000, 'Inversión', 'Adquisición e instalación de 45 equipos biomédicos para los 3 hospitales'),
    (5, 2, 5, 'Metros cuadrados de infraestructura adecuada', 2400, 1800000000, 'Inversión', 'Adecuación de 2,400 m² de infraestructura hospitalaria en 3 municipios'),
    (6, 2, 6, 'Número de profesionales capacitados', 150, 450000000, 'Inversión', 'Capacitación de 150 profesionales de salud en manejo de equipos y protocolos');

INSERT INTO activities (id, project_id, product_id, cost, stage, description)
VALUES
    (10, 2, 4, 400000000, 'Preinversión', 'Estudios de necesidades tecnológicas y especificaciones técnicas de equipos'),
    (11, 2, 4, 2800000000, 'Inversión', 'Proceso de adquisición, importación e instalación de equipos biomédicos'),
    (12, 2, 4, 300000000, 'Inversión', 'Interventoría técnica del proceso de dotación'),
    (13, 2, 5, 250000000, 'Preinversión', 'Elaboración de estudios y diseños de adecuación hospitalaria'),
    (14, 2, 5, 1350000000, 'Inversión', 'Ejecución de obras de adecuación en los 3 hospitales'),
    (15, 2, 5, 200000000, 'Inversión', 'Interventoría de obras de adecuación'),
    (16, 2, 6, 80000000, 'Preinversión', 'Diseño curricular y logístico del programa de capacitación'),
    (17, 2, 6, 320000000, 'Inversión', 'Ejecución del programa de capacitación (6 cohortes)'),
    (18, 2, 6, 50000000, 'Inversión', 'Seguimiento y evaluación del programa de formación');

-- ============================================================
-- 13. PLANES DE DESARROLLO
-- ============================================================
INSERT INTO development_plans (id, project_id, program, national_development_plan, departmental_or_sectoral_development_plan, strategy_departmental, program_departmental, district_or_municipal_development_plan, strategy_district, program_district, community_type, ethnic_group_planning_instruments, other_development_plan, strategy_other, program_other)
VALUES (
    2, 2,
    'Salud para la vida y el bienestar',
    'Plan Nacional de Desarrollo 2022-2026: Colombia Potencia Mundial de la Vida',
    'Plan Departamental de Desarrollo de Antioquia 2024-2027',
    'Antioquia saludable y protegida',
    'Fortalecimiento de la red pública hospitalaria',
    'Plan de Desarrollo Municipal de Caucasia 2024-2027',
    'Salud con equidad para el Bajo Cauca',
    'Mejoramiento de la infraestructura y dotación hospitalaria',
    NULL, NULL, NULL, NULL, NULL
);

INSERT INTO pnds (id, development_plan_id, transformation, pillar, catalyst, component)
VALUES
    (3, 2, 'Transformación 1: Ordenamiento del territorio alrededor del agua', 'Pilar: Seguridad humana y justicia social', 'Salud para la vida', 'Fortalecimiento de la red hospitalaria pública'),
    (4, 2, 'Transformación 5: Convergencia regional', 'Pilar: Seguridad humana y justicia social', 'Reducción de brechas territoriales', 'Acceso a servicios de salud en zonas rurales dispersas');


-- ############################################################
-- ############################################################
-- PROYECTO 3: AGUA Y SANEAMIENTO - Acueducto y alcantarillado
--             rural en Boyacá
-- ############################################################
-- ############################################################

-- ============================================================
-- 1. PROYECTO
-- ============================================================
INSERT INTO projects (id, name, description, process, object_desc, intervention_type, project_typology, main_product, sector, indicator_code)
VALUES (
    3,
    'Construcción del sistema de acueducto y alcantarillado para las veredas del municipio de Tinjacá, Boyacá',
    'Proyecto de construcción de infraestructura de agua potable y saneamiento básico para 12 veredas del municipio de Tinjacá que actualmente carecen de acceso continuo a agua potable y no cuentan con sistema de alcantarillado.',
    'Inversión',
    'Construir el sistema de acueducto y alcantarillado para 12 veredas del municipio de Tinjacá, Boyacá, beneficiando a 2,800 habitantes con acceso continuo a agua potable y disposición adecuada de aguas residuales.',
    'Construcción',
    'Proyecto de inversión',
    'Sistemas de acueducto y alcantarillado construidos',
    'Agua Potable y Saneamiento Básico',
    'APS-003'
);

-- ============================================================
-- 2. LOCALIZACIÓN DEL PROYECTO
-- ============================================================
INSERT INTO project_localizations (id, project_id, region, department, municipality)
VALUES (5, 3, 'Centro Oriente', 'Boyacá', 'Tinjacá');

-- ============================================================
-- 3. ENCUESTA (Survey)
-- ============================================================
INSERT INTO survey (id, project_id, survey_json)
VALUES (
    3, 3,
    '{"respuesta_1": "Construir sistema de acueducto y alcantarillado rural", "respuesta_2": "Veredas del municipio de Tinjacá, Boyacá", "respuesta_3": "Habitantes rurales sin acceso a agua potable", "respuesta_4": "Ausencia de infraestructura de agua y saneamiento"}'::json
);

-- ============================================================
-- 4. ANÁLISIS DE PARTICIPANTES
-- ============================================================
INSERT INTO participants_general (id, project_id, participants_analisis, participants_json)
VALUES (
    3, 3,
    'Los principales actores involucrados en el proyecto son la Alcaldía de Tinjacá, la comunidad rural organizada en Juntas de Acción Comunal y Juntas Administradoras de Acueductos Rurales, la Corporación Autónoma Regional de Boyacá (Corpoboyacá) y el Ministerio de Vivienda, Ciudad y Territorio.',
    '{"total_participantes": 4, "tipo": "comunitario"}'::json
);

INSERT INTO participants (id, participants_general_id, participant_actor, participant_entity, interest_expectative, rol, contribution_conflicts)
VALUES
    (10, 3, 'Comunidad rural de las 12 veredas', 'Juntas de Acción Comunal veredales', 'Acceder a agua potable continua y contar con alcantarillado', 'Beneficiario', 'Fuerte apoyo. Disposición a aportar mano de obra no calificada. Preocupación por tarifas.'),
    (11, 3, 'Alcaldía Municipal de Tinjacá', 'Alcaldía de Tinjacá', 'Mejorar indicadores de cobertura de servicios públicos y calidad de vida', 'Ejecutor', 'Compromiso con el proyecto. Recursos de contrapartida limitados.'),
    (12, 3, 'Corpoboyacá', 'Corporación Autónoma Regional de Boyacá', 'Garantizar uso sostenible de fuentes hídricas y cumplimiento de normas ambientales', 'Regulador / Cooperante', 'Exige cumplimiento de permisos ambientales. Apoya con asistencia técnica.'),
    (13, 3, 'Ministerio de Vivienda', 'MinVivienda', 'Incrementar cobertura nacional de acueducto y alcantarillado rural', 'Financiador', 'Disponibilidad de recursos del PDA. Exige viabilización de proyectos tipo.');

-- ============================================================
-- 5. IDENTIFICACIÓN DEL PROBLEMA
-- ============================================================
INSERT INTO problems (id, project_id, central_problem, current_description, magnitude_problem, problem_tree_json)
VALUES (
    3, 3,
    'Deficiente acceso a agua potable y saneamiento básico en las 12 veredas del municipio de Tinjacá',
    'Las 12 veredas priorizadas no cuentan con sistema de acueducto ni alcantarillado. Los habitantes se abastecen de nacederos, aljibes y quebradas sin tratamiento. Las aguas residuales domésticas se vierten directamente al suelo y fuentes hídricas. Esto afecta a 680 familias (2,800 personas).',
    'Cobertura de acueducto rural: 0% en las 12 veredas. Cobertura de alcantarillado rural: 0%. Tasa de EDA (enfermedad diarreica aguda) en menores de 5 años: 85 por cada 1,000 niños (el doble del promedio departamental). El 95% de las viviendas tienen pozos sépticos artesanales o letrina.',
    '{"nodos": {"problema_central": "Deficiente acceso a agua potable y saneamiento", "causas_directas": ["Ausencia de infraestructura de acueducto", "Ausencia de infraestructura de alcantarillado"], "efectos_directos": ["Alta incidencia de enfermedades hídricas", "Contaminación de fuentes hídricas"]}}'::json
);

INSERT INTO direct_causes (id, problem_id, description)
VALUES
    (5, 3, 'Ausencia de infraestructura de captación, tratamiento y distribución de agua potable'),
    (6, 3, 'Inexistencia de redes de alcantarillado y sistemas de tratamiento de aguas residuales');

INSERT INTO indirect_causes (id, direct_cause_id, description)
VALUES
    (9, 5, 'Dispersión geográfica de las veredas que encarece la inversión en infraestructura'),
    (10, 5, 'Históricamente baja priorización de la zona rural en los planes de inversión municipal'),
    (11, 6, 'Ausencia de estudios de preinversión para sistemas de saneamiento rural'),
    (12, 6, 'Limitada capacidad técnica y financiera del municipio para ejecutar proyectos de saneamiento');

INSERT INTO direct_effects (id, problem_id, description)
VALUES
    (5, 3, 'Alta incidencia de enfermedades de origen hídrico, especialmente EDA en menores de 5 años'),
    (6, 3, 'Contaminación progresiva de fuentes hídricas superficiales y subterráneas');

INSERT INTO indirect_effects (id, direct_effect_id, description)
VALUES
    (9, 5, 'Aumento de gastos de bolsillo en salud para las familias rurales'),
    (10, 5, 'Ausentismo escolar asociado a enfermedades gastrointestinales'),
    (11, 6, 'Pérdida de biodiversidad acuática en microcuencas locales'),
    (12, 6, 'Riesgo de contaminación de fuentes de abastecimiento para otros municipios aguas abajo');

-- ============================================================
-- 6. OBJETIVOS
-- ============================================================
INSERT INTO objectives (id, project_id, general_problem, general_objective)
VALUES (
    3, 3,
    'Deficiente acceso a agua potable y saneamiento básico en las 12 veredas del municipio de Tinjacá',
    'Garantizar el acceso a agua potable continua y saneamiento básico adecuado para los 2,800 habitantes de 12 veredas del municipio de Tinjacá'
);

INSERT INTO value_chains (id, project_id, name)
VALUES (3, 3, 'Cadena de valor - Acueducto y alcantarillado rural Tinjacá');

INSERT INTO value_chain_objectives (id, project_id, value_chain_id, name)
VALUES
    (7, 3, 3, 'Construir sistema de acueducto rural'),
    (8, 3, 3, 'Construir sistema de alcantarillado y PTAR'),
    (9, 3, 3, 'Conformar y capacitar juntas administradoras');

INSERT INTO objectives_causes (id, objective_id, type, cause_related, specifics_objectives, cause_id, value_chain_objective_id)
VALUES
    (9, 3, 'directa', 'Ausencia de infraestructura de captación, tratamiento y distribución de agua potable', 'Construir el sistema de acueducto rural para las 12 veredas con captación, PTAP y redes de distribución', 5, 7),
    (10, 3, 'directa', 'Inexistencia de redes de alcantarillado y sistemas de tratamiento', 'Construir redes de alcantarillado y planta de tratamiento de aguas residuales', 6, 8),
    (11, 3, 'indirecta', 'Dispersión geográfica que encarece la inversión', 'Conformar y capacitar juntas administradoras de acueductos rurales para la operación sostenible', 9, 9),
    (12, 3, 'indirecta', 'Limitada capacidad técnica y financiera del municipio', 'Desarrollar capacidad técnica local para la operación y mantenimiento de los sistemas', 12, NULL);

INSERT INTO objectives_indicator (id, objective_id, indicator, unit, meta, source_type, source_validation)
VALUES
    (7, 3, 'Cobertura de acueducto rural en las 12 veredas', 'Porcentaje', 100.0, 'SUI', 'Reporte de la empresa de servicios públicos'),
    (8, 3, 'Cobertura de alcantarillado rural en las 12 veredas', 'Porcentaje', 100.0, 'SUI', 'Reporte de la empresa de servicios públicos'),
    (9, 3, 'Tasa de EDA en menores de 5 años', 'Por 1000', 40.0, 'SIVIGILA', 'Informe epidemiológico municipal');

-- ============================================================
-- 7. POBLACIÓN
-- ============================================================
INSERT INTO population (id, project_id, population_type_affected, number_affected, source_information_affected, population_type_intervention, number_intervention, source_information_intervention, population_json)
VALUES (
    3, 3,
    'Población rural del municipio de Tinjacá',
    4200,
    'DANE - Censo Nacional de Población 2018 y proyecciones 2025',
    'Habitantes de las 12 veredas sin servicio de acueducto ni alcantarillado',
    2800,
    'Encuesta de hogares - Alcaldía de Tinjacá 2025',
    '{"familias": 680, "viviendas": 650, "grupos_etarios": {"0-5": 280, "6-17": 560, "18-59": 1400, "60+": 560}}'::json
);

INSERT INTO affected_population (id, population_id, region, department, city, population_center, location_entity)
VALUES
    (7, 3, 'Centro Oriente', 'Boyacá', 'Tinjacá', 'Vereda El Salitre', 'JAC El Salitre'),
    (8, 3, 'Centro Oriente', 'Boyacá', 'Tinjacá', 'Vereda Arrayanes', 'JAC Arrayanes'),
    (9, 3, 'Centro Oriente', 'Boyacá', 'Tinjacá', 'Vereda Funza', 'JAC Funza');

INSERT INTO intervention_population (id, population_id, region, department, city, population_center, location_entity)
VALUES
    (7, 3, 'Centro Oriente', 'Boyacá', 'Tinjacá', 'Vereda El Salitre', 'JAC El Salitre'),
    (8, 3, 'Centro Oriente', 'Boyacá', 'Tinjacá', 'Vereda Arrayanes', 'JAC Arrayanes'),
    (9, 3, 'Centro Oriente', 'Boyacá', 'Tinjacá', 'Vereda Funza', 'JAC Funza');


-- ============================================================
-- 8. ANÁLISIS DE ALTERNATIVAS
-- ============================================================
INSERT INTO alternatives_general (id, project_id, solution_alternatives, cost, profitability)
VALUES (3, 3, TRUE, TRUE, TRUE);

INSERT INTO alternatives (id, alternative_id, name, active, state)
VALUES
    (7, 3, 'Alternativa 1: Sistema de acueducto por gravedad con PTAP compacta y alcantarillado convencional con PTAR', TRUE, 'seleccionada'),
    (8, 3, 'Alternativa 2: Pozos profundos con bombeo eléctrico y soluciones individuales de saneamiento (pozos sépticos mejorados)', FALSE, 'descartada'),
    (9, 3, 'Alternativa 3: Sistema mixto con captación de agua lluvia y letrina mejorada ventilada', FALSE, 'descartada');

-- ============================================================
-- 9. ANÁLISIS TÉCNICO
-- ============================================================
INSERT INTO technical_analysis (id, project_id, analysis)
VALUES (
    3, 3,
    'La alternativa por gravedad es técnicamente superior porque: 1) La topografía del municipio permite conducción por gravedad, eliminando costos de bombeo. 2) Existe una fuente hídrica (quebrada La Honda) con caudal suficiente y concesión otorgada por Corpoboyacá. 3) La PTAP compacta requiere mínimo personal para operación. 4) El alcantarillado convencional permite tratar las aguas residuales de forma centralizada en una PTAR de lodos activados. 5) Plazo estimado de ejecución: 24 meses.'
);

-- ============================================================
-- 10. LOCALIZACIÓN
-- ============================================================
INSERT INTO localization_general (id, project_id, administrative_political_factors, proximity_to_target_population, proximity_to_supply_sources, communications, land_cost_and_availability, public_services_availability, labor_availability_and_cost, tax_and_legal_structure, environmental_factors, gender_equity_impact, transport_means_and_costs, public_order, other_factors, topography)
VALUES (
    3, 3, TRUE, TRUE, TRUE, FALSE, TRUE, FALSE, TRUE, FALSE, TRUE, TRUE, TRUE, FALSE, FALSE, TRUE
);

INSERT INTO localization (id, localization_general_id, region, department, city, type_group, "group", entity, georeferencing, latitude, longitude)
VALUES
    (7, 3, 'Centro Oriente', 'Boyacá', 'Tinjacá', 'Rural', 'Vereda El Salitre', 'Bocatoma y PTAP', TRUE, 5.5783, -73.6512),
    (8, 3, 'Centro Oriente', 'Boyacá', 'Tinjacá', 'Rural', 'Vereda Funza', 'Tanque de almacenamiento principal', TRUE, 5.5698, -73.6478),
    (9, 3, 'Centro Oriente', 'Boyacá', 'Tinjacá', 'Rural', 'Vereda Arrayanes', 'PTAR', TRUE, 5.5615, -73.6443);

-- ============================================================
-- 11. ESTUDIO DE NECESIDADES (Requirements)
-- ============================================================
INSERT INTO requirements_general (id, project_id, requirements_analysis)
VALUES (
    3, 3,
    'Se analizó la demanda de agua potable actual y proyectada a 25 años (horizonte de diseño), la capacidad de la fuente hídrica, y los requerimientos de saneamiento según la normativa RAS (Resolución 0330 de 2017). Se determinó que la fuente tiene caudal suficiente para abastecer la población de diseño.'
);

INSERT INTO requirements (id, requirements_general_id, good_service_name, good_service_description, supply_description, demand_description, unit_of_measure, start_year, end_year, last_projected_year)
VALUES
    (7, 3, 'Sistema de acueducto rural', 'Bocatoma, aducción, PTAP, tanque de almacenamiento y redes de distribución (18 km)', 'No existe infraestructura de acueducto en las 12 veredas', 'Dotación: 100 L/hab/día. Caudal medio: 3.24 L/s. Población de diseño: 2,800 hab', 'Litros por segundo', 2026, 2028, 2051),
    (8, 3, 'Sistema de alcantarillado sanitario', 'Redes de recolección (14 km), colectores principales y PTAR de lodos activados', 'No existe sistema de alcantarillado. Pozos sépticos artesanales en el 95% de viviendas', 'Caudal de aguas residuales domésticas proyectado: 2.6 L/s', 'Litros por segundo', 2026, 2028, 2051),
    (9, 3, 'Micromedidores domiciliarios', 'Medidores volumétricos para 680 viviendas', 'No existen medidores de consumo', 'Se requieren 680 micromedidores para control de consumo y facturación', 'Unidad', 2026, 2028, 2051);

-- ============================================================
-- 12. PRODUCTOS Y ACTIVIDADES
-- ============================================================
INSERT INTO products (id, project_id, value_chain_objective_id, measured_through, quantity, cost, stage, description)
VALUES
    (7, 3, 7, 'Kilómetros de red de acueducto construidos', 18, 4200000000, 'Inversión', 'Construcción del sistema de acueducto: bocatoma, PTAP, tanque y 18 km de redes'),
    (8, 3, 8, 'Kilómetros de red de alcantarillado construidos', 14, 3100000000, 'Inversión', 'Construcción de 14 km de redes de alcantarillado y PTAR de lodos activados'),
    (9, 3, 9, 'Número de juntas administradoras conformadas', 4, 350000000, 'Inversión', 'Conformación y capacitación de 4 juntas administradoras de acueductos veredales');

INSERT INTO activities (id, project_id, product_id, cost, stage, description)
VALUES
    (19, 3, 7, 600000000, 'Preinversión', 'Estudios y diseños de ingeniería del sistema de acueducto'),
    (20, 3, 7, 3200000000, 'Inversión', 'Construcción de bocatoma, PTAP, tanque y redes de distribución'),
    (21, 3, 7, 400000000, 'Inversión', 'Interventoría de obras de acueducto'),
    (22, 3, 8, 450000000, 'Preinversión', 'Estudios y diseños de redes de alcantarillado y PTAR'),
    (23, 3, 8, 2400000000, 'Inversión', 'Construcción de redes de alcantarillado y PTAR'),
    (24, 3, 8, 250000000, 'Inversión', 'Interventoría de obras de alcantarillado'),
    (25, 3, 9, 50000000, 'Preinversión', 'Diagnóstico comunitario y diseño del programa de formación'),
    (26, 3, 9, 250000000, 'Inversión', 'Ejecución del programa de conformación y capacitación de juntas'),
    (27, 3, 9, 50000000, 'Inversión', 'Acompañamiento y seguimiento a juntas administradoras');

-- ============================================================
-- 13. PLANES DE DESARROLLO
-- ============================================================
INSERT INTO development_plans (id, project_id, program, national_development_plan, departmental_or_sectoral_development_plan, strategy_departmental, program_departmental, district_or_municipal_development_plan, strategy_district, program_district, community_type, ethnic_group_planning_instruments, other_development_plan, strategy_other, program_other)
VALUES (
    3, 3,
    'Agua potable y saneamiento para todos',
    'Plan Nacional de Desarrollo 2022-2026: Colombia Potencia Mundial de la Vida',
    'Plan Departamental de Desarrollo de Boyacá 2024-2027',
    'Boyacá territorio de agua y vida',
    'Ampliación de cobertura de acueducto y alcantarillado rural',
    'Plan de Desarrollo Municipal de Tinjacá 2024-2027',
    'Tinjacá con agua para todos',
    'Infraestructura de servicios públicos rurales',
    'Campesino', NULL, NULL, NULL, NULL
);

INSERT INTO pnds (id, development_plan_id, transformation, pillar, catalyst, component)
VALUES
    (5, 3, 'Transformación 1: Ordenamiento del territorio alrededor del agua', 'Pilar: Ordenamiento del territorio alrededor del agua', 'Agua y saneamiento para la vida', 'Cobertura de acueducto y alcantarillado rural'),
    (6, 3, 'Transformación 5: Convergencia regional', 'Pilar: Ordenamiento del territorio alrededor del agua', 'Cierre de brechas territoriales', 'Acceso a servicios públicos en zonas rurales dispersas');


-- ############################################################
-- ############################################################
-- PROYECTO 4: TRANSPORTE - Mejoramiento de vías terciarias
--             en el norte del Cauca
-- ############################################################
-- ############################################################

-- ============================================================
-- 1. PROYECTO
-- ============================================================
INSERT INTO projects (id, name, description, process, object_desc, intervention_type, project_typology, main_product, sector, indicator_code)
VALUES (
    4,
    'Mejoramiento de vías terciarias para la conectividad rural del norte del Cauca',
    'Proyecto de mejoramiento de 45 km de vías terciarias en los municipios de Toribío, Jambaló y Caldono (norte del Cauca) para mejorar la conectividad rural, reducir tiempos de desplazamiento y facilitar la comercialización de productos agrícolas.',
    'Inversión',
    'Mejorar 45 km de vías terciarias mediante estabilización de subrasante, construcción de placa huella y obras de drenaje en los municipios de Toribío, Jambaló y Caldono, Cauca.',
    'Mejoramiento',
    'Proyecto de inversión',
    'Vías terciarias mejoradas',
    'Transporte',
    'TRA-004'
);

-- ============================================================
-- 2. LOCALIZACIÓN DEL PROYECTO
-- ============================================================
INSERT INTO project_localizations (id, project_id, region, department, municipality)
VALUES
    (6, 4, 'Pacífico', 'Cauca', 'Toribío'),
    (7, 4, 'Pacífico', 'Cauca', 'Jambaló'),
    (8, 4, 'Pacífico', 'Cauca', 'Caldono');

-- ============================================================
-- 3. ENCUESTA (Survey)
-- ============================================================
INSERT INTO survey (id, project_id, survey_json)
VALUES (
    4, 4,
    '{"respuesta_1": "Mejorar vías terciarias rurales", "respuesta_2": "Norte del Cauca (Toribío, Jambaló, Caldono)", "respuesta_3": "Comunidades indígenas y campesinas del norte del Cauca", "respuesta_4": "Mal estado de las vías terciarias que dificulta la conectividad y comercialización"}'::json
);

-- ============================================================
-- 4. ANÁLISIS DE PARTICIPANTES
-- ============================================================
INSERT INTO participants_general (id, project_id, participants_analisis, participants_json)
VALUES (
    4, 4,
    'El proyecto involucra a las comunidades indígenas Nasa organizadas en cabildos y resguardos, las alcaldías municipales, la Gobernación del Cauca, el INVÍAS y las asociaciones de productores agrícolas de la zona. Se realizó consulta previa con las autoridades indígenas.',
    '{"total_participantes": 4, "tipo": "étnico-comunitario"}'::json
);

INSERT INTO participants (id, participants_general_id, participant_actor, participant_entity, interest_expectative, rol, contribution_conflicts)
VALUES
    (14, 4, 'Comunidades indígenas Nasa', 'Cabildos y resguardos de Toribío, Jambaló y Caldono', 'Mejorar la conectividad de los resguardos y facilitar el acceso a mercados', 'Beneficiario / Cooperante', 'Fuerte apoyo tras consulta previa. Aportan mano de obra comunitaria (minga). Exigen respeto al territorio.'),
    (15, 4, 'Alcaldías municipales', 'Alcaldías de Toribío, Jambaló y Caldono', 'Cumplir metas del plan de desarrollo en infraestructura vial', 'Ejecutor', 'Compromiso con contrapartidas. Limitaciones en capacidad técnica para interventoría.'),
    (16, 4, 'INVÍAS', 'Instituto Nacional de Vías', 'Mejorar la red vial terciaria del país', 'Financiador / Cooperante técnico', 'Financia a través del programa Colombia Rural. Exige cumplimiento de especificaciones técnicas INVÍAS.'),
    (17, 4, 'Asociaciones de productores', 'ASPROCAFE Ingrumá, Asociación de productores de fique del Cauca', 'Reducir costos de transporte y pérdidas postcosecha', 'Beneficiario', 'Alto interés. Disposición a cofinanciar tramos estratégicos para comercialización.');

-- ============================================================
-- 5. IDENTIFICACIÓN DEL PROBLEMA
-- ============================================================
INSERT INTO problems (id, project_id, central_problem, current_description, magnitude_problem, problem_tree_json)
VALUES (
    4, 4,
    'Deficiente conectividad vial rural en los municipios de Toribío, Jambaló y Caldono por el mal estado de las vías terciarias',
    'Los 45 km de vías terciarias priorizados se encuentran en afirmado deteriorado, sin obras de drenaje adecuadas y con tramos intransitables en época de lluvias. Esto afecta a 18,000 habitantes de comunidades indígenas y campesinas que dependen de estas vías para su movilidad, acceso a servicios y comercialización de café, fique y productos agrícolas.',
    'El 80% de los tramos priorizados están en estado malo o muy malo según inventario vial del INVÍAS. El tiempo promedio de recorrido al casco urbano más cercano es de 3.5 horas (debería ser 1 hora). Las pérdidas postcosecha por dificultades de transporte alcanzan el 25%. Solo el 15% de los tramos son transitables durante los 12 meses del año.',
    '{"nodos": {"problema_central": "Deficiente conectividad vial rural", "causas_directas": ["Vías terciarias deterioradas", "Ausencia de obras de drenaje"], "efectos_directos": ["Altos tiempos de desplazamiento", "Pérdidas de producción agrícola"]}}'::json
);

INSERT INTO direct_causes (id, problem_id, description)
VALUES
    (7, 4, 'Vías terciarias con superficie de rodadura deteriorada y sin estabilización'),
    (8, 4, 'Ausencia de obras de drenaje (cunetas, alcantarillas, box culvert) que causan erosión');

INSERT INTO indirect_causes (id, direct_cause_id, description)
VALUES
    (13, 7, 'Más de 15 años sin intervención de mejoramiento vial en la zona'),
    (14, 7, 'Alta pluviosidad de la región (2,500 mm/año) que acelera el deterioro sin pavimento'),
    (15, 8, 'Inexistencia de un plan vial municipal que priorice inversiones en drenaje'),
    (16, 8, 'Topografía montañosa que exige obras de arte especiales no ejecutadas');

INSERT INTO direct_effects (id, problem_id, description)
VALUES
    (7, 4, 'Elevados tiempos de desplazamiento de la población rural hacia centros urbanos'),
    (8, 4, 'Altas pérdidas postcosecha y sobrecostos de transporte de productos agrícolas');

INSERT INTO indirect_effects (id, direct_effect_id, description)
VALUES
    (13, 7, 'Dificultad de acceso a servicios de salud y educación para la población rural'),
    (14, 7, 'Aislamiento de comunidades indígenas durante temporada de lluvias'),
    (15, 8, 'Menor competitividad del café y fique del norte del Cauca frente a otras regiones'),
    (16, 8, 'Migración de población joven hacia centros urbanos por falta de oportunidades');

-- ============================================================
-- 6. OBJETIVOS
-- ============================================================
INSERT INTO objectives (id, project_id, general_problem, general_objective)
VALUES (
    4, 4,
    'Deficiente conectividad vial rural en los municipios de Toribío, Jambaló y Caldono',
    'Mejorar la conectividad vial rural mediante el mejoramiento de 45 km de vías terciarias en Toribío, Jambaló y Caldono para reducir tiempos de desplazamiento y facilitar la comercialización agrícola'
);

INSERT INTO value_chains (id, project_id, name)
VALUES (4, 4, 'Cadena de valor - Vías terciarias norte del Cauca');

INSERT INTO value_chain_objectives (id, project_id, value_chain_id, name)
VALUES
    (10, 4, 4, 'Mejorar la superficie de rodadura (placa huella)'),
    (11, 4, 4, 'Construir obras de drenaje y arte'),
    (12, 4, 4, 'Implementar señalización y seguridad vial');

INSERT INTO objectives_causes (id, objective_id, type, cause_related, specifics_objectives, cause_id, value_chain_objective_id)
VALUES
    (13, 4, 'directa', 'Vías terciarias con superficie de rodadura deteriorada', 'Mejorar 45 km de superficie de rodadura mediante placa huella y estabilización de subrasante', 7, 10),
    (14, 4, 'directa', 'Ausencia de obras de drenaje que causan erosión', 'Construir obras de drenaje y arte (cunetas, alcantarillas, box culvert, muros de contención)', 8, 11),
    (15, 4, 'indirecta', 'Más de 15 años sin intervención de mejoramiento vial', 'Implementar señalización vial y elementos de seguridad en tramos críticos', 13, 12),
    (16, 4, 'indirecta', 'Inexistencia de un plan vial municipal', 'Formular el plan vial municipal con priorización de inversiones a 10 años', 15, NULL);

INSERT INTO objectives_indicator (id, objective_id, indicator, unit, meta, source_type, source_validation)
VALUES
    (10, 4, 'Kilómetros de vía terciaria mejorada', 'Kilómetro', 45.0, 'Inventario vial INVÍAS', 'Acta de recibo de obras'),
    (11, 4, 'Tiempo promedio de recorrido al casco urbano', 'Hora', 1.0, 'Medición en campo', 'Informe de interventoría'),
    (12, 4, 'Porcentaje de vías transitables los 12 meses', 'Porcentaje', 95.0, 'Reporte de estado vial', 'Inspección trimestral INVÍAS');

-- ============================================================
-- 7. POBLACIÓN
-- ============================================================
INSERT INTO population (id, project_id, population_type_affected, number_affected, source_information_affected, population_type_intervention, number_intervention, source_information_intervention, population_json)
VALUES (
    4, 4,
    'Población rural de los tres municipios del norte del Cauca',
    52000,
    'DANE - Proyecciones de población 2025 (zona rural)',
    'Población directamente conectada a los 45 km de vías priorizadas',
    18000,
    'Censo comunitario 2025 - Cabildos indígenas y alcaldías',
    '{"etnia": {"nasa": 14000, "mestizo": 3500, "afrodescendiente": 500}, "actividad_economica": {"cafe": 7000, "fique": 3000, "pancoger": 5000, "otros": 3000}}'::json
);

INSERT INTO affected_population (id, population_id, region, department, city, population_center, location_entity)
VALUES
    (10, 4, 'Pacífico', 'Cauca', 'Toribío', 'Resguardo de Tacueyó', 'Cabildo indígena de Tacueyó'),
    (11, 4, 'Pacífico', 'Cauca', 'Jambaló', 'Resguardo de Jambaló', 'Cabildo indígena de Jambaló'),
    (12, 4, 'Pacífico', 'Cauca', 'Caldono', 'Resguardo de Caldono', 'Cabildo indígena de Caldono');

INSERT INTO intervention_population (id, population_id, region, department, city, population_center, location_entity)
VALUES
    (10, 4, 'Pacífico', 'Cauca', 'Toribío', 'Resguardo de Tacueyó', 'Cabildo indígena de Tacueyó'),
    (11, 4, 'Pacífico', 'Cauca', 'Jambaló', 'Resguardo de Jambaló', 'Cabildo indígena de Jambaló'),
    (12, 4, 'Pacífico', 'Cauca', 'Caldono', 'Resguardo de Caldono', 'Cabildo indígena de Caldono');


-- ============================================================
-- 8. ANÁLISIS DE ALTERNATIVAS
-- ============================================================
INSERT INTO alternatives_general (id, project_id, solution_alternatives, cost, profitability)
VALUES (4, 4, TRUE, TRUE, TRUE);

INSERT INTO alternatives (id, alternative_id, name, active, state)
VALUES
    (10, 4, 'Alternativa 1: Mejoramiento con placa huella en tramos críticos (60%), estabilización de subrasante (40%), cunetas y alcantarillas en concreto', TRUE, 'seleccionada'),
    (11, 4, 'Alternativa 2: Pavimentación total con concreto asfáltico MDC-19 en los 45 km', FALSE, 'descartada'),
    (12, 4, 'Alternativa 3: Mantenimiento rutinario con recebo y perfilado sin obras de drenaje', FALSE, 'descartada');

-- ============================================================
-- 9. ANÁLISIS TÉCNICO
-- ============================================================
INSERT INTO technical_analysis (id, project_id, analysis)
VALUES (
    4, 4,
    'La alternativa de placa huella es la más adecuada porque: 1) Es la solución recomendada por INVÍAS para vías terciarias con tráfico TPD menor a 50 vehículos. 2) La placa huella resiste las condiciones de alta pluviosidad de la zona. 3) El costo por kilómetro ($200M) es un 70% menor que la pavimentación asfáltica. 4) Permite el uso de mano de obra local (mingas comunitarias) reduciendo costos. 5) Las obras de drenaje en concreto eliminan la erosión que es la principal causa de deterioro. 6) Plazo de ejecución estimado: 18 meses con frentes simultáneos en los 3 municipios.'
);

-- ============================================================
-- 10. LOCALIZACIÓN
-- ============================================================
INSERT INTO localization_general (id, project_id, administrative_political_factors, proximity_to_target_population, proximity_to_supply_sources, communications, land_cost_and_availability, public_services_availability, labor_availability_and_cost, tax_and_legal_structure, environmental_factors, gender_equity_impact, transport_means_and_costs, public_order, other_factors, topography)
VALUES (
    4, 4, TRUE, TRUE, FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE
);

INSERT INTO localization (id, localization_general_id, region, department, city, type_group, "group", entity, georeferencing, latitude, longitude)
VALUES
    (10, 4, 'Pacífico', 'Cauca', 'Toribío', 'Rural', 'Resguardo Tacueyó', 'Tramo Toribío-Tacueyó (18 km)', TRUE, 2.9553, -76.2667),
    (11, 4, 'Pacífico', 'Cauca', 'Jambaló', 'Rural', 'Resguardo Jambaló', 'Tramo Jambaló-La Mina (15 km)', TRUE, 2.8500, -76.3167),
    (12, 4, 'Pacífico', 'Cauca', 'Caldono', 'Rural', 'Resguardo Caldono', 'Tramo Caldono-Pueblo Nuevo (12 km)', TRUE, 2.8000, -76.3333);

-- ============================================================
-- 11. ESTUDIO DE NECESIDADES (Requirements)
-- ============================================================
INSERT INTO requirements_general (id, project_id, requirements_analysis)
VALUES (
    4, 4,
    'Se evaluó el estado actual de la infraestructura vial, la demanda de transporte (pasajeros y carga agrícola), y los requerimientos técnicos según las especificaciones INVÍAS para vías terciarias. Se priorizaron los tramos con mayor tráfico, peor estado y mayor impacto en conectividad de comunidades.'
);

INSERT INTO requirements (id, requirements_general_id, good_service_name, good_service_description, supply_description, demand_description, unit_of_measure, start_year, end_year, last_projected_year)
VALUES
    (10, 4, 'Placa huella', 'Construcción de placa huella en concreto f''c=210 kg/cm² en tramos críticos (27 km)', 'Los 45 km de vía están en afirmado deteriorado sin superficie estable', 'Se requiere mejorar 27 km de tramos con placa huella para garantizar transitabilidad', 'Kilómetro', 2026, 2028, 2038),
    (11, 4, 'Obras de drenaje', 'Cunetas, alcantarillas, box culvert y muros de contención', 'Actualmente no existen obras de drenaje en el 85% de los tramos', 'Se requieren 120 obras de drenaje distribuidas en los 45 km', 'Unidad', 2026, 2028, 2038),
    (12, 4, 'Señalización vial', 'Señalización vertical y horizontal en puntos críticos', 'No existe señalización vial en ninguno de los tramos', 'Se requiere señalización en 45 km incluyendo 30 puntos críticos', 'Kilómetro', 2026, 2028, 2038);

-- ============================================================
-- 12. PRODUCTOS Y ACTIVIDADES
-- ============================================================
INSERT INTO products (id, project_id, value_chain_objective_id, measured_through, quantity, cost, stage, description)
VALUES
    (10, 4, 10, 'Kilómetros de placa huella construida', 27, 5400000000, 'Inversión', 'Construcción de 27 km de placa huella y estabilización de 18 km de subrasante'),
    (11, 4, 11, 'Número de obras de drenaje construidas', 120, 2400000000, 'Inversión', 'Construcción de 120 obras de drenaje: cunetas, alcantarillas, box culvert y muros'),
    (12, 4, 12, 'Kilómetros señalizados', 45, 450000000, 'Inversión', 'Instalación de señalización vertical y horizontal en 45 km');

INSERT INTO activities (id, project_id, product_id, cost, stage, description)
VALUES
    (28, 4, 10, 700000000, 'Preinversión', 'Estudios topográficos, geotécnicos y diseños de placa huella'),
    (29, 4, 10, 4200000000, 'Inversión', 'Construcción de placa huella y estabilización de subrasante'),
    (30, 4, 10, 500000000, 'Inversión', 'Interventoría técnica de obras de placa huella'),
    (31, 4, 11, 300000000, 'Preinversión', 'Estudios hidrológicos e hidráulicos y diseños de obras de drenaje'),
    (32, 4, 11, 1900000000, 'Inversión', 'Construcción de cunetas, alcantarillas, box culvert y muros'),
    (33, 4, 11, 200000000, 'Inversión', 'Interventoría de obras de drenaje'),
    (34, 4, 12, 50000000, 'Preinversión', 'Estudio de señalización y plan de manejo de tráfico'),
    (35, 4, 12, 350000000, 'Inversión', 'Fabricación e instalación de señalización vial'),
    (36, 4, 12, 50000000, 'Inversión', 'Socialización y capacitación en seguridad vial a la comunidad');

-- ============================================================
-- 13. PLANES DE DESARROLLO
-- ============================================================
INSERT INTO development_plans (id, project_id, program, national_development_plan, departmental_or_sectoral_development_plan, strategy_departmental, program_departmental, district_or_municipal_development_plan, strategy_district, program_district, community_type, ethnic_group_planning_instruments, other_development_plan, strategy_other, program_other)
VALUES (
    4, 4,
    'Colombia Rural: Caminos para la paz y la productividad',
    'Plan Nacional de Desarrollo 2022-2026: Colombia Potencia Mundial de la Vida',
    'Plan Departamental de Desarrollo del Cauca 2024-2027',
    'Cauca conectado y competitivo',
    'Mejoramiento de la red vial terciaria departamental',
    'Plan de Desarrollo Municipal de Toribío 2024-2027',
    'Toribío territorio de paz con infraestructura',
    'Conectividad vial para el desarrollo rural',
    'Indígena',
    'Plan de Vida del Pueblo Nasa - Proyecto Nasa',
    NULL, NULL, NULL
);

INSERT INTO pnds (id, development_plan_id, transformation, pillar, catalyst, component)
VALUES
    (7, 4, 'Transformación 5: Convergencia regional', 'Pilar: Ordenamiento del territorio alrededor del agua', 'Infraestructura para la conectividad', 'Red vial terciaria para la integración territorial'),
    (8, 4, 'Transformación 4: Derecho humano a la alimentación', 'Pilar: Derecho humano a la alimentación', 'Productividad agrícola', 'Conectividad para la comercialización agropecuaria');


-- ============================================================
-- ============================================================
-- VERIFICACIÓN GLOBAL: Resumen de registros por tabla
-- ============================================================
-- ============================================================

-- Descomentar para verificar todos los proyectos:

-- SELECT 'projects' AS tabla, COUNT(*) AS registros FROM projects
-- UNION ALL SELECT 'project_localizations', COUNT(*) FROM project_localizations
-- UNION ALL SELECT 'survey', COUNT(*) FROM survey
-- UNION ALL SELECT 'participants_general', COUNT(*) FROM participants_general
-- UNION ALL SELECT 'participants', COUNT(*) FROM participants
-- UNION ALL SELECT 'problems', COUNT(*) FROM problems
-- UNION ALL SELECT 'direct_causes', COUNT(*) FROM direct_causes
-- UNION ALL SELECT 'indirect_causes', COUNT(*) FROM indirect_causes
-- UNION ALL SELECT 'direct_effects', COUNT(*) FROM direct_effects
-- UNION ALL SELECT 'indirect_effects', COUNT(*) FROM indirect_effects
-- UNION ALL SELECT 'objectives', COUNT(*) FROM objectives
-- UNION ALL SELECT 'value_chains', COUNT(*) FROM value_chains
-- UNION ALL SELECT 'value_chain_objectives', COUNT(*) FROM value_chain_objectives
-- UNION ALL SELECT 'objectives_causes', COUNT(*) FROM objectives_causes
-- UNION ALL SELECT 'objectives_indicator', COUNT(*) FROM objectives_indicator
-- UNION ALL SELECT 'population', COUNT(*) FROM population
-- UNION ALL SELECT 'affected_population', COUNT(*) FROM affected_population
-- UNION ALL SELECT 'intervention_population', COUNT(*) FROM intervention_population
-- UNION ALL SELECT 'characteristics_population', COUNT(*) FROM characteristics_population
-- UNION ALL SELECT 'alternatives_general', COUNT(*) FROM alternatives_general
-- UNION ALL SELECT 'alternatives', COUNT(*) FROM alternatives
-- UNION ALL SELECT 'technical_analysis', COUNT(*) FROM technical_analysis
-- UNION ALL SELECT 'localization_general', COUNT(*) FROM localization_general
-- UNION ALL SELECT 'localization', COUNT(*) FROM localization
-- UNION ALL SELECT 'requirements_general', COUNT(*) FROM requirements_general
-- UNION ALL SELECT 'requirements', COUNT(*) FROM requirements
-- UNION ALL SELECT 'products', COUNT(*) FROM products
-- UNION ALL SELECT 'activities', COUNT(*) FROM activities
-- UNION ALL SELECT 'development_plans', COUNT(*) FROM development_plans
-- UNION ALL SELECT 'pnds', COUNT(*) FROM pnds;

-- ============================================================
-- PASO 5: ACTUALIZAR SECUENCIAS para que el próximo INSERT
--         auto-incremente correctamente desde el valor máximo+1
-- ============================================================
SELECT setval('projects_id_seq', (SELECT COALESCE(MAX(id),0) FROM projects));
SELECT setval('project_localizations_id_seq', (SELECT COALESCE(MAX(id),0) FROM project_localizations));
SELECT setval('survey_id_seq', (SELECT COALESCE(MAX(id),0) FROM survey));
SELECT setval('participants_general_id_seq', (SELECT COALESCE(MAX(id),0) FROM participants_general));
SELECT setval('participants_id_seq', (SELECT COALESCE(MAX(id),0) FROM participants));
SELECT setval('problems_id_seq', (SELECT COALESCE(MAX(id),0) FROM problems));
SELECT setval('direct_causes_id_seq', (SELECT COALESCE(MAX(id),0) FROM direct_causes));
SELECT setval('indirect_causes_id_seq', (SELECT COALESCE(MAX(id),0) FROM indirect_causes));
SELECT setval('direct_effects_id_seq', (SELECT COALESCE(MAX(id),0) FROM direct_effects));
SELECT setval('indirect_effects_id_seq', (SELECT COALESCE(MAX(id),0) FROM indirect_effects));
SELECT setval('objectives_id_seq', (SELECT COALESCE(MAX(id),0) FROM objectives));
SELECT setval('value_chains_id_seq', (SELECT COALESCE(MAX(id),0) FROM value_chains));
SELECT setval('value_chain_objectives_id_seq', (SELECT COALESCE(MAX(id),0) FROM value_chain_objectives));
SELECT setval('objectives_causes_id_seq', (SELECT COALESCE(MAX(id),0) FROM objectives_causes));
SELECT setval('objectives_indicator_id_seq', (SELECT COALESCE(MAX(id),0) FROM objectives_indicator));
SELECT setval('population_id_seq', (SELECT COALESCE(MAX(id),0) FROM population));
SELECT setval('affected_population_id_seq', (SELECT COALESCE(MAX(id),0) FROM affected_population));
SELECT setval('intervention_population_id_seq', (SELECT COALESCE(MAX(id),0) FROM intervention_population));
SELECT setval('characteristics_population_id_seq', (SELECT COALESCE(MAX(id),0) FROM characteristics_population));
SELECT setval('alternatives_general_id_seq', (SELECT COALESCE(MAX(id),0) FROM alternatives_general));
SELECT setval('alternatives_id_seq', (SELECT COALESCE(MAX(id),0) FROM alternatives));
SELECT setval('technical_analysis_id_seq', (SELECT COALESCE(MAX(id),0) FROM technical_analysis));
SELECT setval('localization_general_id_seq', (SELECT COALESCE(MAX(id),0) FROM localization_general));
SELECT setval('localization_id_seq', (SELECT COALESCE(MAX(id),0) FROM localization));
SELECT setval('requirements_general_id_seq', (SELECT COALESCE(MAX(id),0) FROM requirements_general));
SELECT setval('requirements_id_seq', (SELECT COALESCE(MAX(id),0) FROM requirements));
SELECT setval('products_id_seq', (SELECT COALESCE(MAX(id),0) FROM products));
SELECT setval('activities_id_seq', (SELECT COALESCE(MAX(id),0) FROM activities));
SELECT setval('development_plans_id_seq', (SELECT COALESCE(MAX(id),0) FROM development_plans));
SELECT setval('pnds_id_seq', (SELECT COALESCE(MAX(id),0) FROM pnds));

COMMIT;
