import posixpath

from fabric.api import env, puts, sudo, task
from fabric.contrib import files
from fabtools import require, user
from fabtools.files import is_file
from prefab import pipeline, secrets, utils


__all__ = (
    'application_secrets', 'certify', 'recertify', 'firewall',
)


@task
def application_secrets(**kwargs):
    """
    Upload and template the application secrets.
    """
    context = secrets.context('application', **kwargs)
    with user.masquerade('labuser'):
        files.upload_template('project/setup/secrets.tmpl.py', 'secrets.py', context=context)


@task
@pipeline.once
def certify(force=False):
    """
    Generates a self-signed server cert.
    """
    cert_dir = '/etc/nginx/certs/'
    paths = {
        'key': posixpath.join(cert_dir, 'server.key'),
        'crt': posixpath.join(cert_dir, 'server.crt'),
    }

    if not (is_file(paths['key']) and is_file(paths['crt'])) or force:
        require.directory(cert_dir, use_sudo=True)

        config = {'cn': env.host}
        config.update(paths)

        sudo(
            "openssl req -x509 -newkey rsa:2048 -nodes "
            "-keyout %(key)s -out %(crt)s -days 365 "
            "-subj '/CN=%(cn)s'" % config
        )


@task
def recertify():
    """
    Forces regeneration of self-signed server certs.
    """
    certify(force=True)


@task
@pipeline.once
def firewall():
    """
    Configure the host's firewall based on its assigned roles.
    """
    roles = utils.host_roles(env.host)

    if not roles:
        puts("Warning: Host '%s' has no roles" % env.host)
        return

    port_defs = {
        'application': {None: {80, 443, }, },  # None implies the default zone
        'broker': {'internal': {6379, }, },
        'database': {'internal': {5432, }, },
    }

    source_defs = {
        'application': {},
        'broker': {'internal': set(utils.role_hosts('application')), },
        'database': {'internal': set(utils.role_hosts('application')), },
    }

    ports = {}
    sources = {}
    for role in roles:
        # ports.update(port_defs[role])
        # sources.update(source_defs[role])

        # we need to make sure that we update the value, itself not the value for the key.
        for key, value in port_defs[role].items():
            if key not in ports:
                ports[key] = value
            else:
                ports[key].update(value)

        for key, value in source_defs[role].items():
            if key not in sources:
                sources[key] = value
            else:
                sources[key].update(value)

    require.firewall.basic_config(ports, sources)
