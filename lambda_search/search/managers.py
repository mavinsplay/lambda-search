from django.db import models

import search.models


__all__ = ()


class DataMagager(models.Manager):
    def _active(self):
        return (
            self.get_queryset()
            .filter(
                **{
                    f"{search.models.Data.database.field.name}__"
                    f"{search.models.ManagedDatabase.active.field.name}": True,
                    f"{search.models.Data.database.field.name}__"
                    f"{search.models.ManagedDatabase.is_encrypted.field.name}":
                    True,
                },
            )
            .order_by(
                f"{search.models.Data.database.field.name}__"
                f"{search.models.ManagedDatabase.name.field.name}",
            )
        )

    def _search_value(self, input_data):
        return (
            self._active()
            .filter(
                **{
                    f"{search.models.Data.value.field.name}__iexact":
                    input_data,
                },
            )
            .values(
                search.models.Data.database.field.name,
                search.models.Data.user_index.field.name,
            )
            .distinct()
        )

    def _search(self, indexes):
        query = models.Q()
        for index in indexes:
            query |= models.Q(
                **{
                    search.models.Data.database.field.name: index[
                        search.models.Data.database.field.name
                    ],
                    search.models.Data.user_index.field.name: index[
                        search.models.Data.user_index.field.name
                    ],
                },
            )

        if not indexes:
            return self.none()

        return (
            self._active()
            .filter(query)
            .order_by(
                f"{search.models.Data.database.field.name}__"
                f"{search.models.ManagedDatabase.name.field.name}",
                search.models.Data.user_index.field.name,
            )
        )

    def search(self, input_data):
        indexes = list(self._search_value(input_data))

        if not indexes:
            return self.none()

        return (
            self._search(indexes)
            .select_related(search.models.Data.database.field.name)
            .only(
                f"{search.models.Data.database.field.name}__"
                f"{search.models.ManagedDatabase.name.field.name}",
                f"{search.models.Data.database.field.name}__"
                f"{search.models.ManagedDatabase.history.field.name}",
                search.models.Data.database.field.name,
                search.models.Data.user_index.field.name,
                search.models.Data.column_name.field.name,
                search.models.Data.value.field.name,
            )
        )
