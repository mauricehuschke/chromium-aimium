# AIM-001 – Native Buildbasis und belastbare Prüfevidenz

Status: **READY**. Priorität: P0. Abhängigkeit: bestehende Foundation.
Ziel: den tatsächlichen nativen Zustand klären und den ersten reproduzierbaren
Build nachweisen, ohne Python-CI mit Browserfunktion zu verwechseln.

## Vor Beginn

Lies die Root-`AGENTS.md`, [Übergabe](../codex-handoff.md),
[Ist-Stand](../current-state.md) und [Buildleitfaden](../development.md).
Prüfe PR #1 und den aktuellen Head von `codex/aimium-foundation`. Starte einen
eigenen Arbeitsbranch auf diesem Stand. Kein Reset vorhandener Nutzerarbeit.

## Teilpakete und Umfang

**001-A – Audit und schnelle Checks.** Prüfe Source-Pin, vorhandene Tests und
Buildskript. Führe die Python-Suite und Beispielvalidierung aus. Erweitere die
CI-Auslösepfade für native Aimium-Dateien und tatsächlich geänderte Chromium-
Registrierungsstellen. Ermittle diese aus dem Diff statt pauschal alle
Chromium-Dateien zu triggern. Halte die schnelle CI schlank und secret-frei.

**001-B – Native Umgebung.** Prüfe pro Ziel Host/CPU, freien Speicher, vollständigen
gclient-Checkout, DEPS/Toolchain und die zum Commit gehörenden Plattformanleitungen.
Keine SDK-Version aus alten Chatnachrichten ungeprüft übernehmen. Bestehende
Checkouts nicht durch `reset --hard`, Auto-Sync oder Overwrite reparieren.
Dokumentiere konkrete fehlende Voraussetzungen. Kein ungefragtes Buchen von Runnern.

**001-C – Build und Smoke.** Baue `chrome` sowie die vorgesehenen Browsertests.
Führe die Feature-an/aus-Tests aus und prüfe normalen Browserstart/Navigation mit
einem separaten Entwicklungsprofil. Behebe echte GN/C++/WebUI/TypeScript-Probleme
in kleinen Änderungen. Entdeckte Tests und ausgeführte Tests nachweisen.

**001-D – Wiederholbarkeit.** Dokumentiere Commit, Upstream, DEPS, Host/CPU,
Werkzeugstände, GN-Argumente, Befehle und Ergebnisse. Ergänze eine Evidenzmatrix
für Windows x64, Linux x64, macOS arm64 und macOS x64. Der native Workflow setzt
vorbereitete Runner voraus; prüfe einen zulässigen manuellen Startweg, solange
die Workflowdatei nicht auf `main` liegt. Ein ungeprüfter Merge ist keine Lösung.

## Abnahme

- [ ] Schnelle Tests und Beispiele sind mit konkreter SHA protokolliert.
- [ ] Native Änderungswege lösen die vorgesehenen Prüfungen aus.
- [ ] Mindestens ein vollständiger nativer Build plus beide Aimium-Smoke-Fälle
      und normale Navigation ist als erster Teilnachweis vorhanden.
- [ ] Für jedes weitere Ziel steht ein echter Ergebnisstatus; P0 wird nicht als
      vollständig abgenommen markiert, solange vereinbarte native Nachweise fehlen.
- [ ] VS-Code-/Terminalweg und reproduzierbare Befehle stimmen mit dem Code überein.
- [ ] Keine Sandboxabschaltung, echte Nutzerprofile oder unkontrollierte Secrets.

## Befehlsgrundlage

```sh
python -m unittest discover -s aimium/tests -p 'test_*.py' -v
python aimium/contracts/validate.py --examples
python aimium/tools/build.py check --target <native-target>
python aimium/tools/build.py build --target <native-target> --dry-run
python aimium/tools/build.py build --target <native-target> --browser-tests --jobs <host-limit>
```

Die Platzhalter bewusst setzen. Der geprüfte Build verlangt einen sauberen
committeten Quellstand. Ein Sparse-Checkout ist kein nativer Build-Checkout.

## Nicht enthalten / Blockerregel

Keine Sidebar, Connectorimplementierung, Entschlackung, Signierung oder Release.
Bei fehlender Buildkapazität 001-A und die erreichbaren Prüfungen abschließen,
001-B/C mit konkretem Grund `BLOCKED` melden. Keine weitergehende native
Funktionsabnahme behaupten. Bericht nach Root-`AGENTS.md`; danach AIM-002 nur
soweit die Integrationsbasis wirklich verfügbar ist.
