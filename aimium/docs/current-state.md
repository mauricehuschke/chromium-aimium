# Aimium – Projektstand

## Einordnung

Aimium ist eine Entwicklungsgrundlage für einen nativen Chromium-Browser.
Foundation-Quellcode, Datenverträge und Buildwerkzeuge sind implementiert.
Ein vollständiger nativer Browserbuild mit den erforderlichen Smoke-Tests und
normaler Navigation ist noch nicht bestätigt. Eine unterbrochene Buildausführung
liefert keine native Abnahme.

Die Chromium-Basis ist ein Entwicklungsstand, keine verifizierte Stable-Basis.
[upstream.json](../upstream.json) hält die Upstream-Identität fest.
`release_eligible: false` bleibt bestehen.

## Implementierter Umfang und offene Funktionen

| Bereich | Im Quellcode vorhanden | Noch offen |
| --- | --- | --- |
| Aimium-WebUI | Featuregeschützte `chrome://aimium`-Foundationseite und beide Feature-an/aus-Smoke-Tests | Vollständige native Kompilierung, Ressourcenerzeugung und ausgeführte Browsertests |
| Datenverträge | Versionierte Schemata, synthetische Beispiele, Python-Referenzvalidator und Tests | Produktiver Store, Laufzeit und native Durchsetzung |
| Buildwerkzeuge | Planung, Vorchecks, lokale Buildbefehle, Source-Identität und getrennte native Testresultate | Vollständige native Plattformnachweise |
| VS-Code-Aufgaben | Nutzerseitiger Build-/Smoke-Start, Vorchecks, Dry-run sowie lokale Python- und Vertragsprüfungen | Tatsächlich ausgeführter nativer Build und Browserprüfung |
| Sitzungspaare | Produktanforderungen und Vertragsgrundlage | Native Agentenfläche, dauerhafte Workspaces, Profil-/Tabbindung und Wiederherstellung |
| KI und Browseraktionen | Verträge und Architekturgrenzen | Connectoraufrufe, Schlüsselspeicher, Browseraktionsdienst und Seitenwissen |
| Workflows | Definitions-/Run-Verträge | Store, Executor, Aktivierungsverwaltung, echter Monitor, Editor und Trigger |
| Produktbetrieb | Entwicklungsgrundlage | Entschlackung, lokale Headless-Laufzeit, optionale Dienste, Sync sowie Installer und Updates |

Die Python-Werkzeuge sind Referenz- und Entwicklungswerkzeuge, kein Backend für
das Browserprodukt. Vorhandene Testquellen oder ein erfolgreicher leichter Check
beweisen weder Browserfunktion noch eine vollständige Produktintegration.

## Native Abnahme

| Ziel | Browserbuild einschließlich Ressourcen | Beide Aimium-Smokes | Normaler Start und Navigation |
| --- | --- | --- | --- |
| Windows x64 | Nicht bestätigt | Nicht bestätigt | Nicht bestätigt |
| Linux x64 | Nicht bestätigt | Nicht bestätigt | Nicht bestätigt |
| macOS arm64 | Nicht bestätigt | Nicht bestätigt | Nicht bestätigt |
| macOS x64 | Nicht bestätigt | Nicht bestätigt | Nicht bestätigt |

Jedes Ziel benötigt einen eigenen Nachweis. Für eine konkrete Prüfung gelten
`PASSED`, `FAILED` oder `NOT_RUN` entsprechend dem tatsächlichen Ergebnis.
Unterbrochene Builds sind als unterbrochen zu behandeln; sie dürfen nicht als
bestandener Vollbuild erscheinen. Leichte Python-Prüfungen übertragen sich nicht
auf diese Matrix.

## Projektregeln für Prüfungen

Prüfungen und Builds erfolgen lokal. GitHub Actions sind deaktiviert; vorhandene
Workflowdateien stellen keinen aktuellen Prüfnachweis dar. Native Builds startet
ausschließlich der Nutzer in VS Code. Agenten starten oder wiederholen keine
nativen Builds, GN-Generierung, Compiler oder Linker.

Der vollständige Quellroot `src` und eine passende lokale Buildumgebung sind
Voraussetzung. Die Standardaufgabe
**Aimium: Build + Smoke (lokal)** baut den Browser und die fokussierten
Aimium-Browsertests und führt nach erfolgreichem Build die Tests aus.
Normale Website-Navigation bleibt eine separate Prüfung.
Details: [Entwicklungsleitfaden](development.md) und
[VS-Code-Aufgaben](../../.vscode/tasks.json).

Source-Identität, Werkzeug-/Abhängigkeitsstand, GN-Argumente, Befehle und
unveränderte Ergebnisse gehören in lokale Buildbelege. Rohlogs, Browserprofile,
Secrets, tatsächliche lokale Pfade und Hostinventare gehören nicht in die
öffentliche Projektdokumentation.

## Nächste Integrationsschritte

- **AIM-001: IN_PROGRESS.** Prüfmechanismen sind implementiert; vollständiger
  nativer Build, beide Smokes und normale Navigation bleiben Abnahmegates.
- **AIM-002: PLANNED.** Dauerhafte Sitzungspaare benötigen die nachgewiesene native
  Integrationsbasis aus [AIM-001](tasks/AIM-001-native-baseline.md).
- **AIM-003: PLANNED.** Manuelle Workflows und Monitor benötigen die verlässlichen
  Workspace-/Profil-/Tabbindungen aus [AIM-002](tasks/AIM-002-session-pairs.md).

Unabhängige Vertrags- und Testvorbereitung darf parallel erfolgen. Sie schließt
kein natives Gate und nimmt keine spätere Produktphase ab. M1 bleibt ein
gespeichertes Sitzungspaar mit einem gespeicherten, manuell gestarteten Workflow
und echtem Monitor. Verbindliche Ziele und Reihenfolge stehen in der
[Produktvision](product-vision.md) und im
[Entwicklungsplan](development-plan.md).
