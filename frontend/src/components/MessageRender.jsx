// MessageRenderer.jsx
import { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import '../styles/MessageRender.css';

const components = {
    table: ({ children }) => (
        <div className="table-wrapper">
            <table>{children}</table>
        </div>
    ),
};

const remarkLineBreaks = () => (tree) => {
    const replaceBreakTags = (node) => {
        if (!node.children) return;

        node.children = node.children.map((child) => {
            if (child.type === 'html' && /^<br\s*\/?\s*>$/i.test(child.value.trim())) {
                return { type: 'break' };
            }

            replaceBreakTags(child);
            return child;
        });
    };

    replaceBreakTags(tree);
};

const MessageRenderer = memo(({ text }) => {
    return (
        <div className="message-markdown">
            <ReactMarkdown remarkPlugins={[remarkGfm, remarkLineBreaks]} components={components}>
                {text}
            </ReactMarkdown>
        </div>
    );
});

export default MessageRenderer;
