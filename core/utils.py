import json
import importlib
import functools

from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError

import models


def class_to_import_string(cls):
    return '%s.%s' % (cls.__module__, cls.__name__)


def import_from_string(s, **kwargs):
    module_path, attr_name = s.rsplit('.', 1)
    try:
        module = importlib.import_module(module_path)
        return getattr(module, attr_name)
    except (AttributeError, ModuleNotFoundError):
        if 'default' in kwargs:
            return kwargs['default']
        raise


def get_engine_conn_cls(engine: str):
    path = f'core.datasources.{engine}.Connection'
    return import_from_string(path)


def get_engine_introspection_cls(engine: str):
    path = f'core.datasources.{engine}.Introspection'
    return import_from_string(path)


def get_engine_conn_params_schema_cls(engine: str):
    path = f'core.datasources.{engine}.ConnectionParams'
    return import_from_string(path)


def get_engine_error_cls(engine: str):
    path = f'core.datasources.{engine}.Error'
    return import_from_string(path)


def get_ssh_tunnel_error_cls():
    return BaseSSHTunnelForwarderError


def stop_ssh_tunnel_decorator(func, tunnel):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
        finally:
            if tunnel:
                tunnel.stop()
        return ret
    return inner


def get_datasource_conn(datasource: models.DataSource):
    engine = datasource.engine.title
    conn_cls = get_engine_conn_cls(engine)
    settings = json.loads(datasource.settings)
    tunnel = get_ssh_tunnel(datasource)
    if tunnel is not None:
        tunnel.start()
        settings.update({'host': tunnel.local_bind_host, 'port': tunnel.local_bind_port})
    conn = conn_cls(**settings)
    conn.close = stop_ssh_tunnel_decorator(conn.close, tunnel)
    return conn


def get_ssh_tunnel(datasource: models.DataSource):
    if datasource.ssh_tunnel_id is None:
        return
    settings = json.loads(datasource.settings)
    ssh_tunnel = datasource.ssh_tunnel
    return SSHTunnelForwarder(
        ssh_address_or_host=(ssh_tunnel.host, int(ssh_tunnel.port)),
        ssh_username=ssh_tunnel.username,
        ssh_password=ssh_tunnel.password,
        remote_bind_address=(settings['host'], int(settings['port'])),
    )
