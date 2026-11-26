# Desktop monitoring and control

[Catalog](../README.md)

## [PhoneBox — ersinkoc/phonebox](https://github.com/ersinkoc/phonebox)

**Status (2026-11-26):** User-saved optional desktop companion application; not an agent skill, MCP, installed component or security-approved tool. Source documentation checked at 0fa26aef9456a04bd68b6ce38d7e16f3ec04c840; no runtime or security audit performed.

**Use:** Repurpose an Android phone as a configurable PC dashboard for CPU/GPU/RAM, local coding sessions (Claude Code, Codex, OpenCode), quota information, GitHub activity, media and optional touch controls. The user has a spare Samsung Galaxy S22 Ultra; its Android version should satisfy Android 5+ minimum. Actual pairing and widget compatibility remain untested. Useful for monitoring development and local WanGP workloads. Overlaps myoffice session monitoring, but adds physical dashboard and hardware monitoring; neither is required.

**Setup:** Windows 10/11, Linux or macOS desktop agent plus Android APK from official releases; USB (ADB debugging) or Wi-Fi pairing without ADB. Prefer trusted local Wi-Fi for first read-only pilot. No root or PhoneBox account required; MIT; optional provider services may cost money. Provider quota availability depends on actual login and integration, especially custom API providers such as FreeLLMAPI.

**Security:** Documentation states loopback settings server, paired keys and pinned TLS for USB/Wi-Fi; no project telemetry, but optional integrations access external services and local session data. Some session views can expose prompts/replies on paired phone. Agent permission prompts, macros, shell commands, process controls and other write actions should remain disabled during pilot. Windows release unsigned per checked README; avoid executing remote setup scripts blindly or bypassing security warnings. Review exact release provenance/checksums, APK, installer, permissions and network binding; SkillSpector alone is not an executable audit. Keep phone locked, avoid exposing port publicly, and do not enable ADB unless needed. For desk use, consider battery protection, ventilation, screen timeout/dimming and OLED burn-in.

**Sources:** [README](https://github.com/ersinkoc/phonebox/blob/0fa26aef9456a04bd68b6ce38d7e16f3ec04c840/README.md), [privacy policy](https://github.com/ersinkoc/phonebox/blob/0fa26aef9456a04bd68b6ce38d7e16f3ec04c840/PRIVACY.md), [guide](https://github.com/ersinkoc/phonebox/blob/0fa26aef9456a04bd68b6ce38d7e16f3ec04c840/docs/GUIDE.md), [releases](https://github.com/ersinkoc/phonebox/releases/latest), [demo](https://ersinkoc.github.io/phonebox/).

No installation, activation, device change, inventory or baseline change authorized by this catalog entry.
