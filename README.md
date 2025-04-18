# Microsoft Code Redeemer

![Microsoft](https://img.shields.io/badge/Microsoft-0078D4?style=for-the-badge&logo=microsoft&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)

An advanced automation tool designed to simplify the process of redeeming Microsoft promotional codes in batches. This tool uses web automation with Selenium to efficiently process multiple codes, saving time and reducing manual effort.

## 🚀 Features

- **Batch Code Processing** - Redeem multiple promotional codes automatically
- **User Profile Integration** - Uses your existing Chrome profile for authentication
- **Detailed Logging** - Comprehensive logs to track the redemption process
- **Error Handling** - Automatically detects and records problematic codes
- **Progress Tracking** - Real-time visual progress indicators
- **Smart Authentication** - Detects and waits for authentication flows to complete

## 📋 Requirements

- Python 3.6+
- Google Chrome Browser
- Windows OS (optimized for Windows environment)
- Dependencies listed in `requirements.txt`

## 🔧 Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```
3. Or simply run `start.bat` which will handle the installation automatically

## 💻 Usage

1. Add your Microsoft promotional codes to `codigos.txt` (one code per line)
2. Run the application using `start.bat`
3. Select option 1 to start the code redemption process
4. Follow on-screen instructions to complete authentication if needed
5. The program will automatically process all codes

## ⚙️ Configuration

The program is pre-configured to work with Windows and Chrome. The main configuration points are:

- Chrome profile path in `main.py` (currently set to use Profile 17)
- Logging level and format in `main.py`
- Timeout settings for web interactions

## 📊 Logging

The application maintains detailed logs in `microsoft_redeem.log`, tracking:

- Authentication steps
- Code redemption attempts
- Success/failure status
- Error messages

Codes that fail to redeem are saved to `codigos_nao_resgatados.txt` with reasons for failure.

## 🛠️ Technical Details

- Uses Selenium for browser automation
- Implements frame detection for handling complex Microsoft page structures
- Includes JavaScript injection capabilities for challenging UI interactions
- Smart input element detection with multiple selector strategies
- Resource management to prevent Chrome process accumulation

## ⚠️ Disclaimer

This tool is provided for educational purposes only. Use at your own risk and responsibility. The author is not responsible for any misuse or violations of Microsoft's terms of service.

## 📝 License

Copyright © 2025 Gabriel

---

*Built with 💙 and code*
