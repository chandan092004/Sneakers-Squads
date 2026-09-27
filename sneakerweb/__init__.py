try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

try:
    from django.db.backends.mysql.base import DatabaseWrapper
    # Allow MySQL 8.0 with Django 6.1
    DatabaseWrapper.check_database_version_supported = lambda self: None
except Exception:
    pass
