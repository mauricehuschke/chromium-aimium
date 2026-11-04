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

### Richtigen Ordner und Voraussetzungen wählen

Der vollständige Chromium-Aufbau trennt den äußeren Workspace vom Quellroot:

| Pfad | Aufgabe |
| --- | --- |
| Äußerer gclient-Workspace | Enthält `.gclient`, Abhängigkeitsmetadaten und das Verzeichnis `src` |
| `src` | Git-Quellroot; diesen Ordner in VS Code öffnen und von hier die Aufgaben ausführen |
| `out/Aimium/win-x64-ninja` | Inkrementelle Windows-Ninja-Ausgabe, relativ zum Git-Quellroot |

Ein Sparse-Checkout für Bearbeitung und Vertragsprüfungen ist keine native
Buildumgebung. Benötigt werden ein vollständiger, zum gewählten Commit passender
gclient-/DEPS-Stand, depot_tools, Python **3.11 oder neuer**, die plattformgerechte
Toolchain und ausreichend RAM und freier Datenträgerplatz. Auf Windows gehören
die zur Chromium-Revision passenden Visual-Studio-C++-, ATL-/MFC- und
Windows-SDK-Komponenten dazu. Der Vorcheck fordert standardmäßig mindestens
100 GiB freien Platz; er ist keine Vorhersage der endgültigen Buildgröße.

Bei einem neuen Workspace muss `src` den Aimium-Fork mit einem geprüften
Implementierungsstand enthalten. Ein unveränderter Upstream-Checkout enthält
die Aimium-Erweiterungen nicht.

Die maßgeblichen Plattformanleitungen sind
[Windows](../docs/windows_build_instructions.md),
[Linux](../docs/linux/build_instructions.md) und
[macOS](../docs/mac_build_instructions.md). macOS benötigt einen passenden Mac
mit Xcode und SDK; Linux seine beschriebenen Systemabhängigkeiten sowie für
native Browsertests die grafische Testumgebung.

Windows-Aufgaben verwenden [tools/python.cmd](tools/python.cmd).
Der Helper lädt eine vorhandene `..\env.cmd` aus dem äußeren Workspace
als optionale lokale Konfiguration, etwa für Python- und Toolchainpfade.
Die Konfiguration kann unabhängig von der Standardsuche ausdrücklich gewählt
werden:

- `AIMIUM_LOCAL_ENV`: Pfad zu einer bestimmten `env.cmd` anstelle der Standardsuche.
- `AIMIUM_PYTHON`: Pfad zum Python-Interpreter; Python 3.11+ bleibt erforderlich.
- `AIMIUM_DEPOT_TOOLS`: Verzeichnis der lokal eingerichteten depot_tools.

Der Launcher verwendet den gewählten Interpreter auch für nachgelagerte
`python3`-Batchaufrufe, etwa Protobuf-Plugins. Diese Auswahl gilt nur für den
Taskprozess und seine Unterprozesse; System-PATH und App-Aliase werden nicht geändert.

Eine bereits passend eingerichtete Umgebung benötigt keine `env.cmd`.
Persönliche Konfiguration, Zugangsschlüssel und andere Geheimnisse gehören nicht
ins Repository. Auf Linux und macOS verwenden die Aufgaben `python3`; auch dort
ist Python 3.11+ erforderlich.

Native Builds verlangen einen **sauberen, committeten Quellstand**. Die Aufgaben
führen keinen automatischen Sync, Reset, Checkoutwechsel oder Toolchain-Install
durch. Fehlende Voraussetzungen werden gemeldet und zuerst gezielt behoben.

### Aufgaben ausführen

Die Aufgaben in [../.vscode/tasks.json](../.vscode/tasks.json) verwenden
VS-Code-Bordmittel. Eine Microsoft-Python-Erweiterung ist dafür nicht notwendig.

| Aufgabe | Wirkung |
| --- | --- |
| **Aimium: Build + Smoke (lokal)** | Standard für **Strg+Umschalt+B** (macOS: **Cmd+Umschalt+B**): Browser und `browser_tests` bauen, anschließend die fokussierten Aimium-Smoke-Tests ausführen |
| **Aimium: Voraussetzungen prüfen** | Native Umgebung prüfen; kein Compilerlauf |
| **Aimium: Buildplan prüfen** | Vorcheck und Dry-run des Buildplans; kein Compilerlauf |
| **Aimium: Python-Tests (lokal)** | Lokale Python-Suite; kein nativer Browsernachweis |
| **Aimium: Vertragsbeispiele (lokal)** | Synthetische Verträge validieren; keine Provider-/Browseraufrufe |

Die Buildaufgaben fragen die Zahl paralleler Compilerjobs ab: Standard ist **4**,
**8** ist ausdrücklich auswählbar. Die Benutzeraktion in VS Code ist der
Buildstart. Es gibt keinen automatischen Buildstart beim Öffnen des Projekts
und keinen durch Agenten gestarteten Build.

Für Windows sind dies die entsprechenden Befehle im integrierten Terminal des
Quellroots; die zweite Zeile zeigt ein Beispiel mit acht Compilerjobs:

```powershell
.\aimium\tools\python.cmd aimium\tools\build.py check --target win-x64 --browser-tests --out-dir out/Aimium/win-x64-ninja
.\aimium\tools\python.cmd aimium\tools\build.py build --target win-x64 --browser-tests --jobs 8 --out-dir out/Aimium/win-x64-ninja
```

Nur nach bestandenem Vorcheck den Build auslösen. Für eine reine Prüfung der
zweiten Zeile dient die Aufgabe **Aimium: Buildplan prüfen**; sie ergänzt
`--dry-run`. `--browser-tests` im echten Build baut nicht nur das
Testprogramm, sondern startet danach die fokussierten Tests
`AimiumUIBrowserTest.*:AimiumUIDisabledBrowserTest.*`.
Es ist kein Test aller Chromium-Browsertests.

Unter Linux gilt `linux-x64`. Auf macOS muss das Ziel zur CPU passen:
`mac-arm64` für Apple Silicon oder `mac-x64` für Intel; bei der
Zielauswahl den tatsächlichen Host wählen. Ein Buildplan für eine andere
Architektur ist kein eingerichteter Crossbuild. Die Windows-Ninja-Einstellungen
werden nicht als geprüfte Einstellungen für andere Hosts ausgegeben.

### Vorhandenen Ninja-Cache wiederverwenden

Für Windows legt [build/targets.json](build/targets.json) **`use_siso=false`**
und **`use_remoteexec=false`** fest. `build.py` verwendet damit den
lokalen Ninja-Buildweg. Für Windows-Builds den Ausgabepfad
**`out/Aimium/win-x64-ninja`** verwenden; ohne `--out-dir` würde ein anderer
Standardpfad gewählt.

Beim erneuten Aufruf im selben Outdir nutzt Ninja noch gültige Ergebnisse.
Nach einem Abbruch bleiben gültige Objekte erhalten; nur fehlende, unvollständige
oder durch Änderungen veraltete Arbeit muss erneut entstehen. Eine Änderung von
`--jobs` ändert die Parallelität und löscht den Cache nicht.

Wiederverwendung setzt einen kompatiblen Quell-/DEPS-Stand, dieselbe passende
Toolchain und kompatible GN-Argumente voraus. Ninja entscheidet anhand seiner
Abhängigkeiten, was neu gebaut werden muss. `build.py` überschreibt
abweichende vorhandene `args.gn` nicht stillschweigend. Ein anderer
Commit kann gültige Teilergebnisse wiederverwenden, ist aber nur mit einem neuen
eindeutigen Source-Nachweis und erneut ausgeführten Tests geprüft.

Siso-Ausgaben und Ninja-Zustand werden nicht vermischt. Liegt bereits eine
kompatible Ninja-Ausgabe vor, denselben Outdir weiterverwenden und zum Fortsetzen
nicht löschen oder durch einen neuen Cache ersetzen. Bei anderen Buildsystemen
oder inkompatiblen Argumenten getrennte Ausgaben verwenden. Inkrementelles Bauen
spart gültige Arbeit, garantiert aber weder einen erfolgreichen Restbuild noch
eine bestimmte Restdauer.

### Ergebnis und Browserpfad

Der Windows-Browser wird unter
`out/Aimium/win-x64-ninja/chrome.exe` relativ zum Git-Quellroot
erwartet. Seine bloße Existenz ist kein erfolgreicher Buildnachweis.

Im selben Ausgabeverzeichnis liegen `aimium-build-manifest.json` und nach
dem Testlauf `aimium-browser-tests.json`. Der Manifeststatus
`built` zusammen mit `native_tests.status: passed` muss zur
tatsächlichen Quelle und Browserdatei passen. Das Tool verlangt die beiden
benannten Smoke-Tests und frische erfolgreiche Ausführungsdaten; eine leere
Testauswahl oder ein alter Ergebnisbericht genügt nicht.

Nach einem erfolgreichen Build zeigt `--enable-features=Aimium` zusammen mit
`chrome://aimium` lediglich die Foundationseite. Das Feature ist
standardmäßig deaktiviert. Für einen späteren Browserstart ist ein neues,
getrenntes Entwicklungsprofil erforderlich; kein bestehendes Chrome-Profil
verwenden. Normale Navigation auf kontrollierten lokalen Fixtures bleibt ein
gesonderter Nachweis und wird durch die VS-Code-Aufgabe nicht automatisch
abgenommen.

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
