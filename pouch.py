# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///

import argparse
from datetime import datetime
from pathlib import Path
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parent


def targets(home):
    return {
        home / ".agents/skills": ROOT / "skills",
        home / ".codex/AGENTS.md": ROOT / "instructions/AGENTS.md",
        home / ".config/opencode/AGENTS.md": ROOT / "instructions/AGENTS.md",
    }


def linked(destination, source):
    return destination.is_symlink() and destination.resolve() == source.resolve()


def install(home):
    backup = home / ".pouch/backups" / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    for destination, source in targets(home).items():
        if not source.exists():
            raise FileNotFoundError(f"source missing: {source}")
        if linked(destination, source):
            print(f"linked: {destination}")
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        # Create the link before moving the old path. Windows can deny symlinks.
        with TemporaryDirectory(prefix=".pouch-", dir=destination.parent) as temporary:
            link = Path(temporary) / destination.name
            link.symlink_to(source, target_is_directory=source.is_dir())
            saved = None
            if destination.exists() or destination.is_symlink():
                saved = backup / destination.relative_to(home)
                saved.parent.mkdir(parents=True, exist_ok=True)
                destination.rename(saved)
                print(f"backup: {saved}")
            try:
                link.rename(destination)
            except OSError:
                if saved is not None:
                    saved.rename(destination)
                raise
        print(f"linked: {destination}")
    return 0


def status(home):
    missing = 0
    for destination, source in targets(home).items():
        if not source.exists():
            state = "source missing"
            missing += 1
        elif linked(destination, source):
            state = "linked"
        else:
            state = "occupied" if destination.exists() or destination.is_symlink() else "missing"
            missing += 1
        print(f"{state}: {destination} -> {source}")
    return int(missing > 0)


def uninstall(home):
    for destination, source in targets(home).items():
        if linked(destination, source):
            destination.unlink()
            print(f"removed: {destination}")
        else:
            print(f"kept: {destination}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="One little place for all my AI bits.")
    parser.add_argument("command", choices=("install", "status", "uninstall"))
    command = parser.parse_args().command
    try:
        return {"install": install, "status": status, "uninstall": uninstall}[command](Path.home())
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        if getattr(error, "winerror", None) == 1314:
            print("Enable Windows Developer Mode, then run install again.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
