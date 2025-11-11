# AI Trading Advisor - Documentation

Guide complet du module AI Trading Advisor de ZenMarket AI.

## Vue d'ensemble

Le module AI Trading Advisor est une extension quantitative de ZenMarket AI qui fournit des signaux de trading basés sur l'analyse technique automatisée. Il complète l'analyse fondamentale (news + sentiment) avec des indicateurs techniques et des recommandations actionables.

---

## Architecture

### Modules

```
src/advisor/
├── indicators.py          # Calcul des indicateurs techniques
├── signal_generator.py    # Génération des signaux BUY/SELL/HOLD
├── plotter.py            # Graphiques techniques matplotlib
├── advisor_report.py     # Génération du rapport complet
└── __main__.py           # Point d'entrée standalone
```

### Flux de traitement

```
1. Récupération données (yfinance)
   ↓
2. Calcul indicateurs (MA, RSI, BB, ATR)
   ↓
3. Génération signaux (logique multi-critères)
   ↓
4. Création graphiques (matplotlib)
   ↓
5. Génération rapport (Markdown + AI commentary)
```

---

## Indicateurs Techniques

### Moving Averages (MA)
- **MA20**: Moyenne mobile sur 20 périodes (court terme)
- **MA50**: Moyenne mobile sur 50 périodes (moyen terme)
- **Usage**: Détection de tendance via croisements

### RSI (Relative Strength Index)
- **Période**: 14 jours
- **Zones**:
  - Surachat: > 70
  - Neutre: 30-70
  - Survente: < 30
- **Usage**: Identification des conditions extrêmes

### Bandes de Bollinger
- **Période**: 20 jours
- **Écart-type**: 2.0
- **Composantes**:
  - Bande supérieure (résistance dynamique)
  - Bande médiane (MA20)
  - Bande inférieure (support dynamique)
- **Usage**: Mesure de volatilité et niveaux clés

### ATR (Average True Range)
- **Période**: 14 jours
- **Usage**: Mesure de volatilité pour dimensionner positions

---

## Logique des Signaux

### Système de points

Chaque signal est déterminé par un système de points cumulatifs :

#### Points positifs (BUY)
- MA20 > MA50: **+2 points**
- RSI < 30 (survente): **+1 à +3 points** (selon intensité)
- Prix sous BB inférieure: **+1 point**
- Prix sous MA20 en tendance haussière: **+1 point**

#### Points négatifs (SELL)
- MA20 < MA50: **-2 points**
- RSI > 70 (surachat): **-1 à -3 points** (selon intensité)
- Prix au-dessus BB supérieure: **-1 point**
- Prix au-dessus MA20 en tendance baissière: **-1 point**

### Règles de décision

```python
if total_points >= 3:
    signal = BUY
    confidence = min(1.0, points / 6.0)

elif total_points <= -3:
    signal = SELL
    confidence = min(1.0, abs(points) / 6.0)

else:
    signal = HOLD
    confidence = 0.5
```

### Règles de sécurité

- **Anti-achat en surachat extrême**: Si RSI > 80, annule signal BUY → HOLD
- **Anti-vente en survente extrême**: Si RSI < 20, annule signal SELL → HOLD

---

## Utilisation

### Mode standalone

```bash
# Analyser les tickers par défaut (depuis .env)
python -m src.advisor

# Analyser des tickers spécifiques
python -m src.advisor --tickers "^GDAXI,^IXIC,BTC-USD"

# Sans graphiques (plus rapide)
python -m src.advisor --no-charts

# Mode debug
python -m src.advisor --log-level DEBUG
```

### Mode intégré

```bash
# Générer uniquement le rapport trading
python -m src.main --trading-only

# Générer les deux rapports (news + trading)
python -m src.main --trading-advisor

# Sans graphiques
python -m src.main --trading-advisor --no-charts
```

---

## Format du Rapport

### Structure Markdown

1. **Vue d'ensemble**
   - Biais de marché global (Haussier/Baissier/Neutre)
   - Distribution des signaux (%)
   - Confiance moyenne

2. **Tableau des signaux**
   - Ticker, Tendance, RSI, MA20, MA50
   - Signal (📈 BUY / 📉 SELL / ⚖️ HOLD)
   - Confiance, Commentaire

3. **Analyse détaillée par ticker**
   - Prix actuel et indicateurs
   - Raisons du signal (liste détaillée)
   - Contexte technique

4. **Analyse IA**
   - Commentaire généré par OpenAI/Claude
   - Synthèse des opportunités
   - Contexte de marché

5. **Recommandations**
   - Approche suggérée selon biais
   - Points de vigilance
   - Gestion du risque

### Graphiques générés

Pour chaque ticker :
- **Chart principal** (3 sous-plots):
  - Prix + MA20/50 + Bollinger Bands
  - RSI avec zones 30/70
  - Volume (avec couleurs selon direction)

Graphiques d'ensemble :
- **Signal Overview**: Distribution et confiances
- **RSI Heatmap**: Niveaux RSI de tous les tickers

---

## Exemples de Signaux

### Signal d'Achat (BUY)

```
Ticker: DAX
Prix: 19,245.67
MA20: 19,280.50 (>)
MA50: 19,100.00
RSI: 61.2

Signal: 📈 BUY (Confiance: 0.75)

Raisons:
- Croisement haussier MM20 > MM50
- RSI neutre (61.2)
- Prix sous MA20 (opportunité d'achat)
- Momentum positif confirmé
```

### Signal de Vente (SELL)

```
Ticker: EUR/USD
Prix: 1.1045
MA20: 1.1020 (<)
MA50: 1.1065
RSI: 39.3

Signal: 📉 SELL (Confiance: 0.68)

Raisons:
- Croisement baissier MM20 < MM50
- RSI survendu (39.3)
- Prix au-dessus MA20 (rebond technique possible)
- Pression vendeuse détectée
```

### Signal Neutre (HOLD)

```
Ticker: NASDAQ
Prix: 18,567.89
MA20: 18,580.00
MA50: 18,590.00
RSI: 48.5

Signal: ⚖️ HOLD (Confiance: 0.50)

Raisons:
- MAs en convergence
- RSI neutre (48.5)
- Consolidation latérale
- Attente de signal directionnel clair
```

---

## Configuration

### Variables d'environnement

Utilise la même configuration que le module principal (`.env`) :

```env
# Tickers à analyser
MARKET_INDICES=^GDAXI,^IXIC,^GSPC,EURUSD=X,BTC-USD

# IA pour commentaires
AI_PROVIDER=openai
OPENAI_API_KEY=your_key_here

# Options de rapport
REPORT_INCLUDE_CHARTS=true
TIMEZONE=Europe/Paris
```

### Personnalisation des seuils

Dans le code (si besoin) :

```python
generator = SignalGenerator(
    rsi_overbought=70.0,      # Seuil surachat
    rsi_oversold=30.0,         # Seuil survente
    rsi_strong_overbought=80.0,
    rsi_strong_oversold=20.0
)
```

---

## Tests

### Exécution des tests

```bash
# Tests des indicateurs
pytest tests/test_indicators.py -v

# Tests des signaux
pytest tests/test_signal_generator.py -v

# Tous les tests advisor
pytest tests/test_*.py -k "indicator or signal" -v
```

### Couverture

- `test_indicators.py`: Tests des calculs MA, RSI, BB, ATR
- `test_signal_generator.py`: Tests de la logique de signaux

---

## Intégration avec l'analyse fondamentale

Le Trading Advisor est conçu pour compléter le Financial Brief :

| Financial Brief | Trading Advisor |
|----------------|-----------------|
| Actualités financières | Signaux techniques |
| Sentiment de marché | Indicateurs quantitatifs |
| Analyse qualitative | Analyse quantitative |
| "Pourquoi ?" | "Quand ?" |

### Utilisation combinée

1. **Matin**: Lire le Financial Brief pour comprendre le contexte
2. **Ensuite**: Consulter le Trading Advisor pour les signaux d'entrée/sortie
3. **Décision**: Combiner fondamental + technique pour confirmer

Exemple :
- Financial Brief : "Sentiment positif sur le DAX suite aux données PMI"
- Trading Advisor : "Signal BUY confirmé avec MA20 > MA50, RSI neutre"
- **→ Opportunité d'achat renforcée**

---

## Limitations

### Ce que le module fait
- Analyse technique automatisée
- Signaux basés sur indicateurs classiques
- Graphiques de qualité professionnelle
- Aide à la décision

### Ce que le module ne fait PAS
- Garantir la rentabilité (aucun système n'est infaillible)
- Prédire le futur avec certitude
- Remplacer l'analyse humaine
- Prendre en compte les événements imprévus

### Recommandations
- Toujours croiser avec d'autres analyses
- Utiliser des stop-loss appropriés
- Adapter la taille de position au risque
- Ne jamais investir plus que ce qu'on peut perdre

---

## Roadmap

Améliorations futures possibles :

- [ ] Support pour plus d'indicateurs (MACD, Stochastic, Fibonacci)
- [ ] Backtesting automatisé des signaux
- [ ] Scoring de qualité des signaux historiques
- [ ] Alertes en temps réel (Telegram/Email)
- [ ] Support multi-timeframes (1h, 4h, daily, weekly)
- [ ] Corrélations entre actifs
- [ ] Analyse de volume avancée
- [ ] Machine learning pour optimiser les seuils

---

## Support

Pour questions ou bugs :
- GitHub Issues: https://github.com/TechNatool/zenmarket-ai/issues
- Documentation principale: README.md
- Email: contact@technatool.com

---

**Disclaimer**: Les signaux générés par ce module sont à titre informatif uniquement et ne constituent pas des conseils en investissement. Consultez toujours un conseiller financier professionnel avant de prendre des décisions d'investissement.
