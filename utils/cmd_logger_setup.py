import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime
import time

# 詳細な時間をロギングするクラス（通信速度の目視のため）
class PreciseTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created)
        if datefmt:
            # Pythonのdatetime.strftimeでは%fでマイクロ秒
            return dt.strftime(datefmt)
        else:
            return dt.strftime("%Y-%m-%d %H:%M:%S.%f")

# ログファイル名に秒まで含めるためのローテートハンドラ
class PreciseTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.suffix = "%Y-%m-%d_%H-%M-%S"  # 秒単位でファイル名を区別

# ログレベルの追加
SUCCESS_LEVEL = 25
FAILURE_LEVEL = 35

logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")
logging.addLevelName(FAILURE_LEVEL, "FAILURE")

def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)

def failure(self, message, *args, **kwargs):
    if self.isEnabledFor(FAILURE_LEVEL):
        self._log(FAILURE_LEVEL, message, args, **kwargs)

# 処理時間の記録（開始）
def start(self, label="処理"):
    self._start_time = time.time()
    self.info(f"[{label}] 開始")

# 処理時間の記録（終了）
def finish(self, label="処理"):
    if hasattr(self, "_start_time"):
        elapsed = time.time() - self._start_time
        self.success(f"[{label}] 終了（{elapsed:.3f}秒）")
    else:
        self.success(f"[{label}] 終了（計測なし）")

# ロガーへのメソッド追加（重複回避）
if not hasattr(logging.Logger, "success"):
    logging.Logger.success = success
if not hasattr(logging.Logger, "failure"):
    logging.Logger.failure = failure
if not hasattr(logging.Logger, "start"):
    logging.Logger.start = start
if not hasattr(logging.Logger, "finish"):
    logging.Logger.finish = finish

# ロガーをセットアップする関数
def setup_logger(app_name: str, base_log_dir: Path = Path("logs"), level=logging.DEBUG) -> logging.Logger:
    """
    アプリごとのロガーをセットアップする。

    Parameters:
        app_name (str): ロガー名（通常はアプリ名）。
        base_log_dir (Path): logs ディレクトリの親パス。
        level (int): ログレベル（デフォルト DEBUG）。

    Returns:
        logging.Logger: 設定済みロガー。
    """
    log_dir = base_log_dir / app_name
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(app_name)
    logger.setLevel(level)

    # 既存ハンドラがあれば削除（再設定用）
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = PreciseTimeFormatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S.%f",  # %fが、マイクロ秒を示す。
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File handler（タイムローテート・秒付き）
    file_handler = PreciseTimedRotatingFileHandler(
        filename=str(log_dir / f"{app_name}.log"),
        when="midnight",
        interval=1,
        backupCount=12,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
