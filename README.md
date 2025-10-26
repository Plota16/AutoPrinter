### HOW TO BUILD
```shell
pip install poetry
pip install pyinstaller 

poetry install

# Build the executable
pyinstaller --onefile --console ^
  --add-binary ".venv/Lib/site-packages/pypdfium2_raw/pdfium.dll;." ^
  --add-data "%PYTHON_HOME%/tcl/tcl8.6;tcl8.6" ^
  --add-data "%PYTHON_HOME%/tcl/tk8.6;tk8.6" ^
  src/main.py
```

**Note:** Replace `%PYTHON_HOME%` with your Python installation path (e.g., `C:/Users/YourName/AppData/Local/Programs/Python/Python313`)

Or use the full command:
```shell
pyinstaller --onefile --console --add-binary ".venv/Lib/site-packages/pypdfium2_raw/pdfium.dll;." --add-data "C:/Users/MichalPlocki/AppData/Local/Programs/Python/Python313/tcl/tcl8.6;tcl8.6" --add-data "C:/Users/MichalPlocki/AppData/Local/Programs/Python/Python313/tcl/tk8.6;tk8.6" src/main.py
```

The executable will be created at `dist/main.exe`

### HOW TO RUN IT
```shell
.\dist\main.exe --watch "<ABSOLUTE/PATH/TO/WATCH/DIR>" --printer "Printer Name"
```

**Example:**
```shell
.\dist\main.exe --watch "C:\Users\Test\Downloads\test" --printer "EPSON 123 Series"
```

**Note:** The executable is located in the `dist` folder after building.