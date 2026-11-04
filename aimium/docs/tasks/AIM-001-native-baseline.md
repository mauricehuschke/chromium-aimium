# AIM-001 – Native Buildbasis und belastbare Prüfnachweise

Status: **IN_PROGRESS; native Abnahme offen**. Priorität: P0.
Abhängigkeit: bestehende Foundation.

Ziel ist eine reproduzierbare native Integrationsbasis. Vorhandene
Buildwerkzeuge, Testquellen und Referenzprüfungen ersetzen keinen vollständig
ausgeführten Browserbuild. Der native Vollnachweis ist noch offen; unterbrochene
Kompilierung liefert keine Freigabe von AIM-002 oder AIM-003.

Prüfungen und Builds erfolgen lokal; GitHub Actions sind deaktiviert.
Ausschließlich der Nutzer startet native Builds aus VS Code. Agenten starten
oder wiederholen keine nativen Builds, GN-Generierung, Compiler oder Linker.
Vorhandene kompatible Ninja-Ergebnisse bleiben für inkrementelle Wiederverwendung
erhalten.

## Vor Beginn

Lies die Root-[AGENTS.md](../../../AGENTS.md),
[Produktvision](../product-vision.md), [Projektstand](../current-state.md) und
[Buildleitfaden](../development.md). Prüfe den vorgesehenen Aimium-Quellstand und
vorhandene Änderungen. Arbeite auf einem nachvollziehbaren Implementierungsstand;
keine vorhandene Nutzerarbeit zurücksetzen oder überschreiben.

Ein Sparse-Checkout eignet sich für Dokumentation und Referenzprüfungen.
Native Builds benötigen den vollständigen `src`-Quellroot in einem vorbereiteten
gclient-Workspace.

## Teilpakete und Umfang

**001-A – Audit und leichte lokale Prüfungen.** Prüfe Source-Identität, vorhandene
Tests und Buildskript. Die Python-Suite und Vertragsbeispiele prüfen die
Referenzwerkzeuge lokal. Erfasse die tatsächlich geänderten nativen Aimium-Dateien
und Chromium-Registrierungsstellen aus dem Diff und ordne passende Prüfungen zu.
Vorhandene Workflowdefinitionen bleiben deaktiviert; ihre Konfiguration
kompiliert keinen nativen Code.

**001-B – Native Umgebung.** Prüfe die zur Zielplattform passende vollständige
gclient-/DEPS- und Toolchain-Konfiguration anhand der Plattformanleitung des
gewählten Quellstands. Halte fehlende Voraussetzungen als lokale Blocker fest.
Keine bestehenden Checkouts durch automatischen Sync, Reset, Installation oder
Überschreiben vermeintlich reparieren. Lokale Maschineninventare und
Administrationsprotokolle gehören nicht in die öffentliche Statusdokumentation.

**001-C – Build und Smoke.** Der Nutzer baut `chrome` und die vorgesehenen
`browser_tests` über die lokalen VS-Code-Aufgaben. Nachzuweisen sind
`AimiumUIBrowserTest.LoadsFoundation` und
`AimiumUIDisabledBrowserTest.NotAvailable` sowie normaler Browserstart und
Navigation mit einem neuen, getrennten Entwicklungsprofil. Tatsächlich
entdeckte und erfolgreich ausgeführte Tests sind getrennt zu prüfen.
Echte GN-/C++-/WebUI-/TypeScript-Probleme in kleinen Änderungen beheben und den
erneuten nativen Build dem Nutzer überlassen.

**001-D – Wiederholbarkeit.** Die Werkzeuge müssen Source-Identität, Upstream,
DEPS-/Werkzeugstand, GN-Argumente, Befehle und Ergebnisse nachvollziehbar in
lokalen Prüfbelegen halten. Pro Windows x64, Linux x64, macOS arm64 und macOS x64
ist der tatsächliche Ergebnisstatus zu erfassen. Öffentliche Dokumentation
beschreibt Umfang und Abnahmestand ohne Rohlogs oder lokale Hostinformationen.
Der VS-Code-/Terminalweg muss zu den vorhandenen Buildwerkzeugen passen und ohne
automatischen Buildstart auskommen.

## Abnahmekriterien

Die folgenden Punkte sind Anforderungen; dieses Dokument erklärt sie nicht
pauschal für erfüllt.

- [ ] Python-Suite und Vertragsbeispiele sind für den geprüften Quellstand lokal
      ausgeführt; Ergebnisse sind von nativen Nachweisen getrennt.
- [ ] Die geänderten nativen Dateien und Registrierungsstellen sind durch die
      vorgesehenen Prüfungen abgedeckt.
- [ ] Mindestens ein vollständiger nativer Build samt beiden echten
      Aimium-Smoke-Fällen und normaler Navigation liegt als erster Teilnachweis vor.
- [ ] Für jedes weitere Ziel liegt ein tatsächlicher Ergebnisstatus vor;
      vereinbarte fehlende native Nachweise bleiben offene Abnahmegates.
- [ ] VS-Code-Aufgaben und portable Befehle stimmen mit den Werkzeugen überein;
      Source, Abhängigkeiten, GN-Argumente und Testergebnisse sind zugeordnet.
- [ ] Sandbox, Zertifikatsvalidierung und Profiltrennung bleiben erhalten;
      kontrollierte Fixtures ersetzen persönliche Konten und Profile.

P0 ist erst mit den vereinbarten nativen Plattformnachweisen abgenommen.
`release_eligible: false` bleibt bestehen.

## Befehlsgrundlage

Die [VS-Code-Aufgaben](../../../.vscode/tasks.json) sind der vorgesehene Einstieg.
Standard: **Aimium: Build + Smoke (lokal)** mit Strg+Umschalt+B
(macOS: Cmd+Umschalt+B). Weitere Aufgaben sind
**Aimium: Voraussetzungen prüfen**, **Aimium: Buildplan prüfen**,
**Aimium: Python-Tests (lokal)** und **Aimium: Vertragsbeispiele (lokal)**.

Für lokale Referenzprüfungen auf Linux/macOS mit Python 3.11+:

```sh
python3 -m unittest discover -s aimium/tests -p 'test_*.py' -v
python3 aimium/contracts/validate.py --examples
python3 aimium/tools/build.py plan --target linux-x64
```

Für den Nutzer im integrierten VS-Code-Terminal des vollständigen Windows-Quellroots:

```powershell
.\aimium\tools\python.cmd aimium\tools\build.py check --target win-x64 --browser-tests --out-dir out/Aimium/win-x64-ninja
.\aimium\tools\python.cmd aimium\tools\build.py build --target win-x64 --browser-tests --jobs 8 --out-dir out/Aimium/win-x64-ninja --dry-run
.\aimium\tools\python.cmd aimium\tools\build.py build --target win-x64 --browser-tests --jobs 8 --out-dir out/Aimium/win-x64-ninja
```

Nach einem fehlgeschlagenen Vorcheck oder Dry-run nicht weiterbauen. Die echte
Buildzeile ist ausschließlich nutzerseitig auszuführen. Auf Linux/macOS
`python3` und das zum Host passende Ziel verwenden; die Ziele sind `linux-x64`,
`mac-arm64` und `mac-x64`. Ein Plan für ein anderes Ziel ist kein Crossbuild.

Der Build verlangt einen sauberen, committeten Quellstand. Bei kompatibler
Source-/DEPS-/Toolchain- und GN-Konfiguration denselben Ninja-Outdir
weiterverwenden. Eine Änderung von `--jobs` löscht gültige Ergebnisse nicht;
Siso- und Ninja-Ausgaben dürfen nicht vermischt werden.

## Nicht enthalten und Blockerregel

Keine Sidebar, Connectorimplementierung, Workflow-Engine, Entschlackung,
Signierung oder Release. Bei fehlenden Voraussetzungen die unabhängigen
Prüfungen und die Blockergrenze festhalten; offene native Prüfungen als
`NOT_RUN` führen. Ein unterbrochener Build ist kein Erfolg.

Unabhängige Modell-/Vertragsarbeit kann vorbereitet werden. Native Integration
von [AIM-002](AIM-002-session-pairs.md) und danach
[AIM-003](AIM-003-workflows-and-monitor.md) setzt die tatsächlich nachgewiesene
Baseline voraus.
