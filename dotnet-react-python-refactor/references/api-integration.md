# API Integration Patterns: React Frontend to Python Backend

## API Client Architecture

### Basic Axios Setup

```javascript
// api/client.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle responses and errors
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Service Layer Pattern

```javascript
// services/productService.js
import apiClient from '../api/client';

class ProductService {
  async getAll(params = {}) {
    return apiClient.get('/products', { params });
  }

  async getById(id) {
    return apiClient.get(`/products/${id}`);
  }

  async create(data) {
    return apiClient.post('/products', data);
  }

  async update(id, data) {
    return apiClient.put(`/products/${id}`, data);
  }

  async delete(id) {
    return apiClient.delete(`/products/${id}`);
  }

  async search(query) {
    return apiClient.get('/products/search', {
      params: { q: query }
    });
  }
}

export const productService = new ProductService();
```

## React Query (TanStack Query) Integration

### Setup
```javascript
// App.jsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

### Using Queries
```javascript
// hooks/useProducts.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productService } from '../services/productService';

export function useProducts(filters = {}) {
  return useQuery({
    queryKey: ['products', filters],
    queryFn: () => productService.getAll(filters),
  });
}

export function useProduct(id) {
  return useQuery({
    queryKey: ['product', id],
    queryFn: () => productService.getById(id),
    enabled: !!id, // Only run if id exists
  });
}

export function useCreateProduct() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => productService.create(data),
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
  });
}

export function useUpdateProduct() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => productService.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['product', id] });
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
  });
}

export function useDeleteProduct() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id) => productService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
  });
}
```

### Component Usage
```jsx
// components/ProductList.jsx
import { useProducts, useDeleteProduct } from '../hooks/useProducts';

function ProductList({ category }) {
  const { data: products, isLoading, error } = useProducts({ category });
  const deleteProduct = useDeleteProduct();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const handleDelete = async (id) => {
    if (window.confirm('Delete this product?')) {
      try {
        await deleteProduct.mutateAsync(id);
        toast.success('Product deleted successfully');
      } catch (err) {
        toast.error('Failed to delete product');
      }
    }
  };

  return (
    <div>
      {products.map(product => (
        <div key={product.id}>
          <h3>{product.name}</h3>
          <p>${product.price}</p>
          <button onClick={() => handleDelete(product.id)}>
            Delete
          </button>
        </div>
      ))}
    </div>
  );
}
```

## Python FastAPI Backend Endpoints

### Basic CRUD Endpoints
```python
# routes/products.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["products"])

class ProductCreate(BaseModel):
    name: str
    price: float
    category_id: int
    description: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    description: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    category_id: int
    description: Optional[str]
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    category: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if category:
        query = query.filter(Product.category_id == category)
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return None
```

## Error Handling

### Python Backend Error Handling
```python
# exceptions.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

class BusinessLogicError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

@app.exception_handler(BusinessLogicError)
async def business_logic_exception_handler(request: Request, exc: BusinessLogicError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )

# Usage
@router.post("/products")
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    if product.price < 0:
        raise BusinessLogicError("Price cannot be negative", status_code=400)
    # ...
```

### React Error Handling
```javascript
// hooks/useApiError.js
import { useState, useCallback } from 'react';
import { toast } from 'react-toastify';

export function useApiError() {
  const [error, setError] = useState(null);

  const handleError = useCallback((err) => {
    let message = 'An unexpected error occurred';

    if (err.response) {
      // Server responded with error
      const { status, data } = err.response;
      
      if (data?.detail) {
        message = Array.isArray(data.detail) 
          ? data.detail.map(e => e.msg).join(', ')
          : data.detail;
      } else if (status === 404) {
        message = 'Resource not found';
      } else if (status === 403) {
        message = 'Access forbidden';
      } else if (status === 500) {
        message = 'Server error';
      }
    } else if (err.request) {
      // Request made but no response
      message = 'Network error - please check your connection';
    }

    setError(message);
    toast.error(message);
    return message;
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return { error, handleError, clearError };
}

// Usage in component
function ProductForm() {
  const createProduct = useCreateProduct();
  const { handleError } = useApiError();

  const onSubmit = async (data) => {
    try {
      await createProduct.mutateAsync(data);
      toast.success('Product created!');
    } catch (err) {
      handleError(err);
    }
  };
}
```

## File Upload Integration

### Python Backend
```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(400, "Invalid file type")
    
    # Validate file size (5MB max)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(400, "File too large")
    
    # Save file
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(contents)
    
    return {"filename": file.filename, "path": file_path}
```

### React Frontend
```jsx
// components/FileUpload.jsx
import { useState } from 'react';
import apiClient from '../api/client';

function FileUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);

    try {
      const response = await apiClient.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setProgress(percentCompleted);
        },
      });

      console.log('Upload successful:', response);
      setFile(null);
      setProgress(0);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!file || uploading}>
        {uploading ? `Uploading ${progress}%` : 'Upload'}
      </button>
    </div>
  );
}
```

## Pagination

### Python Backend
```python
from pydantic import BaseModel
from typing import List, Generic, TypeVar

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

@router.get("/products", response_model=PaginatedResponse[ProductResponse])
async def get_products_paginated(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # Get total count
    total = db.query(Product).count()
    
    # Get paginated results
    products = db.query(Product)\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return {
        "items": products,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }
```

### React Frontend with React Query
```javascript
// hooks/useProductsPaginated.js
import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';

export function useProductsPaginated(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ['products', 'paginated', page, pageSize],
    queryFn: () => apiClient.get('/products', {
      params: { page, page_size: pageSize }
    }),
    keepPreviousData: true, // Keep old data while fetching new
  });
}

// Component
function ProductListPaginated() {
  const [page, setPage] = useState(1);
  const { data, isLoading, isFetching } = useProductsPaginated(page);

  return (
    <div>
      {isLoading ? (
        <div>Loading...</div>
      ) : (
        <>
          <div className={isFetching ? 'opacity-50' : ''}>
            {data.items.map(product => (
              <div key={product.id}>{product.name}</div>
            ))}
          </div>
          
          <div>
            <button 
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Previous
            </button>
            
            <span>Page {page} of {data.total_pages}</span>
            
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page >= data.total_pages}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
```

## WebSocket Integration

### Python Backend (FastAPI)
```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {client_id} left")
```

### React Frontend
```javascript
// hooks/useWebSocket.js
import { useEffect, useRef, useState } from 'react';

export function useWebSocket(url) {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      setMessages(prev => [...prev, event.data]);
    };

    ws.current.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      ws.current?.close();
    };
  }, [url]);

  const sendMessage = (message) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(message);
    }
  };

  return { messages, isConnected, sendMessage };
}

// Usage
function Chat({ clientId }) {
  const { messages, isConnected, sendMessage } = useWebSocket(
    `ws://localhost:8000/ws/${clientId}`
  );
  const [input, setInput] = useState('');

  const handleSend = () => {
    sendMessage(input);
    setInput('');
  };

  return (
    <div>
      <div>Status: {isConnected ? 'Connected' : 'Disconnected'}</div>
      <div>
        {messages.map((msg, i) => (
          <div key={i}>{msg}</div>
        ))}
      </div>
      <input value={input} onChange={(e) => setInput(e.target.value)} />
      <button onClick={handleSend}>Send</button>
    </div>
  );
}
```

## API Versioning

### Python Backend
```python
# v1/routes.py
from fastapi import APIRouter

router_v1 = APIRouter(prefix="/api/v1")

@router_v1.get("/products")
async def get_products_v1():
    return {"version": "1.0", "products": []}

# v2/routes.py
router_v2 = APIRouter(prefix="/api/v2")

@router_v2.get("/products")
async def get_products_v2():
    return {"version": "2.0", "products": [], "enhanced": True}

# main.py
app.include_router(router_v1)
app.include_router(router_v2)
```

### React Frontend
```javascript
// api/client.js
const createApiClient = (version = 'v1') => {
  return axios.create({
    baseURL: `${process.env.REACT_APP_API_URL}/api/${version}`,
  });
};

export const apiV1 = createApiClient('v1');
export const apiV2 = createApiClient('v2');
```
