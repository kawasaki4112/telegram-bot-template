from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, BigInteger, DateTime, Boolean, ForeignKey, event, Enum as SQLAEnum
from uuid import uuid4
from datetime import datetime
from enum import Enum


class BaseEntity(DeclarativeBase):
    __abstract__ = True

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modified_on: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


@event.listens_for(BaseEntity, "before_update", propagate=True)
def _update_modified_on(mapper, connection, target):
    target.modified_on = datetime.utcnow()


# ENUMERATIONS
class OrderStatus(Enum):
    PENDING = 'PENDING'
    PAID = 'PAID'
    FAILED = 'FAILED'
    COMPLETED = 'COMPLETED'


class PaymentStatus(Enum):
    SUCCEEDED = 'SUCCEEDED'
    FAILED = 'FAILED'


# MODELS
class User(BaseEntity):
    __tablename__ = 'users'

    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    is_banned: Mapped[bool] = mapped_column(Boolean, default=True)

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    downloads: Mapped[list["Download"]] = relationship("Download", back_populates="user")
    licenses: Mapped[list["License"]] = relationship("License", back_populates="assigned_user")


class Product(BaseEntity):
    __tablename__ = 'products'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    files: Mapped[list["ProductFile"]] = relationship(
        "ProductFile", back_populates="product", cascade="all, delete-orphan"
    )
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="product")
    licenses: Mapped[list["License"]] = relationship("License", back_populates="product", cascade="all, delete-orphan")


class ProductFile(BaseEntity):
    __tablename__ = 'product_files'

    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey('products.id', ondelete='CASCADE'), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    checksum: Mapped[str | None] = mapped_column(String(64))

    product: Mapped["Product"] = relationship("Product", back_populates="files")
    downloads: Mapped[list["Download"]] = relationship("Download", back_populates="product_file")


class Order(BaseEntity):
    __tablename__ = 'orders'

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True
    )
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        SQLAEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="orders")
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(BaseEntity):
    __tablename__ = 'order_items'

    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False
    )
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey('products.id'), nullable=False
    )
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
    licenses: Mapped[list["License"]] = relationship("License", back_populates="order_item")
    downloads: Mapped[list["Download"]] = relationship("Download", back_populates="order_item")


class Payment(BaseEntity):
    __tablename__ = 'payments'

    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False
    )
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        SQLAEnum(PaymentStatus), default=PaymentStatus.SUCCEEDED, nullable=False
    )
    transaction_id: Mapped[str | None] = mapped_column(String(255))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime)

    order: Mapped["Order"] = relationship("Order", back_populates="payments")


class License(BaseEntity):
    __tablename__ = 'licenses'

    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey('products.id', ondelete='CASCADE'), nullable=False
    )
    key_value: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    assigned_to_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey('users.id'), nullable=True
    )
    order_item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey('order_items.id'), nullable=True
    )
    issued_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    used_at: Mapped[datetime | None] = mapped_column(DateTime)

    product: Mapped["Product"] = relationship("Product", back_populates="licenses")
    assigned_user: Mapped["User"] = relationship("User", back_populates="licenses")
    order_item: Mapped["OrderItem"] = relationship("OrderItem", back_populates="licenses")


class Download(BaseEntity):
    __tablename__ = 'downloads'

    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey('users.id'), nullable=True
    )
    product_file_id: Mapped[str] = mapped_column(
        String(36), ForeignKey('product_files.id'), nullable=False
    )
    order_item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey('order_items.id'), nullable=True
    )
    downloaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ip_address: Mapped[str | None] = mapped_column(String(45))

    user: Mapped["User"] = relationship("User", back_populates="downloads")
    product_file: Mapped["ProductFile"] = relationship("ProductFile", back_populates="downloads")
    order_item: Mapped["OrderItem"] = relationship("OrderItem", back_populates="downloads")
