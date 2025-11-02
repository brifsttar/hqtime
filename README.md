# Tempo Auto Badgeage

My workplace forces me to clock-in four times a day, every day. So I made this script that does it for me.

## Features

* Performs automatic _badgeages_ for a single day (you need to run it each day)
* Supports _télétravail flottant_
* Randomizes badge times within a configurable range _because why not_
* Doesn't badge on weekends, holidays or planned absences

## Not supported (yet?)

* Making sure that anything above actually works
* Half days off
* Discord notifications for badgeages & errors

## Usage

### Requirements & Installation

- Python 3.8+ (probably works with older versions too, but untested)
- A system keyring supported by the [`keyring`](https://pypi.org/project/keyring/) Python package (e.g. `secret-service` on Linux, `Keychain` on macOS, [`Credential Locker`](https://learn.microsoft.com/en-us/windows/apps/develop/security/credential-locker) on Windows)
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Install `playwright` browsers:
  ```bash
  playwright install
  ```

### Credentials

You first need to store your credentials in the system keyring:

```bash
python -m keyring set tempo prenom.nom
```

### Running the script

```
usage: main.py [-h] [--badgeage-times Entrée-matin Sortie-midi Entrée-après-midi Sortie-soir] [--ttf_day TTF_DAY] [--random-offset-range RANDOM_OFFSET_RANGE] username

positional arguments:
  username              Username for tempo.univ-eiffel.fr, as stored on the local keyring

optional arguments:
  -h, --help            show this help message and exit
  --badgeage-times Entrée-matin Sortie-midi Entrée-après-midi Sortie-soir
                        Times around which to badge (default: [8, 12, 12.75, 18])
  --ttf_day TTF_DAY     Day of the week for "télétravail flottant" (0=Monday, 6=Sunday) (default: 2)
  --random-offset-range RANDOM_OFFSET_RANGE
                        Range in minutes for random offset around badgeage times (default: 30)
```

### Scheduling

You can use `cron` (Linux/macOS) or Task Scheduler (Windows) to run the script at system startup or at specific times.
