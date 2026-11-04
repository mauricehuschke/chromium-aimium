# Aimium – bestätigte Produktvision

Stand: 4. November 2026. Grundlage: die vom Produkteigentümer präzisierte Vision.
Dieses Dokument beschreibt das Ziel, nicht bereits ausgelieferte Funktionen.
Technischer Ist-Stand: [current-state.md](current-state.md).

## Ein Browser für KI-gestützte Webseitenarbeit

Aimium ist ein entschlacktes Chromium-Derivat für Windows, Linux und macOS.
Der Hauptanwendungsfall ist das gemeinsame Bedienen und Automatisieren von
Webseiten durch Nutzer und KI. Es gibt keinen separaten normalen Browsermodus
ohne zugehörigen Agentenbereich. Ohne eingerichteten Connector bleibt manuelle
Webseitenbedienung möglich; links wird der fehlende Connector ehrlich angezeigt.

Jeder Produkttab ist ein benanntes, dauerhaft gespeichertes **Sitzungspaar**:
links Agent, Prompt und Kontext; rechts die echte Webseite. Rechts kann zwischen
Webseite, Workflow-Explorer, grafischem Workflow-Editor und Ausführungsansicht
gewechselt werden. Der zugehörige Webseitenzustand darf dabei nicht beiläufig
verloren gehen. Einstellungen und Browser-Systemdialoge sind keine zusätzliche
Produktvariante.

Beim Start werden die zuletzt geöffneten Sitzungspaare wiederhergestellt.
Ein Tab kann geschlossen werden, ohne Sitzung, Agentenkontext oder Workflows zu
löschen. Beim erneuten Besuch einer zugehörigen Webseite bietet Aimium passende
gespeicherte Sitzungen zur Wiederaufnahme an. Mehrere Sitzungen derselben Website
sind möglich. Die Zuordnung zu einer Domain ersetzt keine Benutzerentscheidung
über Profil, Konto oder Sicherheitsfreigaben.

## Mensch und Agent arbeiten in derselben Sitzung

Der Nutzer kann die Webseite vollständig manuell verwenden, sich anmelden und
jederzeit übernehmen. Der Agent arbeitet mit derselben realen Chromium-Seite und
dem zugeordneten Profil. Ein Modellwechsel verändert weder Cookies noch die
Website-Anmeldung. Geteilte Profile müssen bewusst gewählt werden; getrennte
Konten bleiben getrennt. Abgelaufene Logins und MFA werden an den Nutzer übergeben.

Der Agent soll aus einem Prompt Informationen auslesen, Navigation und Formulare
bedienen, Ergebnisse prüfen und mehrstufige Aufgaben ausführen können. Er baut
prüfbares, versioniertes Wissen über die jeweilige Website auf. Das bedeutet
zunächst Seiten- und Aufgabenwissen, keine automatische Modellschulung mit dem
Browserverlauf. Seitenänderungen erfordern erneute Prüfung statt blindes Klicken.

## Wiederverwendbare Workflows je Sitzung

Pro Sitzung gibt es beliebig viele gespeicherte Workflows im Produktmodell;
technische Ressourcenlimits bleiben sichtbar. Der Nutzer erstellt und verändert
sie manuell, gemeinsam mit dem Agenten oder vollständig aus einem Prompt.

Ein grafischer Editor nach dem Bedienprinzip von ComfyUI stellt Nodes mit
Anschlüssen, Kanten, Datenfluss, Bedingungen, Schleifen und Unterprozessen dar.
KI-Nodes können an mehreren Stellen Seiteninhalte mit einem eigenen Prompt
auswerten. Ihre Ergebnisse steuern weitere Schritte. Agentenänderungen werden
als prüfbarer Graphentwurf übernommen, nicht als ungeprüfter Programmcode.

Workflows können manuell, zeitgesteuert und durch definierte Ereignisse auf der
Webseite starten. Dynamische Seiten werden beobachtet; bei Bedarf wird geprüft
oder aktualisiert. Ein Refresh darf manuelle Eingaben oder eine laufende Aktion
nicht unbemerkt zerstören. Intervalle im Sekundenbereich sind grundsätzlich ein
Produktwunsch, abhängig von Ressourcen, Website und Ausführungsgrenzen.

Beispiel: Eine Nachrichtenseite alle fünf Minuten prüfen, neue Meldungen anhand
persönlicher Kriterien bewerten, relevante Nachrichten zusammenfassen und über
einen ausdrücklich angebundenen E-Mail-Dienst versenden. Eine häufigere
Beobachtung muss nicht bei jeder Prüfung einen kostenpflichtigen Modellaufruf
auslösen. Änderungserkennung und KI-Auswertung können getrennt werden.

## Übersicht und Nachvollziehbarkeit

Eine globale Übersicht und eine sitzungsbezogene Ansicht zeigen getrennt:
aktivierte Workflows, die auf einen Auslöser warten; konkrete wartende oder
laufende Ausführungen; pausierte, fehlerhafte und abgeschlossene Läufe.

Bei einer Ausführung sieht der Nutzer aktuellen Node, gegebenenfalls Schleifen-
iteration und Unterprozess, vorherige Schritte, Wartegrund, Auslöser und Ergebnis.
Er kann pausieren, fortsetzen, abbrechen oder übernehmen. Die Anzeige entsteht
aus realem Ausführungszustand. Ein auf einen Trigger wartender Workflow ist kein
bereits gestarteter Run. Für nicht implementierte Trigger gibt es keine fingierte
Überwachung oder scheinbar aktive Statusanzeige.

## Lokal zuerst, Cloud bewusst optional

Browsersteuerung, Triggerüberwachung, Zeitplanung und Workflow-Ausführung liegen
lokal im Nutzerkontext. Zunächst muss Aimium geöffnet sein. Vollständiges Beenden
und Rechner-Ruhezustand beenden die Verfügbarkeit der lokalen Laufzeit; eine
sichtbare Nachholregel bestimmt den Umgang mit verpassten Auslösern.

Später soll eine lokale Headless-Laufzeit ohne geöffnetes Browserfenster arbeiten.
Dafür muss der Rechner weiter laufen. Headless bedeutet nicht Cloud-Ausführung
und nicht Ausführung auf einem ausgeschalteten Gerät.

Mehrere Connectoren sind gleichzeitig konfigurierbar, etwa OpenAI, OpenRouter,
Replicate und lokale Anbieter. Pro Sitzung wird ausgewählt; einzelne KI-Nodes
können bewusst abweichende Bindungen besitzen. Ein lokales Modell verarbeitet
lokal; ein externes Modell verarbeitet den freigegebenen Kontext beim Anbieter.
Ein lokaler HTTP-Endpunkt allein beweist keinen lokalen Verarbeitungsort.
Optional herunterladbare lokale Modelle sind ein späterer Ausbau dieses Wegs.

Ein kleines, freiwilliges Unterstützer-Abo kann bereitgestellte Modelle und
einen E-Mail-Dienst anbieten. Später sind spezialisierte leistungsfähigere Nodes
möglich. Das Abo ist kein zwingender Zugang zu den Kernfunktionen.

Optionaler Cloud-Sync kann gespeicherte Sitzungsdefinitionen und Workflows auf
einem anderen Gerät verfügbar machen. Er überträgt nicht stillschweigend
Cookies, Schlüssel, Browserprofile, sensible Inhalte oder aktive Ausführungsrechte.
Synchronisierte Workflows dürfen nicht unbeabsichtigt auf mehreren Geräten
zugleich starten. Cloud-Hosting der Nutzer-Workflow-Laufzeit ist nicht vereinbart.

## Entschlackung und erste Priorität

Gespeicherte Sitzungen übernehmen im Produkt die Rolle klassischer Favoriten.
Weitere nicht benötigte Chromium-Funktionen werden gezielt entfernt oder
abgeschaltet. Sicherheit, Webkompatibilität, Downloads, Anmeldung und eine
wartbare Updatebasis dürfen dadurch nicht beschädigt werden.

Der erste nutzbare Produktmeilenstein ist: **eine dauerhafte Sitzung mit einem
gespeicherten, manuell startbaren Workflow und echter Fortschrittsübersicht**.
Die notwendigen Build- und Sitzungsgrundlagen kommen davor. Zeit- und
Webseitenereignisse folgen darauf, lokaler Headless-Betrieb später. Der
[Entwicklungsplan](development-plan.md) macht diese Reihenfolge abarbeitbar.
