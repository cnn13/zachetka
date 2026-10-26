class BootstrapFormMixin:
    """Общее оформление полей без привязки к конкретной форме."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = "form-select" if field.widget.__class__.__name__ == "Select" else "form-control"
            field.widget.attrs["class"] = f"{field.widget.attrs.get('class', '')} {css_class}".strip()
