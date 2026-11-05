# Aimium – lokale Entwicklung und Validierung

## Ausführungsregeln und Stand

Prüfungen und Builds erfolgen lokal. GitHub Actions sind deaktiviert; vorhandene
Workflowdefinitionen dürfen nicht als ausgeführte Prüfung gelten.
Native Builds startet ausschließlich der Nutzer in VS Code oder im Terminal. Agenten starten
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

## Profile, VS Code und Buildrechner

Die [lokale Buildanleitung](../README.md#lokaler-build-in-vs-code) ist der
vollständige Einstieg für VS Code, PowerShell und weitere Buildrechner.

| Auswahl | Verhalten |
| --- | --- |
| `--profile dev` (Standard) | Debug-/Component-Build; `symbol_level=1`, Blink-/V8-Symbole aus |
| `--profile optimized` | Bisherige optimierte statische Konfiguration unverändert |
| `--jobs 12` | Standard; CLI vor `AIMIUM_BUILD_JOBS` vor Projektvorgabe |
| `--verbose` | Wrapper-Befehle und ausführliche Ninja-Kompilierbefehle |
| `--browser-tests` | Zusätzlich großes Testbinary bauen und beide Aimium-Smokes prüfen |
| `--min-free-gib` | Positiver Mindestwert freien Platzes beim Vorcheck; Standard 100 |

Vorgaben: [targets.json](../build/targets.json).
`dev` verwendet `out/Aimium/<target>-dev`.
`optimized` behält Windows `out/Aimium/win-x64-ninja` und sonst
`out/Aimium/<target>`. Windows verwendet weiterhin lokalen Ninja-Betrieb.

Der erstmalige Profilwechsel braucht viele neue Objekte und zusätzlichen Platz;
er verspricht keinen sofortigen Restzeitgewinn. Alte Ausgaben bleiben erhalten.
Nicht verschiedene Profile in denselben Outdir schreiben oder gültige Caches
nur zum Fortsetzen löschen. Die festen Profile enthalten keine allgemeinen
Compileroptionen für beliebige Debugging-Anforderungen.

Strg+Umschalt+B beziehungsweise Cmd+Umschalt+B startet
**Aimium: Browser bauen (lokal)**, ohne Testbinary. Für Abnahme und passende
Codeänderungen ausdrücklich **Aimium: Build + Smoke (lokal)** verwenden.
Weitere Aufgaben prüfen Voraussetzungen/Plan, bauen ausführlich, setzen das
optimierte Profil fort oder prüfen Python-/Vertragswerkzeuge.
Jobs (Vorgabe zwölf) und Mindestplatz sind frei eingebbar, Profile auswählbar.
macOS verlangt die passende native Architektur. Kein Start beim Projektöffnen;
keine Python-Erweiterung erforderlich.

Der Windows-[Launcher](../tools/python.cmd) lädt optional die private äußere
`env.cmd` oder `AIMIUM_LOCAL_ENV`.
`AIMIUM_PYTHON` und `AIMIUM_DEPOT_TOOLS` wählen lokale Werkzeuge ohne
globale PATH-/App-Alias-Änderungen. Nachgelagerte `python3`-Batchaufrufe
verwenden denselben Interpreter. Linux/macOS verwenden `python3`,
überall Python 3.11+.

## Source-Konsistenz und Wiederverwendung

`plan` liest die Quellenidentität und beschreibt Befehle ohne GN-Generierung.
`check` und `build --dry-run` prüfen ohne Kompilierung.
Nur der Nutzer startet `build` nach bestandenem Vorcheck auf sauberem,
committetem Quellstand. Das Tool synchronisiert, installiert, committet und
wechselt keine Quellen. Es überschreibt keine inkompatiblen `args.gn`.

Die Betriebssystem-Sperre `.aimium-build.lock` verhindert zwei Wrapper-Builds
im selben Outdir. Prozessende gibt sie frei, die kleine Datei darf liegen bleiben.
Direkte Ninja-Aufrufe umgehen die Sperre.

Ninja prüft Source-/DEPS-, Toolchain- und Befehlsänderungen.
Plattformen, Architekturen und inkompatible Konfigurationen brauchen eigene
Ausgaben. Jobs und Verbose-Ausgabe ändern keine GN-Argumente.
Abgebrochene Schritte werden wiederholt; fertige kompatible Ergebnisse
müssen nicht erneut kompiliert werden. Ein anderer Commit braucht eine neue
Quellenzuordnung und frische Tests.

Weitere Buildrechner benötigen eigene vorbereitete gclient-Workspaces, SDKs
und Toolchains. Ausgaben mit absoluten Pfaden sind kein allgemein portabler
Cache. Höhere Jobzahlen lassen sich per CLI, Umgebungswert oder VS-Code-Eingabe
wählen. Automatische Remoteausführung, CI-Runner und Infrastrukturkäufe werden
nicht eingerichtet.

`.gclient_entries` wird als Daten gelesen, nicht ausgeführt.
Virtuelle Einträge `destination:object-or-package` werden ihren echten
Installationsverzeichnissen zugeordnet. Der Vorcheck ersetzt weder gclients
Integritätsprüfung noch die GN-/Compiler-Kompatibilitätsprüfung.
Versionswerkzeuge brauchen echte Upstream-Metadaten; keine erfundenen
`LASTCHANGE`-Daten erzeugen.

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
`out/Aimium/win-x64-dev/chrome.exe`. Seine Existenz allein reicht nicht.
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
