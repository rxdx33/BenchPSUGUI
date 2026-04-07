# BenchPSUGUI

A simple Python desktop application for controlling VISA-compatible bench power supplies via a clean GUI built with CustomTkinter.

## Features

- **Auto-detect instruments** — lists all available VISA resources on startup for easy selection
- **Set voltage & current** — enter target values and apply them to the power supply with a single click (or press Enter)
- **Output enable/disable** — toggle the PSU output ON or OFF with dedicated buttons
- **Live readings** — poll and display the actual output voltage and current in real time (updates every second)
- **Clean on exit** — instrument connection is properly closed when the window is closed

## Requirements

- Python 3.x
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [PyVISA](https://pyvisa.readthedocs.io/)
- A VISA backend (e.g. [NI-VISA](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html) or [pyvisa-py](https://pyvisa-py.readthedocs.io/))

Install dependencies:

```bash
pip install customtkinter pyvisa
```

> If you don't have NI-VISA installed, you can use the pure-Python backend instead:
> ```bash
> pip install pyvisa-py
> ```

## Usage

1. Connect your power supply to the PC via USB or serial — it should appear as a COM port or VISA resource.
2. Run the application:
   ```bash
   python main.py
   ```
3. Select your power supply from the **instrument dropdown**.
4. Set the desired **voltage (V)** and **current (A)** and click **Set**.
5. Toggle the output using the **ON / OFF** buttons.
6. Click **Read** to start polling live output readings.

## Compatibility

This application communicates using standard SCPI commands (`VSET1`, `ISET1`, `VOUT1?`, `IOUT1?`, `OUT1`/`OUT0`). It is intended for power supplies that support this command set such as TENMA units.

If your power supply uses different commands, you will need to modify the relevant functions in `main.py`.
