import customtkinter as ctk
import pyvisa as visa

# Macros
DEBUG = False
rm = visa.ResourceManager()
instrument = None  # Global handle to the PSU

def connectToResource(resource):
    global instrument
    if instrument:
        try:
            instrument.close()
        except Exception:
            pass
    try:
        instrument = rm.open_resource(resource)
        instrument.timeout = 5000
        id = instrument.query('*IDN?') # validation
        print(f"Connected to {resource}")
        print(f"Identification: {str(id)}")
    except visa.VisaIOError as e:
        print(f"Connection error: {e}")
        instrument = None

def psuEnable(bEnable):
    if instrument:
        try:
            if bEnable:
                instrument.write('OUT1')
                print("PSU ON")
            else:
                instrument.write('OUT0')
                print("PSU OFF")
        except Exception as e:
            print(f"Failed to turn PSU ON: {e}")
    else:
        print("No PSU connected.")

def setVoltageCurrent(voltageVar, currentVar):
    # Read values from the UI, validate and send to instrument 

    try:
        v = float(voltageVar.get().strip())
        i = float(currentVar.get().strip())
    except ValueError:
        print("Invalid input", "Voltage and Current must be numeric values.")
        return

    if instrument:
        try:
            instrument.write(f'VSET1:{v}')
            instrument.write(f'ISET1:{i}')
            print(f"Set voltage to {v} V and current to {i} A")
        except Exception as e:
            print("Write error", f"Failed to send settings: {e}")
    else:
        print(f"No PSU detected!")

def getLiveReadings(instrument):
    voltage, current = None, None
    try:
        voltage = float(instrument.query('VOUT1?').strip())
        current = float(instrument.query('IOUT1?').strip())
        # print("Voltage reading: " + voltage)    
        # print("Current reading: " + current)
    except visa.VisaIOError:
        print(f"VISA error reading from instrument: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return voltage, current

def onClose(app):
    if instrument:
        try:
            instrument.close()
        except Exception:
            pass
    app.destroy()

def guiSetup():
    def handleLiveReadings():
        if instrument:
            voltage, current = getLiveReadings(instrument)
        if voltage is not None and current is not None:
            getVoltageLabel.configure(text=f"Voltage: {voltage} V")
            getCurrentLabel.configure(text=f"Current: {current} A")
        else:
            getVoltageLabel.configure(text="Voltage: Error")
            getCurrentLabel.configure(text="Current: Error")
            return  # stop polling on error
        # Recursively update every second
        app.after(1000, handleLiveReadings) 

    # GUI setup
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("PSU Control")
    app.geometry("380x380")
    app.resizable(False, False)

    mainFrame = ctk.CTkFrame(app)
    mainFrame.pack(padx=10, pady=10, fill="both", expand=True)

    # Resource selection dropdown
    psuControlLabel = ctk.CTkLabel(mainFrame, text="PSU Control", font=ctk.CTkFont(size=16, weight="bold"))
    psuControlLabel.grid(row=0, column=0, sticky='w', padx=(5, 0), pady=(5, 0))
    labelSelect = ctk.CTkLabel(mainFrame, text="Set PSU instrument:")
    labelSelect.grid(row=1, column=0, sticky='w', padx=(5, 0), pady=(5, 0))

    availableResources = rm.list_resources()
    selectedResource = ctk.StringVar(value="Select a power supply...")

    dropdown = ctk.CTkOptionMenu(
        mainFrame,
        variable=selectedResource,
        values=list(availableResources),
        command=connectToResource
    )
    dropdown.grid(row=1, column=1, columnspan=2, sticky='ew', padx=5, pady=5)

    # PSU controls
    label = ctk.CTkLabel(mainFrame, text="PSU Enable:", width=50)
    label.grid(row=2, column=0, sticky='w', padx=5, pady=(4, 8))
    #current_label.grid(row=6, column=0, sticky='w', padx=5, pady=(4, 8))

    # Lambda functions prevent it from running when initialised, only when clicked
    onButton = ctk.CTkButton(mainFrame, text="ON", command=lambda: psuEnable(True), fg_color="green", hover_color="#006400", width=60)
    onButton.grid(row=2, column=1, padx=10, pady=(10, 5))

    offButton = ctk.CTkButton(mainFrame, text="OFF", command=lambda: psuEnable(False), fg_color="red", hover_color="#922525", width=60)
    offButton.grid(row=2, column=2, padx=10, pady=(10, 5))

    # Voltage and Current inputs
    voltageVar = ctk.StringVar(value="0.0")
    currentVar = ctk.StringVar(value="0.0")

    setParametersLabel = ctk.CTkLabel(mainFrame, text="Set Parameters", font=ctk.CTkFont(size=16, weight="bold"))
    setParametersLabel.grid(row=3, column=0, sticky='w', padx=5, pady=(8, 4))

    setVoltageLabel = ctk.CTkLabel(mainFrame, text="Voltage (V):")
    setVoltageLabel.grid(row=4, column=0, sticky='w', padx=5, pady=(8, 4))
    setVoltageEntry = ctk.CTkEntry(mainFrame, textvariable=voltageVar, width=120)
    setVoltageEntry.grid(row=4, column=1, sticky='w', padx=5, pady=(8, 4))

    setCurrentLabel = ctk.CTkLabel(mainFrame, text="Current (A):")
    setCurrentLabel.grid(row=5, column=0, sticky='w', padx=5, pady=(4, 8))
    setCurrentEntry = ctk.CTkEntry(mainFrame, textvariable=currentVar, width=120)
    setCurrentEntry.grid(row=5, column=1, sticky='w', padx=5, pady=(4, 8))

    # Set button to apply settings (spans the two rows)
    setButton = ctk.CTkButton(mainFrame, text="Set", command=lambda: setVoltageCurrent(voltageVar, currentVar), width=80)
    setButton.grid(row=4, column=2, rowspan=2, padx=10, pady=8)

    mainFrame.columnconfigure((0, 1, 2), weight=1)

    # Voltage and Current outputs
    getParametersLabel = ctk.CTkLabel(mainFrame, text="Live Output", font=ctk.CTkFont(size=16, weight="bold"))
    getParametersLabel.grid(row=6, column=0, sticky='w', padx=5, pady=(8, 4))

    getVoltageLabel = ctk.CTkLabel(mainFrame, text="Voltage (V):")
    getVoltageLabel.grid(row=7, column=0, sticky='w', padx=5, pady=(8, 4))

    getCurrentLabel = ctk.CTkLabel(mainFrame, text="Current (A):")
    getCurrentLabel.grid(row=8, column=0, sticky='w', padx=5, pady=(4, 8))

    # Bind Enter/Return key to submit from either entry
    setVoltageEntry.bind("<Return>", lambda e: setVoltageCurrent(voltageVar, currentVar))
    setCurrentEntry.bind("<Return>", lambda e: setVoltageCurrent(voltageVar, currentVar))

    # Recursive!
    readButton = ctk.CTkButton(mainFrame, text="Read", command=handleLiveReadings, width=80)
    readButton.grid(row=7, column=2, rowspan=2, padx=10, pady=8)

    app.protocol("WM_DELETE_WINDOW", lambda: onClose(app))
    app.mainloop()

if __name__ == "__main__":
    # Setup and run
    guiSetup() 