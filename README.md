# Aimium

Aimium entsteht als nativer Chromium-Browser für Windows, Linux und macOS.
Das Ziel ist gemeinsame Webseitenarbeit von Mensch und Agent: Jeder Produkttab
ist ein dauerhaft gespeichertes Paar mit Agent, Prompt und Kontext links und der
echten Website rechts. Die rechte Ansicht kann später auch Workflow-Explorer,
Editor und Ausführung zeigen; der Zustand der zugehörigen Website bleibt dabei
erhalten.

Mehrere Workspaces und mehrere Workflows je Workspace gehören zum Zielbild.
Der Nutzer kann die Website selbst bedienen und jederzeit übernehmen. Ein
Modellwechsel verändert weder das zugeordnete Browserprofil noch die Anmeldung
auf der Website. Ohne eingerichteten Connector soll manuelle Bedienung möglich
bleiben.

Browseraktionen, Überwachung und Workflows laufen lokal, zunächst bei geöffnetem
Aimium. Lokale und ausdrücklich gewählte externe Modelle sind optionale
Anbindungen. Eine lokale Headless-Laufzeit, zusätzliche Cloud-Dienste und der
optionale Sync von Definitionen folgen später; sie ersetzen keine lokale
Workflow-Ausführung.

Der erste nutzbare Meilenstein **M1** ist ein gespeichertes Sitzungspaar mit einem
gespeicherten, manuell gestarteten Workflow und einem Monitor, der tatsächliche
Schritte, Wartegründe und Ergebnisse zeigt.

## Was heute vorhanden ist

Der aktuelle Stand ist eine **Entwicklungsgrundlage (P0), kein fertiger
KI-Browser**. Vorhanden sind Quellcode für die featuregeschützte
`chrome://aimium`-Foundationseite, Datenverträge, Referenzprüfungen und
Buildwerkzeuge. Dauerhafte Sitzungspaare, linke Agentenfläche, Modellaufrufe,
Browseraktionen, Workflow-Engine und Monitor sind noch nicht als Produkt
implementiert.

Ein vollständiger nativer Browserbuild, die nativen Smoke-Tests und normale
Browsernavigation sind noch nicht bestätigt. Die native Abnahme bleibt offen,
`release_eligible: false`.

Projektprüfungen werden lokal ausgeführt; GitHub Actions sind deaktiviert.
Künftige native Builds startet ausschließlich der Nutzer in VS Code;
Agenten starten keine Builds.

## In VS Code weiterarbeiten

Für den nativen Build den vollständigen Git-Quellroot `src` in VS Code öffnen.
Eine Ebene darüber liegt der äußere gclient-Workspace mit `.gclient`; er ist
nicht der Git-Quellroot. Ein Sparse-Editingcheckout genügt für Dokumentation und
Python-Prüfungen, aber nicht für Chromium-Builds.

Neue Workspaces benötigen den Aimium-Fork mit einem geprüften
Implementierungsstand. Ein unveränderter Upstream-Checkout enthält die
Aimium-Erweiterungen nicht.

Mit den Aufgaben aus [`.vscode/tasks.json`](.vscode/tasks.json) startet
**Strg+Umschalt+B** (macOS: **Cmd+Umschalt+B**) die Standardaufgabe
**Aimium: Build + Smoke (lokal)**.
Weitere Aufgaben sind **Aimium: Voraussetzungen prüfen**,
**Aimium: Buildplan prüfen**, **Aimium: Python-Tests (lokal)** und
**Aimium: Vertragsbeispiele (lokal)**. Eine Microsoft-Python-Erweiterung ist
dafür nicht erforderlich.

Die [lokale Buildanleitung](aimium/README.md#lokaler-build-in-vs-code) erklärt
Voraussetzungen, Python 3.11+, die optionale lokale `env.cmd` und die
Wiederverwendung von `out/Aimium/win-x64-ninja`. Die Standardaufgabe
kompiliert tatsächlich und führt danach die fokussierten nativen Smoke-Tests
aus; sie prüft normale Website-Navigation nicht automatisch.

Zum Projekt: [Leitfaden](aimium/README.md),
[bestätigte Vision](aimium/docs/product-vision.md),
[Entwicklungsplan](aimium/docs/development-plan.md),
[Projektstand](aimium/docs/current-state.md),
[Architektur](aimium/docs/architecture.md) und
[Entwicklungsdetails](aimium/docs/development.md).

## Herkunft: Chromium

![Chromium-Logo](chrome/app/theme/chromium/product_logo_64.png)

Aimium ist ein Fork des offenen [Chromium-Projekts](https://www.chromium.org).
Die importierte Basis ist ein Entwicklungsstand, keine verifizierte Stable-Basis;
ihre Identität steht in [aimium/upstream.json](aimium/upstream.json).

Für einen vollständigen Quellcheckout folgt man der
[Chromium-Anleitung](docs/get_the_code.md); eine reine Git-Kopie liefert die
externen Buildabhängigkeiten nicht mit. Weitere Dokumentation beginnt unter
[docs/README.md](docs/README.md). Die
[Übersicht der Chromium-Verzeichnisstruktur](https://www.chromium.org/developers/how-tos/getting-around-the-chrome-source-code)
erläutert die Produktverzeichnisse. Neue oberste Verzeichnisse sind grundsätzlich
für Produkte vorgesehen; deren Programme gehören in das jeweilige
Produktverzeichnis. Upstream-Chromiumfehler können unter
[crbug.com/new](https://crbug.com/new) gemeldet werden.

Die [Chromium-Lizenz](LICENSE) und die Hinweise der Drittanbieter gelten weiter.
Aimium ersetzt oder ändert diese Lizenzen nicht; siehe auch die
[Chromium-Regeln für Drittanbieterabhängigkeiten](docs/adding_to_third_party.md).
