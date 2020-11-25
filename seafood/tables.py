import django_tables2 as tables
from seafood.models import SeaFood


class ViewsTable(tables.Table):
    """{"sfd_yyyy": "년", "sfd_mm": "월", "sfd_dd": "일", "sfd_species": "어종", "sfd_orign": "원산지",
         "sfd_standard": "규격", "packing_uint": "포장단위", "quantity": "수량", "highest": "최고가",
         "lowest": "최저가",
         "average": "평균가", }"""

    sfd_yyyy = tables.Column(verbose_name='년도')
    sfd_mm = tables.Column(verbose_name='월')
    sfd_dd = tables.Column(verbose_name='일')
    sfd_species = tables.Column(verbose_name='어종')
    sfd_orign = tables.Column(verbose_name='원산지')
    sfd_standard = tables.Column(verbose_name='규격')
    packing_uint = tables.Column(verbose_name='포장단위')
    quantity = tables.Column(verbose_name='수량')
    highest = tables.Column(verbose_name='최고가')
    lowest = tables.Column(verbose_name='최저가')
    average = tables.Column(verbose_name='평균가')

    class Meta:
        # django_tables2 모듈에서 사용하는 템플릿 사용
        model = SeaFood
        template_name = "django_tables2/bootstrap.html"
        attrs = {
            "th": {
                "_ordering": {
                    "orderable": "sortable",  # Instead of `orderable`
                    "ascending": "ascend",  # Instead of `asc`
                    "descending": "descend"  # Instead of `desc`
                }
            }
        }
        # id 컬럼은 불필요
        fields = ("sfd_yyyy", "sfd_mm", "sfd_dd", "sfd_species", "sfd_orign",
                  "sfd_standard", "packing_uint", "quantity", "highest",
                  "lowest", "average",)
