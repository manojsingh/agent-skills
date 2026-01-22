import React from 'react';
import PropTypes from 'prop-types';
import './Input.css';

/**
 * Text input component with label and validation
 */
const Input = ({ 
  id,
  name,
  label,
  type = 'text',
  value = '',
  placeholder,
  error,
  disabled = false,
  required = false,
  onChange,
  onBlur,
  className = '',
  ...props 
}) => {
  const inputId = id || `input-${name}`;
  const hasError = Boolean(error);

  return (
    <div className={`input-group ${className}`}>
      {label && (
        <label htmlFor={inputId} className="input-label">
          {label}
          {required && <span className="required">*</span>}
        </label>
      )}
      <input
        id={inputId}
        name={name}
        type={type}
        value={value}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        onChange={onChange}
        onBlur={onBlur}
        className={`input ${hasError ? 'input--error' : ''}`}
        aria-invalid={hasError}
        aria-describedby={hasError ? `${inputId}-error` : undefined}
        {...props}
      />
      {hasError && (
        <span id={`${inputId}-error`} className="input-error" role="alert">
          {error}
        </span>
      )}
    </div>
  );
};

Input.propTypes = {
  /** Input ID */
  id: PropTypes.string,
  /** Input name attribute */
  name: PropTypes.string.isRequired,
  /** Input label */
  label: PropTypes.string,
  /** Input type */
  type: PropTypes.oneOf(['text', 'email', 'password', 'number', 'tel', 'url', 'search']),
  /** Input value */
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  /** Placeholder text */
  placeholder: PropTypes.string,
  /** Error message */
  error: PropTypes.string,
  /** Disabled state */
  disabled: PropTypes.bool,
  /** Required field */
  required: PropTypes.bool,
  /** Change handler */
  onChange: PropTypes.func.isRequired,
  /** Blur handler */
  onBlur: PropTypes.func,
  /** Additional CSS classes */
  className: PropTypes.string,
};

export default Input;
