from rest_framework.filters import BaseFilterBackend
from django.db.models import Count, Subquery, IntegerField, OuterRef


class ContactListOrderingBackend(BaseFilterBackend):
    ALLOWED_ORDERING_FIELDS = ['first_name', 'last_name', 'phone_number', 'email']

    def filter_queryset(self, request, queryset, view):
        ordering = request.query_params.get('ordering', None)
        if ordering is None:
            return queryset.order_by("-created_at")

        desc = ordering[0] == "-"
        order_field = ordering[1:] if desc else ordering
        if order_field not in self.ALLOWED_ORDERING_FIELDS:
            return queryset.order_by("-created_at")

        if order_field == "phone_number":
            """
                Ordering phone number by most used to least used
                @NOTE: We are querying for each ROW phone number count,
                - This can be slow for huge queries
            """

            phone_counts = queryset.values('phone_number').annotate(nc=Count('phone_number'))
            phone_number_count_sub_annotation = Subquery(
                queryset=phone_counts.fiter(
                    phone_number=OuterRef('phone_number')
                ).values('nc')[:1],
                output_field=IntegerField()
            )
            queryset = queryset.annotate(phone_number_count=phone_number_count_sub_annotation)

            if desc:
                order_by = "-phone_number_count"
            else:
                order_by = "phone_number_count"

            queryset = queryset.order_by(order_by)
        else:
            queryset = queryset.order_by(ordering)

        return queryset
