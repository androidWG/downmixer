import datetime
import logging.config

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
ITALIC_SEQ = "\033[3m"
UNDERLINE_SEQ = "\033[4m"


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
    prefix = "debug_" if debug else ""
    filename = f'{prefix}downmixer_{datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")}.log'

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
                "class": "util.log_setup.ColoredFormatter",
            },
            "millisecondFormatter": {
                "format": file_format,
                "datefmt": "%H:%M:%S.%f",
                "style": "%",
                "class": "util.log_setup.MillisecondFormatter",
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
                "handlers": ["console", "file"],
                "level": "DEBUG" if debug else "INFO",
                "propagate": True,
            }
        },
        "disable_existing_loggers": True,
    }

    logging.config.dictConfig(config)

    print("Logging setup finished")
