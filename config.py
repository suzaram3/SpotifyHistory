import configparser
import logging
import logging.config


class Config():
    """
    Configuration manager for SpotifyHistory project.
    """

    def __init__(self):
        """
        Initialize the Config object by loading configuration files and setting up logging.
        """
        self._load_configuration()
        self._setup_logging()
        self._get_db_config()

    def _load_configuration(self):
        """
        Load configuration files using configparser.
        """
        config_files = [
            "/root/SpotifyHistory/settings/db.conf",
            "/root/SpotifyHistory/settings/file_paths.conf",
            "/root/SpotifyHistory/settings/spotify.conf",
        ]
        self.config = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation()
        )
        self.config.read(config_files)

    def _setup_logging(self):
        """
        Set up logging using the configuration file specified for logging.
        """
        try:
            logging.config.fileConfig(
                "/root/SpotifyHistory/settings/logging.conf"
            )
            self.console_logger = logging.getLogger("console")
            self.file_logger = logging.getLogger("prod")
        except Exception as e:
            print("Error setting up logging:", str(e))

    def _get_db_config(self):
        """
        Get the database configuration information from db.conf.
        """
        self.db_config = {}
        if "prod" in self.config:
            self.db_config["host"] = self.config.get("prod", "host")
            self.db_config["port"] = self.config.getint("prod", "port")
            self.db_config["user"] = self.config.get("prod", "user")
            self.db_config["password"] = self.config.get("prod", "password")
            self.db_config["database"] = self.config.get("prod", "database")
            self.db_config["db_uri"] = self.config.get("prod", "db_uri")