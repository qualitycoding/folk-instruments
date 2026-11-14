# Test fixtures (frozen)

Malformed event files for T-161. `garbage.bin` is 4096 bytes from Python's `random` module with seed 7; `huge_line.events`
has a 200 000-digit number on line 1. They are inputs to the render tool's error handling and contain no audio.
