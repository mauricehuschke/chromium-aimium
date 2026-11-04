# AIM-003 – Gespeicherte manuelle Workflows und echte Laufübersicht

Status: **PLANNED**. Priorität: P2 / erster nutzbarer Meilenstein M1.
Abhängigkeit: Workspace-/Profil-/Tab-Lifecycle aus AIM-002, native Prüfbasis.
Ziel: Ein gespeicherter Prozess arbeitet tatsächlich in seiner Sitzung; Nutzer
sieht den aktuellen Schritt und kann eingreifen.

## Zentrale Modellentscheidung

Trenne Workflowdefinition, immutable Version, Aktivierung/Triggerregistrierung,
konkreten Run, Node-Aufruf und Browseraktion. Ein wartender Trigger ist kein Run.
Eine Definition kann mehrfach ausgeführt werden; jede Ausführung pinnt Version,
Bindings und Freigaben. Die vorhandenen JSON-Schemas sind Referenzverträge,
keine bereits vorhandene Engine. Die Produktion läuft nicht im Pythonvalidator.

## Teilpakete und Umfang

**003-A – Speicherung.** Mehrere Workflows je Workspace, Versionsspeicherung,
validierte Bindungen, dauerhaftes Run-/Node-/Aktionsjournal. Ergänze das fehlende
Aktivierungsmodell mit eigenem Status. Manuelle Aktivierungen sind bereit für
manuellen Start; nicht implementierte Timer/Webbeobachter bleiben deaktiviert.
Lege Migrationen und ID-/Sequenzregeln fest.

**003-B – Kleinster echter Executor.** Implementiere eine bewusst kleine Auswahl
aus dem vorhandenen/ausdrücklich erweiterten Nodevertrag: manuell starten,
beobachten/extrahieren, Datenverarbeitung, Bedingung, begrenztes Warten,
typisierte Browseraktion und Abschluss. Validierung von Datenabhängigkeiten,
Timeouts und Grenzen vor Start. Unsupported Nodes verständlich abweisen.
Keine künstlichen Fortschrittstimer. Vollständige Schleifen/Subprozesse und
KI-Nodes folgen später, werden aber im Datenmodell nicht durch ein einziges
`current_node_id` für alle Wiederholungen ununterscheidbar gemacht.

**003-C – Browsergrenze und Wiederaufnahme.** Ein nativer Aktionsdienst bedient
denselben sichtbaren Tab; kein beliebiges JS/Shell-Tool. Schreibrecht pro Tab,
Generationen für Dokument/Beobachtung/Berechtigung, Nutzerübernahme und Abbruch.
Vor externen Änderungen Absicht speichern, danach Wirkung bestätigen. Unklarer
Ausgang führt zu `needs_reconciliation` und behält die Aktions-ID. Pausieren,
Abbrechen und Neustart dürfen einen bereits abgesendeten Effekt nicht verdecken.

**003-D – UI.** Explorer mit gespeicherten Workflows, minimaler editierbarer
Node-/Eigenschaftsdarstellung und manueller Starttaste. Globaler sowie
sitzungsbezogener Monitor mit Run, aktuellem Node-Aufruf, Verlauf, Wartegrund,
Fehler und Ergebnis. Pausieren/Fortsetzen/Abbrechen sowie Nutzerübernahme anbinden.
Der vollständige ComfyUI-artige Editor ist P4; hier keine zweite konkurrierende
Workflowrepräsentation aufbauen.

## Verbindliche Tests für M1

- [ ] Zwei gespeicherte Workflows gehören zur richtigen Sitzung und lassen sich
      nach Neustart öffnen und manuell starten.
- [ ] Kontrollierte Testwebsite: beobachten → Daten prüfen → Testfeld ändern →
      Ergebnis bestätigen → Ende; echte Zustands-/Nodewechsel im Monitor.
- [ ] Zweiter schreibender Run wartet bei belegtem Tab. Manuelle Navigation oder
      Übernahme macht alte Elementreferenzen/Antworten unwirksam.
- [ ] Nach Abbruch führen verspätete Antworten keine weitere Aktion aus.
- [ ] Prozessabbruch unmittelbar nach externem Speichern führt beim Neustart
      zur Ergebnisprüfung, nicht zum erneuten Absenden.
- [ ] Ein bearbeiteter Graph erzeugt eine neue Version; ein laufender Run bleibt
      auf der vorherigen Fassung. Journal und Übergänge sind dauerhaft.
- [ ] Der Monitor unterscheidet bereit/aktiviert von konkreten Runs; echte
      Timer-/Webseitenüberwachung wird noch nicht behauptet.
- [ ] Persistenz-, Nebenläufigkeits-, Fehlerpfad- und native UI-Tests sind belegt.

## Nicht enthalten / Ausblick

Keine bezahlten Provideraufrufe, automatischen Zeit-/Seitenereignisse, E-Mail,
Cloud-Ausführung, Headless-Dienste oder umfassender Graph-Designer. Verwende
Testkonten und lokale Fixture-Websites. Dieses Paket darf in 003-A bis 003-D
geteilt werden, wird aber erst als M1 abgenommen, wenn der vollständige Ablauf
integriert ist. Danach folgen Agenten/Connectoren, Editor und Trigger laut Plan.
