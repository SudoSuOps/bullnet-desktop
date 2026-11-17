# BullNet Desktop

Branded build of the Mattermost Desktop App (upstream `mattermost/desktop`, base tag `v6.4.0`) locked to the BullNet office.

## What differs from upstream

| Area | Change | Where |
| --- | --- | --- |
| Name and IDs | Product `BullNet`, package `bullnet-desktop`, app ID `ai.bullnet.Desktop` | `package.json`, `electron-builder.ts`, `src/main/app/initialize.ts`, `src/main/notifications/dnd-windows.ts`, `src/main/utils.ts`, `src/assets/linux/create_desktop_file.sh` |
| Server | One locked server, `https://office.swarmandbee.ai`; users cannot add or edit servers | `src/common/config/buildConfig.ts` |
| Updates | Mattermost update feed off; BullNet ships its own builds | `buildConfig.ts` |
| Help menu | Mattermost user guide / Academy / upgrade links hidden | `buildConfig.ts` |
| Deep links | `bullnet://` instead of `mattermost://`, so it never fights the stock app | `src/common/constants.ts`, `electron-builder.ts` |
| Crash reports | Sentry off by default | `src/common/config/defaultPreferences.ts` |
| Icons | App, tray, macOS menu bar, DMG background rendered from the brand kit | `scripts/bullnet-brand.py`, sources in `resources/bullnet/` |
| In-app logo | BullNet lockup in headers; the B in the loading animation | `src/renderer/components/Images/Logo.tsx`, `src/renderer/components/LoadingAnimation/LoadingIcon.tsx` |
| Strings | Three user-facing "Mattermost" messages say BullNet | `i18n/en.json` |

The app data folder is `~/.config/BullNet` (Linux), separate from the stock Mattermost app.

## Build (Linux)

```bash
source ~/.nvm/nvm.sh && nvm use 24.16.0
npm ci
# icons (needs a venv with cairosvg + pillow)
python3 -m venv /tmp/iconenv && /tmp/iconenv/bin/pip install cairosvg pillow
/tmp/iconenv/bin/python scripts/bullnet-brand.py
npm run build-prod
npx electron-builder --linux deb tar.gz appimage --x64 --publish=never
```

Output lands in `release/<version>/`.

## Windows and macOS

Same source; build on those systems with `npm run package:windows` / `npm run package:mac`. Both must be code-signed before distributing:
- Windows: code-signing certificate (`.pfx`) and `signtool`.
- macOS: Apple Developer account, "Developer ID Application" certificate, then notarization.

## Updating to a new upstream release

```bash
git fetch upstream --tags
git rebase <new-tag>   # resolve conflicts in the files listed above
```

Upstream is Apache 2.0 licensed; keep `LICENSE.txt` and `NOTICE.txt`.
