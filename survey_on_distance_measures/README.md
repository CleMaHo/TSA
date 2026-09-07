# A Survey on Time-Series Distance Measures – Zusammenfassung

Quelle: Paparrizos, Li, Yang, Wu, D'Hondt, Papapetrou. *A Survey on Time-Series Distance Measures*. arXiv:2412.20574v1, 2024.

Zielgruppe dieser Zusammenfassung: Programmierer, die ein Verfahren zur Ähnlichkeitsbestimmung von Zeitreihen auswählen oder implementieren wollen, ohne tief in der Materie zu stecken.

## Abstract (übersetzt und eingeordnet)

Distanzmaße sind einer der Grundbausteine jeder Zeitreihenanalyse: Sie stecken hinter Suche, Indexierung, Klassifikation, Clustering und Anomalieerkennung. Weil Zeitreihendaten heute in extrem vielen Feldern anfallen (Industrie, Medizin, Finanzen, IoT, ...), ist die Wahl eines guten Distanzmaßes praxisrelevant geworden. Die Autoren tragen über 100 State-of-the-Art-Distanzmaße zusammen und ordnen sie in 7 Kategorien: Lock-Step, Sliding, Elastic, Kernel, Feature-basiert, Modellbasiert und Embedding-basiert. Für jede Kategorie werden die mathematischen Grundlagen sowie Stärken/Schwächen und Anwendungsfälle diskutiert, sowohl für univariate (eine Sensorgröße) als auch multivariate (mehrere Kanäle/Sensoren gleichzeitig) Zeitreihen.

Kernbotschaft der Autoren: Es gibt kein universell bestes Distanzmaß. Welches Maß sinnvoll ist, hängt davon ab, welche Art von "Störung" oder "Verzerrung" in den Daten zu erwarten ist (Skalierung, Verschiebung in der Zeit, unterschiedliche Länge, fehlende Abschnitte, Rauschen). Deshalb lohnt sich ein grobes Verständnis der Kategorien, statt exhaustiv alle Maße auszuprobieren.

## Warum reicht "einfacher Punktvergleich" oft nicht?

Die klassische euklidische Distanz (ED) vergleicht zwei Zeitreihen Punkt für Punkt an der exakt gleichen Zeitposition. Das funktioniert gut, wenn beide Reihen synchron und gleich lang sind. Es bricht aber schnell zusammen bei:

- **Skalierung/Verschiebung der Amplitude** – zwei Reihen haben die gleiche Form, aber unterschiedliche Höhe/Offset (lässt sich meist durch Normalisierung, z. B. Z-Normierung, vorher beheben).
- **Zeitliche Verschiebung (Shift)** – das gleiche Muster tritt bei beiden Reihen zu leicht unterschiedlicher Zeit auf.
- **Uneinheitliche Länge** – die Reihen haben unterschiedlich viele Messpunkte.
- **Lokale Verzerrung (Warping)** – ein Muster läuft bei einer Reihe schneller/langsamer ab als bei der anderen (z. B. ein Maschinenzyklus, der mal 3,9 s und mal 4,1 s dauert).
- **Rauschen/Ausreißer/fehlende Abschnitte.**

Die 7 Kategorien der Survey sind im Grunde 7 unterschiedliche Strategien, mit genau diesen Problemen umzugehen.

## Die 7 Kategorien im Detail

### 1. Lock-Step-Maße

**Funktionsweise:** Vergleich Index für Index (i-ter Punkt von X mit i-tem Punkt von Y), Differenzen werden aggregiert. Die Familie deckt weit mehr ab als nur die euklidische Distanz – die Survey listet über 40 Varianten, u. a. Manhattan, Minkowski/Chebyshev, normierte L1-Maße (Sørensen, Canberra, Lorentzian), Schnittmengen-Maße (Jaccard, Tanimoto), Inner-Product-Maße (Cosinus), Entropie-basierte Maße (Kullback-Leibler, Jensen-Shannon) u. v. m.

**Vorteile:**
- Sehr geringer Rechenaufwand, O(n).
- Trivial zu implementieren.
- Bei sauber synchronisierten, gleich langen Reihen oft überraschend konkurrenzfähig (die Survey widerlegt explizit den Mythos, ED sei elastischen Maßen bei großen Datenmengen immer unterlegen).

**Nachteile:**
- Keine Toleranz gegenüber zeitlicher Verschiebung – ein einziges verschobenes Muster kann die Distanz stark verfälschen.
- Setzt gleiche Länge voraus.
- Empfindlich gegenüber Rauschen/Ausreißern (außer robustere Varianten wie Manhattan/Canberra/Lorentzian).

**Wann einsetzen:** Als schnelle Baseline, immer wenn Messreihen exakt synchron abgetastet sind (gleiche Sampling-Rate, gleicher Start-/Endzeitpunkt), oder wenn Rechenzeit/Datenmenge kritisch ist (z. B. Vorfilterung riesiger Datensätze, bevor ein teureres Maß nur noch auf Kandidaten angewendet wird).

### 2. Elastische Maße (Elastic)

**Funktionsweise:** Statt Index-zu-Index wird eine optimale, nichtlineare Ausrichtung ("Alignment") zwischen den Zeitreihen gesucht – ein Punkt kann dabei mit mehreren Punkten der anderen Reihe verglichen werden (One-to-many). Das bekannteste Verfahren ist **Dynamic Time Warping (DTW)**: Es baut eine Kostenmatrix per dynamischer Programmierung auf und findet den günstigsten "Pfad" durch diese Matrix von Anfang bis Ende beider Reihen. Dadurch werden Zeitverzerrungen (unterschiedlich schnelle Abschnitte) ausgeglichen.

Wichtige Varianten von DTW:
- **Constrained DTW (Sakoe-Chiba-Band):** Begrenzt, wie weit sich die Ausrichtung vom Diagonalpfad entfernen darf ("Warping Window"). Schneller, oft sogar genauer, weil unsinnig weite Verzerrungen verhindert werden.
- **Weighted DTW:** Bestraft große zeitliche Abstände stärker.
- **Derivative DTW:** Vergleicht die Ableitung (Steigung) statt der Rohwerte – fokussiert auf Formähnlichkeit statt Absolutwert.

Weitere Maße derselben Familie, mit unterschiedlichen "Kostenfunktionen":
- **LCSS (Longest Common Subsequence):** Zählt "Matches" (Werte innerhalb einer Toleranzschwelle ε) statt Distanzen zu summieren – dadurch sehr robust gegen Ausreißer, ignoriert aber, wie groß eine Abweichung tatsächlich ist.
- **EDR (Edit Distance on Real Sequences):** Wie LCSS, wandelt Unterschiede in binär 0/1 um (Edit-Distance-Prinzip aus der Textverarbeitung).
- **ERP (Edit Distance with Real Penalty):** Kombiniert Edit-Distance-Idee mit echten (nicht binarisierten) Abständen, dadurch eine echte Metrik (erfüllt Dreiecksungleichung), was Indexierung/Beschleunigung erlaubt.
- **MSM (Move-Split-Merge):** Erlaubt Verschieben, Aufteilen und Zusammenführen von Punkten – ebenfalls eine echte Metrik, zusätzlich unempfindlich gegen Verschiebung der Grundlinie (translationsinvariant).
- **TWED (Time Warp Edit Distance):** Bestraft zusätzlich zu inhaltlichen Unterschieden auch Abstände in der Zeit selbst (Steifheitsparameter), verhindert dadurch unrealistisch weitreichende Verzerrungen.

**Vorteile:**
- Robust gegen Phasenverschiebung und ungleichmäßige Geschwindigkeit – der Klassiker für "gleiche Form, aber zeitlich verzerrt".
- Funktioniert auch bei unterschiedlicher Länge der Zeitreihen.
- Sehr gut erforscht, viele fertige Implementierungen verfügbar.

**Nachteile:**
- Quadratischer Aufwand O(n²) (bzw. O(n·m) bei unterschiedlicher Länge) – bei langen Reihen oder vielen Vergleichen (z. B. Nearest-Neighbor-Suche über große Datenbanken) spürbar langsamer als Lock-Step (Faktor 10–1000 in der Praxis).
- DTW selbst ist keine echte Metrik (Dreiecksungleichung verletzt) → schließt bestimmte Indexstrukturen/Beschleunigungen aus. ERP und MSM lösen das.
- Kann bei zu freier Ausrichtung "übertrieben" warpen und unähnliche Muster künstlich ähnlich machen (Grund für "Warping Windows").

**Beschleunigung:** Für zeitkritische Anwendungen (z. B. Nearest-Neighbor-Suche) gibt es zwei Standardtricks, unabhängig vom gewählten elastischen Maß:
- **Lower Bounding:** Eine billig zu berechnende Unterschranke (z. B. LB_Keogh) filtert von vornherein aussichtslose Kandidaten heraus, ohne die teure volle Berechnung durchführen zu müssen.
- **Early Abandoning:** Berechnung wird abgebrochen, sobald die bisherige Teildistanz bereits größer ist als der aktuell beste bekannte Wert.

**Wann einsetzen:** Wiederkehrende Muster/Zyklen mit variabler Dauer oder Phase (z. B. Maschinenzyklen, Gangmuster, Sprachsignale, EKG). Der Standard-Startpunkt, wenn "gleiche Form, aber zeitlich verschoben/gestreckt" die Kernannahme ist.

### 3. Sliding-Maße

**Funktionsweise:** Statt eine (elastische) Ausrichtung im Detail zu berechnen, wird die eine Zeitreihe komplett gegen die andere verschoben ("geshiftet"), für jede Verschiebung ein einfaches Lock-Step-Maß berechnet, und die beste (günstigste) Verschiebung gewinnt. Das bekannteste Verfahren ist **Shape-Based Distance (SBD)**, das über die (normierte) Kreuzkorrelation arbeitet und die Berechnung mittels FFT (Fast Fourier Transform) beschleunigt.

**Vorteile:**
- Deutlich schneller als elastische Maße: O(n log n) statt O(n²) dank FFT.
- Robust gegen einen globalen Zeitversatz (Shift/Translation) zwischen zwei Reihen.
- SBD ist die Basis von k-Shape, einem etablierten State-of-the-Art-Clustering-Verfahren für Zeitreihen.

**Nachteile:**
- Erlaubt nur eine globale, starre Verschiebung – keine lokale/nichtlineare Verzerrung wie DTW. Wenn nur ein Teilabschnitt verschoben ist, während der Rest synchron bleibt, ist Sliding weniger geeignet als elastische Maße.

**Wann einsetzen:** Guter Mittelweg zwischen Geschwindigkeit und Robustheit gegen Verschiebung, besonders bei (quasi-)periodischen Signalen und wenn eine reine, globale Zeitverschiebung die Hauptstörung ist (nicht lokale Verzerrung).

### 4. Kernel-Maße

**Funktionsweise:** Die Zeitreihe wird implizit in einen (meist höherdimensionalen) Raum projiziert, in dem Ähnlichkeit einfacher/besser trennbar berechnet werden kann (bekanntes Prinzip aus SVMs). Beispiele: Radial Basis Function (RBF) auf Basis der euklidischen Distanz, Global Alignment Kernel (GAK, betrachtet alle möglichen Ausrichtungen statt nur die eine optimale wie DTW), Kernel-DTW.

**Vorteile:** Gut geeignet für Machine-Learning-Pipelines, die einen echten (positiv definiten) Kernel benötigen, z. B. SVMs. Kann nichtlineare Ähnlichkeitsstrukturen erfassen.

**Nachteile:** Mathematisch anspruchsvoller, viele "naive" Kombinationen (z. B. Gaussian-Kernel direkt über DTW) sind nicht positiv definit und daher für manche ML-Verfahren ungeeignet. Weniger intuitiv interpretierbar als DTW & Co.

**Wann einsetzen:** Wenn das Distanzmaß direkt in einen klassischen ML-Algorithmus (SVM, Kernel-PCA etc.) eingespeist werden soll, der einen echten Kernel voraussetzt.

### 5. Feature-basierte Maße

**Funktionsweise:** Statt die Rohdaten zu vergleichen, werden zuerst charakteristische Kennzahlen/Merkmale aus der Zeitreihe extrahiert (z. B. Mittelwert, Trend, Saisonalität, Autokorrelation, spektrale Eigenschaften, Schiefe/Kurtosis), und diese Merkmalsvektoren werden dann mit einem einfachen Maß (meist euklidisch) verglichen. Bekannte Werkzeuge: **tsfresh** (automatisiert Extraktion aus über 60 Verfahren, ~800 Merkmale, mit automatischer Relevanzfilterung), **catch22** (22 sorgfältig ausgewählte, besonders aussagekräftige Merkmale, destilliert aus einem größeren Pool von ca. 7700 Merkmalen).

**Vorteile:**
- Reduziert die Zeitreihe auf eine überschaubare, interpretierbare Beschreibung.
- Funktioniert auch bei unterschiedlich langen/unregelmäßig abgetasteten Reihen, da am Ende nur noch Merkmalsvektoren gleicher Länge verglichen werden.
- Danach beliebig schnelles Distanzmaß möglich (Vergleich findet nur noch auf wenigen Zahlen statt).
- Robust gegenüber Rauschen, wenn die Merkmale selbst robust gewählt sind.

**Nachteile:**
- Informationsverlust möglich, falls relevante Muster nicht durch die gewählten Merkmale erfasst werden.
- Merkmalsauswahl ist aufgabenabhängig – "die" richtigen Merkmale gibt es nicht pauschal.

**Wann einsetzen:** Wenn die grobe Charakteristik einer Zeitreihe (Trend, Periodizität, statistisches Verhalten) wichtiger ist als der exakte zeitliche Verlauf, oder bei sehr verrauschten/unregelmäßigen Daten. Auch sinnvoll als Vorstufe für Clustering, wenn viele Zeitreihen verglichen werden müssen und Rechenzeit ein Thema ist.

### 6. Modellbasierte Maße

**Funktionsweise:** Es wird angenommen, dass die Zeitreihe von einem bestimmten statistischen Modell erzeugt wurde (z. B. Gaussian Mixture Model, Hidden Markov Model, ARIMA). Für jede Zeitreihe wird ein Modell gefittet, und dann werden die Modelle (bzw. deren Parameter oder die von ihnen erzeugten Wahrscheinlichkeitsverteilungen) miteinander verglichen, z. B. per Kullback-Leibler-Divergenz.

**Vorteile:** Erfasst die zugrundeliegende Erzeugungsdynamik/Zustandsstruktur statt nur die Rohwerte, probabilistisch fundiert und gut interpretierbar, wenn das Modell zum Prozess passt.

**Nachteile:** Modellannahme muss zur Realität passen (falsches Modell → schlechte Ergebnisse), Parameterschätzung ist aufwendiger als bei den vorherigen Kategorien.

**Wann einsetzen:** Wenn bekannt ist (oder plausibel angenommen werden kann), welcher Erzeugungsprozess hinter den Daten steckt, z. B. Zustandsmaschinen-artige Prozesse (HMM) oder Prozesse mit klarer Autokorrelationsstruktur (ARIMA). Häufig bei Anomalieerkennung, wenn "normales Verhalten" explizit modelliert werden soll.

### 7. Embedding-basierte Maße

**Funktionsweise:** Ähnlich wie bei Feature-basierten Maßen wird die Zeitreihe in eine neue Repräsentation überführt (ein "Embedding", meist ein Vektor fester Länge in einem latenten Raum), und darauf wird dann ein einfaches Maß (z. B. euklidisch) angewendet. Der Unterschied zu Feature-basiert: Die Repräsentation wird gelernt (oft automatisch, z. B. durch neuronale Netze), nicht von Hand definiert. Beispiele: **GRAIL** (kombiniert Kernel-Ähnlichkeit mit einer Landmarken-Auswahl), **TS2Vec** (Deep-Learning-Ansatz mit dilatierten Convolutional-Netzen), Autoencoder allgemein.

**Vorteile:** Kann sehr gut auf große, hochdimensionale Datenmengen skalieren, kann domänenspezifische Ähnlichkeit direkt aus Daten lernen (kein manuelles Feature-Engineering nötig), einmal berechnete Embeddings sind danach extrem schnell vergleichbar.

**Nachteile:** Braucht (oft größere) Trainingsdaten, ist als "Blackbox" weniger interpretierbar, höherer Implementierungs-/Trainingsaufwand.

**Wann einsetzen:** Große Mengen an Zeitreihen/Sensordaten, wiederkehrende Aufgabe (Training lohnt sich), wenn genug repräsentative Trainingsdaten vorhanden sind und einfachere Verfahren nicht mehr ausreichen bzw. zu langsam werden.

## Übersichtstabelle

| Kategorie | Grundidee | Rechenaufwand | Robust gegen | Typischer Einsatz |
|---|---|---|---|---|
| Lock-Step | Punkt-für-Punkt | O(n) | nichts Besonderes | Baseline, synchrone Daten, Vorfilterung |
| Elastic (DTW & Co.) | Optimale nichtlineare Ausrichtung | O(n²), mit Fenster schneller | Phasenverschiebung, Geschwindigkeitsunterschiede | Zyklen variabler Dauer/Phase |
| Sliding (SBD) | Beste globale Verschiebung, FFT-beschleunigt | O(n log n) | globaler Zeitversatz | (Quasi-)periodische Signale, Clustering |
| Kernel | Implizite Projektion in höherdim. Raum | variiert | – | Einbettung in SVM/Kernel-ML |
| Feature-basiert | Merkmale statt Rohdaten | gering nach Extraktion | Rauschen, ungleiche Länge | Grobcharakteristik, Vorverarbeitung für Clustering |
| Modellbasiert | Vergleich gefitteter Modelle | modellabhängig | – | Bekannte Erzeugungsdynamik, Anomalieerkennung |
| Embedding | Gelernte Repräsentation | Training teuer, Vergleich billig | – | Große Datenmengen, wiederkehrende Aufgabe |

## Multivariate Zeitreihen (mehrere Sensoren/Kanäle gleichzeitig)

Fast alle Maße lassen sich auf mehrkanalige Daten (z. B. mehrere Sensorsignale gleichzeitig) erweitern. Die Survey unterscheidet dabei zwei grundsätzliche Strategien:

- **Dependent (abhängig):** Alle Kanäle werden gemeinsam als eine Einheit behandelt – es gibt nur eine gemeinsame Ausrichtung/ein gemeinsames Modell für alle Kanäle zusammen. Sinnvoll, wenn ein Zeitversatz alle Kanäle gleichermaßen betrifft (z. B. eine unkalibrierte Systemuhr für ein ganzes Sensor-Array).
- **Independent (unabhängig):** Jeder Kanal wird für sich behandelt (eigene Ausrichtung/eigenes Modell je Kanal), die Einzeldistanzen werden anschließend summiert. Sinnvoll, wenn sich die Verzerrung zwischen den Kanälen unterscheiden kann (z. B. unterschiedliche Latenz/Kalibrierung pro Einzelsensor).

Welche der beiden Varianten passt, ist eine inhaltliche Entscheidung über die Datenerzeugung, keine rein mathematische.

## Praktische Einordnung für die Auswahl

Als grobe Entscheidungshilfe, in der Reihenfolge, wie man typischerweise vorgeht:

1. Zuerst Daten normalisieren (z. B. Z-Normierung), das behebt bereits viele Skalierungs-/Offset-Probleme, unabhängig vom späteren Distanzmaß.
2. Sind die Reihen exakt synchron und gleich lang, und ist Performance kritisch? → Lock-Step (euklidisch/Manhattan) als Baseline probieren.
3. Ist mit Phasenverschiebung oder ungleicher Geschwindigkeit zu rechnen (z. B. Zyklen unterschiedlicher Dauer)? → DTW (ggf. mit Sakoe-Chiba-Band zur Beschleunigung) als Standardwahl; ERP oder MSM, falls eine echte Metrik gebraucht wird (z. B. für Indexstrukturen).
4. Nur ein grober, globaler Zeitversatz, dafür will man schnell bleiben? → Sliding-Maße wie SBD.
5. Viele/große Zeitreihen, Rauschen ein Problem, Rohform weniger relevant als Charakteristik? → Feature-basiert (tsfresh/catch22), danach z. B. euklidisch auf den Merkmalen.
6. Bekannte Erzeugungsdynamik oder Anomalieerkennung mit explizitem "Normalzustand"? → Modellbasiert (HMM/ARIMA).
7. Sehr große Datenmengen, wiederkehrende Aufgabe, genug Trainingsdaten vorhanden, einfachere Verfahren zu langsam/ungenau? → Embedding-Ansätze (TS2Vec, Autoencoder).

Wichtig laut Survey: Es gibt kein Maß, das in allen Studien durchgehend am besten abschneidet. Elastische Maße schlagen nicht automatisch Sliding-Maße, und Lock-Step-Maße (richtig normalisiert) sind manchmal überraschend konkurrenzfähig. In der Praxis lohnt es sich daher, mindestens zwei Kandidaten aus unterschiedlichen Kategorien empirisch auf den eigenen Daten zu vergleichen, statt sich auf eine "Standardannahme" zu verlassen.

## Anhang: Vollständige Methodenliste

Die folgenden Tabellen listen alle in der Survey benannten Einzelmethoden auf (nicht nur die im Haupttext erklärten Vertreter), gruppiert wie in der Survey selbst. Formeln sind hier bewusst weggelassen (Details siehe Originalarbeit, Tabellen 1–10) – stattdessen eine kurze Einordnung, was das jeweilige Maß tut bzw. wodurch es sich von den anderen in seiner Unterkategorie unterscheidet.

### A1. Lock-Step-Maße (Tabellen 1–3 der Survey, ~40 Methoden in 9 Unterkategorien)

**Minkowski:** Euclidean, Manhattan, Minkowski (allgemeine p-Norm), Chebyshev (Maximalabweichung, p→∞).

**L1 (angepasste Manhattan-Varianten):** Sørensen (normiert auf [0,1]), Gower (normiert über Reihenlänge), Soergel (normiert über Maximalwerte), Kulczynski (normiert über Minimalwerte), Canberra (sensitiv nahe Null, gut für Daten um den Ursprung), Lorentzian (Log-gedämpfte L1-Variante, robust gegen Ausreißer).

**Intersection (eng verwandt mit L1, über Schnittmengen-Logik):** Intersection, Wave Hedges, Czekanowski (äquivalent zu Sørensen), Motyka, Tanimoto (äquivalent zu Soergel).

**Inner Product (basieren auf Skalarprodukt/Winkel zwischen den Reihen):** Inner Product, Harmonic Mean, Kumar-Hassebrook (ähnlich Harmonic Mean, für Bildsensor-Mustervergleich), Jaccard, Cosine (Winkel zwischen den Vektoren; hängt mit Pearson-Korrelation zusammen), Dice.

**Squared Chord (Summe geometrischer Mittel):** Fidelity, Bhattacharyya (Spezialfall der Mahalanobis-Distanz), Squared-chord, Hellinger, Matusita – häufig in der biologischen Datenanalyse (z. B. Pollenanalyse) eingesetzt.

**Squared L2 (χ²-Familie, quadrierte euklidische Distanz mit Normierung):** Squared Euclidean, Clark, Neyman χ², Pearson χ² (beide asymmetrisch/Divergenzen), Squared χ², Divergence, Additive Symmetric χ², Probabilistic Symmetric χ² (symmetrische Versionen).

**Shannon's Entropy (basieren auf Informationstheorie):** Kullback-Leibler (KL-Divergenz, asymmetrisch), Jeffreys (symmetrische Version von KL), K Divergence, Topsøe, Jensen Shannon, Jensen Difference.

**Vicissitude (Varianten von Wave Hedges mit unterschiedlicher Normierung):** Vicis-Wave Hedges (= Emanon 1), Emanon 2, Emanon 3, Emanon 4, Max-Symmetric χ², Min-Symmetric χ².

**Kombinationsmaße:** Taneja (arithmetisch-geometrisches Mittel-Divergenzmaß), Kumar-Johnson, Avg(L1, L∞) (Mittel aus Manhattan und Chebyshev).

**Sonstige (keine klassischen Lock-Step-Maße im engeren Sinn, aber verwandt):** DISSIM (Integral der euklidischen Distanz über die Zeit, erlaubt unterschiedliche Abtastraten), PCC (Pearson-Korrelationskoeffizient), ACD (Autocorrelation Distance, vergleicht Autokorrelationsvektoren), MD (Markovian Distance, vergleicht Übergangswahrscheinlichkeiten eines Markov-Modells).

### A2. Elastische Maße (Abschnitt 5 der Survey)

**DTW-Familie:** DTW (Standard), Constrained DTW / Sakoe-Chiba-Band (begrenztes Warping-Fenster), Weighted DTW (gewichtete Bestrafung je nach zeitlichem Abstand), Derivative DTW (vergleicht Ableitungen statt Rohwerte).

**Threshold-basiert (Schwellenwert ε entscheidet Match/Mismatch):** LCSS (Longest Common Subsequence), EDR (Edit Distance on Real Sequences), SWALE (Sequence Weighted Alignment, verallgemeinert EDR mit Belohnungs-/Straf-Parametern r/p).

**Metrisch (erfüllen die Dreiecksungleichung, dadurch indexierbar):** ERP (Edit Distance with Real Penalty), MSM (Move-Split-Merge, translationsinvariant), TWED (Time Warp Edit Distance, bestraft zusätzlich zeitlichen Abstand).

**Beschleunigung:** Early Abandoning (Berechnung abbrechen, sobald Zwischenergebnis den bisher besten Kandidaten übersteigt), Lower Bounding (LB_Kim, LB_Keogh, LB_Improved, LB_Enhanced, LB_Petitjean/LB_Webb, GLB-Framework als vereinheitlichter Ansatz für alle elastischen Maße inkl. EDR/SWALE).

### A3. Sliding-Maße (Tabelle 6 der Survey)

NCC_b (biased normalized cross-correlation), NCC_u (unbiased), NCC_c (Basis für SBD, am besten performant laut Survey), NCC (unnormierte Variante), STID (Scaling and Translation Invariant Distance, sucht zusätzlich optimalen Skalierungsfaktor α).

### A4. Kernel-Maße (Tabelle 7 der Survey)

RBF (Radial Basis Function, Gaussian-Kernel über euklidischer Distanz), LGAK (Log Global Alignment Kernel, betrachtet alle Alignments statt nur des optimalen), KDTW (Kernel Dynamic Time Warping, DTW mit positiv-definitem Kernel statt Min/Max-Operationen), SINK (Shift Invariant Kernel, gewichtete Summe über die normierte Kreuzkorrelationssequenz).

### A5. Feature-basierte Maße (Tabelle 8 der Survey, 19 Methoden)

| Methode | Feature-Typ | Dim. |
|---|---|---|
| TSS-IOF-ED | First-/Second-Order-Statistiken | univariat |
| TSC-GC-ED | Globale Merkmale | univariat |
| CBC (Characteristic-Based Clustering) | Umfassend (Trend, Saisonalität, Chaos, Selbstähnlichkeit u.a.) | multivariat |
| TSC-SSF | Statistisch | multivariat |
| TSBF | Statistisch | univariat |
| FEDD | Statistisch | univariat |
| FBC | Fuzzy-Merkmale | univariat |
| hctsa | Umfassend (~4.800–7.700 Merkmale) | univariat |
| tsfresh | Umfassend (~800 Merkmale, automatisierte Relevanzfilterung) | multivariat |
| catch22 | Kanonisch (22 destillierte Merkmale aus hctsa) | multivariat |
| TSC-CN | Visibility-Graph-basiert | multivariat |
| FeatTS | Basiert auf tsfresh | univariat |
| TSC-GPF-ED | Global + Peak-Merkmale | univariat |
| TSC-FDDO | Umfassend | multivariat |
| Time2Feat | Umfassend, interpretierbare Repräsentationen | multivariat |
| theft | Umfassend | univariat |
| AngClust | Winkel-Merkmale (aus PCA) | multivariat |
| FGHIC-SOME | Statistisch | multivariat |
| TSC-VF | Visuelle Merkmale | univariat |
| FTSCP | Umfassend | multivariat |

### A6. Modellbasierte Maße (Tabelle 9 der Survey)

| Methode | Modell | Distanzmaß | Dim. |
|---|---|---|---|
| TSC-ARIMA-ED | ARIMA | Euklidisch (auf Modellkoeffizienten) | univariat |
| TSC-D-HMM | HMM | Log-Likelihood | multivariat |
| ICL | GMM | Log-Likelihood | multivariat |
| TSC-AR-HT | AR | Hypothesentest | univariat |
| MBCD | Markov-Kette | KL-Distanz | multivariat |
| TSC-LPC-ARIMA | ARIMA | Euklidisch | multivariat |
| BHMMC | HMM | BIC | multivariat |
| FCM-SV | GMM | Log-Likelihood (Fuzzy-C-Means-Score) | univariat |
| HMM-TWM | HMM | Euklidisch | univariat |
| TSC-ARMAM | ARMA | Log-Likelihood | univariat |
| CLUSTSEG | Regressions-Mischmodell | L2-Distanz | univariat |
| LMAR / LMMAR | LMAR/LMMAR | Mahalanobis-Distanz | univariat |
| TSC-HMM-S-KL | HMM | Symmetrische KL-Divergenz | multivariat |
| MV-ARF | AR-Ensembles | MSE | multivariat |
| K-MODELS | ARMA/ARIMA | K-Models-Loss | univariat |

### A7. Embedding-basierte Maße (Tabelle 10 der Survey)

| Methode | Embedding-Prinzip | Dim. |
|---|---|---|
| GRAIL | SINK-Kernel-Ähnlichkeit + spektrale Zerlegung, mit Landmarken-Auswahl | univariat |
| RWS (Random Warping Series) | Approximiert GAK über zufällig gezogene Referenzreihen | univariat |
| SPIRAL | Approximiert die DTW-Distanzmatrix über Sampling + Faktorisierung | univariat |
| SIDL (Shift-invariant Dictionary Learning) | Lernt ein Dictionary shift-invarianter Muster + Sparse Coding | univariat |
| Autoencoder | Generisches neuronales Netz (Encoder/Decoder) | univariat |
| Time2Vec | Einzelne lernbare Schicht mit periodischer Aktivierung | univariat |
| TS2Vec | Dilatierte CNNs + hierarchisches kontrastives Lernen | multivariat |
| LLM Encoding | Multimodales LLM-basiertes Embedding | multivariat |

Zusätzlich diskutiert die Survey allgemein Deep-Learning-Backbones für Embeddings: LSTMs (klassisch für sequenzielle Daten), bidirektionale LSTMs, 1D-CNNs sowie multimodale Ansätze, die Zeitreihen mit Text/Bild-Daten kombinieren.
