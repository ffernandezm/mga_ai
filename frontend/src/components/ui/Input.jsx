const Input = ({ value, onChange, placeholder, className }) => {
    return (
        <input
            type="text"
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            className={`border p-2 rounded ${className}`}
        />
    );
};

export default Input;
