import React from 'react';
import PropTypes from 'prop-types';
import './Button.css';

/**
 * Primary UI component for user interaction
 */
const Button = ({ 
  variant = 'primary', 
  size = 'medium', 
  disabled = false, 
  onClick, 
  children,
  type = 'button',
  className = '',
  ...props 
}) => {
  const classNames = [
    'btn',
    `btn--${variant}`,
    `btn--${size}`,
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      type={type}
      className={classNames}
      disabled={disabled}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
};

Button.propTypes = {
  /** Button variant */
  variant: PropTypes.oneOf(['primary', 'secondary', 'danger', 'success', 'outline']),
  /** Button size */
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  /** Disabled state */
  disabled: PropTypes.bool,
  /** Click handler */
  onClick: PropTypes.func,
  /** Button content */
  children: PropTypes.node.isRequired,
  /** Button type */
  type: PropTypes.oneOf(['button', 'submit', 'reset']),
  /** Additional CSS classes */
  className: PropTypes.string,
};

export default Button;
