from django.db import models

__all__ = ()


class DataMagager(models.Manager):
    def _active(self):
        from search.models import Data, ManagedDatabase

        return (
            self.get_queryset()
            .filter(
                **{
                    f"{Data.database.field.name}__"
                    f"{ManagedDatabase.active.field.name}": True,
                    f"{Data.database.field.name}__"
                    f"{ManagedDatabase.is_encrypted.field.name}": True,
                },
            )
            .order_by(
                f"{Data.database.field.name}__"
                f"{ManagedDatabase.name.field.name}",
            )
        )

    def _search_value(self, input_data):
        from search.models import Data

        return (
            self._active()
            .filter(
                **{
                    f"{Data.value.field.name}__iexact": input_data,
                },
            )
            .values(
                Data.database.field.name,
                Data.user_index.field.name,
            )
            .distinct()
        )

    def _search(self, indexes):
        from search.models import Data, ManagedDatabase

        query = models.Q()
        for index in indexes:
            query |= models.Q(
                **{
                    Data.database.field.name: index[Data.database.field.name],
                    Data.user_index.field.name: index[
                        Data.user_index.field.name
                    ],
                },
            )

        if not indexes:
            return self.none()

        return (
            self._active()
            .filter(query)
            .order_by(
                f"{Data.database.field.name}__"
                f"{ManagedDatabase.name.field.name}",
                Data.user_index.field.name,
            )
        )

    def search(self, input_data):
        from search.models import Data, ManagedDatabase

        indexes = list(self._search_value(input_data))

        if not indexes:
            return self.none()

        return (
            self._search(indexes)
            .select_related(Data.database.field.name)
            .only(
                f"{Data.database.field.name}__"
                f"{ManagedDatabase.name.field.name}",
                f"{Data.database.field.name}__"
                f"{ManagedDatabase.history.field.name}",
                Data.database.field.name,
                Data.user_index.field.name,
                Data.column_name.field.name,
                Data.value.field.name,
            )
        )
