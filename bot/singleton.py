"""Защита от одновременного запуска нескольких экземпляров бота."""

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

logger = logging.getLogger(__name__)

LOCK_FILE = Path(__file__).parent / "data" / "bot.lock"
BOT_DIR = Path(__file__).parent.resolve()


def _is_process_running(pid: int) -> bool:
    """Проверяет, существует ли процесс с указанным PID."""
    if pid <= 0:
        return False

    if sys.platform == "win32":
        import ctypes

        synchronize = 0x00100000
        handle = ctypes.windll.kernel32.OpenProcess(synchronize, False, pid)
        if not handle:
            return False
        ctypes.windll.kernel32.CloseHandle(handle)
        return True

    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _get_process_command_line(pid: int) -> str:
    """Возвращает командную строку процесса или пустую строку."""
    if sys.platform == "win32":
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"(Get-CimInstance Win32_Process -Filter 'ProcessId={pid}').CommandLine",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return (result.stdout or "").strip()

    proc_cmdline = Path(f"/proc/{pid}/cmdline")
    if proc_cmdline.exists():
        return proc_cmdline.read_text(encoding="utf-8", errors="ignore").replace("\0", " ")
    return ""


def _is_our_bot_process(pid: int) -> bool:
    """Проверяет, что процесс — именно наш app.py из каталога bot/."""
    if not _is_process_running(pid):
        return False

    command_line = _get_process_command_line(pid)
    if "app.py" not in command_line:
        return False

    return str(BOT_DIR).lower() in command_line.lower()


def find_bot_processes() -> list[int]:
    """Возвращает PID всех запущенных экземпляров app.py."""
    if sys.platform == "win32":
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
                "Where-Object { $_.CommandLine -like '*app.py*' } | "
                "Select-Object -ExpandProperty ProcessId",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        pids: list[int] = []
        for line in (result.stdout or "").splitlines():
            line = line.strip()
            if line.isdigit():
                pids.append(int(line))
        return pids

    result = subprocess.run(
        ["pgrep", "-f", "app.py"],
        capture_output=True,
        text=True,
        check=False,
    )
    return [int(pid) for pid in (result.stdout or "").split() if pid.isdigit()]


def _terminate_process(pid: int) -> None:
    """Принудительно завершает процесс."""
    if not _is_process_running(pid):
        return

    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/F", "/PID", str(pid)],
            capture_output=True,
            check=False,
        )
        return

    try:
        os.kill(pid, 15)
    except OSError:
        return


def stop_running_instance() -> None:
    """Останавливает все запущенные экземпляры бота и снимает блокировку."""
    current_pid = os.getpid()
    pids = {pid for pid in find_bot_processes() if pid != current_pid}

    if LOCK_FILE.exists():
        try:
            lock_pid = int(LOCK_FILE.read_text(encoding="utf-8").strip())
            if lock_pid > 0:
                pids.add(lock_pid)
        except ValueError:
            pass
        LOCK_FILE.unlink(missing_ok=True)

    for pid in pids:
        logger.info("Остановка процесса бота: PID %s", pid)
        _terminate_process(pid)

    for _ in range(10):
        if not any(_is_our_bot_process(pid) for pid in pids):
            break
        time.sleep(0.5)


class SingleInstanceLock:
    """Файловая блокировка: только один процесс app.py может работать."""

    def acquire(self) -> None:
        """Захватывает блокировку или завершает процесс, если бот уже запущен."""
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

        if LOCK_FILE.exists():
            try:
                old_pid = int(LOCK_FILE.read_text(encoding="utf-8").strip())
            except ValueError:
                old_pid = 0

            if old_pid and _is_our_bot_process(old_pid):
                logger.error(
                    "Бот уже запущен (PID %s). "
                    "Выполните: .\\stop_bot.ps1 или python app.py --force",
                    old_pid,
                )
                sys.exit(1)

            LOCK_FILE.unlink(missing_ok=True)

        LOCK_FILE.write_text(str(os.getpid()), encoding="utf-8")
        logger.info("Блокировка экземпляра: PID %s", os.getpid())

    def release(self) -> None:
        """Освобождает блокировку при штатном завершении."""
        if not LOCK_FILE.exists():
            return

        try:
            if int(LOCK_FILE.read_text(encoding="utf-8").strip()) == os.getpid():
                LOCK_FILE.unlink(missing_ok=True)
                logger.info("Блокировка экземпляра снята")
        except (OSError, ValueError):
            pass
