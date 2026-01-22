# Testing Strategies for .NET to React + Python Migration

## Python Backend Testing

### Unit Testing with pytest

**Setup**
```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app

@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Create test client with database override"""
    from fastapi.testclient import TestClient
    from app.dependencies import get_db
    
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
```

**Testing Models and Business Logic**
```python
# tests/test_models.py
import pytest
from app.models import Product, Category

def test_create_product(db_session):
    """Test product creation"""
    category = Category(name="Electronics")
    db_session.add(category)
    db_session.commit()
    
    product = Product(
        name="Laptop",
        price=999.99,
        category_id=category.id
    )
    db_session.add(product)
    db_session.commit()
    
    assert product.id is not None
    assert product.name == "Laptop"
    assert product.category.name == "Electronics"

def test_product_price_validation():
    """Test price cannot be negative"""
    with pytest.raises(ValueError):
        Product(name="Test", price=-10.0, category_id=1)
```

**Testing API Endpoints**
```python
# tests/test_products.py
import pytest
from fastapi import status

def test_get_products(client, db_session):
    """Test GET /products endpoint"""
    # Arrange
    category = Category(name="Test Category")
    db_session.add(category)
    db_session.commit()
    
    products = [
        Product(name=f"Product {i}", price=10.0 * i, category_id=category.id)
        for i in range(1, 4)
    ]
    db_session.add_all(products)
    db_session.commit()
    
    # Act
    response = client.get("/api/products")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Product 1"

def test_get_product_by_id(client, db_session):
    """Test GET /products/{id} endpoint"""
    category = Category(name="Test")
    db_session.add(category)
    db_session.commit()
    
    product = Product(name="Test Product", price=99.99, category_id=category.id)
    db_session.add(product)
    db_session.commit()
    
    response = client.get(f"/api/products/{product.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["price"] == 99.99

def test_get_product_not_found(client):
    """Test 404 when product doesn't exist"""
    response = client.get("/api/products/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_product(client, db_session):
    """Test POST /products endpoint"""
    category = Category(name="Test")
    db_session.add(category)
    db_session.commit()
    
    product_data = {
        "name": "New Product",
        "price": 49.99,
        "category_id": category.id,
        "description": "Test description"
    }
    
    response = client.post("/api/products", json=product_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "New Product"
    assert "id" in data

def test_create_product_validation_error(client):
    """Test validation errors on product creation"""
    invalid_data = {
        "name": "",  # Empty name should fail
        "price": -10  # Negative price should fail
    }
    
    response = client.post("/api/products", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_update_product(client, db_session):
    """Test PUT /products/{id} endpoint"""
    category = Category(name="Test")
    db_session.add(category)
    db_session.commit()
    
    product = Product(name="Old Name", price=10.0, category_id=category.id)
    db_session.add(product)
    db_session.commit()
    
    update_data = {"name": "New Name", "price": 20.0}
    response = client.put(f"/api/products/{product.id}", json=update_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "New Name"
    assert data["price"] == 20.0

def test_delete_product(client, db_session):
    """Test DELETE /products/{id} endpoint"""
    category = Category(name="Test")
    db_session.add(category)
    db_session.commit()
    
    product = Product(name="To Delete", price=5.0, category_id=category.id)
    db_session.add(product)
    db_session.commit()
    product_id = product.id
    
    response = client.delete(f"/api/products/{product_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify deletion
    deleted_product = db_session.query(Product).filter(Product.id == product_id).first()
    assert deleted_product is None
```

**Testing Authentication**
```python
# tests/test_auth.py
def test_login_success(client, db_session):
    """Test successful login"""
    # Create test user
    from app.auth import get_password_hash
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password123")
    )
    db_session.add(user)
    db_session.commit()
    
    # Attempt login
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post("/auth/login", data={
        "username": "nonexistent",
        "password": "wrong"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token"""
    response = client.get("/api/protected")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_protected_endpoint_with_token(client, db_session):
    """Test accessing protected endpoint with valid token"""
    # Create and login user
    from app.auth import get_password_hash, create_access_token
    user = User(
        username="testuser",
        hashed_password=get_password_hash("password123")
    )
    db_session.add(user)
    db_session.commit()
    
    token = create_access_token(data={"sub": user.username})
    
    response = client.get(
        "/api/protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
```

### Integration Testing
```python
# tests/test_integration.py
def test_product_workflow(client, db_session):
    """Test complete product CRUD workflow"""
    # Create category first
    category = Category(name="Electronics")
    db_session.add(category)
    db_session.commit()
    
    # 1. Create product
    product_data = {
        "name": "Smartphone",
        "price": 599.99,
        "category_id": category.id
    }
    create_response = client.post("/api/products", json=product_data)
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    
    # 2. Read product
    read_response = client.get(f"/api/products/{product_id}")
    assert read_response.status_code == 200
    assert read_response.json()["name"] == "Smartphone"
    
    # 3. Update product
    update_data = {"price": 499.99}
    update_response = client.put(f"/api/products/{product_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["price"] == 499.99
    
    # 4. Delete product
    delete_response = client.delete(f"/api/products/{product_id}")
    assert delete_response.status_code == 204
    
    # 5. Verify deletion
    verify_response = client.get(f"/api/products/{product_id}")
    assert verify_response.status_code == 404
```

## React Frontend Testing

### Setup with Jest and React Testing Library

**Configuration**
```javascript
// setupTests.js
import '@testing-library/jest-dom';
import { server } from './mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

**Mock Service Worker (MSW) Setup**
```javascript
// mocks/handlers.js
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/products', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        { id: 1, name: 'Product 1', price: 10.0 },
        { id: 2, name: 'Product 2', price: 20.0 },
      ])
    );
  }),

  rest.get('/api/products/:id', (req, res, ctx) => {
    const { id } = req.params;
    return res(
      ctx.status(200),
      ctx.json({ id: parseInt(id), name: 'Product 1', price: 10.0 })
    );
  }),

  rest.post('/api/products', async (req, res, ctx) => {
    const body = await req.json();
    return res(
      ctx.status(201),
      ctx.json({ id: 3, ...body })
    );
  }),

  rest.put('/api/products/:id', async (req, res, ctx) => {
    const { id } = req.params;
    const body = await req.json();
    return res(
      ctx.status(200),
      ctx.json({ id: parseInt(id), ...body })
    );
  }),

  rest.delete('/api/products/:id', (req, res, ctx) => {
    return res(ctx.status(204));
  }),
];

// mocks/server.js
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

### Component Testing

**Testing Simple Components**
```javascript
// ProductCard.test.jsx
import { render, screen } from '@testing-library/react';
import ProductCard from './ProductCard';

describe('ProductCard', () => {
  const mockProduct = {
    id: 1,
    name: 'Test Product',
    price: 99.99,
    description: 'Test description'
  };

  it('renders product information correctly', () => {
    render(<ProductCard product={mockProduct} />);
    
    expect(screen.getByText('Test Product')).toBeInTheDocument();
    expect(screen.getByText('$99.99')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });

  it('calls onDelete when delete button is clicked', () => {
    const handleDelete = jest.fn();
    render(<ProductCard product={mockProduct} onDelete={handleDelete} />);
    
    const deleteButton = screen.getByRole('button', { name: /delete/i });
    deleteButton.click();
    
    expect(handleDelete).toHaveBeenCalledWith(1);
  });
});
```

**Testing Components with API Calls**
```javascript
// ProductList.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ProductList from './ProductList';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const wrapper = ({ children }) => (
  <QueryClientProvider client={createTestQueryClient()}>
    {children}
  </QueryClientProvider>
);

describe('ProductList', () => {
  it('displays loading state initially', () => {
    render(<ProductList />, { wrapper });
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('displays products after loading', async () => {
    render(<ProductList />, { wrapper });
    
    await waitFor(() => {
      expect(screen.getByText('Product 1')).toBeInTheDocument();
      expect(screen.getByText('Product 2')).toBeInTheDocument();
    });
  });

  it('displays error message on API failure', async () => {
    server.use(
      rest.get('/api/products', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    render(<ProductList />, { wrapper });
    
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
```

**Testing Forms**
```javascript
// ProductForm.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProductForm from './ProductForm';

describe('ProductForm', () => {
  it('submits form with correct data', async () => {
    const user = userEvent.setup();
    const handleSubmit = jest.fn();
    
    render(<ProductForm onSubmit={handleSubmit} />);
    
    await user.type(screen.getByLabelText(/name/i), 'New Product');
    await user.type(screen.getByLabelText(/price/i), '49.99');
    await user.type(screen.getByLabelText(/description/i), 'Test desc');
    
    await user.click(screen.getByRole('button', { name: /submit/i }));
    
    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith({
        name: 'New Product',
        price: '49.99',
        description: 'Test desc'
      });
    });
  });

  it('displays validation errors', async () => {
    const user = userEvent.setup();
    render(<ProductForm />);
    
    await user.click(screen.getByRole('button', { name: /submit/i }));
    
    expect(await screen.findByText(/name is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/price is required/i)).toBeInTheDocument();
  });
});
```

**Testing Hooks**
```javascript
// useProducts.test.js
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useProducts, useCreateProduct } from './useProducts';

const wrapper = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useProducts', () => {
  it('fetches products successfully', async () => {
    const { result } = renderHook(() => useProducts(), { wrapper });
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    
    expect(result.current.data).toHaveLength(2);
    expect(result.current.data[0].name).toBe('Product 1');
  });
});

describe('useCreateProduct', () => {
  it('creates product successfully', async () => {
    const { result } = renderHook(() => useCreateProduct(), { wrapper });
    
    const newProduct = {
      name: 'New Product',
      price: 29.99,
      category_id: 1
    };
    
    result.current.mutate(newProduct);
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data.name).toBe('New Product');
  });
});
```

### End-to-End Testing with Cypress

**Setup**
```javascript
// cypress.config.js
module.exports = {
  e2e: {
    baseUrl: 'http://localhost:3000',
    setupNodeEvents(on, config) {},
  },
};
```

**E2E Tests**
```javascript
// cypress/e2e/products.cy.js
describe('Product Management', () => {
  beforeEach(() => {
    // Reset database or use fixtures
    cy.task('db:seed');
    cy.visit('/products');
  });

  it('displays list of products', () => {
    cy.get('[data-testid="product-card"]').should('have.length.at.least', 1);
    cy.contains('Product 1').should('be.visible');
  });

  it('creates a new product', () => {
    cy.get('[data-testid="add-product-btn"]').click();
    
    cy.get('input[name="name"]').type('Cypress Test Product');
    cy.get('input[name="price"]').type('99.99');
    cy.get('textarea[name="description"]').type('Created by Cypress');
    
    cy.get('button[type="submit"]').click();
    
    cy.contains('Product created successfully').should('be.visible');
    cy.contains('Cypress Test Product').should('be.visible');
  });

  it('edits existing product', () => {
    cy.get('[data-testid="product-card"]').first().within(() => {
      cy.get('[data-testid="edit-btn"]').click();
    });
    
    cy.get('input[name="name"]').clear().type('Updated Name');
    cy.get('button[type="submit"]').click();
    
    cy.contains('Product updated successfully').should('be.visible');
    cy.contains('Updated Name').should('be.visible');
  });

  it('deletes product', () => {
    cy.get('[data-testid="product-card"]').first().within(() => {
      cy.get('[data-testid="delete-btn"]').click();
    });
    
    cy.get('[data-testid="confirm-dialog"]').within(() => {
      cy.contains('Delete').click();
    });
    
    cy.contains('Product deleted successfully').should('be.visible');
  });

  it('handles authentication flow', () => {
    cy.visit('/login');
    
    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    
    cy.url().should('include', '/dashboard');
    cy.contains('Welcome, testuser').should('be.visible');
  });
});
```

## Test Coverage

**Generate Coverage Reports**
```bash
# Python
pytest --cov=app --cov-report=html tests/

# React
npm test -- --coverage --watchAll=false
```

**Coverage Thresholds**
```json
// package.json
{
  "jest": {
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

## Testing Best Practices

1. **Follow AAA Pattern**: Arrange, Act, Assert
2. **Test Behavior, Not Implementation**: Focus on what the code does, not how
3. **Use Descriptive Test Names**: Make test purpose clear from the name
4. **Keep Tests Independent**: Each test should run in isolation
5. **Mock External Dependencies**: Database, APIs, file system
6. **Test Error Cases**: Don't just test happy path
7. **Maintain Test Data**: Use fixtures and factories
8. **Regular Test Maintenance**: Keep tests up to date with code changes
9. **Fast Tests**: Unit tests should run quickly
10. **CI/CD Integration**: Run tests automatically on every commit
