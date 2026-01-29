/**
 * Funciones de formateo y transformación
 */

/**
 * Formatear fecha a formato legible
 */
export function formatDate(date: string | Date, locale: string = 'es-ES'): string {
    const d = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat(locale, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    }).format(d);
}

/**
 * Formatear hora
 */
export function formatTime(date: string | Date, locale: string = 'es-ES'): string {
    const d = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat(locale, {
        hour: '2-digit',
        minute: '2-digit',
    }).format(d);
}

/**
 * Formatear fecha y hora
 */
export function formatDateTime(date: string | Date, locale: string = 'es-ES'): string {
    return `${formatDate(date, locale)} ${formatTime(date, locale)}`;
}

/**
 * Truncar texto
 */
export function truncate(text: string, length: number = 100): string {
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}

/**
 * Capitalizar primera letra
 */
export function capitalize(text: string): string {
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

/**
 * Convertir snake_case a Title Case
 */
export function snakeCaseToTitle(text: string): string {
    return text
        .split('_')
        .map((word) => capitalize(word))
        .join(' ');
}

/**
 * Generar slug desde texto
 */
export function slugify(text: string): string {
    return text
        .toLowerCase()
        .trim()
        .replace(/\s+/g, '-')
        .replace(/[^\w-]/g, '');
}

/**
 * Copiar al portapapeles
 */
export async function copyToClipboard(text: string): Promise<boolean> {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch {
        return false;
    }
}

/**
 * Descargar como archivo
 */
export function downloadFile(content: string, filename: string, type: string = 'text/plain'): void {
    const blob = new Blob([content], { type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}
