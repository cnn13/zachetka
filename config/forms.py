from django import forms


class BootstrapFormMixin:
    """Добавляет Bootstrap-классы всем полям формы (чтобы форма выглядела как на сайте)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            css = "form-select" if isinstance(widget, forms.Select) else "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {css}".strip()
