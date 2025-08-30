import logging

def setup_logger(log_file="automation.log"):
    logger = logging.getLogger("automation")
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    # Console handler (stdout)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # File handler
    fh = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    fh.setLevel(logging.INFO)

    # Format
    formatter = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger