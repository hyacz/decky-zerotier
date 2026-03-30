# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Decky Loader plugin that provides ZeroTier VPN client functionality for Steam Deck. Runs on SteamOS (Linux x86_64). Requires root privileges (`plugin.json` flags: `["root"]`).

## Build & Development Commands

```bash
pnpm i              # Install dependencies
pnpm run build      # Build frontend (rollup -> dist/)
pnpm run watch      # Watch mode for frontend development
```

There is no test framework configured (`pnpm test` is a no-op placeholder).

### Deploying to Steam Deck

Configure `.vscode/settings.json` from `.vscode/defsettings.json` with Deck SSH connection details, then use VSCode tasks:

- `buildall` — pnpm install + rollup build
- `deploy` — rsync plugin to Deck via SSH
- `allinone+` — build + deploy + restart Decky plugin_loader service

### Release Build (CI)

GitHub Actions (`.github/workflows/plugin.yml`) uses `decky` CLI to build a release zip on tag push:
```bash
decky plugin build -b -s directory -o ./out
```

## Architecture

### Backend (`main.py`)

Python `Plugin` class running inside Decky Loader's Python runtime. Key lifecycle methods:
- `_main()` — starts ZeroTier daemon as a subprocess, runs for plugin lifetime
- `_unload()` / `_uninstall()` — cleanup hooks

Backend methods become callable from frontend via Decky's IPC — the method name is used as the call key. All methods are `async`. The `zerotier_cli()` helper wraps subprocess calls to the `bin/zerotier-one` binary with `-q -j` flags, returning parsed JSON.

### Frontend (`src/`)

TypeScript/React injected into Steam's gamepad UI. Uses `@decky/api` and `@decky/ui` components.

- `callable()` from `@decky/api` creates typed stubs that call backend methods by name (e.g., `callable<[], NodeStatus>("info")` calls `Plugin.info()`)
- `definePlugin()` in `index.tsx` is the entry point — returns plugin metadata, content React tree, and icon
- Components: `NetworkButton`, `JoinNetworkModal`, `NetworkDetailModal`
- Types: `model.ts` defines `NodeStatus` and `Network` interfaces
- JSX uses Steam's bundled React via `window.SP_REACT.createElement` (configured in tsconfig)

### Frontend-Backend Communication

No manual serialization. `callable("method_name")` in TypeScript maps directly to `async def method_name()` on the Python `Plugin` class. Decky Loader handles routing and serialization automatically.

### Remote Binary

ZeroTier binary (`bin/zerotier-one`) is downloaded at install time via `remote_binary` in `package.json`. SHA256 hash is verified before use. Binary is a static build of ZeroTierOne v1.16.0.

## Decky Plugin Runtime Notes

- **Cannot run locally on non-SteamOS**: Decky Loader injects into Steam's CEF-based gamepad UI (`steam -gamepadui`). No dev server or emulator exists for the frontend.
- **Testing requires a Steam Deck (or Linux with Steam)**: Deploy via SSH/rsync to the Deck, then restart the `plugin_loader` systemd service.
- **CEF debugging**: Create `~/.steam/steam/.cef-enable-remote-debugging` to enable Chrome DevTools on localhost.
- **`debug` flag in plugin.json**: Enables hot reload during development.
- **pnpm lockfile version**: CI requires `lockfileVersion: '6.0'` in `pnpm-lock.yaml`. Use `pnpm add -g pnpm && pnpm i` to ensure compatibility.
- **Plugin file structure**: Release zip must contain `dist/`, `package.json`, `plugin.json`, `main.py`, `LICENSE`, `README.md`, and optionally `defaults/`.
- **Settings/config**: Store under `DECKY_PLUGIN_SETTINGS_DIR` (Python: `decky.DECKY_PLUGIN_SETTINGS_DIR`). This plugin uses `decky_networks.json` there for persisting disconnected network state.

## Key Conventions

- Frontend uses `@decky/ui` components (`PanelSection`, `PanelSectionRow`, `DialogButton`, `showModal`)
- Backend uses `decky.logger` for logging, `decky.emit()` for pushing events to frontend
- Plugin data directories: settings → `DECKY_PLUGIN_SETTINGS_DIR`, runtime → `DECKY_PLUGIN_RUNTIME_DIR`, logs → `DECKY_PLUGIN_LOG_DIR`
