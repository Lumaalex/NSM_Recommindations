#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЛОКАЛЬНЫЙ СЕРВЕР ДЛЯ ТЕЛЕФОНА
=============================
Запуск на компьютере:   python tools/serve.py [порт]
Затем на телефоне (та же Wi‑Fi сеть) открыть в Safari напечатанный адрес и
«Поделиться» → «На экран «Домой»».

Зачем: предпросмотр HTML-файла на iPhone/iPad (Quick Look) не выполняет JavaScript,
поэтому из мессенджера конструктор не запускается. Через Safari по http:// — работает всё:
черновики, темы, скачивание .docx.
"""
import http.server
import os
import socket
import socketserver
import sys
import urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = 'Конструктор_рекомендаций.html'


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def end_headers(self):
        # телефон всегда должен получать свежую версию
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write('%s %s\n' % (self.address_string(), fmt % args))


def lan_ips():
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        ips.append(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.append(info[4][0])
    except Exception:
        pass
    out = []
    for i in ips:
        if i not in out and not i.startswith('127.'):
            out.append(i)
    return out or ['127.0.0.1']


def main():
    if not os.path.exists(os.path.join(ROOT, FILE)):
        raise SystemExit('Не найден файл: ' + os.path.join(ROOT, FILE))
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    path = '/' + urllib.parse.quote(FILE)
    print('Конструктор рекомендаций поднят на порту %d.' % PORT)
    print('  на компьютере:  http://localhost:%d%s' % (PORT, path))
    for ip in lan_ips():
        print('  на телефоне:    http://%s:%d%s   (та же Wi‑Fi сеть, открыть в Safari)' % (ip, PORT, path))
    print('В Safari на телефоне: «Поделиться» → «На экран «Домой»».')
    print('Остановить: Ctrl+C\n')
    with socketserver.ThreadingTCPServer(('0.0.0.0', PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nостановлено')


if __name__ == '__main__':
    main()
