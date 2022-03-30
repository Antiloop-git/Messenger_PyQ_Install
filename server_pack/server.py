"""
server
"""

import sys
import os
import argparse
import logging
import configparser

from PyQt5 import QtWidgets as QtGui
from PyQt5 import QtCore

from common.variables import DEFAULT_PORT

from common.decos import log
from server_pack.server.core import MessageProcessor
from server_pack.server.database import ServerStorage


# Инициализация логирования сервера.
logger = logging.getLogger('server')


@log
def arg_parser(default_port, default_address):
    ''' Парсер аргументов коммандной строки. '''
    # logger.debug(f'Инициализация парсера аргументов коммандной строки: {sys.argv}')
    logging.debug("Инициализация парсера аргументов коммандной строки: %sys.argv")
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=default_port, type=int, nargs='?')
    parser.add_argument('-a', default=default_address, nargs='?')
    parser.add_argument('--no_gui', action='store_true')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    gui_flag = namespace.no_gui
    logger.debug('Аргументы успешно загружены.')
    return listen_address, listen_port, gui_flag


@log
def config_load():
    '''Парсер конфигурационного ini файла.'''
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")
    # Если конфиг файл загружен правильно, запускаемся, иначе конфиг по
    # умолчанию.
    if 'SETTINGS' not in config:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_database.db3')
    return config

@log
def main():
    ''' Основная функция'''
    # Загрузка файла конфигурации сервера
    config = config_load()

    # Загрузка параметров командной строки, если нет параметров, то задаём
    # значения по умоланию.
    listen_address, listen_port, gui_flag = arg_parser(
        config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])

    # Инициализация базы данных
    database = ServerStorage(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))

    # Создание экземпляра класса - сервера и его запуск:
    server = MessageProcessor(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    # Если  указан параметр без GUI то запускаем простенький обработчик
    # консольного ввода
    if gui_flag:
        while True:
            command = input('Введите exit для завершения работы сервера.')
            if command == 'exit':
                # Если выход, то завршаем основной цикл сервера.
                server.running = False
                server.join()
                break

    # Если не указан запуск без GUI, то запускаем GUI:
    else:
        # Создаём графическое окуружение для сервера:
        server_app = QtGui.QApplication(sys.argv)
        server_app.setAttribute(QtCore.Qt.AA_DisableWindowContextHelpButton)
        # main_window = MainWindow(database, server, config)

        # Запускаем GUI
        server_app.exec_()

        # По закрытию окон останавливаем обработчик сообщений
        server.running = False


if __name__ == '__main__':
    main()
