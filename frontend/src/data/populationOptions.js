// data/populationOptions.js
import entidadesCsv from "./entidades_territoriales.csv?raw";

function buildOptionsFromCsv(csv) {
    const lines = csv.split("\n").slice(1).filter((l) => l.trim());
    const regionsSet = new Set();
    const departments = {};
    const cities = {};

    for (const line of lines) {
        const [region, department, city] = line.split(";").map((s) => s.trim());
        if (!region || !department) continue;

        regionsSet.add(region);

        if (!departments[region]) departments[region] = new Set();
        departments[region].add(department);

        if (city) {
            if (!cities[department]) cities[department] = new Set();
            cities[department].add(city);
        }
    }

    // Convert sets to sorted arrays
    const regions = [...regionsSet].sort();
    const deptObj = {};
    for (const [region, deptSet] of Object.entries(departments)) {
        deptObj[region] = [...deptSet].sort();
    }
    const cityObj = {};
    for (const [dept, citySet] of Object.entries(cities)) {
        cityObj[dept] = [...citySet].sort();
    }

    return { regions, departments: deptObj, cities: cityObj };
}

const { regions, departments, cities } = buildOptionsFromCsv(entidadesCsv);

const populationOptions = {
    regions,
    departments,
    cities,
    populationCenters: ["Rural", "Urbano"],
    locationEntities: ["Indígena", "Afrodescendiente", "ROM", "Otro"],
};

export default populationOptions;
