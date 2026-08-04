import api from "../services/api";

const PAGE = {
    width: 595.28,
    height: 841.89,
    marginX: 48,
    marginTop: 56,
    marginBottom: 56,
};

const COLORS = {
    navy: [23, 43, 77],
    teal: [23, 113, 122],
    gold: [196, 149, 58],
    text: [45, 55, 72],
    muted: [98, 108, 125],
    line: [214, 220, 229],
    panel: [245, 247, 250],
    white: [255, 255, 255],
};

const LOCATION_FACTOR_LABELS = {
    administrative_political_factors: "Aspectos administrativos y politicos",
    proximity_to_target_population: "Cercania a la poblacion objetivo",
    proximity_to_supply_sources: "Cercania a fuentes de abastecimiento",
    communications: "Comunicaciones",
    land_cost_and_availability: "Costo y disponibilidad de terrenos",
    public_services_availability: "Disponibilidad de servicios publicos domiciliarios",
    labor_availability_and_cost: "Disponibilidad y costo de mano de obra",
    tax_and_legal_structure: "Estructura impositiva y legal",
    environmental_factors: "Factores ambientales",
    gender_equity_impact: "Impacto para la equidad de genero",
    transport_means_and_costs: "Medios y costos de transporte",
    public_order: "Orden publico",
    other_factors: "Otros",
    topography: "Topografia",
};

const META_KEYS = new Set([
    "id",
    "project_id",
    "value_chain_objective_id",
    "product_id",
    "requirements_general_id",
    "localization_general_id",
    "objective_id",
    "created_at",
    "updated_at",
    "createdAt",
    "updatedAt",
    "isEditing",
    "isNew",
]);

function formatDate(value) {
    return new Intl.DateTimeFormat("es-CO", {
        dateStyle: "long",
        timeStyle: "short",
    }).format(value);
}

function formatValue(value) {
    if (value === null || value === undefined || value === "") {
        return "No registra informacion";
    }

    if (typeof value === "boolean") {
        return value ? "Si" : "No";
    }

    if (typeof value === "number") {
        return Number.isInteger(value) ? String(value) : value.toLocaleString("es-CO");
    }

    if (Array.isArray(value)) {
        return value.length ? value.map((item) => formatValue(item)).join(", ") : "No registra informacion";
    }

    return String(value).trim() || "No registra informacion";
}

function buildFilename(projectName) {
    const safeName = String(projectName || "proyecto")
        .normalize("NFD")
        .replace(/[^\w\s-]/g, "")
        .trim()
        .replace(/[\s_-]+/g, "_")
        .toLowerCase();

    return `${safeName || "proyecto"}_resumen_mga.pdf`;
}

async function getResource(url, fallbackValue = null) {
    try {
        const response = await api.get(url);
        return response.data;
    } catch (error) {
        if (error.response?.status === 404) {
            return fallbackValue;
        }
        throw error;
    }
}

function getFirstRecord(value) {
    if (Array.isArray(value)) {
        return value[0] || null;
    }
    return value || null;
}

function cleanRecord(record) {
    if (!record || typeof record !== "object") {
        return record;
    }

    const cleaned = {};

    Object.entries(record).forEach(([key, value]) => {
        if (META_KEYS.has(key) || value === null || value === undefined || value === "") {
            return;
        }

        if (Array.isArray(value)) {
            if (value.length > 0) {
                cleaned[key] = value;
            }
            return;
        }

        if (typeof value === "object") {
            const nested = cleanRecord(value);
            if (nested && Object.keys(nested).length > 0) {
                cleaned[key] = nested;
            }
            return;
        }

        cleaned[key] = value;
    });

    return cleaned;
}

function createPdfWriter(doc) {
    let y = PAGE.marginTop;
    let pageNumber = 1;

    const addPageDecor = () => {
        doc.setDrawColor(...COLORS.line);
        doc.setLineWidth(0.75);
        doc.line(PAGE.marginX, PAGE.height - 28, PAGE.width - PAGE.marginX, PAGE.height - 28);
        doc.setFont("helvetica", "normal");
        doc.setFontSize(9);
        doc.setTextColor(...COLORS.muted);
        doc.text(`MGA IA · Exportacion de proyecto · Pagina ${pageNumber}`, PAGE.marginX, PAGE.height - 14);
    };

    const newPage = () => {
        addPageDecor();
        doc.addPage();
        pageNumber += 1;
        y = PAGE.marginTop;
    };

    const ensureSpace = (heightNeeded = 24) => {
        if (y + heightNeeded > PAGE.height - PAGE.marginBottom) {
            newPage();
        }
    };

    const writeWrappedText = (text, options = {}) => {
        const {
            x = PAGE.marginX,
            fontSize = 11,
            color = COLORS.text,
            width = PAGE.width - PAGE.marginX * 2,
            lineGap = 5,
            fontStyle = "normal",
            topGap = 0,
            bottomGap = 12,
        } = options;

        const normalizedText = formatValue(text);
        const lines = doc.splitTextToSize(normalizedText, width);
        const textHeight = lines.length * (fontSize + lineGap - 2);

        ensureSpace(topGap + textHeight + bottomGap);
        y += topGap;
        doc.setFont("helvetica", fontStyle);
        doc.setFontSize(fontSize);
        doc.setTextColor(...color);
        doc.text(lines, x, y);
        y += textHeight + bottomGap;
    };

    const drawSectionTitle = (title, subtitle) => {
        ensureSpace(72);
        doc.setFillColor(...COLORS.panel);
        doc.roundedRect(PAGE.marginX, y, PAGE.width - PAGE.marginX * 2, 38, 6, 6, "F");
        doc.setFillColor(...COLORS.gold);
        doc.rect(PAGE.marginX, y, 6, 38, "F");
        doc.setFont("helvetica", "bold");
        doc.setFontSize(15);
        doc.setTextColor(...COLORS.navy);
        doc.text(title, PAGE.marginX + 18, y + 16);
        if (subtitle) {
            doc.setFont("helvetica", "normal");
            doc.setFontSize(9.5);
            doc.setTextColor(...COLORS.muted);
            doc.text(subtitle, PAGE.marginX + 18, y + 29);
        }
        y += 52;
    };

    const drawField = (label, value) => {
        writeWrappedText(label, {
            fontSize: 9,
            fontStyle: "bold",
            color: COLORS.teal,
            bottomGap: 4,
        });
        writeWrappedText(value, {
            fontSize: 11,
            color: COLORS.text,
            bottomGap: 10,
        });
    };

    const drawTwoColumnFields = (fields) => {
        const columnGap = 18;
        const columnWidth = (PAGE.width - PAGE.marginX * 2 - columnGap) / 2;

        for (let i = 0; i < fields.length; i += 2) {
            const pair = fields.slice(i, i + 2);
            const lines = pair.map(({ label, value }) => {
                const combined = `${label}: ${formatValue(value)}`;
                return doc.splitTextToSize(combined, columnWidth);
            });

            const rowHeight = Math.max(...lines.map((entry) => entry.length), 1) * 14 + 8;
            ensureSpace(rowHeight + 12);

            pair.forEach(({ label, value }, index) => {
                const x = PAGE.marginX + index * (columnWidth + columnGap);
                doc.setFont("helvetica", "bold");
                doc.setFontSize(9);
                doc.setTextColor(...COLORS.teal);
                doc.text(label, x, y);
                doc.setFont("helvetica", "normal");
                doc.setFontSize(10.5);
                doc.setTextColor(...COLORS.text);
                const wrappedValue = doc.splitTextToSize(formatValue(value), columnWidth);
                doc.text(wrappedValue, x, y + 13);
            });

            y += rowHeight + 2;
        }

        y += 6;
    };

    const drawBullets = (items, level = 0) => {
        if (!items || items.length === 0) {
            writeWrappedText("No registra informacion", { bottomGap: 10 });
            return;
        }

        items.forEach((item) => {
            const label = typeof item === "string" ? item : item?.text || item?.description || JSON.stringify(item);
            const indent = PAGE.marginX + level * 18;
            const width = PAGE.width - indent - PAGE.marginX;
            const lines = doc.splitTextToSize(label, width - 12);
            const height = lines.length * 12 + 6;

            ensureSpace(height + 2);
            doc.setFont("helvetica", "normal");
            doc.setFontSize(10.5);
            doc.setTextColor(...COLORS.text);
            doc.text("•", indent, y);
            doc.text(lines, indent + 10, y);
            y += height;

            const children = item?.children || item?.indirect_causes || item?.indirect_effects || item?.activities;
            if (children?.length) {
                drawBullets(children, level + 1);
            }
        });

        y += 4;
    };

    const drawRecordCards = (items, fieldLabels = {}) => {
        if (!items || items.length === 0) {
            writeWrappedText("No registra informacion", { bottomGap: 10 });
            return;
        }

        items.forEach((item, index) => {
            const cleaned = cleanRecord(item);
            const rows = Object.entries(cleaned || {});
            const cardHeightEstimate = Math.max(56, rows.length * 22 + 28);
            ensureSpace(cardHeightEstimate);
            doc.setFillColor(...COLORS.white);
            doc.setDrawColor(...COLORS.line);
            doc.roundedRect(PAGE.marginX, y, PAGE.width - PAGE.marginX * 2, 18 + rows.length * 18, 6, 6, "FD");
            doc.setFont("helvetica", "bold");
            doc.setFontSize(11);
            doc.setTextColor(...COLORS.navy);
            doc.text(`Registro ${index + 1}`, PAGE.marginX + 14, y + 13);
            y += 28;

            rows.forEach(([key, value]) => {
                const label = fieldLabels[key] || key.replace(/_/g, " ");
                if (Array.isArray(value)) {
                    writeWrappedText(label, {
                        x: PAGE.marginX + 14,
                        fontSize: 9,
                        fontStyle: "bold",
                        color: COLORS.teal,
                        bottomGap: 4,
                    });
                    drawBullets(value, 1);
                    return;
                }

                writeWrappedText(`${label}: ${formatValue(value)}`, {
                    x: PAGE.marginX + 14,
                    width: PAGE.width - PAGE.marginX * 2 - 28,
                    fontSize: 10,
                    color: COLORS.text,
                    bottomGap: 6,
                });
            });

            y += 6;
        });
    };

    const finalize = () => {
        addPageDecor();
    };

    return {
        drawSectionTitle,
        drawField,
        drawTwoColumnFields,
        drawBullets,
        drawRecordCards,
        writeWrappedText,
        ensureSpace,
        finalize,
        getY: () => y,
        setY: (value) => {
            y = value;
        },
    };
}

async function fetchProjectExportData(projectId) {
    const [
        project,
        projectLocalizations,
        developmentPlan,
        problemTree,
        participantsGeneralRaw,
        population,
        objectivesRaw,
        alternativesGeneral,
        requirementsGeneralRaw,
        technicalAnalysis,
        localizationGeneral,
        valueChainObjectivesRaw,
        productsRaw,
        activitiesRaw,
    ] = await Promise.all([
        getResource(`/projects/${projectId}`),
        getResource(`/project_localizations/project/${projectId}`, []),
        getResource(`/development_plans/${projectId}`),
        getResource(`/problems/${projectId}`),
        getResource(`/participants_general/${projectId}`, []),
        getResource(`/population/${projectId}`),
        getResource(`/objectives/${projectId}`, []),
        getResource(`/alternatives_general/${projectId}`),
        getResource(`/requirements_general/${projectId}`, []),
        getResource(`/technical_analysis/project/${projectId}`),
        getResource(`/localization_general/project/${projectId}`),
        getResource(`/value_chain_objectives/`, []),
        getResource(`/products/`, []),
        getResource(`/activities/`, []),
    ]);

    const participantsGeneral = getFirstRecord(participantsGeneralRaw);
    const requirementsGeneral = getFirstRecord(requirementsGeneralRaw);
    const objectives = getFirstRecord(objectivesRaw);

    const projectObjectiveIds = (valueChainObjectivesRaw || [])
        .filter((objective) => objective.project_id === Number(projectId))
        .map((objective) => objective.id);

    const products = (productsRaw || []).filter((product) => projectObjectiveIds.includes(product.value_chain_objective_id));
    const activities = activitiesRaw || [];

    const valueChainObjectives = (valueChainObjectivesRaw || [])
        .filter((objective) => objective.project_id === Number(projectId))
        .map((objective) => ({
            ...objective,
            products: products
                .filter((product) => product.value_chain_objective_id === objective.id)
                .map((product) => ({
                    ...product,
                    activities: activities.filter((activity) => activity.product_id === product.id),
                })),
        }));

    return {
        project,
        projectLocalizations: projectLocalizations || [],
        developmentPlan,
        problemTree,
        participantsGeneral,
        population,
        objectives,
        alternativesGeneral,
        requirementsGeneral,
        technicalAnalysis,
        localizationGeneral,
        valueChainObjectives,
    };
}

export async function exportProjectToPdf(projectId) {
    const { jsPDF } = await import("jspdf");
    const data = await fetchProjectExportData(projectId);
    const doc = new jsPDF({ unit: "pt", format: "a4" });
    const writer = createPdfWriter(doc);

    doc.setFillColor(...COLORS.navy);
    doc.rect(0, 0, PAGE.width, 162, "F");
    doc.setFillColor(...COLORS.gold);
    doc.rect(0, 150, PAGE.width, 12, "F");
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...COLORS.white);
    doc.setFontSize(24);
    doc.text("Resumen Ejecutivo del Proyecto", PAGE.marginX, 70);
    doc.setFontSize(16);
    doc.text(formatValue(data.project?.name), PAGE.marginX, 100);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(11);
    doc.text("Consolidado de la informacion registrada en el frontend de MGA IA", PAGE.marginX, 125);

    writer.setY(200);
    writer.drawTwoColumnFields([
        { label: "Proyecto", value: data.project?.name },
        { label: "Fecha de exportacion", value: formatDate(new Date()) },
        { label: "Sector", value: data.project?.sector },
        { label: "Codigo indicador", value: data.project?.indicator_code },
    ]);
    writer.drawField("Descripcion general", data.project?.description);

    writer.drawSectionTitle("1. Ficha del proyecto", "Datos generales y cobertura territorial inicial");
    writer.drawTwoColumnFields([
        { label: "Proceso", value: data.project?.process },
        { label: "Objeto", value: data.project?.object_desc },
        { label: "Tipo de intervencion", value: data.project?.intervention_type },
        { label: "Tipologia", value: data.project?.project_typology },
        { label: "Producto principal", value: data.project?.main_product },
        { label: "Sector", value: data.project?.sector },
        { label: "Codigo indicador", value: data.project?.indicator_code },
        { label: "Nombre consolidado", value: data.project?.name },
    ]);
    writer.writeWrappedText("Localizaciones del proyecto", {
        fontSize: 10,
        fontStyle: "bold",
        color: COLORS.teal,
        bottomGap: 6,
    });
    writer.drawRecordCards(data.projectLocalizations, {
        region: "Region",
        department: "Departamento",
        municipality: "Municipio",
    });

    writer.drawSectionTitle("2. Plan de desarrollo", "Alineacion con planes y detalle PND");
    writer.drawTwoColumnFields([
        { label: "Programa", value: data.developmentPlan?.program },
        { label: "Plan nacional", value: data.developmentPlan?.national_development_plan },
        { label: "Plan departamental o sectorial", value: data.developmentPlan?.departmental_or_sectoral_development_plan },
        { label: "Estrategia departamental", value: data.developmentPlan?.strategy_departmental },
        { label: "Programa departamental", value: data.developmentPlan?.program_departmental },
        { label: "Plan distrital o municipal", value: data.developmentPlan?.district_or_municipal_development_plan },
        { label: "Estrategia distrital", value: data.developmentPlan?.strategy_district },
        { label: "Programa distrital", value: data.developmentPlan?.program_district },
        { label: "Tipo de comunidad", value: data.developmentPlan?.community_type },
        { label: "Instrumentos de grupos etnicos", value: data.developmentPlan?.ethnic_group_planning_instruments },
        { label: "Otro plan", value: data.developmentPlan?.other_development_plan },
        { label: "Programa de otro plan", value: data.developmentPlan?.program_other },
    ]);
    writer.writeWrappedText("Detalle PND", {
        fontSize: 10,
        fontStyle: "bold",
        color: COLORS.teal,
        bottomGap: 6,
    });
    writer.drawRecordCards(data.developmentPlan?.pnds || [], {
        transformation: "Transformacion",
        pillar: "Pilar",
        catalyst: "Catalizador",
        component: "Componente",
    });

    writer.drawSectionTitle("3. Arbol de problemas", "Sintesis del problema central, causas y efectos");
    writer.drawField("Problema central", data.problemTree?.central_problem);
    writer.drawField("Descripcion actual", data.problemTree?.current_description);
    writer.drawField("Magnitud del problema", data.problemTree?.magnitude_problem);
    writer.writeWrappedText("Causas", {
        fontSize: 10,
        fontStyle: "bold",
        color: COLORS.teal,
        bottomGap: 6,
    });
    writer.drawBullets(data.problemTree?.direct_causes || []);
    writer.writeWrappedText("Efectos", {
        fontSize: 10,
        fontStyle: "bold",
        color: COLORS.teal,
        bottomGap: 6,
    });
    writer.drawBullets(data.problemTree?.direct_effects || []);

    writer.drawSectionTitle("4. Participantes", "Analisis y actores registrados");
    writer.drawField("Analisis de participantes", data.participantsGeneral?.participants_analisis);
    writer.drawRecordCards(data.participantsGeneral?.participants || [], {
        participant_actor: "Actor",
        participant_entity: "Entidad",
        interest_expectative: "Intereses y expectativas",
        rol: "Rol",
        contribution_conflicts: "Contribuciones y conflictos",
    });

    writer.drawSectionTitle("5. Poblacion", "Dimensionamiento, focalizacion y caracterizacion");
    writer.drawTwoColumnFields([
        { label: "Tipo poblacion afectada", value: data.population?.population_type_affected },
        { label: "Cantidad poblacion afectada", value: data.population?.population_number_affected },
        { label: "Fuente poblacion afectada", value: data.population?.population_info_affected },
        { label: "Tipo poblacion intervencion", value: data.population?.population_type_intervention },
        { label: "Cantidad poblacion intervencion", value: data.population?.population_number_intervention },
        { label: "Fuente poblacion intervencion", value: data.population?.population_info_intervention },
    ]);
    writer.drawField("Analisis de poblacion", data.population?.population_json?.analysis);
    writer.writeWrappedText("Poblacion afectada", {
        fontSize: 10,
        fontStyle: "bold",
        color: COLORS.teal,
        bottomGap: 6,
    });
    writer.drawRecordCards(data.population?.affected_population || [], {
        region: "Region",
        department: "Departamento",
        city: "Ciudad",
        population_center: "Centro poblado",
        location_entity: "Entidad de localizacion",
    });
    writer.writeWrappedText("Poblacion de intervencion", {
        fontSize: 10,
        fontStyle: "bold",
        color: COLORS.teal,
        bottomGap: 6,
    });
    writer.drawRecordCards(data.population?.intervention_population || [], {
        region: "Region",
        department: "Departamento",
        city: "Ciudad",
        population_center: "Centro poblado",
        location_entity: "Entidad de localizacion",
    });
    writer.writeWrappedText("Caracteristicas de poblacion", {
        fontSize: 10,
        fontStyle: "bold",
        color: COLORS.teal,
        bottomGap: 6,
    });
    writer.drawRecordCards(data.population?.characteristics_population || []);

    writer.drawSectionTitle("6. Objetivos", "Objetivo general, causas relacionadas e indicadores");
    writer.drawField("Problema general", data.objectives?.general_problem);
    writer.drawField("Objetivo general", data.objectives?.general_objective);
    writer.writeWrappedText("Causas y objetivos especificos", {
        fontSize: 10,
        fontStyle: "bold",
        color: COLORS.teal,
        bottomGap: 6,
    });
    writer.drawRecordCards(data.objectives?.objectives_causes || [], {
        type: "Tipo",
        cause_related: "Causa relacionada",
        specifics_objectives: "Objetivo especifico",
    });
    writer.writeWrappedText("Indicadores", {
        fontSize: 10,
        fontStyle: "bold",
        color: COLORS.teal,
        bottomGap: 6,
    });
    writer.drawRecordCards(data.objectives?.objectives_indicators || [], {
        indicator: "Indicador",
        unit: "Unidad",
        meta: "Meta",
        source_type: "Tipo de fuente",
        source_validation: "Fuente de verificacion",
    });

    writer.drawSectionTitle("7. Alternativas", "Criterios de evaluacion y alternativas registradas");
    writer.drawTwoColumnFields([
        { label: "Soluciones alternativas", value: data.alternativesGeneral?.solution_alternatives },
        { label: "Costo", value: data.alternativesGeneral?.cost },
        { label: "Rentabilidad", value: data.alternativesGeneral?.profitability },
    ]);
    writer.drawRecordCards(data.alternativesGeneral?.alternatives || [], {
        name: "Nombre",
        active: "Activa",
        state: "Estado",
    });

    writer.drawSectionTitle("8. Necesidades", "Analisis de brechas y detalle de bienes o servicios");
    writer.drawField("Analisis general", data.requirementsGeneral?.requirements_analysis || data.requirementsGeneral?.analysis);
    writer.drawRecordCards(data.requirementsGeneral?.requirements || [], {
        good_service_name: "Bien o servicio",
        good_service_description: "Descripcion",
        supply_description: "Oferta",
        demand_description: "Demanda",
        unit_of_measure: "Unidad de medida",
        start_year: "Ano inicial",
        end_year: "Ano final",
        last_projected_year: "Ultimo ano proyectado",
    });

    writer.drawSectionTitle("9. Analisis tecnico", "Sintesis narrativa construida en frontend");
    writer.drawField("Analisis", data.technicalAnalysis?.analysis);

    writer.drawSectionTitle("10. Localizacion", "Factores seleccionados y registros territoriales");
    const selectedFactors = Object.entries(data.localizationGeneral || {})
        .filter(([key, value]) => LOCATION_FACTOR_LABELS[key] && value === true)
        .map(([key]) => LOCATION_FACTOR_LABELS[key]);
    writer.writeWrappedText("Factores marcados", {
        fontSize: 10,
        fontStyle: "bold",
        color: COLORS.teal,
        bottomGap: 6,
    });
    writer.drawBullets(selectedFactors);
    writer.drawRecordCards(data.localizationGeneral?.localizations || [], {
        region: "Region",
        department: "Departamento",
        city: "Ciudad",
        type_group: "Tipo de agrupacion",
        group: "Agrupacion",
        entity: "Entidad",
        georeferencing: "Georreferenciacion",
        latitude: "Latitud",
        longitude: "Longitud",
    });

    writer.drawSectionTitle("11. Cadena de valor", "Objetivos, productos y actividades");
    if (!data.valueChainObjectives.length) {
        writer.writeWrappedText("No registra informacion", { bottomGap: 10 });
    } else {
        data.valueChainObjectives.forEach((objective, index) => {
            writer.writeWrappedText(`Objetivo ${index + 1}: ${formatValue(objective.name)}`, {
                fontSize: 12,
                fontStyle: "bold",
                color: COLORS.navy,
                bottomGap: 8,
            });
            writer.drawRecordCards(objective.products || [], {
                name: "Producto",
                description: "Descripcion",
                measured_through: "Medido a traves de",
                quantity: "Cantidad",
                cost: "Costo",
                stage: "Etapa",
                activities: "Actividades",
            });
        });
    }

    writer.finalize();
    doc.save(buildFilename(data.project?.name));
}