"""EuroTempl System
Copyright (c) 2024 Pygmalion Records

Connection model implementation for the EuroTempl system.
This model manages the relationships and physical connections between component 
instances, implementing a parametric approach to defining connections while 
ensuring compliance with engineering standards.
"""
from django.db.models import Q

from django.utils import timezone
from django.db import models
from django.db.models import JSONField
from django.core.exceptions import ValidationError
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator
import uuid
from enum import Enum

class ConnectionStatus(str, Enum):
    """Enumeration of possible connection statuses."""
    PLANNED = 'planned'
    IN_PROGRESS = 'in_progress'
    COMPLETE = 'complete'
    OBSOLETE = 'obsolete'

    @classmethod
    def choices(cls):
        return [(status.value, status.name) for status in cls]

class ConnectionType(str, Enum):
    """Enumeration of standard connection types."""
    BOLTED = 'bolted'
    SLOTTED = 'slotted'
    WELDED = 'welded'
    SCREWED = 'screwed'
    ADHESIVE = 'adhesive'

    @classmethod
    def choices(cls):
        return [(type.value, type.name) for type in cls]

class Connection(gis_models.Model):
    """
    Represents physical connections between component instances in the EuroTempl system.
    Maintains detailed information about connection types, properties, and spatial relationships
    while ensuring compliance with engineering standards.
    """

    # Core fields
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the connection"
    )

    # Component instance relationships
    instance_1 = models.ForeignKey(
        'ComponentInstance',
        on_delete=models.RESTRICT,
        related_name='connections_as_first',
        help_text="First connected instance"
    )

    instance_2 = models.ForeignKey(
        'ComponentInstance',
        on_delete=models.RESTRICT,
        related_name='connections_as_second',
        help_text="Second connected instance"
    )

    # Connection specifications
    connection_type = models.CharField(
        max_length=50,
        choices=ConnectionType.choices(),
        help_text="Classification of connection type"
    )

    connection_properties = JSONField(
        default=dict,
        help_text="Detailed specifications including fastener details, EMI shielding"
    )

    # Spatial data
    spatial_relationship = gis_models.GeometryField(
        dim=3,
        spatial_index=True,
        help_text="3D geometric representation of connection"
    )

    spatial_bbox = gis_models.PolygonField(
        null=True,
        help_text="Spatial bounding box for quick filtering"
    )

    # Structural properties
    is_structural = models.BooleanField(
        default=False,
        help_text="Indicates if connection is load-bearing"
    )

    # Status and hierarchy
    status = models.CharField(
        max_length=20,
        choices=ConnectionStatus.choices(),
        default=ConnectionStatus.PLANNED.value,
        help_text="Current lifecycle status"
    )

    parent_connection = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Reference to parent connection in hierarchy"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp"
    )

    modified_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp"
    )

    status_changed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When status was last changed"
    )

    class Meta:
        db_table = 'et_connection'
        indexes = [
            models.Index(fields=['connection_type']),
            models.Index(fields=['status']),
            models.Index(fields=['is_structural']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(instance_1_id__lt=models.F('instance_2_id')),
                name='prevent_duplicate_connections'
            )
        ]

    def clean(self):
        """Validate the connection according to EuroTempl business rules."""
        if self.instance_1 and self.instance_2:
            # Ensure instances are different
            if self.instance_1 == self.instance_2:
                raise ValidationError("Cannot create a connection between the same instance")
            
            # Check for existing connections in either direction
            existing = Connection.objects.filter(
                (Q(instance_1=self.instance_1) & Q(instance_2=self.instance_2)) |
                (Q(instance_1=self.instance_2) & Q(instance_2=self.instance_1))
            ).exclude(pk=self.pk)
        
        if existing.exists():
            raise ValidationError("A connection between these instances already exists")
        self._validate_spatial_integrity()
        self._validate_grid_alignment()
        self._validate_property_schema()
        self._validate_emi_continuity()
        self._validate_material_compatibility()
        self._validate_temporal_consistency()

    def _validate_spatial_integrity(self):
        """Ensure geometric data represents a valid 3D connection."""
        if not self.spatial_relationship or not self.spatial_relationship.valid:
            raise ValidationError({
                'spatial_relationship': 'Must provide valid 3D geometric data'
            })

    def _validate_grid_alignment(self):
        """Validate alignment with 25mm base grid."""
        if not self.spatial_relationship:
            return

        coords = self.spatial_relationship.coords
        for coord in coords[0]:
            x, y, z = coord
            if any(c % 25 != 0 for c in (x, y)):
                raise ValidationError({
                    'spatial_relationship': 'Connection points must align with 25mm grid system'
                })

    def _validate_property_schema(self):
        """Validate connection properties conform to type-specific schemas."""
        if not isinstance(self.connection_properties, dict):
            raise ValidationError({
                'connection_properties': 'Properties must be a dictionary'
            })

        required_properties = {
            ConnectionType.BOLTED.value: {'fastener_type', 'torque_spec'},
            ConnectionType.SLOTTED.value: {'slot_size', 'insertion_depth'},
            ConnectionType.WELDED.value: {'weld_type', 'weld_length'},
        }

        if self.connection_type in required_properties:
            missing = required_properties[self.connection_type] - self.connection_properties.keys()
            if missing:
                raise ValidationError({
                    'connection_properties': f'Missing required properties: {missing}'
                })

    def _validate_emi_continuity(self):
        """Validate EMI shielding continuity requirements."""
        if 'emi_shielding' in self.connection_properties:
            if not isinstance(self.connection_properties['emi_shielding'], bool):
                raise ValidationError({
                    'connection_properties': 'EMI shielding must be a boolean value'
                })

    def _validate_material_compatibility(self):
        """Validate material compatibility between connected components."""
        # Implementation would check material compatibility based on 
        # component instance material properties
        pass

    def _validate_temporal_consistency(self):
        """Ensure temporal consistency of timestamps."""
        if self.modified_at and self.created_at and self.modified_at < self.created_at:
            raise ValidationError('Modified timestamp cannot be earlier than created timestamp')

    def update_status(self, new_status):
        """
        Update the connection status and record the timestamp.
        
        Args:
            new_status (str): New status value from ConnectionStatus enum
        """
        valid_statuses = [status.value for status in ConnectionStatus]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")
        
        self.status = new_status
        self.status_changed_at = timezone.now()
        self.save()

    def calculate_bounding_box(self):
        """Calculate and update the spatial bounding box."""
        if self.spatial_relationship:
            self.spatial_bbox = self.spatial_relationship.envelope3d
            self.save(update_fields=['spatial_bbox'])

    def save(self, *args, **kwargs):
        """Override save to ensure validation and bounding box calculation."""
        # Ensure consistent ordering of instances
        if self.instance_1_id > self.instance_2_id:
            self.instance_1_id, self.instance_2_id = self.instance_2_id, self.instance_1_id
        self.full_clean()
        if not self.spatial_bbox and self.spatial_relationship:
            self.calculate_bounding_box()
        super().save(*args, **kwargs)

    def __str__(self):
        """String representation of the connection."""
        return f"Connection {self.id} ({self.connection_type}) between {self.instance_1.id} and {self.instance_2.id}"