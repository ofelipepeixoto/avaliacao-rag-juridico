"""Falha fechada: runtime deve ter somente loopback e bloquear TCP/DNS externo."""
from pathlib import Path
import errno
import os
import socket
if os.environ.get('RADAR_OFFLINE_GUARD') == 'linux_seccomp_socket_denial':
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            socket.socket(family).close()
        except OSError as error:
            if error.errno != errno.EPERM:
                raise SystemExit('Seccomp não comprovado: errno inesperado')
        else:
            raise SystemExit('Seccomp não comprovado: criação de socket permitida')
    unix_socket, peer = socket.socketpair()
    peer.close()
    with unix_socket:
        try:
            unix_socket.connect('/tmp/radar-offline-preflight-does-not-exist')
        except OSError as error:
            if error.errno != errno.EPERM:
                raise SystemExit('Seccomp não comprovado: connect Unix não negado')
        else:
            raise SystemExit('Seccomp não comprovado: conexão Unix permitida')
    print('Seccomp conferido: IPv4/IPv6 e connect Unix negados; IPC socketpair local permitido')
    raise SystemExit(0)
interfaces = {p.name for p in Path('/sys/class/net').iterdir()}
assert interfaces == {'lo'}, interfaces
for address in [('1.1.1.1', 443), ('8.8.8.8', 53)]:
    try:
        socket.create_connection(address, timeout=1).close()
    except OSError:
        pass
    else:
        raise SystemExit('ERRO: rede externa acessível')
try:
    socket.getaddrinfo('example.com', 443)
except OSError:
    pass
else:
    raise SystemExit('ERRO: DNS externo acessível')
print('Isolamento conferido: só loopback; TCP e DNS externo bloqueados')
