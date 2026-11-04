# Aimium – mehrphasiger Entwicklungsplan

Version 1, 4. November 2026. Produktgrundlage:
[bestätigte Vision](product-vision.md). Ausgangscode:
[geprüfter Stand](current-state.md). Einstieg für Codex:
[Übergabeauftrag](codex-handoff.md).

Dieser Plan ersetzt die bisherige Phasenreihenfolge in `roadmap.md`. Er ist eine
Arbeitsgrundlage mit Abnahmekriterien, keine Termin- oder Fertigstellungszusage.
Die ersten drei Pakete sind einzeln spezifiziert; spätere Pakete werden vor
Beginn anhand des dann vorhandenen Codes weiter zerlegt.

## Priorität und Ausführungsregeln

Der erste nutzbare Meilenstein **M1** ist ein gespeichertes Sitzungspaar mit einem
gespeicherten, manuell startbaren Workflow und echter Anzeige seines Fortschritts.
Build- und Sitzungsgrundlagen sind dafür notwendige Vorarbeiten. Wir ziehen
weder Abo noch komplexe Trigger oder Headless-Betrieb vor diesen Meilenstein.

Alle drei Desktopbetriebssysteme bleiben Ziele ab Projektbeginn. Die initiale
native Matrix ist Windows x64, Linux x64, macOS arm64 und macOS x64. Ein erster
Host-Build ist ein Teilnachweis, keine plattformübergreifende Abnahme. Andere
Architekturen benötigen eine gesonderte Entscheidung.

Jedes Paket führt Status, Abhängigkeiten, begrenzten Umfang, Tests und Evidenz.
Statusfolge: `PLANNED` → `READY` → `IN_PROGRESS` → `IMPLEMENTED` →
`VERIFIED` → `ACCEPTED`; `BLOCKED` ist mit Grund und Entsperrbedingung zulässig.
Quellcode vorhanden bedeutet `IMPLEMENTED`, nicht automatisch `VERIFIED`.
Die Produkteigentümerin oder der Produkteigentümer entscheidet über Abnahme und
Merge. Fehlende Runner werden sichtbar gemacht; unabhängiges Vertrags-/Testdesign
kann parallel erfolgen, aber keine native Integration wird dadurch abgenommen.

## Phasenübersicht

| Phase | Ergebnis | Abhängigkeit | Ausgangsstatus |
| --- | --- | --- | --- |
| P0 | Belastbare Entwicklungs- und native Buildbasis | Foundation-PR | Teilweise implementiert, native Evidenz offen |
| P1 | Dauerhafte Sitzungspaare und native Zweiteilung | P0-Integrationsbasis | Geplant |
| P2 | Manuelle Workflows je Sitzung mit Laufübersicht: M1 | P1 | Geplant |
| P3 | Connectoren, Agentensteuerung und Seitenwissen | P1/P2-Aktionsgrenze | Geplant |
| P4 | Vollständiger visueller Editor und KI-Workflowgestaltung | P2/P3 | Geplant |
| P5 | Zeit-/Webseitenereignisse mit echter Warteübersicht | P2, P4 für vollständige Bedienung | Geplant |
| P6 | Entschlackung, Härtung, Updates und Desktop-Release | P0–P5 für Kernrelease | Geplant, Updatepflege querschnittlich |
| P7 | Lokale Headless-Ausführung ohne Browserfenster | P5 und belastbare Wiederaufnahme | Später |
| P8 | Optionales Unterstützer-Abo, Modelle, E-Mail, Spezial-Nodes | Connector-/Node-Grenzen P3/P4 | Optional parallel, blockiert Kern nicht |
| P9 | Optionaler Cloud-Sync gespeicherter Definitionen | Versionierung, lokale Stores, Geräteidentität | Optional später |

## P0 – Entwicklungsbasis und native Nachweise

**Leitpaket AIM-001:** [Native Baseline](tasks/AIM-001-native-baseline.md).

P0.1 prüft PR, Branch, Source-Pin, vorhandene Tests und Toolchains. P0.2 erweitert
die Änderungsabdeckung der schnellen CI auf die tatsächlich betroffenen nativen
Integrationspfade, ohne einen nativen Build vorzutäuschen. P0.3 stellt einen
vollständigen gclient-Checkout her und behebt echte Buildfehler. P0.4 führt die
Aimium-Smoke-Tests plus normalen Browserstart/Navigation in separatem Profil aus
und dokumentiert die Plattformmatrix. P0.5 hält VS-Code-Arbeitsweg, Reproduktions-
befehle und einen sicheren manuellen Runnerpfad fest.

Abnahme: konkrete Source-SHA, Dependencies und GN-Argumente sind bekannt;
Chromium und WebUI bauen; Feature an/aus sowie normale Navigation sind geprüft.
Die Matrix zeigt pro Ziel `PASSED`, `FAILED` oder `NOT_RUN`. P0 gilt erst mit den
vereinbarten nativen Nachweisen als vollständig abgenommen. Stable-Migration und
ein echter Chromium-Updateprobelauf werden früh vorbereitet und sind Releasegate.
Keine teure Infrastruktur bestellen und keine Runnerfreigabe aus Dokumentation
ableiten. `release_eligible` bleibt false.

## P1 – Gespeicherte Sitzungspaare als Browsergrundmodell

**Leitpaket AIM-002:** [Sitzungspaare](tasks/AIM-002-session-pairs.md).

P1.1 baut Workspace-/Profilzuordnung und einen versionierten lokalen Store.
P1.2 ergänzt die native linke Agentenfläche und rechte Webseiten-/Workflowansicht.
P1.3 implementiert Anlegen, Benennen, Wechseln, Schließen, Wiederöffnen und
Wiederherstellen zuletzt offener Paare. P1.4 bietet passende gespeicherte
Sitzungen bei erneutem Webseitenbesuch an und trennt explizites Löschen vom
Schließen. P1.5 definiert Lebenszyklus, Nutzerübernahme und Tab-/Dokumentgenerationen.

Abnahme: zwei benannte Sitzungen behalten Daten nach Neustart; auch zwei Konten
auf derselben Website bleiben gemäß gewählter Profilstrategie getrennt. Wechsel
der rechten Ansicht zerstört die zugehörige Website nicht. Modellwahl und
Websiteidentität bleiben unabhängig. Es wird kein zweiter automatisierter Login
und kein iframe-Ersatz verwendet. Ohne Connector gibt es keine Scheinantworten.
In der ersten Version pausiert das Schließen eines Sitzungspaars dessen aktive
Arbeit und macht Beobachter unverfügbar; es löscht keine Definitionen. Die genaue
Nutzerbestätigung und der Umgang mit ausstehenden externen Effekten sind testbar.

## P2 – Erster Workflow-Meilenstein mit echtem Monitor

**Leitpaket AIM-003:** [Workflows und Monitor](tasks/AIM-003-workflows-and-monitor.md).

P2.1 speichert mehrere immutable Workflowversionen pro Workspace und löst
symbolische Bindungen auf. P2.2 trennt Definition, Aktivierung/Triggerregistrierung,
konkreten Run, Node-Aufruf und einzelne Browseraktion. P2.3 implementiert einen
kleinen dauerhaften Executor: manuell starten, Zustand lesen, Daten verarbeiten,
Bedingung, begrenztes Warten, typisierte Browseraktion und Ende. Bestehende
Schemas werden dafür geprüft und ausdrücklich versioniert erweitert, nicht
stillschweigend umgedeutet. P2.4 ergänzt Journal, tabbezogene Schreibrechte,
Pausieren, Abbruch, Nutzerübernahme und Wiederaufnahme mit Ergebnisabgleich.
P2.5 liefert eine einfache bearbeitbare Workflowdarstellung sowie globalen und
sitzungsbezogenen Monitor aus echtem Backendzustand.

Abnahme M1: im sichtbaren Tab einer kontrollierten Testseite einen gespeicherten
Workflow starten, echte Nodewechsel und Resultate sehen, abbrechen und nach
Neustart Definition/Verlauf wiederfinden. Ein zweiter Run darf nicht gleichzeitig
in denselben Tab schreiben. Ein Absturz nach externer Änderung führt zur
Ergebnisprüfung, nicht zu unbedingter Wiederholung. Keine Fortschrittssimulation.

Für die spätere Übersicht existiert bereits das Aktivierungsmodell. In P2 wird
nur ein echter manueller Start angeboten. Nicht implementierte Zeit- und
Webseitentrigger erscheinen nicht als aktiv überwacht. Eine manuelle Aktivierung
heißt beispielsweise „bereit für manuellen Start“. Echtes „wartet auf Trigger“
mit registriertem Beobachter wird in P5 abgenommen. Ein Cloud-Modell und E-Mail
sind keine Voraussetzungen, um die lokale Ausführung zuverlässig zu beweisen.

## P3 – Connectoren, Agent und Seitenwissen

P3.1 implementiert einen nativen Connector-/Credential-Service mit mehreren
Konfigurationen und plattformgerecht geschützter Speicherung; bei fehlendem
Schlüsselspeicher kein stiller unsicherer Fallback. P3.2 ergänzt einen Remote-
und einen lokalen Adapter, anschließend OpenAI, OpenRouter, Replicate und
geprüfte kompatible Endpunkte. Modellfähigkeiten, asynchrone Jobs, Streaming,
Abbruch, Fehler und Budgets werden pro Adapter getestet.

P3.3 projiziert freigegebenen Seitenkontext: semantische Elemente, begrenzte
DOM-/Accessibility-Daten und bei Bedarf Screenshots. P3.4 verbindet Modell-
vorschläge mit demselben geprüften Browseraktionsdienst aus P2. Read-only-
Anbieter-/Kontexttests gehen der Freigabe von Modell-veranlassten Schreibaktionen
voraus. P3.5 ergänzt versioniertes Seitenwissen aus Erkundung, Vormachen und
bestätigten Läufen. P3.6 untersucht optional herunterladbare lokale Modelle mit
Lizenz-/Integritätsprüfung, Ressourcenlimits und Entladen bei Nichtbenutzung.

Abnahme: Connectorwechsel erhält Websiteidentität; Nutzer sieht Verarbeitungsort
und Kontextfreigabe; lokale Verarbeitung wird ohne heimlichen Remote-Fallback
getestet. Nicht jeder Connector ist ein Browser-Steuermodell. Seiteninhalt und
Modellantwort können keine Rechte erweitern, Secrets lesen oder den Zielanbieter
ändern. Veraltete Antworten nach Navigation/Abbruch/Nutzerübernahme bewirken
keine Aktion. Loginprobleme gehen an den Nutzer. Seitenwissen ist prüfbar und
löschbar, keine stillschweigende Modellschulung.

## P4 – Vollständiger Graph und gemeinsame Workflowbearbeitung

P4.1 baut den Node-/Port-/Kanteneditor mit Schema- und Datenflussvalidierung.
P4.2 ergänzt explizite Schleifen, Unterprozesse, Fehlerpfade, Timeouts, Variablen,
mehrere KI-Nodes und vererbte Grenzen. P4.3 bietet Prompt → Graphentwurf →
Validierung → Vorschau → Testlauf → neue gespeicherte Version. Manuelle und
KI-Änderungen benutzen denselben Versions-/Prüfweg. P4.4 ergänzt Templates,
Import/Export und Graph-Debugging mit echter aktueller Position.

Abnahme: Speichern/Wiederöffnen bewahrt die Graphbedeutung; falsche Ports,
unaufgelöste Bindungen, unerreichbare Nodes und indirekte Rekursion werden
abgewiesen. Schleifen haben Grenzen und ihr eigener Node-Aufruf enthält
Iterations-/Unterprozessidentität. Ein laufender Run verwendet seine gepinnte
Version, auch wenn der Nutzer die nächste bearbeitet. Importierte Prozesse
übernehmen keine Credentials oder Ausführungsfreigaben. Freitext wird nicht allein
durch einen Feldnamenfilter als geheimnisfrei eingestuft.

## P5 – Zeit- und Webseitenereignisse

P5.1 definiert versionierte Triggerverträge mit Intervall/Kalenderzeit, Zeitzone,
Sommerzeitregeln, Nachholregel, Überlappung und maximaler Warteschlange. P5.2
implementiert lokale Uhr-/Sleep-Wake-Behandlung und eindeutige Auslöseidentitäten.
P5.3 beobachtet definierte Websitebedingungen: Element erscheint, Wert ändert
sich, Bedingung wechselt, Navigation oder anderer Prozess endet. P5.4 legt pro
Website Strategie und Intervall fest: dynamische Beobachtung, Polling oder
kontrollierter Refresh. Refresh teilt die Tabkoordination mit Mensch und Agent.
P5.5 verbindet Registrierung, Verfügbarkeit, Fehler und nächste erwartete Prüfung
mit dem Monitor. Debounce, Coalescing, Backoff und Limits verhindern Ereignisstürme.

Abnahme: ein aktivierter Workflow wartet sichtbar auf seinen realen Trigger;
ausgelöste Runs zeigen Ursache und Nodeposition. Deaktivieren verhindert neue
Runs, laufende Runs folgen einer ausdrücklich gewählten Regel. Neustart, doppelte
Ereignisse, Uhrsprung, Ruhezustand und belegte Tabs verursachen keine unkontrolliert
doppelten externen Änderungen. Für Webseitenereignisse während Offlinezeit wird
kein vollständiger Verlauf versprochen. Browser schließen macht die Laufzeit
sichtbar unverfügbar. Sekundenintervalle werden mit Ressourcenbudget getestet;
Pollingfrequenz und Modellaufruffrequenz bleiben getrennt.

## P6 – Schlanker, sicherer und aktualisierbarer Desktopbrowser

P6.1 misst Ausgangswerte für Startzeit, RAM/CPU, Hintergrundverkehr, Größe und
Upstream-Patchumfang. P6.2 ersetzt die Favoritenbedienung durch gespeicherte
Sitzungen und entfernt weitere nicht benötigte Bedienflächen/Dienste gezielt.
P6.3 prüft Buildausschlüsse separat; bloßes Ausblenden ist keine Größenersparnis.
P6.4 stellt Stable-Basis, kleine Integrationspatches und einen wiederholbaren
Upstream-Upgradeweg sicher. P6.5 ergänzt eigene Produkt-/Profilidentität,
Installationspakete, Signierung/Notarisierung und Updates. P6.6 umfasst
Bedrohungsmodell, Geheimnis-/Datenflussprüfungen, Migrationen und Rückfallkonzept.

Abnahme: plattformbezogene native und Workflowtests, belegte Einsparungen ohne
Sicherheitsverlust, installierbare signierte Pakete, getestetes Profil-/Daten-
upgrade und Updatekanal. Browser- und Komponentenupdates werden einzeln erfasst.
Ein Chromium-Sicherheitsupdate darf unabhängig von neuen KI-Funktionen erfolgen;
letztere bleiben deaktivierbar. Keine Pflicht zur Cloudanmeldung für lokale
Kernfunktionen. Die öffentliche Freigabe bleibt gesonderte Eigentümerentscheidung.
Updatepflege beginnt bereits in P0 und wartet nicht bis P6.

## P7 – Spätere lokale Headless-Laufzeit

P7.1 trennt Laufzeit und Fensterlebensdauer. P7.2 integriert einen ausdrücklich
aktivierbaren lokalen Hintergrundprozess und gegebenenfalls OS-Autostart.
P7.3 koordiniert exklusiven Profilzugriff, Laufzeitbesitz und Übergabe zwischen
Fenster und Hintergrundbetrieb. P7.4 behandelt Anmeldedialoge, MFA, Updates,
Schlafzustand und Abstürze mit sichtbaren Pausen statt verdeckten Fehlversuchen.

Abnahme: derselbe gespeicherte Prozess läuft ohne Browserfenster lokal weiter;
ein später geöffnetes Fenster zeigt den tatsächlichen Zustand und erlaubt
Übernahme. Keine zwei Instanzen schreiben gleichzeitig in dasselbe Profil.
Kein Lauf bei ausgeschaltetem Rechner; ausgefallene Trigger folgen der Nachholregel.
Headless stellt keine Umgehung von Webseiten- oder Konto-Schutzmechanismen dar.

## P8 – Optionale Dienste und Unterstützer-Abo

P8.1 entwirft die kleine freiwillige Subscription und transparente Limits, ohne
lokale Kernfunktionen zu sperren. P8.2 bietet vom Abo bereitgestellte Modelle
hinter der vorhandenen Connectorgrenze an. P8.3 ergänzt eine E-Mail-Node mit
expliziten Empfängern, Vorschau/Freigaberegeln, Rate-Limits und Ergebnisjournal.
P8.4 erlaubt später spezialisierte Nodes mit deklarierten Fähigkeiten und
Berechtigungen; kein beliebiges fremdes Skript mit Browserrechten.

Abnahme: Ausfall/Kündigung des Abos lässt lokale Funktionen nutzbar. Für Dienste
werden nur nötige Daten übertragen. E-Mail-Versand erhält eine stabile Aktions-
identität und behandelt unklaren Versandstatus ohne blindes erneutes Senden.
Der Cloud-Dienst führt die lokalen Browser-Workflows nicht ersatzweise aus.
Diese Phase kann nach P3/P4 parallel zu P5–P7 laufen. Anbieter, Zahlungsabwicklung
und Preise sind noch offen; keine Verträge ohne ausdrückliche Freigabe.

## P9 – Optionaler Sync gespeicherter Definitionen

P9.1 definiert die explizit synchronisierbaren Daten: Sitzungsmetadaten und
Workflowversionen, nicht automatisch Profile, Cookies, Schlüssel oder Laufdaten.
P9.2 implementiert Verschlüsselungs-/Schlüsselkonzept, Konflikte, Offlinebetrieb,
Löschung und Migration. P9.3 bindet auf einem anderen Gerät lokale Profile und
Connectoren bewusst neu zu. P9.4 regelt Ausführungsbesitz pro Gerät; beim Import
oder Sync ist automatische Aktivierung standardmäßig aus.

Abnahme: eine gespeicherte Sitzung mit Graphen lässt sich auf einem zweiten
Gerät wieder aufnehmen, ohne Secrets zu kopieren oder ungewollt doppelte
Zeitpläne zu starten. Gleichzeitige Bearbeitung verliert keine bestätigte Version.
Unabhängige Ausführung auf mehreren Geräten erfordert eine klare Nutzerfreigabe.

## Gemeinsame Test- und Sicherheitsstrategie

Kontrollierte Testwebsites liefern Login, dynamische Inhalte, Redirects, Frames,
Formulare, Downloads und absichtlich mehrdeutige Zustände. Tests injizieren
Abbruch, verspätete Antworten, verlorene Bestätigung und Prozessabsturz an
Aktionsgrenzen. Native Berechtigungs-, Store- und Zustandsautomaten werden separat
geprüft; Provideradapter haben deterministische Fixtures und ausdrücklich
freigegebene Integrationsprüfungen. Echte Accounts/Secrets gehören nicht in CI.

Das Monitorjournal enthält IDs, Zustandswechsel, Zeitstempel und begrenzte,
redigierte Ergebnisdaten. Keine dauerhafte Speicherung aller Screenshots oder
Seiteninhalte ohne bewusste Retentionsregeln. Kosten-, Laufzeit-, Node-, Schleifen-
und Kontextgrenzen gelten auch in verschachtelten Prozessen.

## Nächste drei Arbeitsaufträge

| Paket | Startbedingung | Konkretes Ergebnis |
| --- | --- | --- |
| [AIM-001](tasks/AIM-001-native-baseline.md) | Repositoryzugriff, geprüfter Foundation-Stand | Native Evidenzmatrix, korrigierte CI-Abdeckung, reproduzierbarer Buildweg |
| [AIM-002](tasks/AIM-002-session-pairs.md) | Erste belastbare native Integrationsbasis; übrige Ziele sichtbar offen | Persistente benannte Sitzungspaare mit linker Fläche |
| [AIM-003](tasks/AIM-003-workflows-and-monitor.md) | Workspace-/Profil-/Tab-Lebenszyklus aus AIM-002 | Manuell ausgeführter gespeicherter Prozess mit echter Laufübersicht |

Zunächst AIM-001 abarbeiten. Danach die kleinstmöglichen integrierten Teiländerungen
von AIM-002 und AIM-003 mit Tests liefern. Kein pauschaler Auftrag, alle zehn
Phasen ungeprüft in einem Commit umzusetzen.
