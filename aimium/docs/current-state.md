# Aimium – geprüfter Ausgangsstand und Übergabestatus

Prüfdatum: 4. November 2026. Diese Bestandsaufnahme bezieht sich auf den Code
**vor dem Dokumentations-Übergabecommit**. Spätere Bearbeiter müssen Branch und
CI erneut abfragen. Ein gespeicherter Auftrag ist kein gestarteter Codex-Task.

## Repository und Nachweise

| Gegenstand | Beim Abgleich festgestellt |
| --- | --- |
| Repository | `mauricehuschke/chromium-aimium` |
| Defaultbranch | `main` bei `514870670a5dc0192b33b0e88ba7ff16a7d0d477` |
| Implementierungsbranch | `codex/aimium-foundation` |
| Geprüfter Implementierungscommit | `71fed74bcab7df9c6d5864c4d81e7e5d2a1c57de` |
| Foundation-PR | [PR #1](https://github.com/mauricehuschke/chromium-aimium/pull/1), offen, Draft, nicht gemergt |
| Chromium-Basis | `159.0.8142.0`, Commit `c80042ad683c5620adc9760ec7b5950c80f9d9ce`, Entwicklungsstand, nicht verifizierte Stable-Basis |
| Leichte CI | [Run 41727557560](https://github.com/mauricehuschke/chromium-aimium/actions/runs/41727557560), erfolgreich |
| Umfang dieser historischen CI | 56 Python-Tests und acht Beispielvalidierungen je Windows/Linux/macOS laut Run und PR; keine nativen Browser-Builds |

Die Quellbasis und die bisherigen Prüfaussagen sind im [PR](https://github.com/mauricehuschke/chromium-aimium/pull/1)
und in [upstream.json](../upstream.json) nachvollziehbar. Die Übergabedokumentation
wird auf dem Foundation-Branch ergänzt. `main` wird dafür nicht umgestellt und
PR #1 nicht automatisch abgenommen.

## Vorhanden, aber nicht gleichbedeutend mit fertigem Produkt

| Bereich | Nachgewiesener Umfang | Fehlender Nachweis/Funktion |
| --- | --- | --- |
| Aimium-WebUI | Quellcode für `chrome://aimium`, deaktiviertes Feature-Flag, zwei native Smoke-Tests | Native Kompilierung, Ressourcenerzeugung und Ausführung der Browsertests |
| Datenverträge | Sechs Schema-Dateien, Referenzvalidator, Beispiele, Python-Tests | Produktiver Store, Laufzeit und native Durchsetzung |
| Buildwerkzeuge | Plan/Preflight für `win-x64`, `linux-x64`, `mac-arm64`, `mac-x64` | Vollständige Plattform-Builds und geprüfte Installationen |
| CI | Schnelle Checks und manuell vorgesehener nativer Workflow | Eingerichtete/verfügbare native Runner nicht durch diese Abfrage belegt |
| Sitzungspaare | Architektur und Vertragsgrundlage | Native linke Ansicht, persistente Sitzung, Wiederherstellung |
| KI/Automation | Verträge und Entwurf | Connectoraufrufe, Schlüsselspeicher, Browseraktionsdienst, Seitenwissen |
| Workflows | Graph- und Run-Verträge | Store, Executor, Aktivierungsverwaltung, Monitor, Grapheditor, Trigger |
| Produktbetrieb | Entwicklungsgrundlage | Entschlackung, Headless-Betrieb, Abo, E-Mail, Sync, Installer/Updater |

## Konkrete Befunde für die nächsten Pakete

1. Die Path-Filter in [aimium-checks.yml](../../.github/workflows/aimium-checks.yml)
   erfassen nur `aimium/**` und Aimium-Workflowdateien. Reine Änderungen an nativen
   Aimium-Dateien oder deren Chromium-Registrierungsstellen können diese Checks
   nicht auslösen. AIM-001 soll das prüfen und gezielt korrigieren. Ein breiterer
   Filter kompiliert allein noch keinen nativen Code.
2. [aimium-native-build.yml](../../.github/workflows/aimium-native-build.yml) setzt
   vorbereitete Self-hosted-Runner, `AIMIUM_NATIVE_BUILDS_ENABLED` und
   `AIMIUM_CHROMIUM_SOURCE` voraus. Er setzt keinen Checkout zurück. Tatsächliche
   Runnerverfügbarkeit und Auslösbarkeit müssen geprüft werden. Die Workflowdatei
   liegt noch im nicht gemergten PR; ein zulässiger manueller Startweg ist Teil
   von AIM-001, kein Grund für einen ungeprüften Merge.
3. Der Run-Vertrag beschreibt eine konkrete Ausführung. Ein separates Modell
   für Aktivierung, Triggerregistrierung und deren Wartezustand fehlt. AIM-003
   muss diese Unterscheidung anlegen; echte Zeit-/Seitenbeobachter folgen in P5.
4. Die ältere Architektur enthält noch offene Produktentscheidungen zum
   Laufzeitmodell. Diese sind durch [product-vision.md](product-vision.md)
   entschieden: zunächst offenes Aimium, später lokale Headless-Laufzeit;
   Cloud-Modelle/Dienste optional, Nutzer-Workflows nicht serverseitig ausführen.
5. Die bisherigen knappen Chat-Planungen deckten Connectoren, vollständigen
   Editor, Sicherheit, Updates und Sync nicht vollständig ab. Der
   [neue Entwicklungsplan](development-plan.md) ersetzt diese verkürzte Reihenfolge.

## Arbeitsstand zum Übergabezeitpunkt

- AIM-001: **READY** für Bestandsaufnahme/CI-Korrektur; native Abnahme offen.
- AIM-002: **PLANNED**, hängt für native Integration von AIM-001 ab.
- AIM-003: **PLANNED**, hängt von der Sitzungsgrundlage aus AIM-002 ab.
- Kein Implementierungspaket wird durch diesen Dokumentationscommit abgeschlossen.
- Kein neuer Codex-/Work-Task wurde durch die Speicherung gestartet.

## Fortschreibung durch den nächsten Bearbeiter

Für neue Evidenz Datum, Task-ID, geprüfte SHA, Host/CPU, Befehl, Ergebnis und
Artefakt-/Logreferenz ergänzen. Historische CI-Ergebnisse nicht als Tests des
neuen Commits ausgeben. Native Tests ohne passende Umgebung als `NOT_RUN` oder
`BLOCKED` führen; das Projekt bleibt `release_eligible: false`.
