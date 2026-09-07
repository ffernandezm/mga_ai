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
    assert.match(source, /return response\.data;/);
    assert.doesNotMatch(source, /return response;\s*\/\/ wrapper payload/);
});

test("Objectives consumes direct objective and problem payloads", async () => {
    const source = await readSource("src/components/Objectives.jsx");

    assert.match(source, /const data = await api\.get\(`\/objectives\/\$\{projectId\}`\);/);
    assert.match(source, /const data = await api\.get\(`\/problems\/\$\{projectId\}`\);/);
    assert.match(source, /setGeneralProblem\(data\.central_problem\)/);
    assert.match(source, /setObjectivesCauses\(obj\.objectives_causes \|\| \[\]\)/);
    assert.match(source, /api\.post\(`\/objectives\/\$\{projectId\}\/`, payload\)/);
    assert.doesNotMatch(source, /\b(?:res|response|result)\.data\b/);
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
