import npyscreen

from lib import console, app_config, parser_command_line
from lib.clock import ClockThread
from lib.console_ui import ConsoleUI
from lib.log_queue import LogQueue
from lib.monitor import MonitorThreadGenerator
from lib.parser import ParserThread

if __name__ == '__main__':
    config = parser_command_line.parse_config()

    # Update the application config (global for the app), according to the checked parsed arguments
    app_config.update(config)

    log_queue = LogQueue()

    # Launch the parser thread responsible for adding logs to the LogQueue
    ParserThread(log_queue).start()

    console_model = console.ConsoleModel()
    generator = MonitorThreadGenerator(log_queue, console_model)

    # Launch the clock thread spawning Monitor thread
    ClockThread(generator=generator).start()

    try:
        # Run the main UI thread
        ConsoleUI(console_model).run()

    except KeyboardInterrupt:
        print('Program interrupted')

    except npyscreen.wgwidget.NotEnoughSpaceForWidget:
        print('\nNot enough space available to render the monitoring console!\n--> Please resize or go full screen\n')