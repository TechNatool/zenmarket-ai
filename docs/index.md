# ZenMarket AI

**AI-powered financial intelligence and market analysis system**

[![CI/CD](https://github.com/TechNatool/zenmarket-ai/workflows/CI/CD/badge.svg)](https://github.com/TechNatool/zenmarket-ai/actions)
[![codecov](https://codecov.io/gh/TechNatool/zenmarket-ai/branch/main/graph/badge.svg)](https://codecov.io/gh/TechNatool/zenmarket-ai)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview

ZenMarket AI is a professional-grade financial intelligence system that combines AI-powered analysis with robust trading simulation capabilities. It provides comprehensive market analysis, risk management, and backtesting tools for algorithmic trading research and development.

## Key Features

- **🤖 AI-Powered Analysis**: Integration with OpenAI and Anthropic for intelligent market insights
- **📊 Technical Analysis**: Comprehensive indicators (RSI, MACD, Bollinger Bands, ATR, etc.)
- **💼 Trading Simulator**: Paper trading environment with realistic order execution
- **⚖️ Risk Management**: Position sizing, circuit breakers, and drawdown protection
- **📈 Backtesting**: Comprehensive backtesting with detailed performance metrics
- **📰 Market Intelligence**: Financial news analysis and sentiment scoring
- **🔒 Security**: Built-in safeguards and security best practices

## Architecture

```mermaid
graph TB
    A[Market Data] -->|yfinance| B[Data Collection]
    C[News Sources] -->|feedparser| B
    B --> D[Analysis Engine]
    D --> E[AI Processing]
    E -->|OpenAI/Anthropic| F[Insights]
    D --> G[Technical Indicators]
    G --> H[Signal Generator]
    H --> I[Execution Engine]
    I --> J[Risk Manager]
    J --> K[Broker Simulator]
    K --> L[Position Manager]
    L --> M[Performance Tracker]
    M --> N[Reports & Visualization]
```

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run simulator
python -m src.cli simulate --symbol AAPL --strategy conservative

# Run backtest
python -m src.cli backtest --symbol AAPL --start 2024-01-01 --end 2024-12-31
```

## Documentation

- [Installation Guide](getting-started/installation.md)
- [Configuration](getting-started/configuration.md)
- [CLI Usage](user-guide/cli.md)
- [Contributing](CONTRIBUTING.md)

## Development

```bash
# Setup development environment
make setup

# Run quality checks
make precommit

# Run tests
make test

# Generate coverage report
make cov
```

## Security

ZenMarket AI operates in paper trading mode by default. Review the [Security Policy](SECURITY.md) before any production use.

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Support

- 📧 Email: contact@technatool.com
- 🐛 Issues: [GitHub Issues](https://github.com/TechNatool/zenmarket-ai/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/TechNatool/zenmarket-ai/discussions)
