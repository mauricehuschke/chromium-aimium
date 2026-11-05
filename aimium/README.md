# Aimium

Aimium ist ein natives Chromium-Browserprojekt für Windows, Linux und macOS.
Die folgenden Produktziele beschreiben die geplante Nutzung. Der tatsächlich
vorhandene Foundationstand und seine offenen Nachweise stehen getrennt darunter.

## Ziel: gespeicherte Sitzungspaare

Jeder Produkttab ist immer ein benanntes, dauerhaft gespeichertes Paar:
links Agent, Prompt und Kontext; rechts die echte Website. Workflow-Explorer,
grafischer Editor und Ausführungsansicht gehören zu diesem Paar. Der Wechsel
zwischen diesen Ansichten erhält den Websitezustand und die Anmeldung.

Mehrere Workspaces, mehrere Sitzungen derselben Website und mehrere Workflows
je Workspace sind vorgesehen. Schließen bedeutet nicht Löschen: gespeicherte
Sitzung, Kontext und Workflows sollen wieder geöffnet und nach einem Neustart
wiederhergestellt werden können.

Mensch und Agent arbeiten mit derselben echten Chromium-Seite und dem bewusst
zugeordneten Browserprofil. Der Nutzer kann sich selbst anmelden, manuell
arbeiten und jederzeit übernehmen. Die Profilidentität bleibt bei einem Wechsel
von Connector oder Modell erhalten; getrennte Konten benötigen bewusst getrennte
Profile. Ohne Connector zeigt die Agentenfläche den fehlenden Einrichtungsstand,
während die Website manuell nutzbar bleibt.

Browseraktionen, Beobachtung und Workflow-Ausführung finden lokal statt.
Anfangs muss Aimium geöffnet sein. Modelle können lokal laufen oder ausdrücklich
gewählte externe Anbieter verwenden; freigegebener Kontext geht nur an die
gewählte Anbindung. Ein Modellwechsel ist kein Wechsel der Websiteanmeldung.
Lokale Headless-Ausführung, optionale Unterstützer-/E-Mail-Dienste und Cloud-Sync
von Definitionen folgen später. Cookies, Schlüssel und aktive Browserrechte
werden dadurch nicht automatisch übertragen.

**M1** ist eine dauerhafte Sitzung mit einem gespeicherten, manuell gestarteten
Workflow und einem echten Monitor. Er zeigt den tatsächlichen aktuellen Schritt,
Wartegründe und Verlauf und ermöglicht Pause, Abbruch und menschliche Übernahme.
Zeit- und Webseitenereignisse kommen später; ein auf einen Auslöser wartender
Workflow ist kein bereits laufender Run.

Verbindliche Einzelheiten: [Produktvision](docs/product-vision.md),
[Entwicklungsplan](docs/development-plan.md) und
[Architektur](docs/architecture.md).

## Tatsächlicher Stand: P0-Foundation

Die Foundation enthält:

- Eine featuregeschützte native `chrome://aimium`-WebUI im Quellcode.
- Versionierte Datenverträge und synthetische Beispiele für Workspaces,
  Connectoren, Workflows, Runs und Browseraktionen.
- Einen Python-Referenzvalidator und lokale Tests der Vertrags-/Buildwerkzeuge.
- Buildplanung, Vorprüfungen und einen gesonderten nativen Buildweg für
  Windows x64, Linux x64 sowie macOS arm64 und x64.

Die WebUI ist eine Foundationseite. Native Sitzungspaare, linke Agentenfläche,
dauerhafter Workspace-Store, Connector-/Credential-Service, Modellaufrufe,
Browseraktionsdienst, Workflow-Engine, Monitor, Editor und Scheduler sind damit
noch nicht implementiert. Der Python-Validator ist ein Entwicklungswerkzeug,
kein produktives Browserbackend.

Ein vollständiger nativer Browserbuild, beide nativen Smoke-Tests und normale
Navigation sind noch nicht bestätigt. Der [Projektstand](docs/current-state.md)
trennt vorhandenen Code von offenen nativen Nachweisen.

Projektprüfungen werden lokal ausgeführt; GitHub Actions sind deaktiviert.
Künftige native Builds startet ausschließlich der Nutzer in VS Code.
Agenten starten keine Builds und aktivieren Actions nicht eigenständig.

Die native AIM-001-Abnahme bleibt offen. Unabhängige Vertrags-/Testvorbereitung
ersetzt sie nicht; die native Integration von
[AIM-002](docs/tasks/AIM-002-session-pairs.md) und
[AIM-003](docs/tasks/AIM-003-workflows-and-monitor.md) folgt erst hinter dem
Baseline-Gate. `release_eligible: false` bleibt bestehen.

## Lokaler Build in VS Code

### Workspace und lokale Umgebung

Den vollständigen Git-Quellroot `src` öffnen. Eine Ebene darüber liegt der
gclient-Workspace mit `.gclient`. Ein Sparse-Checkout genügt nur für
Dokumentation und Python-Prüfungen. Native Builds brauchen passende
DEPS-Abhängigkeiten, depot_tools, Python 3.11+, Toolchain, RAM und freien Speicher.
Grundlage sind die Anleitungen dieses Quellstands für
[Windows](../docs/windows_build_instructions.md),
[Linux](../docs/linux/build_instructions.md) und [macOS](../docs/mac_build_instructions.md).

Windows verwendet `aimium/tools/python.cmd`. Optional lädt er `env.cmd`
aus dem äußeren Workspace; `AIMIUM_LOCAL_ENV` wählt eine andere private Datei,
`AIMIUM_PYTHON` den Interpreter und `AIMIUM_DEPOT_TOOLS` depot_tools.
Nachgelagerte `python3`-Batchaufrufe verwenden denselben Interpreter.
Globale PATH-Einstellungen und Windows-App-Aliase bleiben unverändert.
Linux/macOS verwenden `python3`. Keine VS-Code-Python-Erweiterung nötig.
Lokale Pfade, Zugangsdaten, CA-Bundles, Profile und Rohlogs bleiben außerhalb Git.

### Profile und zwölf parallele Jobs

| Profil | Zweck und Einstellungen | Standardausgabe |
| --- | --- | --- |
| `dev` (Standard) | Debug-/Component-Build; `symbol_level=1`, Blink-/V8-Symbole aus | `out/Aimium/<target>-dev` |
| `optimized` | Bisherige optimierte, statische Konfiguration unverändert | Windows `out/Aimium/win-x64-ninja`; sonst `out/Aimium/<target>` |

Component-Builds verkürzen insbesondere das erneute Linken nach Änderungen.
Grundlage sind Chromiums [Component-Build-Anleitung](../docs/component_build.md)
und [Empfehlungen für schnellere Builds](../docs/windows_build_instructions.md#faster-builds).
`dev` verzichtet auf lokale Variablen-/Typinformationen und auf
Blink-/V8-Quellcode-Debugging. Für solche Debugging-Anforderungen ist ein
gesondertes geprüftes Profil nötig. Beide Profile sind Entwicklungsbuilds,
keine offiziellen oder freigegebenen Releases.

**Der erstmalige Wechsel auf `dev` braucht viele neue C++-Objekte und
zusätzlichen Platz.** Andere Compilerargumente erlauben keine allgemeine
Wiederverwendung optimierter Objekte. Der alte Zwischenstand bleibt separat
erhalten. Unterschiedliche Profile niemals in denselben Ausgabeordner schreiben.

Standard sind **zwölf parallele Compilerjobs**, nicht zwölf Threads insgesamt:
Compiler und Linker können intern weitere Threads nutzen. Auswahlreihenfolge:
`--jobs`, dann `AIMIUM_BUILD_JOBS`, dann zwölf.
VS Code übergibt den gewählten Wert ausdrücklich. Auf stärkeren Buildrechnern
mehr Jobs wählen, bei Speicherdruck reduzieren; dadurch wird kein Cache gelöscht.

### VS-Code-Aufgaben

**Strg+Umschalt+B** (macOS: **Cmd+Umschalt+B**) startet
**Aimium: Browser bauen (lokal)**. Vorgabe: Profil `dev`, zwölf Jobs.

| Aufgabe | Wirkung |
| --- | --- |
| **Aimium: Browser bauen (lokal)** | Browser ohne Testbinary bauen; täglicher Standard |
| **Aimium: Build + Smoke (lokal)** | Browser und `browser_tests` bauen; beide Aimium-Smokes entdecken und ausführen |
| **Aimium: Browser bauen (ausführlich)** | Browser mit `--verbose` bauen |
| **Aimium: Optimierten Build fortsetzen** | Altes Profil mit passendem Ausgabeordner verwenden |
| **Aimium: Voraussetzungen prüfen** | Vorcheck ohne GN-Generierung oder Kompilierung |
| **Aimium: Buildplan prüfen** | Vorcheck und Dry-run ohne Kompilierung |
| **Aimium: Python-Tests (lokal)** | Referenz-/Werkzeugtests |
| **Aimium: Vertragsbeispiele (lokal)** | Synthetische Beispiele prüfen |

Profil ist auswählbar, Jobs und Mindestplatz sind frei eingebbar.
Standardmäßig verlangt der Vorcheck 100 GiB freien Platz.
`--min-free-gib` beziehungsweise die VS-Code-Eingabe ändern diese Startprüfung
nach bewusster Kapazitätsplanung; sie schaffen keinen Platz und prognostizieren
den Restbedarf nicht. Ein neues Profil braucht Platz trotz vorhandenem Altprofil.

### PowerShell und andere Terminals

Aus dem vollständigen Windows-Quellroot:

```powershell
.\aimium\tools\python.cmd aimium\tools\build.py check --target win-x64 --profile dev
.\aimium\tools\python.cmd aimium\tools\build.py build --target win-x64 --profile dev --jobs 12 --dry-run
.\aimium\tools\python.cmd aimium\tools\build.py build --target win-x64 --profile dev --jobs 12
```

Nach fehlgeschlagenem Vorcheck/Dry-run zuerst die gemeldete Ursache beheben.
Für die native Abnahme ausdrücklich `--browser-tests` ergänzen.
Der Filter reduziert die spätere Testausführung, nicht die Kompilierung des
großen Testbinarys. Browser-only nimmt AIM-001 nicht ab.

Bisherigen Windows-Ninja-Zwischenstand fortsetzen:

```powershell
.\aimium\tools\python.cmd aimium\tools\build.py build --target win-x64 --profile optimized --jobs 12
```

Phasenmeldungen erscheinen sofort vor Sourceprüfung, Vorcheck, GN, Kompilierung
und Tests. `--verbose` zeigt zusätzlich Befehlsargumente und ausführliche
Ninja-Kompilierbefehle. Einzelne Phasen haben trotzdem keinen laufenden
Prozentzähler. Auf Linux/macOS `python3` und das passende native Ziel verwenden.

### Ninja wiederverwenden und auf anderen Rechnern bauen

Windows bleibt bei lokalem Ninja (`use_siso=false`, `use_remoteexec=false`);
andere Plattformen behalten ihren Buildsystemstandard.
Den Ausgabeordner innerhalb desselben kompatiblen Profils behalten:
Ninja verwendet fertige Objekte weiter und baut fehlende/veraltete Arbeit neu.
Unvollständige Schritte werden nach Abbruch wiederholt.
Jobzahl und `--verbose` ändern keine GN-Argumente.
`build.py` überschreibt widersprüchliche vorhandene `args.gn` nicht.

Eine Betriebssystem-Sperre verhindert überlappende Aimium-Wrapper-Builds im
selben Outdir. Sie wird beim Prozessende freigegeben; die kleine
`.aimium-build.lock`-Datei darf liegen bleiben. Terminal und VS Code
teilen diese Sperre; direkte Ninja-Aufrufe umgehen sie.

Weitere Rechner brauchen denselben geprüften Commit und einen eigenen
vorbereiteten gclient-Workspace mit passenden SDKs, Toolchains und privater
Umgebung. Native Plattform, Profil und passende Jobzahl wählen, beispielsweise:

```sh
AIMIUM_BUILD_JOBS=48 python3 aimium/tools/build.py build --target linux-x64 --profile dev
```

Die Profile sind übertragbar, `out/` ist kein allgemein portabler Cache:
absolute Pfade, Source-/DEPS-Stand, SDKs und Toolchains müssen passen.
Pro Rechner, Plattform und Profil eigene Ausgaben aufbauen und weiterverwenden.
Keine automatische SSH-Verteilung, Remote Execution, Cache-Server oder
GitHub Actions werden eingerichtet. Ein anderer Buildhost führt keine
Nutzer-Workflows remote aus.

### Ergebnis und Abnahme

Der erwartete Windows-Browser liegt unter
`out/Aimium/win-x64-dev/chrome.exe`, optimiert weiterhin unter
`out/Aimium/win-x64-ninja/chrome.exe`.
Im jeweiligen Ordner liegen `aimium-build-manifest.json` und nach
Testausführung `aimium-browser-tests.json`.

`status: built` mit `native_tests.status: not_run` ist ein Browser-only-
Ergebnis, kein bestandener Smoke-Test. Nur tatsächlich entdeckte und frisch
ausgeführte Feature-an/aus-Smokes sowie normaler Start und Navigation mit einem
getrennten Entwicklungsprofil liefern den vorgesehenen nativen Teilnachweis.
Ein Cachetreffer oder eine vorhandene Browserdatei genügen nicht.

`--enable-features=Aimium` und `chrome://aimium` zeigen nur die
Foundationseite. Persönliche Profile, Sandboxabschaltung und
Zertifikatsumgehung sind keine Testhilfen.

## Weiterarbeit und Releasegrenzen

Einstieg: [vollständige Übergabe](docs/codex-handoff.md),
[AIM-001](docs/tasks/AIM-001-native-baseline.md),
[Entwicklungsdetails](docs/development.md), [Verträge](contracts/README.md),
[Beispiele](examples/) und [Buildwerkzeuge](tools/).
Für Agenten gelten zusätzlich die [Repositoryregeln](../AGENTS.md).

Die importierte Chromium-Version ist ein Entwicklungsstand und keine verifizierte
Stable-Basis; siehe [upstream.json](upstream.json). Produktionsbranding, eigene
Installations-/Profilidentität, Stable-Migration, Signierung, Notarisierung,
Installer und getestete Updates sind weitere Releasegates. Leichte Python- oder
Vertragsprüfungen ersetzen keine nativen Nachweise für Windows, Linux und macOS.

Die [Chromium-Lizenz](../LICENSE) und sämtliche Drittanbieterhinweise bleiben
gültig. Dieses Verzeichnis ersetzt oder ändert keine Upstream-Lizenzen; siehe
[Chromiums Regeln für Drittanbieterabhängigkeiten](../docs/adding_to_third_party.md).
