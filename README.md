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

- Fetches breaking news from [SymbolScout API](https://symbolscout.farkaslabs.xyz/api/news/breaking)
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
2. Optionally create a virtual environment and activate it
```
python -m virtualenv venv
source venv/bin/activate
```
3. Install the required packages:
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

It's highly recommended to run this script in a tmux session to ensure it continues running even if your connection drops.

1. Start a new tmux session:
   ```
   tmux new -s symbolscout_passivbot
   ```

2. Navigate to the project directory:
   ```
   cd path/to/SymbolScout-PassivBot-Sentinel
   ```

3. Activate the virtual environment (if you made one) and run the script:
   ```
   source venv/bin/activate
   python main.py
   ```

4. Detach from the tmux session by pressing `Ctrl-B` and then `D`.

5. You can reattach to the session later to check on the script:
    ```
    tmux attach -t symbolscout_passivbot
    ```

The script will run continuously in the background, checking for news updates at the interval specified in the configuration.

### Stopping the Script

To stop the script:

1. Reattach to the tmux session:
   ```
   tmux attach -t symbolscout_passivbot
   ```

2. Stop the script by pressing `Ctrl-C`.

3. Exit the tmux session:
   ```
   exit
   ```

## State Management

The script maintains its state using a `last_processed_state.json` file. This file is created after processing news and helps the script keep track of which news articles have already been processed.

### Resetting Processed News State

If you need to reprocess news (for example, after making configuration changes or if you suspect some news was missed):

1. Stop the script (if it's running)
2. Delete the `last_processed_state.json` file:
   ```
   rm last_processed_state.json
   ```
3. Restart the script

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