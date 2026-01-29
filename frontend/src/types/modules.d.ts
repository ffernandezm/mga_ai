/**
 * Declaration file for JSX modules without explicit type definitions
 * This allows importing .jsx files in TypeScript without strict type checking
 */

declare module '*.jsx' {
    import { ReactElement } from 'react';
    const component: () => ReactElement;
    export default component;
}
