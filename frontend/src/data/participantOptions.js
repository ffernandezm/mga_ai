const participantOptions = {
    actor: [
        "Departamental",
        "Distrital",
        "Embajada",
        "Empresas industriales y Comerciales del Estado",
        "Municipal",
        "Otro",
    ],
    entidad: {
        Departamental: [
            "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bolívar", "Boyacá",
            "Caldas", "Caquetá", "Casanare", "Cauca", "Cesar", "Chocó",
            "Córdoba", "Cundinamarca", "Guainía", "Guaviare", "Huila",
            "La Guajira", "Magdalena", "Meta", "Nariño", "Norte de Santander",
            "Putumayo", "Quindío", "Risaralda", "San Andrés y Providencia",
            "Santander", "Sucre", "Tolima", "Valle del Cauca", "Vaupés", "Vichada"
        ],
        Distrital: [
            "Barranquilla", "Bogotá", "Buenaventura", "Cartagena", "Santa Marta"
        ],
        Embajada: [
            "Embajada de Colombia en EE.UU.", "Embajada de Colombia en México",
            "Embajada de Colombia en España", "Embajada de Colombia en Alemania",
            "Embajada de Colombia en Brasil"
        ],
        "Empresas industriales y Comerciales del Estado": [
            "Ecopetrol", "Findeter", "Banco Agrario", "ISA", "Fiducoldex"
        ],
        Municipal: [
            "Municipio A", "Municipio B", "Municipio C" // Puedes extenderlo
        ],
        Otro: [
            "Otra entidad 1", "Otra entidad 2"
        ]
    },
    rol: [
        "A favor",
        "En contra",
        "Neutral",
        "No definida"
    ]
};

export default participantOptions;
