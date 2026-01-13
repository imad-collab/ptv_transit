---
description: Run tests and provide summary report
allowed-tools: Bash(pytest:*), Bash(python:*)
---

# Run Tests

Execute the test suite and provide a clear summary.

## Available Test Modes

Based on `$ARGUMENTS`, run different test configurations:

### No arguments (default): Quick test
```bash
pytest --tb=short -q
```

### "all": Full test suite with coverage
```bash
pytest --cov=src --cov-report=term-missing -v
```

### "phase0" or "realtime": Phase 0 tests only
```bash
pytest tests/test_realtime/ -v
```

### "phase1" or "data": Phase 1 tests only
```bash
pytest tests/test_data/ -v
```

### "phase2" or "graph": Phase 2 tests only
```bash
pytest tests/test_graph/ -v
```

### "fast": Fastest possible run
```bash
pytest --tb=no -q
```

### "failed": Re-run only failed tests
```bash
pytest --lf -v
```

## Output Format

Present results as:

```
╔══════════════════════════════════════════════════════════════╗
║                      TEST RESULTS                             ║
╠══════════════════════════════════════════════════════════════╣
║ Status:   ✅ PASSED  (or ❌ FAILED)                          ║
║ Tests:    83 passed, 0 failed                                 ║
║ Coverage: 98%                                                 ║
║ Duration: 0.15s                                               ║
╠══════════════════════════════════════════════════════════════╣
║ By Phase:                                                     ║
║   Phase 0 (Realtime): 21 tests ✅                            ║
║   Phase 1 (Data):     62 tests ✅                            ║
║   Phase 2 (Graph):    0 tests  ⏳                            ║
╚══════════════════════════════════════════════════════════════╝
```

## On Failure

If tests fail:
1. Show failing test names
2. Show brief error summary
3. Offer to investigate specific failures

## Usage Examples

```
/test           # Quick test run
/test all       # Full coverage report
/test phase1    # Only Phase 1 tests
/test failed    # Re-run failed tests
```
