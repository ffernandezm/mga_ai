import { AlertCircle, X } from "lucide-react";
import { MGA_SECTION_METADATA, MGA_VALIDATION_SECTION_TO_TAB } from "../utils/constants";

function SectionValidationModal({ validation, sectionName, onClose }) {
    if (!validation) return null;

    const pendingItems = [
        ...(validation.missing_fields || []).map((field) => ({
            key: field.key,
            label: field.label,
            path: field.path,
        })),
        ...(validation.blocking_rules || []).map((rule) => ({
            key: rule.key,
            label: rule.message,
        })),
    ];

    if (validation.incomplete_prerequisites?.length) {
        pendingItems.push({
            key: "prerequisites",
            label: `Secciones previas incompletas: ${validation.incomplete_prerequisites
                .map((section) => MGA_SECTION_METADATA[MGA_VALIDATION_SECTION_TO_TAB[section]]?.label || section)
                .join(", ")}`,
        });
    }

    const focusFirstPending = () => {
        const path = validation.missing_fields?.[0]?.path;
        if (!path) return;
        const escaped = window.CSS?.escape ? window.CSS.escape(path) : path;
        const element = document.querySelector(
            `[data-validation-path="${escaped}"], [name="${escaped}"], #${escaped}`
        );
        onClose();
        window.requestAnimationFrame(() => {
            element?.scrollIntoView({ behavior: "smooth", block: "center" });
            element?.focus({ preventScroll: true });
        });
    };

    return (
        <div className="section-validation-backdrop" role="presentation" onMouseDown={onClose}>
            <section
                className="section-validation-modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="section-validation-title"
                onMouseDown={(event) => event.stopPropagation()}
            >
                <header>
                    <AlertCircle aria-hidden="true" />
                    <h2 id="section-validation-title">No puedes continuar todavía</h2>
                    <button className="section-validation-close" onClick={onClose} aria-label="Cerrar">
                        <X aria-hidden="true" />
                    </button>
                </header>
                <p>Completa los campos obligatorios de la sección {sectionName} antes de continuar.</p>
                <ul>
                    {pendingItems.map((item) => <li key={item.key}>{item.label}</li>)}
                </ul>
                <footer>
                    <button
                        className="btn btn-primary"
                        onClick={focusFirstPending}
                        disabled={!validation.missing_fields?.length}
                    >
                        Ir al primer campo pendiente
                    </button>
                    <button className="btn btn-outline-secondary" onClick={onClose}>Cerrar</button>
                </footer>
            </section>
        </div>
    );
}

export default SectionValidationModal;