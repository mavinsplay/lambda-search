__all__ = ()


class DatabaseRouter:
    def db_for_read(self, model, **hints):
        """Определяет базу данных для операций чтения."""
        db_alias = hints.get("db_alias")
        if db_alias:
            return db_alias

        return "default"

    def db_for_write(self, model, **hints):
        """Определяет базу данных для операций записи."""
        db_alias = hints.get("db_alias")
        if db_alias:
            return db_alias

        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """Разрешает отношения между объектами."""
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ограничивает миграции только основной базой данных."""
        return db == "default"
