# AIM-002 – Dauerhafte Sitzungspaare und native Browserfläche

Status: **PLANNED**. Priorität: P1. Abhängigkeit: AIM-001 für native Integration.
Ziel: Jeder Produkttab wird ein dauerhaftes Paar aus linker Agentenfläche und
rechter Webseite beziehungsweise zugehöriger Workflowansicht.

## Eingaben und Architekturgrenzen

Lies [Vision](../product-vision.md), [Plan](../development-plan.md),
[Architektur](../architecture.md) sowie Workspace-Vertrag und native WebUI.
Verwende die im echten Checkout vorhandenen Chromium-Layout-/Profilmechanismen.
Neue Dateipfade sind vor Implementierung zu prüfen. Kein iframe-Browser und kein
zweites, unabhängig eingeloggtes Playwright-/Headless-Profil.

## Teilpakete und Umfang

**002-A – Modell/Store.** Versionierter lokaler Workspace-Store, vorzugsweise auf
Chromiums SQLite-Infrastruktur, mit stabiler Workspace-ID, Anzeigename,
Profilreferenz, zugehörigen Website-Origins und Wiederöffnungszustand. Opaque
Profil-ID statt frei importierbarem Dateipfad. Schemaänderung und Migration
explizit testen; bestehende v1-Verträge nicht unbemerkt umdeuten.

**002-B – Native Zweiteilung.** Linke Agenten-/Kontextfläche an den richtigen
Workspace binden. Rechte Fläche zwischen realem WebContents und Workflowansicht
umschalten, ohne Websiteidentität zu verlieren. Fehlt ein Connector, klaren
Einrichtungsstatus anzeigen, keine simulierte KI. Manuelle Bedienung bleibt nutzbar.

**002-C – Sitzungslifecycle.** Anlegen, benennen, mehrere Paare wechseln, schließen,
wieder öffnen und zuletzt geöffnete Paare nach Neustart wiederherstellen.
Passende gespeicherte Sitzungen bei erneutem Seitenbesuch anbieten; mehrere
Sitzungen derselben Website berücksichtigen. Explizites Löschen ist separat.
Profilwiederverwendung oder -trennung ist bewusst und sichtbar, nicht aus URL
oder Modellname abgeleitet. SSO-Navigation und Popup-Verhalten festlegen.

**002-D – Grenzen für Folgearbeit.** Ereignisse für Navigation, Tab-/Profilende,
Nutzerübernahme und Dokumentgeneration bereitstellen. Rechtsansichtswechsel
behält den Tab, Schließen macht ihn unverfügbar. Für spätere Ausführungen die
Pause-/Abbruchregel definieren. Produkt-/Entwicklungsprofil niemals mit bestehendem
Chrome-Profil vermischen. Beobachtung manuell geänderter Inhalte berücksichtigen.

## Abnahmeszenarien

- [ ] Zwei benannte Sitzungspaare bleiben nach Neustart erhalten.
- [ ] Schließen und Wiederöffnen verliert weder ID noch zugeordnete Daten.
- [ ] Zwei Konten derselben Testwebsite bleiben bei getrennter Profilwahl getrennt.
- [ ] Modellbindung wechseln verändert die Websiteidentität nicht; Adapteraufrufe
      selbst sind in diesem Paket noch nicht gefordert.
- [ ] Wechsel Webseite/Workflowansicht erhält den zugehörigen Websitezustand.
- [ ] Kein Panel hängt nach Tabwechsel oder Navigation am falschen Konto/Tab.
- [ ] Migrations-, Shutdown- und Wiederherstellungstests sowie native UI-Tests
      sind mit Ergebnissen je Ziel dokumentiert.

## Nicht enthalten / Übergabe

Keine echten Modellaufrufe, keine Workflow-Engine, keine Scheduler, kein Cloud-Sync.
Keine klassische Favoritenfunktion neu implementieren; die spätere Entfernung
vorhandener Chromium-Funktionen gehört in P6.

Als Ergebnis Store-/Servicegrenzen, konkrete native Registrierungsänderungen und
Testnachweise liefern. AIM-003 erhält verlässliche Workspace-/Profil-/Tab-Bindungen
und Lebenszyklusereignisse. Nicht getestete Plattformen bleiben sichtbar offen.
