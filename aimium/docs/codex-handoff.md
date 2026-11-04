# Aimium – vollständige Projektübergabe an Codex / Work

Stand: 4. November 2026. Dieses Dokument enthält den Projektkontext unabhängig
vom bisherigen Chat. Es ist ein gespeicherter Arbeitsauftrag, keine Bestätigung,
dass bereits ein neuer Codex-Task läuft.

## Repository und Einstieg

Repository: `mauricehuschke/chromium-aimium`.
Übergabebasis: **`codex/aimium-foundation`**, einschließlich dieses Dokuments.
Foundation-PR: [#1](https://github.com/mauricehuschke/chromium-aimium/pull/1).
Geprüfter Code-Ausgangspunkt vor dem Übergabecommit:
`71fed74bcab7df9c6d5864c4d81e7e5d2a1c57de`.

Nicht einfach auf `main` beginnen: Beim Abgleich enthielt `main` noch nicht die
Foundation. Ermittle vor der Arbeit den aktuellen Remote-Head, prüfe lokale
Änderungen und lege darauf einen neuen Implementierungsbranch an. Wurde PR #1
inzwischen integriert, nutze den nachgewiesenen integrierten Stand. Keine
Historie zurücksetzen und keine neueren Änderungen überschreiben.

Das Repository enthält bereits den Chromium-Code. Eine zweite Vollkopie als
Chat-Anhang ist nicht erforderlich. Die externen Buildabhängigkeiten müssen
für native Builds weiterhin passend über gclient bereitgestellt werden.

## Lesereihenfolge und Entscheidungsstand

1. Root-[AGENTS.md](../../AGENTS.md): Arbeits- und Validierungsregeln.
2. [Produktvision](product-vision.md): die präzisierten Anforderungen.
3. [Ist-Stand](current-state.md): Code, Evidenz und konkrete Lücken.
4. [Entwicklungsplan](development-plan.md): neue verbindliche Reihenfolge.
5. Das aktuelle [Arbeitspaket](tasks/AIM-001-native-baseline.md), danach nur
   relevante Teile von [Architektur](architecture.md), [Entwicklungsleitfaden](development.md)
   und den [Verträgen](../contracts/README.md).

Die Vision und der neue Plan konkretisieren die älteren offenen Produktfragen:
Jeder Produkttab ist immer ein Sitzungspaar; anfangs offenes Aimium, später lokale
Headless-Laufzeit; optionale Cloudmodelle, E-Mail und Sync, aber keine Cloud-
Ausführung der Nutzer-Workflows. Technische Sicherheitsgrenzen der Architektur
bleiben bestehen. Der erste Produktmeilenstein ist ein manuell startbarer
Workflow mit echtem Monitor, nicht zuerst Subscription oder Headless.

## Arbeitsauftrag

Übernimm die Weiterentwicklung von Aimium auf Basis der gespeicherten Vision.
Beginne **AIM-001**, nicht alle Phasen gleichzeitig. Prüfe zuerst aktuellen
Commit, PR/CI und verfügbare Buildumgebung. Liefere konkrete Änderungen und
Prüfergebnisse, keine erneute reine Architekturabhandlung.

Nach überprüfbarer Integrationsbasis folgt **AIM-002** (dauerhafte Sitzungspaare).
Darauf folgt **AIM-003** (manuelle Workflows und Monitor). Pro Paket kleine,
nachvollziehbare Änderungen und gesonderte Abnahme. Unabhängige Tests und
Modellarbeiten dürfen vorbereitet werden; fehlende native Prüfevidenz darf
nicht verschwiegen werden. Der Gesamtrahmen P0–P9 bleibt für Folgeaufträge erhalten.

Sind Buildkapazität, Toolchain, Netz oder Runner nicht vorhanden, bearbeite die
unabhängig ausführbaren Teile und melde präzise den verbleibenden Blocker.
Keine behaupteten Plattformtests, keine gefälschten UI-Funktionen, kein Merge
oder Release, um einen offenen Buildnachweis zu umgehen.

## Entwicklungsumgebung

Eine Codex-/Work-Umgebung benötigt Zugriff auf dieses Repository und den
Übergabebranch. Python 3.11+ genügt für die bestehenden leichten Prüfungen.
Native Chromium-Builds brauchen einen vollständigen Checkout, gclient,
plattformpassende Toolchain, ausreichend RAM/Speicher und die passende native
Zielumgebung. Die aktuelle CI-Matrix ersetzt das nicht.

Für CI-/Dokumentationsarbeit darf ein gezielter Sparse-Checkout verwendet werden.
Zum Bauen ist ein eigener vollständiger Workspace vorzuziehen. Nicht ohne
Ressourcenprüfung die komplette Chromium-Historie oder alle Plattformabhängigkeiten
in eine kleine Cloudumgebung laden. Keine persönlichen Browserprofile oder
Providersecrets hochladen. Netzwerkzugriff für Abhängigkeiten bewusst einrichten.

Die Entwicklung in Codex Cloud ist vom Aimium-Produktlaufzeitmodell zu
unterscheiden: Ein Cloud-Build macht Nutzer-Workflows nicht zu Cloud-Workflows.
Die lokale Produktausführung bleibt eine verbindliche Anforderung.

Bestehende Einstiegskommandos, aus dem Source-Root:

```sh
python -m unittest discover -s aimium/tests -p 'test_*.py' -v
python aimium/contracts/validate.py --examples
python aimium/tools/build.py plan --target linux-x64
```

Für echte Builds nach Hostwahl `check`, `build --dry-run` und `build` gemäß
[Entwicklungsleitfaden](development.md). Erstes Ergebnis muss die tatsächliche
Umgebungsfähigkeit benennen. Keine Geheimnisse in Befehlsausgaben protokollieren.

## Übergabe in der Oberfläche

Ein neuer Codex-Task muss vom Nutzer in einer passenden lokalen oder Cloud-
Umgebung gestartet werden; dieser Dokumentationscommit startet ihn nicht.
Für Codex Cloud die Umgebung mit dem Repository auswählen beziehungsweise
vorbereiten/veröffentlichen, anschließend einen neuen Auftrag starten. Danach
den Übergabebranch prüfen und den folgenden Startauftrag verwenden.

Offizielle Orientierung, abgerufen am 4. November 2026:
[Codex Cloud](https://learn.chatgpt.com/docs/cloud),
[Work und Codex](https://help.openai.com/de-de/articles/20001275-chatgpt-work-and-codex).
Bezeichnungen und Verfügbarkeit können sich je Konto/Oberfläche unterscheiden.
Ein GitHub-Zugriff in einem Chat ersetzt nicht automatisch die Einrichtung der
Codex-Arbeitsumgebung.

## Direkt verwendbarer Startauftrag

```text
Arbeite am Repository mauricehuschke/chromium-aimium.
Lade den aktuellen Stand von codex/aimium-foundation einschließlich der
Übergabedokumentation; main enthält möglicherweise noch nicht die Foundation.
Prüfe den tatsächlichen Branch und erhalte vorhandene lokale Änderungen.

Lies AGENTS.md und aimium/docs/codex-handoff.md. Übernimm die bestätigte Vision,
den mehrphasigen Entwicklungsplan und den dokumentierten Ist-Stand.
Beginne mit aimium/docs/tasks/AIM-001-native-baseline.md auf einem eigenen
Arbeitsbranch. Führe die erreichbaren Prüfungen aus, korrigiere konkrete
CI-/Buildprobleme und liefere Code plus belastbare Evidenz. Native Builds und
Browsertests nur als erfolgreich ausweisen, wenn tatsächlich ausgeführt.

Nach AIM-001 folgen AIM-002 und AIM-003 gemäß ihren Abhängigkeiten und
Abnahmekriterien. Kein pauschaler Umbau aller Phasen. Fehlt Infrastruktur,
erledige unabhängige Teile und benenne den exakten Blocker. Kein ungeprüfter
Merge, keine Infrastrukturkäufe, keine Secrets im Repo, keine Releases.
Berichte Task-ID, Base-/Head-SHA, Änderungen, Testergebnisse je Plattform,
Nicht-ausgeführt-Punkte und nächsten Arbeitsschritt. Antworte auf Deutsch.
```

## Ergebnisformat für jeden Arbeitsabschnitt

Dokumentiere Aufgabe und Scope, tatsächliche Base-/Head-SHA, geänderte Dateien,
reale Funktion, Tests/Befehle, Hostmatrix, bekannte Risiken, offene Abnahmepunkte
und nächste erlaubte Arbeit. Aktualisiere Ticketstatus und Ist-Stand mit
konkreter Evidenz. Keine erfundene Prozentzahl für das Gesamtprojekt und keine
Zusage unbeaufsichtigter Weiterarbeit ohne tatsächlich gestarteten Task.
