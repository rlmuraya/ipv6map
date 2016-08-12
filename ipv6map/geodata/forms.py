from django import forms


class LocationFilter(forms.Form):
    """Add filters for Location boundary."""

    north = forms.DecimalField(required=False, min_value=-90, max_value=90)
    south = forms.DecimalField(required=False, min_value=-90, max_value=90)
    east = forms.DecimalField(required=False, min_value=-90, max_value=90)
    west = forms.DecimalField(required=False, min_value=-90, max_value=90)

    def get_filters(self):
        """Transform boundaries into filters to be used with a Location query."""
        if not self.is_valid():
            return None

        boundaries = {}
        if self.cleaned_data.get('north') is not None:
            boundaries['latitude__lte'] = self.cleaned_data['north']
        if self.cleaned_data.get('south') is not None:
            boundaries['latitude__gte'] = self.cleaned_data['south']
        if self.cleaned_data.get('east') is not None:
            boundaries['longitude__lte'] = self.cleaned_data['east']
        if self.cleaned_data.get('west') is not None:
            boundaries['longitude__gte'] = self.cleaned_data['west']
        return boundaries
