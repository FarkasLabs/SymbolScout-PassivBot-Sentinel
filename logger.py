import logging
import apprise
from config import load_and_validate_config


class NotifyHandler(logging.Handler):
    def __init__(self, config):
        super().__init__()
        self.apprise = apprise.Apprise()
        for url in config["notifications"]["apprise_urls"]:
            self.apprise.add(url)
        self.notify_config = config["notifications"]["notify_on"]

        # Buffer for collecting symbol changes
        self.symbol_changes = []
        self.collecting_changes = False

    def emit(self, record):
        if record.levelno >= logging.ERROR and self.notify_config.get("errors", False):
            self.notify("Error", record)
        elif record.levelno == logging.INFO:
            if "started symbolscout integration" in record.msg.lower():
                self.notify("Startup", record)
            elif self.notify_config.get("config_updates", False):
                if "removing symbols:" in record.msg.lower():
                    self.symbol_changes.append(f"🔴 {record.msg}")
                    self.collecting_changes = True
                elif "adding symbols:" in record.msg.lower():
                    self.symbol_changes.append(f"🟢 {record.msg}")
                    self.collecting_changes = True
                elif (
                    self.collecting_changes
                    and "updated approved_coins list" in record.msg.lower()
                ):
                    # Send collected changes as one notification
                    self.symbol_changes.append(f"✅ {record.msg}")
                    self.notify("Symbol List Update", "\n".join(self.symbol_changes))
                    # Reset collection
                    self.symbol_changes = []
                    self.collecting_changes = False
                elif "config update" in record.msg.lower():
                    self.notify("Config Update", record)
            elif "new article" in record.msg.lower() and self.notify_config.get(
                "new_news", False
            ):
                self.notify("News", record)

    def notify(self, notification_type, record):
        if isinstance(record, str):
            message = record
        else:
            message = record.msg

        self.apprise.notify(title=f"SymbolScout {notification_type}", body=message)


def setup_logger():
    try:
        config = load_and_validate_config()
        logger = logging.getLogger("SymbolScout")
        logger.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # Check if notifications are enabled
        if "notifications" in config and any(
            config["notifications"]["notify_on"].values()
        ):
            # Notify handler
            nh = NotifyHandler(config)
            nh.setLevel(logging.INFO)
            nh.setFormatter(formatter)
            logger.addHandler(nh)
            logger.info("Notification system initialized")
        else:
            logger.info("Notifications are disabled")

        return logger
    except Exception as e:
        import traceback

        print("Error in setup_logger:")
        print(traceback.format_exc())
        raise


# Create and configure the logger
logger = setup_logger()
