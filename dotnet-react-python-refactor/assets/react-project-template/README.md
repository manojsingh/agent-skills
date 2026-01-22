# React Project Template Structure

This document outlines the recommended React project structure for applications migrated from .NET.

## Directory Structure

```
frontend/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── api/
│   │   └── client.js              # Axios client configuration
│   ├── components/
│   │   ├── common/                # Reusable components
│   │   │   ├── Button.jsx
│   │   │   ├── Input.jsx
│   │   │   └── Modal.jsx
│   │   ├── layout/                # Layout components
│   │   │   ├── Header.jsx
│   │   │   ├── Footer.jsx
│   │   │   └── Sidebar.jsx
│   │   └── features/              # Feature-specific components
│   │       ├── products/
│   │       │   ├── ProductCard.jsx
│   │       │   ├── ProductList.jsx
│   │       │   └── ProductForm.jsx
│   │       └── auth/
│   │           ├── LoginForm.jsx
│   │           └── RegisterForm.jsx
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useProducts.js
│   │   └── useApiError.js
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── Products.jsx
│   │   ├── ProductDetail.jsx
│   │   └── Login.jsx
│   ├── services/
│   │   ├── authService.js
│   │   ├── productService.js
│   │   └── userService.js
│   ├── store/                     # State management (if using Redux/Zustand)
│   │   ├── slices/
│   │   │   ├── authSlice.js
│   │   │   └── productsSlice.js
│   │   └── store.js
│   ├── utils/
│   │   ├── constants.js
│   │   ├── helpers.js
│   │   └── validators.js
│   ├── styles/
│   │   ├── globals.css
│   │   └── theme.js
│   ├── App.jsx
│   ├── index.jsx
│   └── routes.jsx
├── .env.example
├── .gitignore
├── package.json
├── README.md
└── tailwind.config.js             # If using Tailwind CSS
```

## Key Files

### src/index.jsx
```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './api/client';
import App from './App';
import './styles/globals.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
```

### src/App.jsx
```jsx
import { Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Products from './pages/Products';
import Login from './pages/Login';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  return (
    <>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route
            path="/products"
            element={
              <ProtectedRoute>
                <Products />
              </ProtectedRoute>
            }
          />
        </Route>
      </Routes>
      <ToastContainer position="top-right" autoClose={3000} />
    </>
  );
}

export default App;
```

### .env.example
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

### package.json (recommended dependencies)
```json
{
  "name": "frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "@tanstack/react-query": "^5.17.0",
    "axios": "^1.6.5",
    "react-hook-form": "^7.49.3",
    "zod": "^3.22.4",
    "@hookform/resolvers": "^3.3.4",
    "react-toastify": "^10.0.3",
    "zustand": "^4.4.7"
  },
  "devDependencies": {
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.1.5",
    "@testing-library/user-event": "^14.5.1",
    "eslint": "^8.56.0",
    "prettier": "^3.1.1"
  }
}
```

## Initialization Commands

```bash
# Using Create React App
npx create-react-app frontend
cd frontend

# Or using Vite (recommended for faster builds)
npm create vite@latest frontend -- --template react
cd frontend

# Install additional dependencies
npm install react-router-dom @tanstack/react-query axios
npm install react-hook-form zod @hookform/resolvers
npm install react-toastify zustand

# Install dev dependencies
npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm install -D eslint prettier
```

## Best Practices

1. **Component Organization**: Group by feature rather than type
2. **Code Splitting**: Use React.lazy() for route-based code splitting
3. **State Management**: Start with React Query for server state, Context/Zustand for client state
4. **Type Safety**: Consider TypeScript for large applications
5. **Testing**: Write tests alongside components
6. **Styling**: Choose between CSS Modules, Tailwind, or CSS-in-JS early
7. **API Layer**: Centralize API calls in service files
8. **Error Handling**: Use error boundaries and consistent error handling patterns
