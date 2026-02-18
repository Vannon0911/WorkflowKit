"""Crash test suite: verify UI/UX stability against random and edge-case inputs."""

from __future__ import annotations

from pathlib import Path

import pytest

from shinon_os.app import ShinonApp


class TestInputValidation:
    """Verify input parsing handles invalid/edge-case user inputs safely."""

    def test_empty_input(self, tmp_path: Path) -> None:
        """Empty string input should not crash."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            response = app.process_command("")
            assert response is not None
            assert not response.should_quit
        finally:
            app.shutdown()

    def test_whitespace_only(self, tmp_path: Path) -> None:
        """Whitespace-only input should not crash."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            response = app.process_command("   \t  \n  ")
            assert response is not None
            assert not response.should_quit
        finally:
            app.shutdown()

    def test_very_long_input(self, tmp_path: Path) -> None:
        """Very long input string should not crash."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            long_input = "a" * 10000
            response = app.process_command(long_input)
            assert response is not None
            assert not response.should_quit
        finally:
            app.shutdown()

    def test_special_characters(self, tmp_path: Path) -> None:
        """Special characters should not crash."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            special_inputs = [
                "!@#$%^&*()",
                "\\n\\t\\r",
                "éàüöß",
                "中文",
                "🔥💥🎮",
                "<script>alert('xss')</script>",
            ]
            for inp in special_inputs:
                response = app.process_command(inp)
                assert response is not None
                assert not response.should_quit
        finally:
            app.shutdown()

    def test_case_insensitive_commands(self, tmp_path: Path) -> None:
        """Commands in various cases should all work."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            variants = ["HELP", "Help", "HeLp", "help", "HELP ", " HELP"]
            for cmd in variants:
                response = app.process_command(cmd)
                assert response is not None
                assert not response.should_quit
        finally:
            app.shutdown()


class TestPolicyInputLimits:
    """Test policy magnitude boundary conditions."""

    def test_magnitude_zero(self, tmp_path: Path) -> None:
        """Magnitude of zero should not crash (may be invalid, but safe rejection)."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            response = app.process_command("enact TAX_ADJUST 0.0")
            assert response is not None
            # Should either reject gracefully or accept
            assert "INVALID PARAM" in response.output or response.turn_advanced
        finally:
            app.shutdown()

    def test_magnitude_negative(self, tmp_path: Path) -> None:
        """Negative magnitude should be safe."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            response = app.process_command("enact TAX_ADJUST -0.05")
            assert response is not None
            # Should reject gracefully
            assert "INVALID PARAM" in response.output or response.turn_advanced
        finally:
            app.shutdown()

    def test_magnitude_huge(self, tmp_path: Path) -> None:
        """Very large magnitude should be safe."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            response = app.process_command("enact TAX_ADJUST 999999.99")
            assert response is not None
            # Should reject gracefully
            assert "INVALID PARAM" in response.output or response.turn_advanced
        finally:
            app.shutdown()

    def test_magnitude_not_number(self, tmp_path: Path) -> None:
        """Non-numeric magnitude should be safe."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            response = app.process_command("enact TAX_ADJUST abc")
            assert response is not None
            # Should reject gracefully
            assert "INVALID PARAM" in response.output or response.turn_advanced
        finally:
            app.shutdown()


class TestUnknownCommands:
    """Test UI behavior with unknown/misspelled commands."""

    def test_unknown_command(self, tmp_path: Path) -> None:
        """Unknown command should not crash."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            response = app.process_command("xyzzy plugh")
            assert response is not None
            assert not response.should_quit
        finally:
            app.shutdown()

    def test_misspelled_policy(self, tmp_path: Path) -> None:
        """Misspelled policy name should not crash."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            response = app.process_command("enact TAX_ADJUSTT 0.05")
            assert response is not None
            # Should reject gracefully
            assert "INVALID PARAM" in response.output or not response.turn_advanced
        finally:
            app.shutdown()

    def test_empty_policy_name(self, tmp_path: Path) -> None:
        """Empty policy name should not crash."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            response = app.process_command("enact  0.05")
            assert response is not None
            assert "INVALID PARAM" in response.output or not response.turn_advanced
        finally:
            app.shutdown()


class TestViewCommands:
    """Test all view commands for stability."""

    def test_all_view_commands(self, tmp_path: Path) -> None:
        """All view commands should not crash."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            view_commands = [
                "dashboard",
                "market",
                "policies",
                "industry",
                "history",
                "explain prices",
                "explain shortage",
                "explain policy TAX_ADJUST",
                "unlock list",
                "show goals",
                "intel",
            ]
            for cmd in view_commands:
                response = app.process_command(cmd)
                assert response is not None
                assert not response.should_quit
        finally:
            app.shutdown()


class TestLocaleSwitch:
    """Test language switching for stability."""

    def test_locale_switch_de(self, tmp_path: Path) -> None:
        """Switching to German should not crash."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            response = app.process_command("lang de")
            assert response is not None
            assert response.locale_changed
        finally:
            app.shutdown()

    def test_locale_switch_en(self, tmp_path: Path) -> None:
        """Switching to English should not crash."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            response = app.process_command("lang en")
            assert response is not None
            assert response.locale_changed
        finally:
            app.shutdown()

    def test_locale_switch_invalid(self, tmp_path: Path) -> None:
        """Invalid language code should be safe."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            response = app.process_command("lang xx")
            assert response is not None
            # Should reject gracefully
            assert not response.should_quit
        finally:
            app.shutdown()


class TestQuitCommand:
    """Test quit behavior."""

    def test_quit_command(self, tmp_path: Path) -> None:
        """Quit command should set should_quit flag."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            response = app.process_command("quit")
            assert response is not None
            assert response.should_quit
        finally:
            app.shutdown()

    def test_quit_variants(self, tmp_path: Path) -> None:
        """Various quit commands should work."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            for cmd in ["quit", "exit", "q", "Q", "QUIT"]:
                response = app.process_command(cmd)
                assert response is not None
        finally:
            app.shutdown()


class TestSequentialActions:
    """Test multiple actions in sequence for state corruption."""

    def test_rapid_fire_commands(self, tmp_path: Path) -> None:
        """Rapid command sequence should not crash."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            commands = [
                "dashboard",
                "market",
                "enact TAX_ADJUST 0.05",
                "policies",
                "market",
                "enact IMPORT_PROGRAM 10 grain",
                "history",
                "intel",
                "market",
            ]
            for cmd in commands:
                response = app.process_command(cmd)
                assert response is not None
                assert not response.should_quit
        finally:
            app.shutdown()

    def test_mixed_valid_invalid(self, tmp_path: Path) -> None:
        """Mix of valid and invalid inputs should handle gracefully."""
        app = ShinonApp(db_path=tmp_path / "test.sqlite3")
        try:
            app.start_new_game(seed=42)
            commands = [
                "help",
                "invalid_command",
                "enact TAX_ADJUST 0.05",
                "unknown_view",
                "market",
                "enact INVALID_POLICY 1.0",
                "dashboard",
            ]
            for cmd in commands:
                response = app.process_command(cmd)
                assert response is not None
        finally:
            app.shutdown()
