# ORM Migration: Entity Framework to Python

## Entity Framework Core to SQLAlchemy

### Basic Model Mapping

**Entity Framework (C#)**
```csharp
public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }
    public decimal Price { get; set; }
    public DateTime CreatedAt { get; set; }
    public bool IsActive { get; set; }
}

public class AppDbContext : DbContext
{
    public DbSet<Product> Products { get; set; }
}
```

**SQLAlchemy (Python)**
```python
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
```

### Relationships

**One-to-Many (EF)**
```csharp
public class Customer
{
    public int Id { get; set; }
    public string Name { get; set; }
    public List<Order> Orders { get; set; }
}

public class Order
{
    public int Id { get; set; }
    public int CustomerId { get; set; }
    public Customer Customer { get; set; }
    public decimal Total { get; set; }
}
```

**SQLAlchemy**
```python
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    orders = relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    total = Column(Numeric(10, 2))
    customer = relationship("Customer", back_populates="orders")
```

**Many-to-Many (EF)**
```csharp
public class Student
{
    public int Id { get; set; }
    public string Name { get; set; }
    public List<Course> Courses { get; set; }
}

public class Course
{
    public int Id { get; set; }
    public string Title { get; set; }
    public List<Student> Students { get; set; }
}

// In DbContext
modelBuilder.Entity<Student>()
    .HasMany(s => s.Courses)
    .WithMany(c => c.Students)
    .UsingEntity(j => j.ToTable("StudentCourses"));
```

**SQLAlchemy**
```python
from sqlalchemy import Table

# Association table
student_courses = Table('student_courses', Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    courses = relationship("Course", secondary=student_courses, back_populates="students")

class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    students = relationship("Student", secondary=student_courses, back_populates="courses")
```

## Entity Framework to Django ORM

**Entity Framework (C#)**
```csharp
public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }
    public decimal Price { get; set; }
    public int CategoryId { get; set; }
    public Category Category { get; set; }
}

public class Category
{
    public int Id { get; set; }
    public string Name { get; set; }
    public List<Product> Products { get; set; }
}
```

**Django ORM (Python)**
```python
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'categories'

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    class Meta:
        db_table = 'products'
```

## Query Translation

### Simple Queries

**LINQ (C#)**
```csharp
// Get all active products
var products = context.Products
    .Where(p => p.IsActive)
    .ToList();

// Get by ID
var product = context.Products
    .FirstOrDefault(p => p.Id == productId);

// Count
var count = context.Products.Count();
```

**SQLAlchemy**
```python
# Get all active products
products = session.query(Product).filter(Product.is_active == True).all()

# Get by ID
product = session.query(Product).filter(Product.id == product_id).first()

# Count
count = session.query(Product).count()
```

**Django ORM**
```python
# Get all active products
products = Product.objects.filter(is_active=True)

# Get by ID
product = Product.objects.filter(id=product_id).first()
# Or
product = Product.objects.get(pk=product_id)  # Raises DoesNotExist if not found

# Count
count = Product.objects.count()
```

### Complex Queries with Joins

**LINQ (C#)**
```csharp
var results = context.Orders
    .Include(o => o.Customer)
    .Include(o => o.OrderItems)
        .ThenInclude(oi => oi.Product)
    .Where(o => o.Customer.Name.Contains("Smith"))
    .OrderByDescending(o => o.CreatedAt)
    .Take(10)
    .ToList();
```

**SQLAlchemy**
```python
from sqlalchemy.orm import joinedload

results = session.query(Order)\
    .options(joinedload(Order.customer))\
    .options(joinedload(Order.order_items).joinedload(OrderItem.product))\
    .join(Customer)\
    .filter(Customer.name.contains("Smith"))\
    .order_by(Order.created_at.desc())\
    .limit(10)\
    .all()
```

**Django ORM**
```python
results = Order.objects\
    .select_related('customer')\
    .prefetch_related('order_items__product')\
    .filter(customer__name__icontains="Smith")\
    .order_by('-created_at')[:10]
```

### Aggregations

**LINQ (C#)**
```csharp
var stats = context.Orders
    .GroupBy(o => o.CustomerId)
    .Select(g => new {
        CustomerId = g.Key,
        TotalOrders = g.Count(),
        TotalAmount = g.Sum(o => o.Total),
        AverageAmount = g.Average(o => o.Total)
    })
    .ToList();
```

**SQLAlchemy**
```python
from sqlalchemy import func

stats = session.query(
    Order.customer_id,
    func.count(Order.id).label('total_orders'),
    func.sum(Order.total).label('total_amount'),
    func.avg(Order.total).label('average_amount')
)\
.group_by(Order.customer_id)\
.all()
```

**Django ORM**
```python
from django.db.models import Count, Sum, Avg

stats = Order.objects.values('customer_id').annotate(
    total_orders=Count('id'),
    total_amount=Sum('total'),
    average_amount=Avg('total')
)
```

## Data Annotations and Constraints

**Entity Framework Attributes**
```csharp
public class User
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    [MaxLength(100)]
    public string Username { get; set; }
    
    [EmailAddress]
    public string Email { get; set; }
    
    [Range(18, 120)]
    public int Age { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal Balance { get; set; }
}
```

**SQLAlchemy**
```python
from sqlalchemy import CheckConstraint

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False)
    age = Column(Integer, CheckConstraint('age >= 18 AND age <= 120'))
    balance = Column(Numeric(18, 2), default=0)
    
    __table_args__ = (
        CheckConstraint('age >= 18 AND age <= 120', name='age_range_check'),
    )
```

**Django ORM**
```python
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(validators=[EmailValidator()])
    age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(120)])
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
```

## Indexes and Keys

**Entity Framework Fluent API**
```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Product>()
        .HasIndex(p => p.Name)
        .IsUnique();
    
    modelBuilder.Entity<Product>()
        .HasIndex(p => new { p.CategoryId, p.Name });
    
    modelBuilder.Entity<Order>()
        .HasKey(o => new { o.OrderId, o.ProductId });
}
```

**SQLAlchemy**
```python
from sqlalchemy import Index

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    
    __table_args__ = (
        Index('idx_product_name', 'name', unique=True),
        Index('idx_category_name', 'category_id', 'name'),
    )

class Order(Base):
    __tablename__ = 'orders'
    
    order_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, primary_key=True)
```

**Django ORM**
```python
class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    class Meta:
        indexes = [
            models.Index(fields=['name'], name='idx_product_name'),
            models.Index(fields=['category', 'name'], name='idx_category_name'),
        ]
        unique_together = ['category', 'name']
```

## Lazy Loading vs Eager Loading

**Entity Framework**
```csharp
// Lazy loading (requires proxies)
var customer = context.Customers.Find(customerId);
var orders = customer.Orders; // Separate query

// Eager loading
var customer = context.Customers
    .Include(c => c.Orders)
    .FirstOrDefault(c => c.Id == customerId);
```

**SQLAlchemy**
```python
# Lazy loading (default)
customer = session.query(Customer).filter(Customer.id == customer_id).first()
orders = customer.orders  # Separate query

# Eager loading
from sqlalchemy.orm import joinedload
customer = session.query(Customer)\
    .options(joinedload(Customer.orders))\
    .filter(Customer.id == customer_id)\
    .first()
```

**Django ORM**
```python
# Lazy loading (default)
customer = Customer.objects.get(pk=customer_id)
orders = customer.orders.all()  # Separate query

# Eager loading
customer = Customer.objects.prefetch_related('orders').get(pk=customer_id)
# Or for foreign keys
order = Order.objects.select_related('customer').get(pk=order_id)
```

## Transactions

**Entity Framework**
```csharp
using (var transaction = context.Database.BeginTransaction())
{
    try
    {
        context.Products.Add(newProduct);
        context.SaveChanges();
        
        context.Inventory.Add(newInventory);
        context.SaveChanges();
        
        transaction.Commit();
    }
    catch
    {
        transaction.Rollback();
        throw;
    }
}
```

**SQLAlchemy**
```python
from sqlalchemy.exc import SQLAlchemyError

try:
    session.add(new_product)
    session.flush()
    
    session.add(new_inventory)
    session.flush()
    
    session.commit()
except SQLAlchemyError:
    session.rollback()
    raise
```

**Django ORM**
```python
from django.db import transaction

try:
    with transaction.atomic():
        Product.objects.create(name="New Product")
        Inventory.objects.create(product_id=product.id)
except Exception:
    # Transaction automatically rolled back
    raise
```

## Migrations

**Entity Framework Core Migrations**
```bash
dotnet ef migrations add InitialCreate
dotnet ef database update
```

**Alembic (SQLAlchemy)**
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

**Django Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

## Common Patterns

### Repository Pattern

**Entity Framework**
```csharp
public interface IRepository<T> where T : class
{
    Task<T> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();
    Task AddAsync(T entity);
    void Update(T entity);
    void Delete(T entity);
}

public class Repository<T> : IRepository<T> where T : class
{
    private readonly AppDbContext _context;
    private readonly DbSet<T> _dbSet;
    
    public Repository(AppDbContext context)
    {
        _context = context;
        _dbSet = context.Set<T>();
    }
    
    public async Task<T> GetByIdAsync(int id)
    {
        return await _dbSet.FindAsync(id);
    }
    // ... other methods
}
```

**SQLAlchemy**
```python
from typing import Generic, TypeVar, List, Optional
from sqlalchemy.orm import Session

T = TypeVar('T')

class Repository(Generic[T]):
    def __init__(self, session: Session, model: type[T]):
        self.session = session
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[T]:
        return self.session.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self) -> List[T]:
        return self.session.query(self.model).all()
    
    def add(self, entity: T) -> T:
        self.session.add(entity)
        self.session.flush()
        return entity
    
    def delete(self, entity: T):
        self.session.delete(entity)
        self.session.flush()
```

### Unit of Work Pattern

**Entity Framework** (built-in via DbContext)
```csharp
public class UnitOfWork : IUnitOfWork
{
    private readonly AppDbContext _context;
    
    public UnitOfWork(AppDbContext context)
    {
        _context = context;
        Products = new Repository<Product>(_context);
        Orders = new Repository<Order>(_context);
    }
    
    public IRepository<Product> Products { get; }
    public IRepository<Order> Orders { get; }
    
    public async Task<int> SaveChangesAsync()
    {
        return await _context.SaveChangesAsync();
    }
}
```

**SQLAlchemy**
```python
class UnitOfWork:
    def __init__(self, session: Session):
        self.session = session
        self.products = Repository(session, Product)
        self.orders = Repository(session, Order)
    
    def commit(self):
        self.session.commit()
    
    def rollback(self):
        self.session.rollback()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
```

## Type Mapping Reference

| .NET Type | SQL Type | SQLAlchemy | Django |
|-----------|----------|------------|--------|
| int | INT | Integer | IntegerField |
| long | BIGINT | BigInteger | BigIntegerField |
| string | VARCHAR | String | CharField |
| decimal | DECIMAL | Numeric | DecimalField |
| float/double | FLOAT | Float | FloatField |
| bool | BOOLEAN | Boolean | BooleanField |
| DateTime | DATETIME | DateTime | DateTimeField |
| Guid | UUID | UUID (PostgreSQL) | UUIDField |
| byte[] | BLOB/VARBINARY | LargeBinary | BinaryField |
| enum | INT (or VARCHAR) | Enum | IntegerChoices |

## Performance Optimization

### N+1 Query Problem

**Problem (EF)**
```csharp
var customers = context.Customers.ToList();
foreach (var customer in customers)
{
    // N+1: Separate query for each customer
    var orderCount = customer.Orders.Count();
}
```

**Solution (EF)**
```csharp
var customers = context.Customers
    .Include(c => c.Orders)
    .ToList();
```

**Solution (SQLAlchemy)**
```python
# Use joinedload or subqueryload
customers = session.query(Customer)\
    .options(joinedload(Customer.orders))\
    .all()
```

**Solution (Django)**
```python
# Use prefetch_related
customers = Customer.objects.prefetch_related('orders').all()
```

### Bulk Operations

**Entity Framework**
```csharp
context.Products.AddRange(newProducts);
context.SaveChanges();
```

**SQLAlchemy**
```python
session.bulk_insert_mappings(Product, [
    {'name': 'Product 1', 'price': 10.00},
    {'name': 'Product 2', 'price': 20.00},
])
session.commit()
```

**Django ORM**
```python
Product.objects.bulk_create([
    Product(name='Product 1', price=10.00),
    Product(name='Product 2', price=20.00),
])
```
