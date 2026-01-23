# React Component Templates

This directory contains production-ready React component templates that you can use as a starting point when converting .NET views to React components.

## Available Components

### Button (`Button.jsx`)
A flexible button component with multiple variants and sizes.

**Features:**
- Multiple variants: primary, secondary, danger, success, outline
- Three sizes: small, medium, large
- Disabled state
- Type support (button, submit, reset)
- Full accessibility support

**Usage:**
```jsx
import Button from './components/Button';

<Button variant="primary" size="medium" onClick={handleClick}>
  Click Me
</Button>
```

### Input (`Input.jsx`)
A form input component with label, validation, and error handling.

**Features:**
- Multiple input types (text, email, password, number, etc.)
- Label support
- Error message display
- Required field indicator
- Disabled state
- Accessibility with ARIA attributes

**Usage:**
```jsx
import Input from './components/Input';

<Input
  name="email"
  label="Email Address"
  type="email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error={errors.email}
  required
/>
```

### Modal (`Modal.jsx`)
A modal dialog component with overlay.

**Features:**
- Multiple sizes (small, medium, large, fullscreen)
- Header with title and close button
- Body content area
- Optional footer for actions
- Close on escape key
- Close on overlay click (configurable)
- Body scroll prevention
- Smooth animations

**Usage:**
```jsx
import Modal from './components/Modal';
import Button from './components/Button';

const [isOpen, setIsOpen] = useState(false);

<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Confirm Action"
  footer={
    <>
      <Button variant="secondary" onClick={() => setIsOpen(false)}>
        Cancel
      </Button>
      <Button variant="primary" onClick={handleConfirm}>
        Confirm
      </Button>
    </>
  }
>
  <p>Are you sure you want to proceed?</p>
</Modal>
```

## Customization

All components are designed to be easily customizable:

1. **Styling**: Each component has a corresponding CSS file. You can modify these or replace them with your own styling solution (CSS Modules, styled-components, Tailwind, etc.)

2. **Props**: Components use PropTypes for validation. You can extend the props to add more functionality.

3. **Variants**: Add new variants by extending the CSS classes and prop types.

## Integration with Converted Razor Views

When using `convert_razor_to_jsx.py`, you can replace the generated form elements with these components:

**Before (Generated):**
```jsx
<input 
  type="text" 
  name="username" 
  value={props.username || ""} 
  onChange={handleChange} 
/>
```

**After (Using Template):**
```jsx
<Input
  name="username"
  label="Username"
  value={props.username || ""}
  onChange={handleChange}
  error={errors.username}
  required
/>
```

## Best Practices

1. **Accessibility**: All components include ARIA attributes and keyboard support
2. **Validation**: Use the error prop to display validation messages
3. **Consistency**: Use these components throughout your app for consistent UX
4. **Composition**: Combine components to build more complex UIs

## Adding More Components

Consider creating additional components for common patterns:
- Form wrapper component
- Select/Dropdown component
- Checkbox/Radio components
- Table component
- Card component
- Alert/Notification component
- Loading spinner
- Pagination component

## TypeScript

To convert these to TypeScript:
1. Rename files from `.jsx` to `.tsx`
2. Replace PropTypes with TypeScript interfaces
3. Add proper type annotations

Example:
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'outline';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

const Button: React.FC<ButtonProps> = ({ ... }) => { ... };
```
