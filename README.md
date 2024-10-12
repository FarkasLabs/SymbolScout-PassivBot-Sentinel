# SymbolScout Integration for Passivbot

⚠️ **IMPORTANT: This project is currently in a testing phase. Use with caution and at your own risk.** ⚠️

This project integrates SymbolScout's news feed with Passivbot, automatically updating Passivbot configurations based on breaking news about cryptocurrency delistings and token swaps.

## Warning and Disclaimer

This integration is designed to automatically adjust your Passivbot configuration in response to potentially market-impacting news, but it is still in an experimental stage. Please note:

1. The system can remove symbols from Passivbot's approved coins list and/or add them to the ignored coins list based on news events.
2. It attempts to restart Passivbot instances after making configuration changes, which could potentially disrupt ongoing trades if the restart process fails or encounters issues.
3. **It is HIGHLY RECOMMENDED to set up notifications** to stay informed about any changes made to your Passivbot configuration and restart attempts.
4. Regular monitoring of the system's actions is crucial, especially during the initial deployment and testing phases.
5. The developers are not responsible for any financial losses that may occur from using this integration. Use at your own risk and always monitor your trading activity.

By using this integration, you acknowledge these risks and agree to take full responsibility for monitoring and managing your trading activities.

## Features

- Fetches breaking news from SymbolScout API
- Filters news based on specified categories and quote currencies
- Updates Passivbot configuration files to exclude affected symbols
- Restarts Passivbot instances after configuration updates
- Configurable notification system using Apprise

## Prerequisites

- Python 3.7+
- Passivbot installed and configured
- TMux & tmuxp (for Passivbot instance management, this is the only mode implemented at the moment)

## Installation
1. Clone the repository
2. Install the required packages:
```
pip install -r requirements.txt
```

## Configuration
1. Copy `config.example.yml` to `config.local.yml`:
   ```
   cp config.example.yml config.local.yml
   ```

2. Edit `config.local.yml` with your personal settings:
   - Set your SymbolScout API endpoint (only [Breaking News](https://symbolscout.farkaslabs.xyz/api/news/breaking) is supported at the moment, more coming soon!)
   - Configure news monitoring categories and quote currencies
   - Set Passivbot folder and configuration paths
   - Configure TMux settings
   - Set up notifications (**optional but highly recommended**)

The program will use `config.local.yml` if it exists, otherwise it will fall back to `config.yml`.

## Usage

Run the main script:

```
python main.py
```

The script will run continuously, checking for news updates at the interval specified in the configuration.

## Testing

Run the test suite:

```
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links
- [Passivbot](https://github.com/enarjord/Passivbot)
- [SymbolScout](https://symbolscout.farkaslabs.xyz/) 