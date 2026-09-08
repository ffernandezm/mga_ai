import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import path from "node:path";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const sourceRoot = path.join(frontendRoot, "src");

async function readSource(relativePath) {
    return readFile(path.join(frontendRoot, relativePath), "utf8");
}

test("api wrapper contract returns the Axios payload directly", async () => {
    const runtimeEntryPoint = await readSource("src/services/api.js");
    const source = await readSource("src/services/api.ts");
    assert.equal(runtimeEntryPoint.trim(), "export { default } from './api.ts';");
    assert.match(source, /assertNotHtmlApiResponse\(url, response\)/);
    assert.match(source, /contentType\.includes\('text\/html'\)/);
    assert.match(source, /Expected API JSON response but received HTML/);
    assert.doesNotMatch(source, /return response;\s*\/\/ wrapper payload/);
});

test("production API fallback uses the Nginx proxy instead of localhost", async () => {
    const apiSource = await readSource("src/services/api.ts");
    const constantsSource = await readSource("src/utils/constants.ts");
    const objectivesSource = await readSource("src/components/Objectives.jsx");
    const productionFallback = /import\.meta\.env\.DEV \? 'http:\/\/localhost:8000' : '\/api'/;

    assert.match(apiSource, productionFallback);
    assert.match(apiSource, /baseURL:\s*[\s\S]*defaultApiBaseUrl/);
    assert.match(constantsSource, productionFallback);
    assert.match(objectivesSource, /api\.getClient\(\)\.defaults\.baseURL/);
});

test("Objectives consumes canonical objective and problem payloads", async () => {
    const source = await readSource("src/components/Objectives.jsx");

    assert.match(source, /const data = await api\.get\(`\/objectives\/\$\{projectId\}\/`\);/);
    assert.match(source, /const data = await api\.get\(`\/problems\/\$\{projectId\}`\);/);
    assert.match(source, /setGeneralProblem\(data\.central_problem\)/);
    assert.match(source, /setObjectivesCauses\(obj\.objectives_causes \|\| \[\]\)/);
    assert.match(source, /api\.post\(`\/objectives\/\$\{projectId\}\/`, payload\)/);
    assert.doesNotMatch(source, /api\.get\(`\/objectives\/\$\{projectId\}`\)/);
    assert.doesNotMatch(source, /\b(?:res|response|result)\.data\b/);
});

test("Objectives renders direct and indirect causes without specific objectives", async () => {
    const objective = {
        general_problem: "Problema prueba",
        general_objective: "",
        id: 3,
        project_id: 3,
        objectives_causes: [
            {
                type: "directa",
                cause_related: "Causa directa prueba",
                specifics_objectives: null,
                cause_id: 6,
                id: 13,
                objective_id: 3,
            },
            {
                type: "indirecta",
                cause_related: "Causa indirecta prueba",
                specifics_objectives: null,
                cause_id: 8,
                id: 14,
                objective_id: 3,
            },
        ],
        objectives_indicators: [],
    };
    const source = await readSource("src/components/Objectives.jsx");
    const renderedCauses = objective.objectives_causes.map((cause) => ({
        key: cause.id,
        type: cause.type,
        label: cause.cause_related,
        specificObjective: cause.specifics_objectives ?? "",
    }));

    assert.deepEqual(renderedCauses.map((cause) => cause.label), [
        "Causa directa prueba",
        "Causa indirecta prueba",
    ]);
    assert.deepEqual(renderedCauses.map((cause) => cause.specificObjective), ["", ""]);
    assert.match(source, /objectivesCauses\.map\(c =>/);
    assert.match(source, /c\.cause_related/);
    assert.match(source, /c\.specifics_objectives \?\? ""/);
    assert.match(source, /<tr key=\{c\.id\}>/);
});

test("ProblemsTree consumes direct problem, causes, effects, and update payloads", async () => {
    const source = await readSource("src/components/ProblemsTree.jsx");

    assert.match(source, /const data = await api\.get\(`\/problems\/\$\{projectId\}`\);/);
    assert.match(source, /direct_causes = \[\]/);
    assert.match(source, /indirect_causes \|\| \[\]/);
    assert.match(source, /const data = await api\.put\(`\/problems\/\$\{projectId\}`, jsonData\);/);
    assert.doesNotMatch(source, /\b(?:res|response|result)\.data\b/);
});

test("Formulation consumes direct project and validation payloads", async () => {
    const source = await readSource("src/pages/Formulation.jsx");

    assert.match(source, /const data = await api\.get\(`\/projects\/\$\{id\}`\);/);
    assert.match(source, /const data = await api\.get\(`\/projects\/\$\{id\}\/sections\/validation`\);/);
    assert.match(source, /setReview\(data\)/);
    assert.match(source, /setEvaluationSession\(data\)/);
    assert.doesNotMatch(source, /\b(?:res|response|result)\.data\b/);
});

test("no wrapper consumer uses the old response.data shape", async () => {
    async function collectSourceFiles(directory) {
        const files = [];
        for (const entry of await readdir(directory, { withFileTypes: true })) {
            const entryPath = path.join(directory, entry.name);
            if (entry.isDirectory()) {
                files.push(...await collectSourceFiles(entryPath));
            } else if (entry.isFile() && /\.(jsx?|tsx?)$/.test(entry.name)) {
                files.push(entryPath);
            }
        }
        return files;
    }

    const violations = [];
    for (const filePath of await collectSourceFiles(sourceRoot)) {
        const relativePath = path.relative(frontendRoot, filePath);
        if (relativePath === "src/services/api.ts") continue;
        const source = await readFile(filePath, "utf8");
        if (/\b(?:res|response|result)\.data\b/.test(source)) {
            violations.push(relativePath);
        }
    }

    assert.deepEqual(violations, []);
});

test("frontend objectives routes use canonical FastAPI paths without relying on redirects", async () => {
    const objectivesSource = await readSource("src/components/Objectives.jsx");
    const projectServiceSource = await readSource("src/services/projectService.ts");
    const pdfExportSource = await readSource("src/utils/projectPdfExport.js");

    const canonicalObjectiveCalls = [
        { source: objectivesSource, method: "GET", frontend: "/objectives/${projectId}/", backend: "GET /objectives/{project_id}/" },
        { source: objectivesSource, method: "POST", frontend: "/objectives/${projectId}/", backend: "POST /objectives/{project_id}/" },
        { source: objectivesSource, method: "PUT", frontend: "/objectives/${projectId}/${objectiveId}", backend: "PUT /objectives/{project_id}/{objective_id}" },
        { source: objectivesSource, method: "POST", frontend: "/objectives_causes/", backend: "POST /objectives_causes/" },
        { source: objectivesSource, method: "POST", frontend: "/objectives_indicator/", backend: "POST /objectives_indicator/" },
        { source: projectServiceSource, method: "GET", frontend: "/objectives/${projectId}/", backend: "GET /objectives/{project_id}/" },
        { source: pdfExportSource, method: "GET", frontend: "/objectives/${projectId}/", backend: "GET /objectives/{project_id}/" },
    ];

    for (const contract of canonicalObjectiveCalls) {
        assert.ok(
            contract.source.includes(contract.frontend),
            `${contract.method} frontend ${contract.frontend} must match backend ${contract.backend}`
        );
    }

    assert.doesNotMatch(objectivesSource, /api\.get\(`\/objectives\/\$\{projectId\}`\)/);
    assert.doesNotMatch(projectServiceSource, /apiService\.get<[^\n]*`\/objectives\/\$\{projectId\}`\)/);
    assert.doesNotMatch(pdfExportSource, /getResource\(`\/objectives\/\$\{projectId\}`\)/);
});
