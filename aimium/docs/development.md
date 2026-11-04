# Aimium – lokale Entwicklung und Validierung

## Ausführungsregeln und Stand

Prüfungen und Builds erfolgen lokal. GitHub Actions sind deaktiviert; vorhandene
Workflowdefinitionen dürfen nicht als ausgeführte Prüfung gelten.
Native Builds startet ausschließlich der Nutzer in VS Code. Agenten starten
oder wiederholen keine nativen Builds, GN-Generierung, Compiler oder Linker.
Leichte lokale Python- und Vertragsprüfungen bleiben für passende Änderungen
verfügbar. Es gibt keinen automatischen Buildstart beim Öffnen des Projekts.

Die Foundation enthält die featuregeschützte WebUI und Entwicklungsverträge
sowie Build-/Prüfwerkzeuge. Native Sitzungspaare, Agentenfläche,
Connectoraufrufe und Workflow-Ausführung sind noch nicht implementiert.
Ein vollständiger nativer Build mit beiden Aimium-Smokes und normaler Navigation
ist noch nicht bestätigt; unterbrochene Kompilierung ist keine native Abnahme.

Die importierte Chromium-Basis ist `159.0.8142.0` mit Upstream-Commit
`c80042ad683c5620adc9760ec7b5950c80f9d9ce`.
[upstream.json](../upstream.json) kennzeichnet sie als Entwicklungsstand;
sie ist keine verifizierte Stable-Basis. `release_eligible: false` bleibt bestehen.

## Zwei Arten von Checkout

Ein Sparse-Editingcheckout genügt zum Bearbeiten von Dokumentation,
Datenverträgen und Python-Werkzeugen sowie für deren leichte lokale Prüfungen.
Er kompiliert weder Chromium noch GRIT-/WebUI-Ressourcen und führt keine nativen
Browsertests aus.

Vom Git-Quellroot, mit Python 3.11 oder neuer:

```sh
python3 aimium/contracts/validate.py --examples
python3 -m unittest discover -s aimium/tests -p 'test_*.py' -v
python3 aimium/tools/build.py plan --target linux-x64
```

Windows verwendet dafür [python.cmd](../tools/python.cmd) anstelle von
`python3`. Die Planprüfung liest auch `chrome/VERSION` und `DEPS`;
diese Dateien müssen im Editingcheckout vorhanden sein. Ein Plan für ein anderes
Ziel richtet keine Crosskompilierung ein.

Ein nativer Build benötigt einen vollständigen Aimium-Checkout mit passenden
DEPS-Abhängigkeiten, depot_tools und der Toolchain des gewählten Quellstands.
Verbindlich sind dessen Plattformanleitungen:

- [Windows](../../docs/windows_build_instructions.md)
- [Linux](../../docs/linux/build_instructions.md)
- [macOS](../../docs/mac_build_instructions.md)

Der äußere gclient-Workspace enthält `.gclient` und den Git-Quellroot `src`.
In VS Code `src` öffnen; alle folgenden Ausgabeordner sind relativ dazu.
Die gclient-Solution soll unmanaged sein (`"managed": False`), damit Git den
Aimium-Quellstand bestimmt und die bewusst vorbereiteten Abhängigkeiten zu
diesem Stand passen. Ein unveränderter Upstream-Checkout enthält Aimium nicht.

Native Builds brauchen die passende Plattform und Architektur, genügend RAM
und freien Speicher. Windows benötigt die zur Revision passenden C++-/ATL-/MFC-
und SDK-Komponenten, macOS Xcode und SDK. Linux benötigt seine beschriebenen
Systemabhängigkeiten sowie für Browsertests die grafische Testumgebung.
Der Vorcheck fordert standardmäßig mindestens 100 GiB freien Platz.
Das ist eine Mindestprüfung, keine Vorhersage der endgültigen Buildgröße.

## VS-Code-Aufgaben

Die Aufgaben in [tasks.json](../../.vscode/tasks.json) verwenden VS-Code-Bordmittel;
eine Microsoft-Python-Erweiterung ist nicht erforderlich.

| Aufgabe | Wirkung |
| --- | --- |
| **Aimium: Build + Smoke (lokal)** | Browser und `browser_tests` bauen; danach die fokussierten Aimium-Tests ausführen |
| **Aimium: Voraussetzungen prüfen** | Native Umgebung prüfen, ohne zu kompilieren |
| **Aimium: Buildplan prüfen** | Vorcheck und Dry-run, ohne zu kompilieren |
| **Aimium: Python-Tests (lokal)** | Lokale Referenz-/Werkzeugtests |
| **Aimium: Vertragsbeispiele (lokal)** | Synthetische Verträge validieren |

Der Nutzer startet den Standardbuild mit Strg+Umschalt+B auf Windows/Linux
oder Cmd+Umschalt+B auf macOS. Die Buildaufgaben bieten eine Jobauswahl mit
Standard vier; acht und weitere Grenzen sind auswählbar. Unter macOS muss die
Zielauswahl `mac-arm64` für Apple Silicon oder `mac-x64` für Intel zum
Host passen; Linux verwendet `linux-x64`.

Windows-Aufgaben verwenden [python.cmd](../tools/python.cmd). Der Helper kann
eine optionale `env.cmd` aus dem äußeren Workspace laden.
`AIMIUM_LOCAL_ENV` wählt ausdrücklich eine andere lokale Umgebungsdatei;
eine fehlende explizit ausgewählte Datei ist ein Fehler. `AIMIUM_PYTHON`
bestimmt den Interpreter, `AIMIUM_DEPOT_TOOLS` das depot_tools-Verzeichnis
für den Taskprozess. Ohne solche Einstellungen muss die benötigte Umgebung
bereits verfügbar sein. Linux/macOS verwenden `python3` aus PATH.
Auf allen Plattformen ist Python 3.11+ erforderlich.

Der Windows-Launcher bindet auch nachgelagerte `python3`-Batchaufrufe an den
gewählten Interpreter. Dafür setzt er einen prozesslokalen Shim vor den übrigen
PATH; globale PATH-Einstellungen und Windows-App-Ausführungsaliase bleiben gleich.

Lokale Konfiguration bleibt außerhalb der veröffentlichten Quelldateien.
Credentials, persönliche Pfade, CA-Bundles und Maschineninventare gehören nicht
ins Repository.

## Buildbefehle und Source-Konsistenz

`build.py` bietet unterschiedliche Prüftiefen:

| Aufruf | Verhalten |
| --- | --- |
| `plan` | Source-/Zielplan ausgeben; keine GN-Generierung und keine Kompilierung |
| `check` | Voraussetzungen prüfen; keine Kompilierung |
| `build --dry-run` | Vorcheck und vollständigen Befehlsplan ausgeben; keine Kompilierung |
| `build` | Nach bestandenem Vorcheck GN und Compiler starten |
| `build --browser-tests` | Zusätzlich `browser_tests` bauen und die fokussierten Aimium-Tests ausführen |

Die echten Buildaufrufe sind ausschließlich für den Nutzer im integrierten
VS-Code-Terminal des vollständigen Quellroots vorgesehen.

Windows-Beispiel mit acht Compilerjobs:

```powershell
.\aimium\tools\python.cmd aimium\tools\build.py check --target win-x64 --browser-tests --out-dir out/Aimium/win-x64-ninja
if ($LASTEXITCODE -ne 0) { throw 'Resolve the reported prerequisites first.' }
.\aimium\tools\python.cmd aimium\tools\build.py build --target win-x64 --browser-tests --jobs 8 --out-dir out/Aimium/win-x64-ninja --dry-run
if ($LASTEXITCODE -ne 0) { throw 'Build plan failed.' }
.\aimium\tools\python.cmd aimium\tools\build.py build --target win-x64 --browser-tests --jobs 8 --out-dir out/Aimium/win-x64-ninja
if ($LASTEXITCODE -ne 0) { throw 'Build or smoke tests failed; inspect the receipt.' }
```

Auf Linux/macOS `python3` und das passende native Ziel verwenden.
Nach einem nicht erfolgreichen Vorcheck oder Dry-run nicht weiterbauen.

Ein echter Build verlangt einen sauberen, committeten Quellstand und zeichnet
dessen Identität auf. Er überschreibt keine widersprüchlichen vorhandenen
`args.gn`. Das Werkzeug synchronisiert keine Abhängigkeiten, installiert keine
Voraussetzungen, wechselt keinen Branch und committet oder setzt nichts zurück.

Der Abhängigkeitsvorcheck prüft reale Installationsverzeichnisse.
`.gclient_entries` kann GCS-/CIPD-Einträge als `destination:object-or-package`
enthalten; ihr Suffix ist kein Dateipfad. Mehrere Einträge können ein Ziel teilen.
Der Vorcheck ersetzt weder gclients Downloadintegritätsprüfung noch die
Kompatibilitätsprüfung durch GN und Compiler.

Bei flachen Checkouts muss die erforderliche Upstream-Abstammung für die
Versionswerkzeuge vorhanden sein. `build/util/lastchange.py --json` muss echte
Upstream-Metadaten statt einer erfundenen Version ermitteln können.
Keine `LASTCHANGE`-Daten fälschen und keinen Produktquellstand ändern, um
fehlende Metadaten zu verdecken.

## Ninja-Ausgabe inkrementell verwenden

Windows verwendet laut [targets.json](../build/targets.json)
`use_siso=false` und `use_remoteexec=false`, also lokalen Ninja-Betrieb.
Für Windows ausdrücklich `--out-dir out/Aimium/win-x64-ninja` verwenden.
Andere Ziele behalten ihre jeweiligen Ausführungsstandards; die Windowswahl
belegt keine erfolgreiche Prüfung der anderen Plattformen.

Ein kompatibler bestehender Ninja-Outdir bleibt erhalten. Nach einem Abbruch
können gültige Objekte wiederverwendet werden; Ninja baut fehlende oder durch
Abhängigkeiten veraltete Arbeit neu. Eine Änderung von `--jobs` betrifft die
Parallelität und löscht keine gültigen Objekte.

Wiederverwendung setzt kompatible Source-/DEPS-Stände, Toolchain und GN-Argumente
voraus. Plattformen, Architekturen, inkompatible Einstellungen sowie Siso- und
Ninja-Zustand brauchen getrennte Ausgaben. Einen passenden vorhandenen Outdir
nicht allein zum Fortsetzen löschen oder durch einen neuen Cache ersetzen.
Ein Cachetreffer ist kein Testergebnis und garantiert keine bestimmte Restdauer.

## Native Tests und normale Navigation

Die beiden nativen Smoke-Tests gehören zu `//chrome/test:browser_tests`:

- `AimiumUIBrowserTest.LoadsFoundation`
- `AimiumUIDisabledBrowserTest.NotAvailable`

`--browser-tests` muss beide Namen tatsächlich entdecken und frisch ausführen.
Der fokussierte Filter lautet
`--gtest_filter=AimiumUIBrowserTest.*:AimiumUIDisabledBrowserTest.*`.
Es wird nicht die gesamte Chromium-Browsertestsuite gestartet.
Der aktivierte Test prüft die gebündelte Lit-Anwendung, nicht nur ihren Titel.

Der Launcher schreibt `aimium-browser-tests.json` in den Ausgabeordner.
Das Buildwerkzeug entfernt einen vorherigen Testbericht unmittelbar vor dem
neuen Lauf. Alle entdeckten Tests müssen in jeder Iteration einen
`SUCCESS`-Ausführungsdatensatz haben. Fehlende, leere, übersprungene,
fehlgeschlagene oder veraltete Ergebnisse sind kein Erfolg; ein Exitcode null
allein genügt nicht. Automatische Launcher-Wiederholungen sind deaktiviert.

Das lokale `aimium-build-manifest.json` hält Source-Identität, Argumente,
Befehle und Ergebnis sowie getrennt `native_tests` fest.
`status: built` bei `native_tests.status: not_run` belegt keinen bestandenen
Smoke-Test. Ein unterbrochener Build bleibt ohne vollständigen Abnahmenachweis.

Der erwartete Windows-Browser liegt unter
`out/Aimium/win-x64-ninja/chrome.exe`. Seine Existenz allein reicht nicht.
Nach einem erfolgreichen Build sind normaler Start und Navigation gesondert
mit einem neuen, getrennten Entwicklungsprofil und kontrollierten lokalen
HTTP-Fixtures zu prüfen. Persönliche Browserprofile oder Konten nicht verwenden.

Das standardmäßig deaktivierte Feature wird mit `--enable-features=Aimium`
eingeschaltet; `chrome://aimium` zeigt die Foundationseite.
Beide Featurezustände sowie normale Navigation brauchen echte native Nachweise.
Keine Sandboxabschaltung, Zertifikatsumgehung oder Lockerung der Profiltrennung
für einen Test einführen.

## Abnahme und öffentliche Dokumentation

Für die native Baseline sind erforderlich:

1. Vollständige Browser- und Ressourcenbuilds für die vereinbarten Desktopziele.
2. Kompilierte und tatsächlich bestandene Feature-an/aus-Smoke-Tests.
3. Normaler Browserstart und Navigation in einem getrennten Entwicklungsprofil.
4. Zuordnung der Ergebnisse zu Source-, Abhängigkeits-, Toolchain- und GN-Stand.
5. Keine Provideraufrufe, Credentialzugriffe oder echten Websiteänderungen in P0.

Ein erster Plattformnachweis schließt nicht die übrige Matrix.
Leichte Python-Tests, vorhandene Testdateien und die Taskkonfiguration sind keine
Belege für C++-/WebUI-Kompilierung oder Browserfunktion.

Buildbelege und Rohlogs bleiben lokal und außerhalb versionierter Publikationen.
Öffentlich dokumentiert werden Funktionsumfang, portable Reproduktionswege und
offene Abnahmekriterien. Persönliche Informationen, tatsächliche lokale Pfade,
Maschineninventare und Installations-/Administrationschroniken werden nicht
veröffentlicht. Die öffentliche Statusdokumentation enthält keine vergänglichen
Implementierungsheads oder lokalen Laufprotokolle.

## Weitere Releasegates

P0 ist kein signiertes, notarisiertes oder als Produktions-Aimium paketiertes
Release. Separate Anwendungs-/Profilidentität, verifizierte Stable-Basis,
Lizenzen, native Plattformprüfung, Signierung und getestete Installation/Updates
sind weitere Gates. Signing- und Providercredentials gehören in geeignete lokale
Geheimnisspeicher, nicht in die Quellen.

Die [Produktvision](product-vision.md), der
[Entwicklungsplan](development-plan.md) und
[AIM-001](tasks/AIM-001-native-baseline.md) bestimmen die Reihenfolge.
