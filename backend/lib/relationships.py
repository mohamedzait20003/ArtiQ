"""
Eloquent-style ORM Relationships
Provides Laravel-like relationship patterns for models
"""

import time
from typing import Optional, List, Type, Callable, TYPE_CHECKING


if TYPE_CHECKING:
    from lib.eloquent import Eloquent as Model


class Relationship:
    """Base relationship class"""

    def __init__(
        self,
        related_model: Type['Model'],
        foreign_key: str,
        local_key: str = None
    ):
        """
        Initialize relationship

        Args:
            related_model: The related model class
            foreign_key: The foreign key field name
            local_key: The local key field name (defaults to primary key)
        """
        self.related_model = related_model
        self.foreign_key = foreign_key
        self.local_key = local_key

    def get_results(self, parent: 'Model'):
        """Get relationship results - to be implemented by subclasses"""
        raise NotImplementedError


class BelongsTo(Relationship):
    """
    Belongs To relationship (inverse of Has One/Has Many)
    Example: Session belongs to User
    """

    def __call__(self, parent: 'Model') -> Optional['Model']:
        """
        Execute the relationship query

        Args:
            parent: The parent model instance

        Returns:
            Related model instance or None
        """
        foreign_value = getattr(parent, self.foreign_key, None)
        if not foreign_value:
            return None

        local_key = self.local_key or self.related_model.primary_key()[0]
        return self.related_model.get({local_key: foreign_value})


class HasOne(Relationship):
    """
    Has One relationship (one-to-one)
    Example: User has one Session
    """

    def __init__(
        self,
        related_model: Type['Model'],
        foreign_key: str,
        local_key: str = None,
        filter_callback: Callable = None,
        on_delete: str = 'CASCADE'
    ):
        """
        Initialize Has One relationship

        Args:
            related_model: The related model class
            foreign_key: Foreign key on the related model
            local_key: Local key on this model
            filter_callback: Optional callback for additional filtering
            on_delete: CASCADE, SET_NULL, or RESTRICT
        """
        super().__init__(related_model, foreign_key, local_key)
        self.filter_callback = filter_callback
        self.on_delete = on_delete

    def __call__(self, parent: 'Model') -> Optional['Model']:
        """
        Execute the relationship query

        Args:
            parent: The parent model instance

        Returns:
            Related model instance or None
        """
        local_value = getattr(
            parent,
            self.local_key or parent.primary_key()[0]
        )

        try:
            query = {self.foreign_key: local_value}

            # Apply additional filters if provided
            if self.filter_callback:
                query = self.filter_callback(query, parent)

            # Use Eloquent's get method
            return self.related_model.get(query)
        except Exception as e:
            print(f"Error in HasOne relationship: {e}")
            return None


class HasMany(Relationship):
    """
    Has Many relationship (one-to-many)
    Example: Role has many Users
    """

    def __init__(
        self,
        related_model: Type['Model'],
        foreign_key: str,
        local_key: str = None,
        filter_callback: Callable = None,
        on_delete: str = 'CASCADE'
    ):
        """
        Initialize Has Many relationship

        Args:
            related_model: The related model class
            foreign_key: Foreign key on the related model
            local_key: Local key on this model
            filter_callback: Optional callback for additional filtering
            on_delete: CASCADE, SET_NULL, or RESTRICT
        """
        super().__init__(related_model, foreign_key, local_key)
        self.filter_callback = filter_callback
        self.on_delete = on_delete

    def __call__(self, parent: 'Model') -> List['Model']:
        """
        Execute the relationship query

        Args:
            parent: The parent model instance

        Returns:
            List of related model instances
        """
        local_value = getattr(
            parent,
            self.local_key or parent.primary_key()[0]
        )

        try:
            query = {self.foreign_key: local_value}

            # Apply additional filters if provided
            if self.filter_callback:
                query = self.filter_callback(query, parent)

            # Use Eloquent's where method
            return self.related_model.where(query)
        except Exception as e:
            print(f"Error in HasMany relationship: {e}")
            return []


class HasOneThrough(Relationship):
    """
    Has One Through relationship
    Example: User has one Role through RoleID
    """

    def __init__(
        self,
        related_model: Type['Model'],
        through_key: str,
        foreign_key: str = None
    ):
        """
        Initialize Has One Through relationship

        Args:
            related_model: The final related model class
            through_key: The key on parent that references related model
            foreign_key: The key on related model (defaults to primary key)
        """
        self.related_model = related_model
        self.through_key = through_key
        self.foreign_key = foreign_key

    def __call__(self, parent: 'Model') -> Optional['Model']:
        """
        Execute the relationship query

        Args:
            parent: The parent model instance

        Returns:
            Related model instance or None
        """
        through_value = getattr(parent, self.through_key, None)
        if not through_value:
            return None

        foreign_key = self.foreign_key or self.related_model.primary_key()[0]
        return self.related_model.get({foreign_key: through_value})


def active_session_filter(query: dict, parent: 'Model') -> dict:
    """
    Filter for active sessions only (TTL > current time)

    Args:
        query: The base query dict
        parent: The parent model instance

    Returns:
        Updated query dict with TTL filter
    """
    current_time = int(time.time())
    query['TTL'] = {'$gt': current_time}
    return query


# Convenience functions for common relationship patterns
def belongs_to(
    related_model: Type['Model'],
    foreign_key: str,
    local_key: str = None
) -> BelongsTo:
    """
    Create a BelongsTo relationship

    Args:
        related_model: The related model class
        foreign_key: The foreign key field name
        local_key: The local key field name

    Returns:
        BelongsTo relationship instance
    """
    return BelongsTo(related_model, foreign_key, local_key)


def has_one(
    related_model: Type['Model'],
    foreign_key: str,
    local_key: str = None,
    filter_callback: Callable = None,
    on_delete: str = 'CASCADE'
) -> HasOne:
    """
    Create a HasOne relationship

    Args:
        related_model: The related model class
        foreign_key: Foreign key on the related model
        local_key: Local key on this model
        filter_callback: Optional filter callback
        on_delete: CASCADE, SET_NULL, or RESTRICT

    Returns:
        HasOne relationship instance
    """
    return HasOne(
        related_model,
        foreign_key,
        local_key,
        filter_callback,
        on_delete
    )


def has_many(
    related_model: Type['Model'],
    foreign_key: str,
    local_key: str = None,
    filter_callback: Callable = None,
    on_delete: str = 'CASCADE'
) -> HasMany:
    """
    Create a HasMany relationship

    Args:
        related_model: The related model class
        foreign_key: Foreign key on the related model
        local_key: Local key on this model
        filter_callback: Optional filter callback
        on_delete: CASCADE, SET_NULL, or RESTRICT

    Returns:
        HasMany relationship instance
    """
    return HasMany(
        related_model,
        foreign_key,
        local_key,
        filter_callback,
        on_delete
    )


def has_one_through(
    related_model: Type['Model'],
    through_key: str,
    foreign_key: str = None
) -> HasOneThrough:
    """
    Create a HasOneThrough relationship

    Args:
        related_model: The final related model class
        through_key: The key on parent that references related model
        foreign_key: The key on related model

    Returns:
        HasOneThrough relationship instance
    """
    return HasOneThrough(related_model, through_key, foreign_key)
