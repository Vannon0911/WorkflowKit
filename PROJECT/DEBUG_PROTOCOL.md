# DEBUG PROTOCOL

## Quick Start: Debug Mode

Start with debug logging to monitor user inputs and system responses:

```bash
python -m shinon_os --debug
```

Expected output:
```
[SHINON DEBUG MODE] Starting with debug protocol...
[DEBUG INPUT] raw_input='help' len=4 stripped='help'
[DEBUG RESPONSE] turn_advanced=False view=menu output_len=142
```

## What Gets Logged

### Input Logs (terminal)
- Raw input string (as typed)
- Input length for buffer overflow detection
- Stripped version (whitespace removed)

### Response Logs (terminal)
- Turn advancement (was it an action or a view?)
- View name (dashboard, market, policies, etc.)
- Output length (detects text rendering issues)

### System Logs (to file)
- JSON logs in `~/.shinon_os/logs/`
- Full kernel responses with metadata
- Errors and exceptions

## Testing Crash Resilience

Run the crash test suite to verify edge case handling:

```bash
# All crash tests
pytest tests/test_crash_suite.py -v

# Specific test class
pytest tests/test_crash_suite.py::TestInputValidation -v

# Single test
pytest tests/test_crash_suite.py::TestPolicyInputLimits::test_magnitude_zero -v
```

Current coverage:
- ✅ 5 input validation tests (empty, whitespace, long, special chars, case-insensitive)
- ✅ 4 policy magnitude tests (zero, negative, huge, non-numeric)
- ✅ 3 unknown command tests (typos, misspellings, empty names)
- ✅ 11 view command tests (all views should render without crash)
- ✅ 3 locale switch tests (DE/EN/invalid)
- ✅ 2 quit tests (command variants)
- ✅ 2 sequential test sequences (rapid fire, mixed valid/invalid)

**Total: 20 crash resilience tests, all passing.**

## Terminal Output Monitoring

When debug mode is ON, watch for these patterns in the terminal:

### Safe (Expected)
```
[DEBUG INPUT] raw_input='enact TAX_ADJUST 0.05' len=22 stripped='enact TAX_ADJUST 0.05'
[DEBUG RESPONSE] turn_advanced=True view=dashboard output_len=156
```

### Suspicious (Check Logs)
```
[DEBUG INPUT] raw_input='invalid_long_string_here...' len=10000
[DEBUG RESPONSE] turn_advanced=False view=error output_len=0
```

### Critical (Should Not Happen)
- No [DEBUG RESPONSE] after [DEBUG INPUT] = crash detected
- Blank output_len (0) = rendering failed
- Exception in terminal = unhandled error

## Common Debug Scenarios

### Test 1: Rapid Commands
```
python -m shinon_os --debug

# Type quickly
> help
> market
> enact TAX_ADJUST 0.05
> policies
> quit
```

Expected: All commands respond, no hangs.

### Test 2: Invalid Input Handling
```
python -m shinon_os --debug

# Try these
> enact INVALID_POLICY 1.0
> enact TAX_ADJUST abc
> xyzzy plugh
> "" (empty)
> !@#$%^&*()
```

Expected: All get [DEBUG RESPONSE] with rejection message or error flag.

### Test 3: Edge Case Magnitudes
```
python -m shinon_os --debug

# Type these
> enact TAX_ADJUST 0.0
> enact TAX_ADJUST -0.05
> enact TAX_ADJUST 999999.99
> enact IMPORT_PROGRAM 0 grain
```

Expected: All safely rejected with "INVALID PARAM" in output.

## Interpreting Debug Output

### Turn Advanced = True
- An action was executed (policy enacted, game state changed)
- Check the view for updated numbers (treasury, unrest, etc.)

### Turn Advanced = False
- A view was rendered or command was invalid
- Check output for error message or view content

### Output Length = 0
- Possible rendering issue
- Check file logs for exceptions
- Try `--safe-ui` to force plain text mode

## File Logs Location

All detailed system logs go to:
```
Windows: %LOCALAPPDATA%\shinon_os\logs\
Linux:   ~/.shinon_os/logs/
```

Check `debug.jsonl` for JSON-formatted system logs when debug flag is on.

## Next Steps

1. **Manual Testing**: Run `--debug` and verify all commands work smoothly
2. **Automated Testing**: Run `pytest tests/test_crash_suite.py` regularly
3. **Regression Detection**: Compare debug output across versions
4. **Edge Case Addition**: Add more assertions to crash suite as new features land

## Disabling Debug Output

To reduce terminal noise while keeping file logs:
- Remove `--debug` flag from command line
- File logs will still record to `~/.shinon_os/logs/`
