from datetime import datetime
from django.db.models import Sum
from django.core.paginator import Paginator
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.urls import reverse

register = template.Library()


@register.filter
def find_methods(value):
    print(dir(value))
    return ""


@register.simple_tag
def get_proper_elided_page_range(p, number, on_each_side=3, on_ends=2):
    paginator = Paginator(p.object_list, p.per_page)
    return paginator.get_elided_page_range(
        number=number, on_each_side=on_each_side, on_ends=on_ends
    )


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    d = context["request"].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()


@register.simple_tag
def breadcrumb(title, url_name=None, *args, **kwargs):
    if url_name:
        result = f'<li class="breadcrumb-item"><a href="{reverse(url_name, args=args, kwargs=kwargs)}" class="align-middle">{title}</a></li><li class="breadcrumb-item"><span class="bx bx-chevron-right align-middle"></span></li>'
    else:
        result = f'<li class="breadcrumb-item active fs-36" aria-current="page">{conditional_escape(title)}</li>'
    return mark_safe(result)


@register.filter
def split(string, seperator=","):
    return string.split(seperator)


@register.filter
def generate_header(l):
    headers = []
    for i in l:
        year = i.get("fiscal_year")
        quarter = i.get("fiscal_quarter")
        headers.append(f"{year} FQ{quarter}")

    return headers


@register.filter
def pvm_filter(queryset):
    current_year = datetime.now().year
    three_years_after = current_year + 3
    queryset = (
        queryset.filter(
            calenderYear__gte=current_year, calenderYear__lte=three_years_after
        )
        .order_by("fiscal_year", "fiscal_quarter")
        .values("fiscal_year", "fiscal_quarter")
        .annotate(quantity=Sum("quantity"))
    )
    return queryset
