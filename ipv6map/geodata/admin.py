from django.contrib import admin

from . import models


class BaseReadOnlyAdmin(admin.ModelAdmin):
    list_display_links = None

    def has_change_permission(self, request, obj=None):
        return False if obj else True


@admin.register(models.Version)
class VersionAdmin(BaseReadOnlyAdmin):
    list_display = ['publish_date', 'location_count', 'is_active']
    list_filter = ['is_active']

    def location_count(self, obj):
        return obj.location_set.count()


@admin.register(models.Location)
class LocationAdmin(BaseReadOnlyAdmin):
    list_display = ['id', 'latitude', 'longitude', 'density', '_version']
    list_filter = ['version']

    def _version(self, obj):
        return obj.version.publish_date
