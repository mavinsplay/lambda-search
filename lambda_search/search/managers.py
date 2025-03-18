import django.db.models

from search import models


__all__ = ()


class DataMagager(django.db.models.Manager):
    def _active(self):
        return (
            self.get_queryset()
            .filter(
                **{
                    f"{models.Data.database.field.name}__"
                    f"{models.ManagedDatabase.active.field.name}": True,
                    f"{models.Data.database.field.name}__"
                    f"{models.ManagedDatabase.is_encrypted.field.name}": True,
                },
            )
            .order_by(
                f"{models.Data.database.field.name}__"
                f"{models.ManagedDatabase.name.field.name}",
            )
        )

    def _search_value(self, input_data):
        return (
            self._active()
            .filter(
                **{
                    f"{models.Data.value.field.name}__iexact": input_data,
                },
            )
            .values(
                models.Data.database.field.name,
                models.Data.user_index.field.name,
            )
            .distinct()
        )

    def _search(self, indexes):
        query = models.Q()
        for index in indexes:
            query |= models.Q(
                **{
                    models.Data.database.field.name: index[
                        models.Data.database.field.name
                    ],
                    models.Data.user_index.field.name: index[
                        models.Data.user_index.field.name
                    ],
                },
            )

        if not indexes:
            return self.none()

        return (
            self._active()
            .filter(query)
            .order_by(
                f"{models.Data.database.field.name}__"
                f"{models.ManagedDatabase.name.field.name}",
                models.Data.user_index.field.name,
            )
        )

    def search(self, input_data):
        indexes = list(self._search_value(input_data))

        if not indexes:
            return self.none()

        return (
            self._search(indexes)
            .select_related(models.Data.database.field.name)
            .only(
                f"{models.Data.database.field.name}__"
                f"{models.ManagedDatabase.name.field.name}",
                f"{models.Data.database.field.name}__"
                f"{models.ManagedDatabase.history.field.name}",
                models.Data.database.field.name,
                models.Data.user_index.field.name,
                models.Data.column_name.field.name,
                models.Data.value.field.name,
            )
        )
