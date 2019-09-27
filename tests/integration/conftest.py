from time import sleep
from os import devnull
from subprocess import Popen, check_call
from tempfile import NamedTemporaryFile
import socket

import pytest
import py.path

from librouteros import connect
from librouteros.exceptions import LibRouterosError
from librouteros.login import (
    plain,
    token,
)

DEV_NULL = open(devnull, 'w')
VERSION_LOGIN = {'6.43rc21': plain, '6.33.3': token}


def api_session(login_method):
    last_exc = None
    for x in range(30):
        try:
            return connect(
                host='127.0.0.1',
                port=8728,
                username='admin',
                password='',
                login_method=login_method,
            )
        except (LibRouterosError, socket.error, socket.timeout) as exc:
            last_exc = exc
            sleep(1)
    raise RuntimeError('Could not connect to device. Last exception {}'.format(last_exc))


@pytest.fixture(scope='session', params=VERSION_LOGIN.keys())
def disk_image(request):
    """Create a temporary disk image backed by original one."""
    img = NamedTemporaryFile()
    request.addfinalizer(img.close)
    # Path to backing image must be absolute or relative to new image
    backing_img = str(py.path.local().join('images/routeros_{}.qcow2'.format(request.param)))
    cmd = [
        'qemu-img',
        'create',
        '-f',
        'qcow2',
        '-b',
        backing_img,
        img.name,
    ]
    check_call(cmd, stdout=DEV_NULL)
    return (img.name, request.param)


@pytest.fixture(scope='session')
def routeros(request, disk_image):
    image, version = disk_image
    # -accel hvf works on mac and -accel kvm for linux
    cmd = [
        'qemu-system-x86_64',
        '-m',
        '64',
        '-display',
        'none',
        '-hda',
        image,
        '-net',
        'user,hostfwd=tcp::8728-:8728',
        '-net',
        'nic,model=e1000',
        '-cpu',
        'max',
        '-accel',
        'kvm',
    ]
    proc = Popen(cmd, stdout=DEV_NULL, close_fds=True)
    request.addfinalizer(proc.kill)
    return api_session(login_method=VERSION_LOGIN[version])
