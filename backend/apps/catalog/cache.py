from django.core.cache import cache

_VERSION_KEY = "catalog:version"


def _version():
    value = cache.get(_VERSION_KEY)
    if value is None:
        cache.set(_VERSION_KEY, 1, timeout=None)
        return 1
    return int(value)


def catalog_cache_key(*parts):
    return f"catalog:v{_version()}:" + ":".join(str(part) for part in parts)


def invalidate_catalog_cache():
    try:
        cache.set(_VERSION_KEY, _version() + 1, timeout=None)
    except Exception:
        return


def safe_cache_get(key):
    try:
        return cache.get(key)
    except Exception:
        return None


def safe_cache_set(key, value, timeout=30):
    try:
        cache.set(key, value, timeout=timeout)
    except Exception:
        return
