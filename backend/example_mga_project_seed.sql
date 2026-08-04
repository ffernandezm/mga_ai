BEGIN;

DO $$
DECLARE
    v_project_id INTEGER;
    v_participants_general_id INTEGER;
    v_problem_id INTEGER;
    v_direct_cause_1_id INTEGER;
    v_direct_cause_2_id INTEGER;
    v_direct_effect_1_id INTEGER;
    v_direct_effect_2_id INTEGER;
    v_objective_id INTEGER;
    v_value_chain_id INTEGER;
    v_value_chain_objective_1_id INTEGER;
    v_value_chain_objective_2_id INTEGER;
    v_value_chain_objective_3_id INTEGER;
    v_population_id INTEGER;
    v_alternatives_general_id INTEGER;
    v_localization_general_id INTEGER;
    v_requirements_general_id INTEGER;
    v_product_1_id INTEGER;
    v_product_2_id INTEGER;
    v_product_3_id INTEGER;
    v_development_plan_id INTEGER;
BEGIN
    IF EXISTS (
        SELECT 1
        FROM projects
        WHERE name = 'Mejoramiento integral del sistema de acueducto rural en el municipio de La Plata'
    ) THEN
        RAISE EXCEPTION 'Ya existe un proyecto con ese nombre. Ajusta el nombre antes de ejecutar este script.';
    END IF;

    INSERT INTO projects (
        name,
        description,
        process,
        object_desc,
        intervention_type,
        project_typology,
        main_product,
        sector
    )
    VALUES (
        'Mejoramiento integral del sistema de acueducto rural en el municipio de La Plata',
        'Proyecto MGA orientado a ampliar la cobertura, mejorar la continuidad y asegurar la calidad del agua potable en centros poblados rurales del municipio de La Plata, Huila.',
        'Inversion',
        'Optimizar la captacion, tratamiento, almacenamiento y distribucion de agua potable para hogares rurales de los centros poblados San Vicente, Monserrate y El Triunfo.',
        'Mejoramiento',
        'Proyecto de inversion',
        'Servicio de acueducto rural mejorado',
        'Vivienda, Ciudad y Territorio'
    )
    RETURNING id INTO v_project_id;

    INSERT INTO project_localizations (project_id, region, department, municipality)
    VALUES
        (v_project_id, 'Centro Sur', 'Huila', 'La Plata'),
        (v_project_id, 'Centro Sur', 'Huila', 'La Plata'),
        (v_project_id, 'Centro Sur', 'Huila', 'La Plata');

    INSERT INTO survey (project_id, survey_json)
    VALUES (
        v_project_id,
        json_build_object(
            'respuesta_1', 'Mejorar el sistema de acueducto rural',
            'respuesta_2', 'Municipio de La Plata, Huila',
            'respuesta_3', 'Hogares rurales de centros poblados priorizados',
            'respuesta_4', 'Baja continuidad y calidad deficiente del servicio de agua potable'
        )
    );

    INSERT INTO chat_history (project_id, tab, session_id, sender, message)
    VALUES
        (v_project_id, 'problems', 'seed-session-' || v_project_id, 'user', 'Necesito estructurar el problema central del proyecto de acueducto rural.'),
        (v_project_id, 'problems', 'seed-session-' || v_project_id, 'bot', 'El problema central puede formularse a partir de la baja continuidad y calidad del servicio en la zona rural.');

    INSERT INTO participants_general (project_id, participants_analisis, participants_json)
    VALUES (
        v_project_id,
        'Se identificaron actores institucionales, comunitarios y operadores del servicio. El proyecto requiere coordinacion entre administracion municipal, asociaciones de usuarios, autoridad ambiental y comunidad beneficiaria.',
        json_build_object('total_participantes', 5, 'tipo', 'mixto')
    )
    RETURNING id INTO v_participants_general_id;

    INSERT INTO participants (
        participants_general_id,
        participant_actor,
        participant_entity,
        interest_expectative,
        rol,
        contribution_conflicts
    )
    VALUES
        (v_participants_general_id, 'Alcaldia municipal', 'Municipio de La Plata', 'Cumplir metas de cobertura y calidad del agua rural', 'Ejecutor', 'Debe asegurar cierre financiero, supervision y articulacion institucional.'),
        (v_participants_general_id, 'Juntas administradoras del acueducto', 'Acueductos veredales priorizados', 'Contar con infraestructura confiable y asistencia tecnica', 'Operador comunitario', 'Requieren fortalecimiento organizacional para operar el sistema.'),
        (v_participants_general_id, 'Hogares rurales', 'Comunidad beneficiaria', 'Recibir agua apta para consumo con mejor continuidad', 'Beneficiario', 'Existe expectativa alta por resultados y preocupacion por interrupciones temporales durante la obra.'),
        (v_participants_general_id, 'Autoridad ambiental', 'CAM Huila', 'Garantizar uso sostenible de la fuente hidrica', 'Regulador', 'Exige cumplimiento ambiental y manejo adecuado de vertimientos.'),
        (v_participants_general_id, 'Gobernacion del Huila', 'Secretaria de Vias e Infraestructura / Agua', 'Apoyar cierre tecnico y financiero del proyecto', 'Cofinanciador', 'Puede condicionar aportes al cumplimiento de requisitos MGA y estudios previos.');

    INSERT INTO problems (
        project_id,
        central_problem,
        current_description,
        magnitude_problem,
        problem_tree_json
    )
    VALUES (
        v_project_id,
        'Deficiente prestacion del servicio de agua potable en centros poblados rurales del municipio de La Plata',
        'Los centros poblados priorizados presentan captaciones deterioradas, redes con fugas, almacenamiento insuficiente y tratamiento incompleto. La continuidad promedio del servicio es inferior a 12 horas al dia y se registran quejas recurrentes por turbiedad y baja presion.',
        'Se estiman 1450 hogares afectados. Las perdidas de agua superan el 35 por ciento, la continuidad es menor al estandar esperado y solo una parte del caudal distribuido cumple condiciones estables de potabilidad.',
        json_build_object(
            'problema_central', 'Deficiente prestacion del servicio de agua potable',
            'causas_directas', json_build_array('Infraestructura deteriorada del sistema', 'Debil capacidad de operacion y mantenimiento'),
            'efectos_directos', json_build_array('Afectaciones en salud publica', 'Mayores costos y tiempos para acceso al agua')
        )
    )
    RETURNING id INTO v_problem_id;

    INSERT INTO direct_causes (problem_id, description)
    VALUES (v_problem_id, 'Infraestructura de captacion, conduccion, tratamiento y distribucion con rezago tecnico y alto deterioro')
    RETURNING id INTO v_direct_cause_1_id;

    INSERT INTO direct_causes (problem_id, description)
    VALUES (v_problem_id, 'Limitada capacidad de gestion comunitaria para operacion, mantenimiento y control de perdidas')
    RETURNING id INTO v_direct_cause_2_id;

    INSERT INTO indirect_causes (direct_cause_id, description)
    VALUES
        (v_direct_cause_1_id, 'Ausencia de reposicion oportuna de tuberias, valvulas y estructuras de almacenamiento'),
        (v_direct_cause_1_id, 'Tratamiento insuficiente por equipos obsoletos y baja automatizacion'),
        (v_direct_cause_2_id, 'Escasa asistencia tecnica y financiera a los operadores comunitarios'),
        (v_direct_cause_2_id, 'No se cuenta con planes actualizados de micromedicion, mantenimiento y gestion del riesgo');

    INSERT INTO direct_effects (problem_id, description)
    VALUES (v_problem_id, 'Incremento del riesgo sanitario por consumo de agua no apta y almacenamiento inseguro en los hogares')
    RETURNING id INTO v_direct_effect_1_id;

    INSERT INTO direct_effects (problem_id, description)
    VALUES (v_problem_id, 'Mayores costos economicos y de tiempo para las familias por interrupciones frecuentes del servicio')
    RETURNING id INTO v_direct_effect_2_id;

    INSERT INTO indirect_effects (direct_effect_id, description)
    VALUES
        (v_direct_effect_1_id, 'Mayor incidencia de enfermedades gastrointestinales y afectaciones en poblacion infantil y adulta mayor'),
        (v_direct_effect_1_id, 'Percepcion negativa sobre la gestion institucional del servicio publico rural'),
        (v_direct_effect_2_id, 'Reduccion del tiempo disponible para actividades productivas y de cuidado'),
        (v_direct_effect_2_id, 'Dependencia de fuentes alternas con mayor costo y menor confiabilidad');

    INSERT INTO objectives (project_id, general_problem, general_objective)
    VALUES (
        v_project_id,
        'Deficiente prestacion del servicio de agua potable en centros poblados rurales del municipio de La Plata',
        'Mejorar la continuidad, calidad y eficiencia del servicio de agua potable en los centros poblados rurales priorizados del municipio de La Plata'
    )
    RETURNING id INTO v_objective_id;

    INSERT INTO value_chains (project_id, name)
    VALUES (v_project_id, 'Cadena de valor del mejoramiento del acueducto rural')
    RETURNING id INTO v_value_chain_id;

    INSERT INTO value_chain_objectives (project_id, value_chain_id, name)
    VALUES (v_project_id, v_value_chain_id, 'Rehabilitar la infraestructura de captacion, tratamiento y almacenamiento')
    RETURNING id INTO v_value_chain_objective_1_id;

    INSERT INTO value_chain_objectives (project_id, value_chain_id, name)
    VALUES (v_project_id, v_value_chain_id, 'Optimizar las redes de distribucion y control de perdidas')
    RETURNING id INTO v_value_chain_objective_2_id;

    INSERT INTO value_chain_objectives (project_id, value_chain_id, name)
    VALUES (v_project_id, v_value_chain_id, 'Fortalecer la gestion tecnica y comunitaria del servicio')
    RETURNING id INTO v_value_chain_objective_3_id;

    INSERT INTO objectives_causes (
        objective_id,
        type,
        cause_related,
        specifics_objectives,
        cause_id,
        value_chain_objective_id
    )
    VALUES
        (v_objective_id, 'directa', 'Infraestructura de captacion, conduccion, tratamiento y distribucion con rezago tecnico y alto deterioro', 'Recuperar los componentes fisicos criticos del sistema para asegurar potabilidad y continuidad', v_direct_cause_1_id, v_value_chain_objective_1_id),
        (v_objective_id, 'directa', 'Limitada capacidad de gestion comunitaria para operacion, mantenimiento y control de perdidas', 'Fortalecer procedimientos de operacion, mantenimiento y sostenibilidad del servicio', v_direct_cause_2_id, v_value_chain_objective_3_id),
        (v_objective_id, 'indirecta', 'Ausencia de reposicion oportuna de tuberias, valvulas y estructuras de almacenamiento', 'Reducir perdidas tecnicas y mejorar la presion en la red de distribucion', v_direct_cause_1_id, v_value_chain_objective_2_id);

    INSERT INTO objectives_indicator (
        objective_id,
        indicator,
        unit,
        meta,
        source_type,
        source_validation
    )
    VALUES
        (v_objective_id, 'Continuidad promedio del servicio de agua potable', 'Horas por dia', 22.0, 'Reporte operacional', 'Actas de seguimiento del operador y supervison municipal'),
        (v_objective_id, 'Indice de agua no contabilizada', 'Porcentaje', 20.0, 'Balance hidrico', 'Informes tecnicos del proyecto'),
        (v_objective_id, 'Hogares con servicio mejorado de acueducto rural', 'Hogar', 1450.0, 'Censo de usuarios', 'Acta de recibo y verificacion en campo');

    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = 'population'
          AND column_name = 'population_number_affected'
    ) THEN
        INSERT INTO population (
            project_id,
            population_type_affected,
            population_number_affected,
            population_info_affected,
            population_type_intervention,
            population_number_intervention,
            population_info_intervention,
            population_json
        )
        VALUES (
            v_project_id,
            'Hogares rurales con servicio deficiente de agua potable',
            1450,
            'Diagnostico municipal de agua rural 2025',
            'Hogares de centros poblados priorizados',
            980,
            'Base de usuarios validada por la administracion municipal y operadores comunitarios',
            json_build_object(
                'grupos_poblacionales', json_build_object('hogares_rurales', 1450, 'instituciones_educativas', 3, 'puestos_de_salud', 2),
                'enfoques', json_build_object('mujeres_jefas_de_hogar', 312, 'adultos_mayores', 188, 'poblacion_ninez', 524)
            )
        )
        RETURNING id INTO v_population_id;
    ELSE
        INSERT INTO population (
            project_id,
            population_type_affected,
            number_affected,
            source_information_affected,
            population_type_intervention,
            number_intervention,
            source_information_intervention,
            population_json
        )
        VALUES (
            v_project_id,
            'Hogares rurales con servicio deficiente de agua potable',
            1450,
            'Diagnostico municipal de agua rural 2025',
            'Hogares de centros poblados priorizados',
            980,
            'Base de usuarios validada por la administracion municipal y operadores comunitarios',
            json_build_object(
                'grupos_poblacionales', json_build_object('hogares_rurales', 1450, 'instituciones_educativas', 3, 'puestos_de_salud', 2),
                'enfoques', json_build_object('mujeres_jefas_de_hogar', 312, 'adultos_mayores', 188, 'poblacion_ninez', 524)
            )
        )
        RETURNING id INTO v_population_id;
    END IF;

    INSERT INTO affected_population (population_id, region, department, city, population_center, location_entity)
    VALUES
        (v_population_id, 'Centro Sur', 'Huila', 'La Plata', 'San Vicente', 'Centro poblado San Vicente'),
        (v_population_id, 'Centro Sur', 'Huila', 'La Plata', 'Monserrate', 'Centro poblado Monserrate'),
        (v_population_id, 'Centro Sur', 'Huila', 'La Plata', 'El Triunfo', 'Centro poblado El Triunfo');

    INSERT INTO intervention_population (population_id, region, department, city, population_center, location_entity)
    VALUES
        (v_population_id, 'Centro Sur', 'Huila', 'La Plata', 'San Vicente', 'Sistema de acueducto San Vicente'),
        (v_population_id, 'Centro Sur', 'Huila', 'La Plata', 'Monserrate', 'Sistema de acueducto Monserrate'),
        (v_population_id, 'Centro Sur', 'Huila', 'La Plata', 'El Triunfo', 'Sistema de acueducto El Triunfo');

    INSERT INTO alternatives_general (project_id, solution_alternatives, cost, profitability)
    VALUES (v_project_id, TRUE, TRUE, TRUE)
    RETURNING id INTO v_alternatives_general_id;

    INSERT INTO alternatives (alternative_id, name, active, state)
    VALUES
        (v_alternatives_general_id, 'Alternativa 1: Rehabilitacion integral del sistema con obras en captacion, PTAP, almacenamiento, redes y fortalecimiento comunitario', TRUE, 'seleccionada'),
        (v_alternatives_general_id, 'Alternativa 2: Abastecimiento mediante carrotanques y tanques temporales con mantenimiento menor de la red existente', FALSE, 'descartada'),
        (v_alternatives_general_id, 'Alternativa 3: Construccion de un sistema completamente nuevo sin aprovechar infraestructura existente', FALSE, 'descartada');

    INSERT INTO technical_analysis (project_id, analysis)
    VALUES (
        v_project_id,
        'La alternativa seleccionada es tecnicamente viable porque permite aprovechar estructuras existentes recuperables, reducir perdidas, mejorar la desinfeccion y fortalecer la operacion comunitaria. Los estudios preliminares muestran disponibilidad hidrica suficiente, necesidad de reposicion parcial de redes y viabilidad para ejecutar las obras sin suspender totalmente el servicio mediante fases de intervencion.'
    );

    INSERT INTO localization_general (
        project_id,
        administrative_political_factors,
        proximity_to_target_population,
        proximity_to_supply_sources,
        communications,
        land_cost_and_availability,
        public_services_availability,
        labor_availability_and_cost,
        tax_and_legal_structure,
        environmental_factors,
        gender_equity_impact,
        transport_means_and_costs,
        public_order,
        other_factors,
        topography
    )
    VALUES (
        v_project_id,
        TRUE,
        TRUE,
        TRUE,
        TRUE,
        TRUE,
        TRUE,
        TRUE,
        FALSE,
        TRUE,
        TRUE,
        TRUE,
        TRUE,
        FALSE,
        TRUE
    )
    RETURNING id INTO v_localization_general_id;

    INSERT INTO localization (
        localization_general_id,
        region,
        department,
        city,
        type_group,
        "group",
        entity,
        georeferencing,
        latitude,
        longitude
    )
    VALUES
        (v_localization_general_id, 'Centro Sur', 'Huila', 'La Plata', 'Rural', 'Corregimiento San Vicente', 'Bocatoma principal', TRUE, 2.3925, -75.9074),
        (v_localization_general_id, 'Centro Sur', 'Huila', 'La Plata', 'Rural', 'Corregimiento Monserrate', 'Tanque de almacenamiento', TRUE, 2.4011, -75.8968),
        (v_localization_general_id, 'Centro Sur', 'Huila', 'La Plata', 'Rural', 'Corregimiento El Triunfo', 'Red de distribucion sectorizada', TRUE, 2.4098, -75.8846);

    INSERT INTO requirements_general (project_id, requirements_analysis)
    VALUES (
        v_project_id,
        'El estudio de necesidades identifica requerimientos de obra civil, equipos de tratamiento, accesorios hidraulicos, macromedicion, asistencia tecnica y fortalecimiento organizacional. La demanda se proyecto con base en crecimiento poblacional moderado y metas de continuidad del servicio para los proximos diez anos.'
    )
    RETURNING id INTO v_requirements_general_id;

    INSERT INTO requirements (
        requirements_general_id,
        good_service_name,
        good_service_description,
        supply_description,
        demand_description,
        unit_of_measure,
        start_year,
        end_year,
        last_projected_year
    )
    VALUES
        (v_requirements_general_id, 'Sistema de captacion y tratamiento rehabilitado', 'Intervencion de bocatoma, desarenador, PTAP compacta y sistemas de cloracion', 'La infraestructura actual opera con limitaciones tecnicas y equipos obsoletos', 'Se requiere garantizar caudal y calidad para los usuarios priorizados', 'Unidad', 2026, 2027, 2036),
        (v_requirements_general_id, 'Redes de distribucion optimizadas', 'Reposicion de tuberias criticas, valvulas, accesorios y control de fugas', 'La red presenta perdidas elevadas y sectores con baja presion', 'Se requiere mejorar continuidad, presion y eficiencia hidraulica', 'Unidad', 2026, 2027, 2036),
        (v_requirements_general_id, 'Fortalecimiento de la operacion comunitaria', 'Capacitacion, protocolos, herramientas y acompanamiento tecnico a operadores', 'La gestion actual es reactiva y con baja estandarizacion', 'Se requiere sostenibilidad operativa y administrativa del servicio', 'Unidad', 2026, 2027, 2036);

    INSERT INTO products (
        project_id,
        value_chain_objective_id,
        measured_through,
        quantity,
        cost,
        stage,
        description
    )
    VALUES (
        v_project_id,
        v_value_chain_objective_1_id,
        'Componentes del sistema rehabilitados',
        3,
        1650000000,
        'Inversion',
        'Rehabilitacion de bocatoma, planta de tratamiento y almacenamiento principal'
    )
    RETURNING id INTO v_product_1_id;

    INSERT INTO products (
        project_id,
        value_chain_objective_id,
        measured_through,
        quantity,
        cost,
        stage,
        description
    )
    VALUES (
        v_project_id,
        v_value_chain_objective_2_id,
        'Kilometros de red optimizados',
        18,
        1320000000,
        'Inversion',
        'Reposicion y sectorizacion de redes con control de fugas y presion'
    )
    RETURNING id INTO v_product_2_id;

    INSERT INTO products (
        project_id,
        value_chain_objective_id,
        measured_through,
        quantity,
        cost,
        stage,
        description
    )
    VALUES (
        v_project_id,
        v_value_chain_objective_3_id,
        'Operadores fortalecidos',
        3,
        230000000,
        'Inversion',
        'Fortalecimiento tecnico, administrativo y comunitario de los operadores del servicio'
    )
    RETURNING id INTO v_product_3_id;

    INSERT INTO activities (project_id, product_id, cost, stage, description)
    VALUES
        (v_project_id, v_product_1_id, 180000000, 'Preinversion', 'Actualizacion de estudios, disenos hidraulicos y diagnostico estructural del sistema'),
        (v_project_id, v_product_1_id, 1470000000, 'Inversion', 'Ejecucion de obras de rehabilitacion en captacion, tratamiento y almacenamiento'),
        (v_project_id, v_product_2_id, 220000000, 'Preinversion', 'Levantamiento topografico, catastro de redes y modelacion hidraulica'),
        (v_project_id, v_product_2_id, 1100000000, 'Inversion', 'Reposicion de tuberias, instalacion de valvulas, macromedidores y sectorizacion'),
        (v_project_id, v_product_3_id, 80000000, 'Preinversion', 'Diseno del plan de fortalecimiento organizacional y operativo'),
        (v_project_id, v_product_3_id, 150000000, 'Inversion', 'Capacitacion, acompanamiento tecnico y dotacion basica para operacion y mantenimiento');

    INSERT INTO development_plans (
        project_id,
        program,
        national_development_plan,
        departmental_or_sectoral_development_plan,
        strategy_departmental,
        program_departmental,
        district_or_municipal_development_plan,
        strategy_district,
        program_district,
        community_type,
        ethnic_group_planning_instruments,
        other_development_plan,
        strategy_other,
        program_other
    )
    VALUES (
        v_project_id,
        'Agua potable y saneamiento basico para el bienestar rural',
        'Plan Nacional de Desarrollo 2022-2026',
        'Plan Departamental de Desarrollo del Huila 2024-2027',
        'Territorios con infraestructura social y servicios basicos',
        'Fortalecimiento del acceso al agua potable en zonas rurales',
        'Plan de Desarrollo Municipal de La Plata 2024-2027',
        'La Plata rural con servicios publicos dignos',
        'Mejoramiento del acueducto rural y gestion comunitaria del agua',
        NULL,
        NULL,
        'Plan de aseguramiento de la prestacion rural',
        'Sostenibilidad operativa de sistemas rurales',
        'Asistencia tecnica y gestion del riesgo del recurso hidrico'
    )
    RETURNING id INTO v_development_plan_id;

    INSERT INTO pnds (development_plan_id, transformation, pillar, catalyst, component)
    VALUES
        (v_development_plan_id, 'Convergencia regional', 'Seguridad humana y justicia social', 'Acceso a servicios basicos', 'Agua potable rural'),
        (v_development_plan_id, 'Ordenamiento del territorio', 'Transformacion productiva sostenible', 'Gestion del agua', 'Infraestructura de acueducto comunitario');

    RAISE NOTICE 'Proyecto MGA creado con id=%', v_project_id;
END $$;

COMMIT;

-- La tabla characteristics_population se excluye a proposito porque el usuario indico
-- que esos registros se crean de forma predeterminada.
-- Las tablas product_catalogs y pnd_details tampoco se insertan aqui porque se cargan
-- automaticamente desde CSV al iniciar la aplicacion y no dependen del proyecto.

-- Verificacion rapida sugerida:
-- SELECT p.id, p.name FROM projects p WHERE p.name = 'Mejoramiento integral del sistema de acueducto rural en el municipio de La Plata';
-- SELECT COUNT(*) AS participantes FROM participants WHERE participants_general_id IN (SELECT id FROM participants_general WHERE project_id = (SELECT id FROM projects WHERE name = 'Mejoramiento integral del sistema de acueducto rural en el municipio de La Plata'));
-- SELECT COUNT(*) AS productos FROM products WHERE project_id = (SELECT id FROM projects WHERE name = 'Mejoramiento integral del sistema de acueducto rural en el municipio de La Plata');