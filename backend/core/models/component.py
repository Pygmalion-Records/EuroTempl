"""EuroTempl System
Copyright (c) 2024 Pygmalion Records

Component model implementation for the EuroTempl system.
This model defines the foundational entity for modular components,
encapsulating their core characteristics and properties.
"""

from django.db import models
from django.db.models import JSONField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import uuid
import semver
from django.contrib.gis.db import models as gis_models

class Component(gis_models.Model):
    """
    The Component model represents the foundational entity in the EuroTempl system.
    It defines the core characteristics and properties of modular components that can
    be instantiated in actual designs.

    Attributes:
        id (UUIDField): Unique identifier for the component.
        classification (CharField): Hierarchical classification following EuroTempl naming convention.
        name (CharField): Verb-noun pair describing component purpose.
        version (CharField): Component version following semantic versioning.
        functional_properties (JSONField): Stores acoustic, EMI, and other functional characteristics.
        base_geometry (GeometryField): Base geometric definition using PostGIS.
        core_mission (CharField): Single core mission as per EuroTempl principles.
        is_active (BooleanField): Indicates if component is currently active.
        created_at (DateTimeField): Timestamp of component creation.
        modified_at (DateTimeField): Timestamp of last modification.

    Meta:
        db_table (str): Name of the database table.
        indexes (list): Database indexes for optimized querying.
        constraints (list): Unique constraints for the model.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the component"
    )

    classification = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^ET_[A-Z]{3}_[A-Z]{4}_[A-Z]{3}_\d{3}(_[rv]\d+)?$',
                message="Classification must follow EuroTempl format: ET_XXX_XXXX_XXX_000"
            )
        ],
        help_text="Hierarchical classification following EuroTempl naming convention"
    )

    name = models.CharField(
        max_length=100,
        help_text="Verb-noun pair describing component purpose"
    )

    version = models.CharField(
        max_length=20,
        help_text="Component version following semantic versioning"
    )

    functional_properties = JSONField(
        default=dict,
        help_text="Stores acoustic, EMI, and other functional characteristics"
    )

    base_geometry = gis_models.GeometryField(
        dim=3,
        spatial_index=True,
        help_text="Base geometric definition using PostGIS"
    )

    core_mission = models.CharField(
        max_length=200,
        help_text="Single core mission as per EuroTempl principles"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if component is currently active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta class for Component model.

        Attributes:
            db_table (str): Name of the database table.
            indexes (list): Database indexes for optimized querying.
            constraints (list): Unique constraints for the model.
        """
        db_table = 'et_component'
        indexes = [
            models.Index(fields=['classification']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['classification', 'version'],
                name='unique_component_version'
            )
        ]

    def clean(self):
        """
        Validate the component according to EuroTempl business rules.

        Raises:
            ValidationError: If version, functional properties, or base geometry are invalid.
        """
        try:
            semver.VersionInfo.parse(self.version.lstrip('v'))
        except ValueError:
            raise ValidationError({
                'version': 'Version must follow semantic versioning (MAJOR.MINOR.PATCH)'
            })
    
        required_properties = {'acoustic_rating', 'emi_shield_level'}
        if not all(prop in self.functional_properties for prop in required_properties):
            raise ValidationError({
                'functional_properties': 'Must include acoustic_rating and emi_shield_level'
            })
    
        if self.base_geometry:
            if not hasattr(self.base_geometry, 'coords') or not self.base_geometry.coords:
                raise ValidationError({
                    'base_geometry': 'Geometry must be three-dimensional'
                })
            self._validate_grid_alignment()
    
    def _validate_grid_alignment(self):
        """
        Validate that the geometry aligns with the 25mm base grid system.

        Raises:
            ValidationError: If the geometry does not align with the 25mm grid system.
        """
        if not self.base_geometry:
            return
            
        coords = self.base_geometry.coords
        for coord in coords[0]:  # Check first ring coordinates
            x, y, z = coord
            if any(c % 25 != 0 for c in (x, y)):  # Only check x,y alignment !
                raise ValidationError({
                    'base_geometry': 'Geometry must align with 25mm grid system'
                })

    def save(self, *args, **kwargs):
        """
        Override save to ensure validation is always performed.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Return a string representation of the Component.

        Returns:
            str: A string containing the classification, name, and version of the component.
        """
        return f"{self.classification} - {self.name} (v{self.version})"

    def create_instance(self):
        """
        Create a new ComponentInstance from this component definition.

        Returns:
            ComponentInstance: A new instance of the component.
        """
        from .instance import ComponentInstance, ComponentStatus  # Avoid circular import
        
        last_internal_id = ComponentInstance.objects.all().order_by('-internal_id').first()
        next_internal_id = (last_internal_id.internal_id + 1) if last_internal_id else 1
        
        instance = ComponentInstance.objects.create(
            component=self,
            spatial_data=self.base_geometry,
            spatial_bbox=self.base_geometry.envelope,
            instance_properties={"finish": "matte"},
            status=ComponentStatus.PLANNED.value,
            version=1,
            internal_id=next_internal_id
        )
        return instance

    def get_parameters(self):
        """
        Retrieve all parameters associated with this component.

        Returns:
            QuerySet: A queryset of all parameters associated with this component.
        """
        return self.parameter_set.all()

    def get_material_requirements(self):
        """
        Retrieve all material requirements for this component.

        Returns:
            QuerySet: A queryset of all material requirements for this component.
        """
        return self.materialrequirement_set.all()

    def get_documentation(self):
        """
        Retrieve all documentation associated with this component.

        Returns:
            QuerySet: A queryset of all documentation associated with this component.
        """
        return self.documentation_set.all()