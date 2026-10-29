# Changelog

## [1.0.1] - 2026-10-29

### Added
- `roi-cropper web` command — launches the Gradio web interface in-process
- `roi-cropper-web` standalone entry point for direct Gradio server launch

### Fixed
- CLI module not included in wheel distribution, causing `ModuleNotFoundError: No module named 'cli'` on install
