import React from 'react';
import PropTypes from 'prop-types';
import './Modal.css';

/**
 * Modal dialog component
 */
const Modal = ({ 
  isOpen, 
  onClose, 
  title, 
  children,
  footer,
  size = 'medium',
  closeOnOverlayClick = true,
  showCloseButton = true,
}) => {
  // Close on escape key
  React.useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Prevent body scroll when modal is open
  React.useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget && closeOnOverlayClick) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick} role="dialog" aria-modal="true">
      <div className={`modal modal--${size}`}>
        {(title || showCloseButton) && (
          <div className="modal-header">
            {title && <h2 className="modal-title">{title}</h2>}
            {showCloseButton && (
              <button
                type="button"
                className="modal-close"
                onClick={onClose}
                aria-label="Close modal"
              >
                &times;
              </button>
            )}
          </div>
        )}

        <div className="modal-body">
          {children}
        </div>

        {footer && (
          <div className="modal-footer">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};

Modal.propTypes = {
  /** Whether modal is open */
  isOpen: PropTypes.bool.isRequired,
  /** Close handler */
  onClose: PropTypes.func.isRequired,
  /** Modal title */
  title: PropTypes.string,
  /** Modal content */
  children: PropTypes.node.isRequired,
  /** Footer content (usually buttons) */
  footer: PropTypes.node,
  /** Modal size */
  size: PropTypes.oneOf(['small', 'medium', 'large', 'fullscreen']),
  /** Close on overlay click */
  closeOnOverlayClick: PropTypes.bool,
  /** Show close button */
  showCloseButton: PropTypes.bool,
};

export default Modal;
