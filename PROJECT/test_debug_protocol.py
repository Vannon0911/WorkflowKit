"""Manual debug protocol test - verify debug mode works."""

from pathlib import Path

from shinon_os.app_service import AppOptions, AppService


def test_debug_protocol():
    """Demonstrate debug mode terminal output."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.sqlite3"
        options = AppOptions(debug=True, safe_ui=True, no_anim=True)
        service = AppService(options)
        
        try:
            service.bootstrap()
            
            print("\n" + "=" * 70)
            print("DEBUG PROTOCOL TEST: Testing debug mode with various inputs")
            print("=" * 70 + "\n")
            
            # Test sequence matching crash suite scenarios
            test_inputs = [
                ("help", "View command"),
                ("", "Empty input"),
                ("   ", "Whitespace only"),
                ("market", "Valid view"),
                ("invalid_command", "Unknown command"),
                ("enact TAX_ADJUST 0.05", "Valid action"),
                ("enact TAX_ADJUST abc", "Invalid magnitude"),
                ("dashboard", "Dashboard view"),
                ("quit", "Quit command"),
            ]
            
            for user_input, description in test_inputs:
                print(f"\n[TEST] {description}: '{user_input}'")
                response = service.handle_input(user_input)
                print(f"  → Output length: {len(response.message)}")
                print(f"  → View: {response.view}")
                print(f"  → Turn advanced: {response.turn_advanced}")
                if response.should_quit:
                    print(f"  → Quit flag: YES")
                    break
                
        finally:
            service.shutdown()


if __name__ == "__main__":
    test_debug_protocol()
