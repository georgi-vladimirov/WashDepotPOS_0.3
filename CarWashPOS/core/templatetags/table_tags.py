from django import template

register = template.Library()


@register.inclusion_tag("sortable_table.html")
def sortable_table(queryset, fields, headers=None, table_date=None, table_id="sortable-table", table_caption=None):
    """
    Render a sortable table from a QuerySet.

    Usage in template:
        {% load table_tags %}
        {% sortable_table queryset field_list header_list table_date=date table_id="my-table" %}

    Arguments:
        queryset      — Django QuerySet or any iterable of model instances
        fields        — list of field/attribute names to display (strings)
        headers       — list of column header labels; defaults to field names
        table_date    — optional date/string shown above the table
        table_id      — HTML id for the <table> element (default: "sortable-table")
        table_caption — optional <caption> text

    Each field name may also be a callable attribute (e.g. a property or method
    with no arguments), which will be called automatically.
    """
    rows = []
    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field, "")
            if callable(value):
                value = value()
            row.append(value)
        rows.append(row)

    return {
        "table_headers": headers if headers is not None else fields,
        "table_rows": rows,
        "table_date": table_date,
        "table_id": table_id,
        "table_caption": table_caption,
    }
