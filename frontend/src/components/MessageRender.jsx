// MessageRenderer.jsx
import React from 'react';
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

const MessageRenderer = ({ text }) => {
    return (
        <div className="message-markdown">
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
                {text}
            </ReactMarkdown>
        </div>
    );
};

export default MessageRenderer;
