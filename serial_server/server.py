"""
Puzzle Vision Serial Server:
The puzzle vision serial server is meant to collect data from
the serial ports and allow communication to the attached device
from a web site. This will allow us to view the data that is being
transmitted from the AStar32u4, which includes system status,
collected video, and motor data.

The server will allow commands to be sent to the AStar32u4 so that
the system can be configured in the desired manner. Finally, the
server will also show the status of I/O pins on the RPi, and will
act as a general I/O monitor.
"""
import os

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen
import tornado.options

import controllers
import config


tornado.options.define("server_port", default=config.server.PORT,
                       help=config.strings.HELP_SERVER_PORT, type=int)
tornado.options.define("serial_port", default=config.serial.PORT,
                       help=config.strings.HELP_SERIAL_PORT, type=int)
tornado.options.define("statics_root", default=config.routes.STATICS_ROOT,
                       help=config.strings.HELP_STATICS, type=str)
tornado.options.define("templates_root", default=config.routes.TEMPLATES_ROOT,
                       help=config.strings.HELP_TEMPLATES, type=str)


class SerialMonitorApplication(tornado.web.Application):
    controllers = []
    settings = []

    def __init__(self):
        self.initControllers()
        self.initSettings()

        super(SerialMonitorApplication, self).__init__(self.controllers,
                                                       **self.settings)

    def initControllers():
        self.controllers = [
            (config.routes.ROOT, controllers.home_controller.HomeController),
            (r"/serial", SerialChatController),
            (r"/serial/data-monitor", SerialMonitorSocket),
            (
                r"/statics/(.*)",
                tornado.web.StaticFileHandler,
                {
                    'path': tornado.options.statics_root
                }
            )
        ]

    def initSettings():
        self.settings = dict(
            app_title=u"Serial Monitor Application",
            default_handler_class=controllers.error_controller.ErrorController,
            template_path=os.path.join(
                os.path.dirname(__file__),
                tornado.options.templates_root[:-1]
            ),
            statics_path=os.path.join(
                os.path.dirname(__file__),
                tornado.options.statics_root[:-1]
            )
        )


class SerialChatController(tornado.web.RequestHandler):
    def get(self):
        self.render('serial-chat.html')


class SerialMonitorSocket(tornado.websocket.WebSocketHandler):
    connections = []

    def open(self):
        print('New connection - %s', self)
        self.connections.append(self)
        self.write_message('Connected to Serial Monitor Socket')

    def on_message(self, msg):
        print('Received: %s', msg)
        self.write_message('Received: %s' % msg)

    def on_close(self):
        print('Closed - %s', self)
        self.connections.remove(self)


def main():
    tornado.options.parse_command_line()
    httpServer = tornado.httpserver.HTTPServer(SerialMonitorApplication())
    httpServer.listen(tornado.options.server_port)

    # Print so we know the server started
    print('Listening on port:', tornado.options.port)

    # Start the application on the main IO loop
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()