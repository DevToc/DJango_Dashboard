from django.utils.safestring import mark_safe


def tooltip(label, title, placement="top"):
    return mark_safe(
        f'{label}<i  data-toggle="tooltip" data-placement={placement} title="{title}" class="bx bx-info-circle mx-1" aria-hidden="true"></i>'
    )


def get_fiscal_year(year, month):
    if month >= 10:
        return year + 1
    return year


def get_fiscal_quarter(month):
    if month in [10, 11, 12]:
        quarter = 1
    elif month in [1, 2, 3]:
        quarter = 2
    elif month in [4, 5, 6]:
        quarter = 3
    elif month in [7, 8, 9]:
        quarter = 4
    else:
        quarter = None
    return quarter


def calculate_fiscal_year_and_quarter(year, month):
    fiscal_year = get_fiscal_year(year, month)
    fiscal_quarter = get_fiscal_quarter(year, month)
    return fiscal_year, fiscal_quarter


# Example usage
# year = 2022
# month = 9
# fiscal_year, fiscal_quarter = calculate_fiscal_year_and_quarter(year, month)
# print(f"Fiscal year: {fiscal_year}")
# print(f"Fiscal quarter: {fiscal_quarter}")
