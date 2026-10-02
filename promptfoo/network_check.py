"""Falha fechada: runtime deve ter somente loopback e bloquear TCP/DNS externo."""
from pathlib import Path
import socket
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
