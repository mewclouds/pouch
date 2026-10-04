from contextlib import redirect_stdout
import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pouch


class PouchTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(TemporaryDirectory()))
        self.home = root / "home"
        self.source = root / "pouch"
        self.home.mkdir()
        self.source.mkdir()
        (self.source / "AGENTS.md").write_text("Pouch repository rules", encoding="utf-8")
        (self.source / "instructions").mkdir()
        (self.source / "instructions/AGENTS.md").write_text("instructions", encoding="utf-8")
        (self.source / "skills").mkdir()
        self.enterContext(patch.object(pouch, "ROOT", self.source))
        self.enterContext(redirect_stdout(io.StringIO()))

    def test_links_expose_source_edits_and_new_skills(self):
        self.assertEqual(pouch.status(self.home), 1)
        self.assertEqual(pouch.install(self.home), 0)
        self.assertEqual(pouch.status(self.home), 0)
        (self.source / "instructions/AGENTS.md").write_text("new instructions", encoding="utf-8")
        skill = self.source / "skills/new-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("new skill", encoding="utf-8")
        self.assertEqual((self.home / ".codex/AGENTS.md").read_text(encoding="utf-8"), "new instructions")
        self.assertEqual((self.home / ".agents/skills/new-skill/SKILL.md").read_text(encoding="utf-8"), "new skill")
        (self.source / "instructions/AGENTS.md").unlink()
        self.assertEqual(pouch.status(self.home), 1)
        pouch.uninstall(self.home)
        self.assertFalse((self.home / ".codex/AGENTS.md").is_symlink())
        self.assertTrue((self.source / "skills/new-skill/SKILL.md").exists())

    def test_install_preserves_existing_files_and_provider_settings(self):
        skills = self.home / ".agents/skills/custom"
        skills.mkdir(parents=True)
        (skills / "SKILL.md").write_text("custom skill", encoding="utf-8")
        agents = self.home / ".codex/AGENTS.md"
        agents.parent.mkdir()
        agents.write_text("old instructions", encoding="utf-8")
        config = self.home / ".codex/config.toml"
        config.write_text("old settings", encoding="utf-8")
        opencode = self.home / ".config/opencode/opencode.jsonc"
        opencode.parent.mkdir(parents=True)
        opencode.write_text("opencode settings", encoding="utf-8")
        rules = self.home / ".codex/rules/default.rules"
        rules.parent.mkdir()
        rules.write_text("old rules", encoding="utf-8")

        pouch.install(self.home)
        backups = list((self.home / ".pouch/backups").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / ".codex/AGENTS.md").read_text(encoding="utf-8"), "old instructions")
        self.assertEqual((backups[0] / ".agents/skills/custom/SKILL.md").read_text(encoding="utf-8"), "custom skill")
        pouch.install(self.home)
        self.assertEqual(list((self.home / ".pouch/backups").iterdir()), backups)
        pouch.uninstall(self.home)
        self.assertEqual(config.read_text(encoding="utf-8"), "old settings")
        self.assertEqual(opencode.read_text(encoding="utf-8"), "opencode settings")
        self.assertEqual(rules.read_text(encoding="utf-8"), "old rules")
        self.assertTrue((backups[0] / ".codex/AGENTS.md").exists())

    def test_uninstall_keeps_foreign_paths(self):
        pouch.install(self.home)
        agents = self.home / ".codex/AGENTS.md"
        agents.unlink()
        foreign = self.home / "other.md"
        foreign.write_text("other instructions", encoding="utf-8")
        agents.symlink_to(foreign)
        opencode = self.home / ".config/opencode/AGENTS.md"
        opencode.unlink()
        opencode.write_text("local instructions", encoding="utf-8")
        pouch.uninstall(self.home)
        self.assertTrue(agents.is_symlink())
        self.assertEqual(agents.read_text(encoding="utf-8"), "other instructions")
        self.assertEqual(opencode.read_text(encoding="utf-8"), "local instructions")
        self.assertFalse((self.home / ".agents/skills").is_symlink())

    def test_denied_symlink_preserves_existing_directory(self):
        skills = self.home / ".agents/skills"
        skills.mkdir(parents=True)
        (skills / "keep.txt").write_text("keep", encoding="utf-8")
        with patch.object(Path, "symlink_to", side_effect=PermissionError("denied")):
            with self.assertRaises(PermissionError):
                pouch.install(self.home)
        self.assertEqual((skills / "keep.txt").read_text(encoding="utf-8"), "keep")
        self.assertFalse((self.home / ".pouch/backups").exists())

    def test_failed_link_move_restores_existing_directory(self):
        skills = self.home / ".agents/skills"
        skills.mkdir(parents=True)
        (skills / "keep.txt").write_text("keep", encoding="utf-8")
        rename = Path.rename

        def fail_link_move(path, destination):
            if path.parent.name.startswith(".pouch-"):
                raise PermissionError("cannot move link")
            return rename(path, destination)

        with patch.object(Path, "rename", fail_link_move):
            with self.assertRaises(PermissionError):
                pouch.install(self.home)
        self.assertFalse(skills.is_symlink())
        self.assertEqual((skills / "keep.txt").read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
