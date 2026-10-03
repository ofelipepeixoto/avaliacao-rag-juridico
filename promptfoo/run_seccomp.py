"""Fallback Linux sem Docker: bloqueio de rede herdado; não é sandbox de arquivos.

Requer libseccomp. Não contorna namespace indisponível com mocks: um filtro
kernel nega sockets de rede e io_uring aos processos Python, shell e Node descendentes.
O opt-out é auxiliar. Fixtures sintéticas e providers locais continuam obrigatórios.
"""
import argparse
import ctypes
import ctypes.util
import errno
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile


def deny_network():
    library = ctypes.util.find_library('seccomp')
    if not library or not sys.platform.startswith('linux'):
        raise RuntimeError('Fallback exige Linux e libseccomp; use o runner Docker')
    seccomp = ctypes.CDLL(library, use_errno=True)
    seccomp.seccomp_init.argtypes = [ctypes.c_uint32]
    seccomp.seccomp_init.restype = ctypes.c_void_p
    seccomp.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    seccomp.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint]
    class Comparison(ctypes.Structure):
        _fields_ = [('arg', ctypes.c_uint), ('op', ctypes.c_int),
                    ('datum_a', ctypes.c_uint64), ('datum_b', ctypes.c_uint64)]
    seccomp.seccomp_rule_add_array.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int,
                                              ctypes.c_uint, ctypes.POINTER(Comparison)]
    seccomp.seccomp_load.argtypes = [ctypes.c_void_p]
    seccomp.seccomp_release.argtypes = [ctypes.c_void_p]
    context = seccomp.seccomp_init(0x7fff0000)  # SCMP_ACT_ALLOW
    if not context:
        raise RuntimeError('Não foi possível criar filtro seccomp')
    try:
        # Unix socketpairs são IPC local usado pelo runtime Rust/SQLite do Promptfoo.
        # Demais famílias são recusadas. connect continua recusado também no Unix,
        # impedindo contato com sockets de proxy/serviços existentes no host.
        comparison = Comparison(0, 1, socket.AF_UNIX, 0)  # SCMP_CMP_NE
        for name in ('socket', 'socketpair'):
            number = seccomp.seccomp_syscall_resolve_name(name.encode())
            if number < 0 or seccomp.seccomp_rule_add_array(context, 0x00050000 | errno.EPERM,
                                                          number, 1, ctypes.byref(comparison)) != 0:
                raise RuntimeError('Não foi possível registrar negação de sockets de rede')
        for name in ('connect', 'sendto', 'sendmsg', 'sendmmsg',
                     'accept', 'accept4', 'socketcall', 'io_uring_setup'):
            number = seccomp.seccomp_syscall_resolve_name(name.encode())
            if number >= 0 and seccomp.seccomp_rule_add(context, 0x00050000 | errno.EPERM, number, 0) != 0:
                raise RuntimeError('Não foi possível registrar negação de rede')
        if seccomp.seccomp_load(context) != 0:
            raise RuntimeError('Filtro seccomp não carregado; avaliação recusada')
    finally:
        seccomp.seccomp_release(context)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Copiar relatório sintético para este arquivo')
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    # Não repassa credenciais do host. Não modifica HOME ou diretórios pessoais.
    with tempfile.TemporaryDirectory(prefix='radar-promptfoo-') as directory:
        environment = {key: os.environ[key] for key in ('PATH', 'LANG', 'LC_ALL') if key in os.environ}
        environment.update({'RADAR_EVAL_WORK_DIR': directory,
                            'RADAR_OFFLINE_GUARD': 'linux_seccomp_socket_denial',
                            'PROMPTFOO_CONFIG_DIR': directory+'/config',
                            'PROMPTFOO_DISABLE_TELEMETRY': '1',
                            'PROMPTFOO_DISABLE_UPDATE': '1', 'PROMPTFOO_DISABLE_SHARING': '1',
                            'PYTHONDONTWRITEBYTECODE': '1'})
        deny_network()
        result = subprocess.run(['sh', str(root/'promptfoo/run_inside.sh')],
                                cwd=root, env=environment, timeout=300)
        if result.returncode == 0 and arguments.output:
            arguments.output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(Path(directory)/'promptfoo-results.json', arguments.output)
        return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
