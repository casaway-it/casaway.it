# Casaway site tasks. Run `just` to list.

set shell := ["bash", "-euo", "pipefail", "-c"]

# List available recipes
default:
    @just --list

# Run local dev server with live reload (http://localhost:1313)
serve:
    hugo server

# Alias for `serve`
dev: serve

# Production build to ./public
build:
    hugo --gc --minify

# Production build, warning on missing IT translations
build-strict:
    hugo --gc --minify --printI18nWarnings

# Remove build artifacts
clean:
    trash public resources 2>/dev/null || true

# Run the GitHub Actions workflow locally (requires `act`)
ci:
    act

# Lint the GitHub Actions workflow
lint:
    actionlint .github/workflows
    zizmor .github/workflows

# Generate missing Things-to-Do cover images via Google Imagen
# Args: ARGS — passed to scripts/imagen-activities.py (e.g. just images --only id1,id2)
images *ARGS:
    ./scripts/imagen-activities.py {{ARGS}}

