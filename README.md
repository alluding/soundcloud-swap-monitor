# SoundCloud Swap/Username Monitor

## Features

- **Username Monitoring:** Continuously checks the SoundCloud profiles of specified usernames.
- **User ID Logging:** Logs changes in user IDs for monitored usernames.
- **Invalid Username Handling:** Handles cases where a previously invalid username becomes valid again.

## Getting Started

### Prerequisites

- Python 3.7
- `requests`, `colorama` libraries. You can install them using:
  ```bash
  pip install requests colorama
  ```

### Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/kyaasky/soundcloud-swap-monitor.git
   cd soundcloud-swap-monitor
   ```

2. Create a file named `usernames.txt` in the project directory and add the usernames to monitor, each on a new line.

3. Run the script:
   ```bash
   python main.py
   ```

4. The script will continuously monitor the specified usernames and log changes in user IDs.

## Configuration

- `Config.PROXY`: Proxy configuration for making requests.
- `Config.SLEEP_DELAY`: Sleep delay in seconds between each monitoring iteration.
- `Config.USERNAME_FILE_PATH`: Path to the file containing usernames to monitor.

## Contributing

Feel free to contribute by opening issues or creating pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

---
