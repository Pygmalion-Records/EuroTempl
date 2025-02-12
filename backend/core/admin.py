"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

from django.contrib import admin
from .models import (
    ComponentInstance,
    Connection,
    ConnectionStatus,
    Component,
    Parameter,
    MaterialRequirement,
    Documentation
)

@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('classification', 'name', 'version', 'is_active', 'modified_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('classification', 'name')
    readonly_fields = ('id', 'created_at', 'modified_at')
    fieldsets = (
        ('Core Information', {
            'fields': ('classification', 'name', 'version', 'core_mission')
        }),
        ('Properties', {
            'fields': ('functional_properties', 'base_geometry')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'connection_type', 'status', 'is_structural', 'modified_at')
    list_filter = ('connection_type', 'status', 'is_structural')
    search_fields = ('id', 'instance_1__id', 'instance_2__id')
    readonly_fields = ('id', 'created_at', 'modified_at', 'status_changed_at')
    fieldsets = (
        ('Connection Details', {
            'fields': ('instance_1', 'instance_2', 'connection_type')
        }),
        ('Properties', {
            'fields': ('connection_properties', 'spatial_relationship', 'spatial_bbox')
        }),
        ('Status', {
            'fields': ('status', 'is_structural', 'parent_connection')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'modified_at', 'status_changed_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(ComponentInstance)
class ComponentInstanceAdmin(admin.ModelAdmin):
    list_display = ('internal_id', 'component', 'status', 'version')
    list_filter = ('status', 'created_at')
    search_fields = ('internal_id', 'component__name')
    readonly_fields = ('id', 'created_at', 'modified_at')

@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ('name', 'component')  # Removed parameter_type
    search_fields = ('name', 'component__name')

@admin.register(MaterialRequirement)
class MaterialRequirementAdmin(admin.ModelAdmin):
    list_display = ('component', 'quantity')  # Removed material_type
    search_fields = ('component__name',)

@admin.register(Documentation)
class DocumentationAdmin(admin.ModelAdmin):
    list_display = ('title', 'component')  # Removed doc_type
    search_fields = ('title', 'component__name')