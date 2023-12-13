import copy
import datetime
import logging.config

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
ITALIC_SEQ = "\033[3m"
UNDERLINE_SEQ = "\033[4m"

BLACK, RED, GREEN, YELLOW, ORANGE, PURPLE, CYAN, GREY = range(8)

COLORS = {
    "WARNING": YELLOW,
    "INFO": GREY,
    "DEBUG": ORANGE,
    "CRITICAL": YELLOW,
    "ERROR": RED,
}


class MillisecondFormatter(logging.Formatter):
    """A formatter for standard library 'logging' that supports '%f' wildcard in format strings."""

    converter = datetime.datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        converter = self.converter(record.created)
        if datefmt:
            s = converter.strftime(datefmt)[:-3]
        else:
            t = converter.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        new_record = copy.copy(record)
        levelname = new_record.levelname

        if levelname in COLORS:
            levelname_color = (
                COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            )
            new_record.levelname = levelname_color
        return logging.Formatter.format(self, new_record)


def formatter_message(message, use_color=True):
    if use_color:
        message = (
            message.replace("$RESET", RESET_SEQ)
            .replace("$BOLD", BOLD_SEQ)
            .replace("$ITALIC", ITALIC_SEQ)
            .replace("$UNDER", UNDERLINE_SEQ)
        )
    else:
        message = (
            message.replace("$RESET", "")
            .replace("$BOLD", "")
            .replace("$ITALIC", "")
            .replace("$UNDER", "")
        )
    return message


def setup_logging(debug: bool = False):
    base_format = (
        "[$BOLD%(levelname)-8s$RESET] ($BOLD%(filename)s:%(lineno)d$RESET) %(message)s"
    )
    debug_base_format = (
        "[$BOLD%(levelname)-8s$RESET] {$ITALIC%(threadName)-10s$RESET} (%(funcName)s @ "
        "$BOLD%(filename)s:%(lineno)d$RESET) %(message)s "
    )
    chosen_format = debug_base_format if debug else base_format

    colored_format = formatter_message(chosen_format)
    file_format = formatter_message(chosen_format, False)

    config = {
        "version": 1,
        "formatters": {
            "coloredFormatter": {
                "format": colored_format,
                "style": "%",
                "validate": False,
                "class": "setup_logging.ColoredFormatter",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "coloredFormatter",
                "stream": "ext://sys.stdout",
            }
        },
        "loggers": {
            "downmixer": {
                "handlers": ["console"],
                "level": "DEBUG" if debug else "INFO",
                "propagate": True,
            }
        },
        "disable_existing_loggers": True,
    }

    logging.config.dictConfig(config)

    print("Logging setup finished")
