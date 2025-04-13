import os
import sys
import subprocess
import colorama
from colorama import Fore, Style
import time

def check_and_install_dependencies():
    try:
        with open('requirements.txt', 'r') as file:
            required = file.read().splitlines()
        
        print("Verificando dependências...")
        
        try:
            import pip
        except ImportError:
            print("Pip não encontrado. Instalando pip...")
            subprocess.check_call([sys.executable, "-m", "ensurepip"])
        
        for package in required:
            if package:
                try:
                    __import__(package.split('>=')[0])
                except ImportError:
                    print(f"Instalando {package}...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        print("Todas as dependências estão instaladas!")
        
    except Exception as e:
        print(f"Erro ao verificar/instalar dependências: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_and_install_dependencies()

import psutil
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='microsoft_redeem.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

selenium_logger = logging.getLogger('selenium')
selenium_logger.setLevel(logging.WARNING)
urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.WARNING)

def kill_chrome_processes():
    try:
        if os.name == 'nt':
            subprocess.run("taskkill /f /im chrome.exe", shell=True)
        else:
            os.system("pkill -f chrome")
    except Exception as e:
        logger.warning(f"Erro ao tentar matar processos Chrome: {e}")

def apply_cookies(driver, cookies):
    if not cookies:
        return False
    
    try:
        driver.get("https://microsoft.com")
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                logger.warning(f"Erro ao adicionar cookie: {e}")
        return True
    except Exception as e:
        logger.error(f"Erro ao aplicar cookies: {e}")
        return False

def setup_driver():
    try:
        chrome_options = Options()
        
        profile_path = "C:\\Users\\gabri\\AppData\\Local\\Google\\Chrome\\User Data"
        chrome_options.add_argument(f"user-data-dir={profile_path}")
        chrome_options.add_argument("profile-directory=Profile 17")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--dns-prefetch-disable")
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
        chrome_options.add_experimental_option("detach", True)
        
        os.environ['WDM_LOG'] = '0'
        os.environ['WDM_LOG_LEVEL'] = '0'
        service = Service(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)
        
        return driver
                
    except Exception as e:
        logger.error(f"Erro ao configurar o Chrome WebDriver: {e}")
        raise

def read_js_script():
    try:
        with open('inject.js', 'r') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Erro ao ler arquivo JavaScript: {e}")
        return None

def wait_for_page_load(driver, timeout=30):
    try:
        return WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
    except TimeoutException:
        return False

def wait_for_frame_and_switch(driver, timeout=30):
    try:
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        if frames:
            for frame in frames:
                try:
                    driver.switch_to.frame(frame)
                    if driver.find_elements(By.TAG_NAME, "input"):
                        logger.info("Frame com input encontrado")
                        return True
                except:
                    pass
                driver.switch_to.default_content()
        return False
    except Exception as e:
        logger.warning(f"Erro ao procurar frames: {e}")
        return False

def find_and_interact_with_input(driver, code):
    selectors = [
        (By.CSS_SELECTOR, "input[type='text']"),
    ]

    wait = WebDriverWait(driver, 10)
    
    wait_for_frame_and_switch(driver)
    
    for by, selector in selectors:
        try:
            logger.info(f"Tentando selector: {selector}")
            element = wait.until(
                EC.presence_of_element_located((by, selector))
            )
            
            element.click()
            element.clear()
            
            element.send_keys(code)
            
            logger.info("Código inserido com sucesso")
            return True
                    
        except Exception as e:
            logger.warning(f"Falha ao tentar selector: {e}")
            continue
    
    return False

def verify_driver_health(driver):
    try:
        driver.current_url
        return True
    except:
        return False

def wait_for_auth_complete(driver, timeout=15):
    expected_urls = [
        "redeem.microsoft.com",
        "account.microsoft.com/billing/redeem",
    ]
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_url = driver.current_url
        
        if any(url in current_url for url in expected_urls):
            logger.info(f"URL válida encontrada: {current_url}")
            return True
        elif "account.microsoft.com/auth" in current_url:
            logger.info("Aguardando autenticação...")
            time.sleep(2)
        else:
            logger.info(f"Redirecionando... URL atual: {current_url}")
            time.sleep(2)
    return False

def save_invalid_code(code, reason=""):
    filename = "codigos_nao_resgatados.txt"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(filename, 'a') as file:
            file.write(f"{timestamp} | Código: {code} | Motivo: {reason}\n")
        logger.info(f"Código inválido salvo em {filename}")
    except Exception as e:
        logger.error(f"Erro ao salvar código inválido: {e}")

def check_code_response(driver):
    try:
        time.sleep(2)
        
        error_selectors = [
            (By.XPATH, '/html/body/main/div/div/div/div/div[1]/div[2]/p/span[1]'),
            (By.CSS_SELECTOR, 'p.errorMessageText--NWPmAAeE'),
            (By.CSS_SELECTOR, 'p[role="alert"]')
        ]
        
        for by, selector in error_selectors:
            try:
                error_element = driver.find_element(by, selector)
                if error_element:
                    error_text = error_element.text
                    logger.info(f"Mensagem de erro encontrada: {error_text}")
                    return False, error_text
            except:
                continue
        
        error_texts = [
            "This code wasn't found",
            "try re-entering it",
            "Invalid characters",
            "code is damaged",
            "Get more info"
        ]
        
        page_text = driver.page_source
        for error in error_texts:
            if error in page_text:
                return False, "Código inválido ou não encontrado"
        
        success_indicators = [
            "Obrigado",
            "Thank you",
            "confirmation",
            "redeemed",
            "success"
        ]
        
        for indicator in success_indicators:
            if indicator in page_text:
                return True, ""
        
        return False, "Não foi possível confirmar o sucesso da operação"
        
    except Exception as e:
        logger.warning(f"Erro ao verificar resposta: {e}")
        return False, str(e)

def redeem_code(driver, code, progress_callback):
    try:
        progress_callback("Acessando página de resgate...")
        driver.get('https://redeem.microsoft.com/')
        
        if not wait_for_auth_complete(driver, timeout=30):
            raise Exception("Timeout esperando página de resgate")
        
        progress_callback("Inserindo código...")
        time.sleep(2)
        
        for attempt in range(2):
            if find_and_interact_with_input(driver, code):
                break
            if attempt == 1:
                raise Exception("Não foi possível encontrar o campo de entrada")
            driver.refresh()
            time.sleep(1)

        progress_callback("Confirmando código...")
        buttons = [(By.CSS_SELECTOR, 'button[type="submit"]')]
        
        for by, selector in buttons:
            try:
                button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((by, selector))
                )
                button.click()
                progress_callback("Verificando resposta...")
                
                success, message = check_code_response(driver)
                if not success:
                    progress_callback(f"Falha: {message}")
                    return False
                    
                break
            except:
                continue
        
        progress_callback("Código processado com sucesso")
        return True
        
    except Exception as e:
        progress_callback(f"Erro: {str(e)}")
        return False

def read_codes_from_file(filepath):
    try:
        with open(filepath, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        logger.error(f"Erro ao ler códigos do arquivo: {e}")
        return []

def print_banner():
    banner = """
███╗   ███╗██╗ ██████╗██████╗  ██████╗ ███████╗ ██████╗ ███████╗████████╗
████╗ ████║██║██╔════╝██╔══██╗██╔═══██╗██╔════╝██╔═══██╗██╔════╝╚══██╔══╝
██╔████╔██║██║██║     ██████╔╝██║   ██║███████╗██║   ██║█████╗     ██║   
██║╚██╔╝██║██║██║     ██╔══██╗██║   ██║╚════██║██║   ██║██╔══╝     ██║   
██║ ╚═╝ ██║██║╚██████╗██║  ██║╚██████╔╝███████║╚██████╔╝██║        ██║   
╚═╝     ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝        ╚═╝   
                                                                           
██████╗ ███████╗██████╗ ███████╗███████╗███╗   ███╗██╗███████╗           
██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝████╗ ████║██║██╔════╝           
██████╔╝█████╗  ██║  ██║█████╗  █████╗  ██╔████╔██║██║███████╗           
██╔══██╗██╔══╝  ██║  ██║██╔══╝  ██╔══╝  ██║╚██╔╝██║██║╚════██║           
██║  ██║███████╗██████╔╝███████╗███████╗██║ ╚═╝ ██║██║███████║           
╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝╚══════╝╚═╝     ╚═╝╚═╝╚══════╝           
    """
    print("\033[94m" + banner + "\033[0m")
    print("\n" + "="*80 + "\n")

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def update_progress_display(total_codes, current_code, code_masked, progress_desc, success_count, fail_count):
    clear_console()
    print_banner()
    
    print(f"\n{Fore.CYAN}Progresso Geral: {current_code}/{total_codes} códigos{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Sucesso: {success_count} {Fore.RED}Falhas: {fail_count}{Style.RESET_ALL}")
    print("\n" + "="*80 + "\n")
    
    print(f"Processando: {Fore.YELLOW}{code_masked}{Style.RESET_ALL}")
    print(f"Status: {progress_desc}")
    print("\n" + "-"*80 + "\n")

def main():
    colorama.init()
    driver = None
    try:
        clear_console()
        print_banner()
        
        codigos = read_codes_from_file('codigos.txt')
        if not codigos:
            print(f"{Fore.RED}Nenhum código encontrado para processar{Style.RESET_ALL}")
            return
        
        driver = setup_driver()
        success_count = fail_count = 0
        total_codes = len(codigos)
        
        for i, codigo in enumerate(codigos, 1):
            codigo_mascarado = f"{codigo[:5]}...{codigo[-5:]}"
            
            with tqdm(total=100, 
                     desc="Progresso", 
                     bar_format="{desc}: {percentage:3.0f}%|{bar}| {postfix}",
                     colour="blue",
                     leave=False) as pbar:
                
                def update_progress(desc):
                    pbar.set_description(desc)
                    update_progress_display(
                        total_codes, i, codigo_mascarado,
                        desc, success_count, fail_count
                    )
                
                success = redeem_code(driver, codigo, update_progress)
                
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                
                pbar.update(100)
                final_status = f"{Fore.GREEN}✓ Sucesso{Style.RESET_ALL}" if success else f"{Fore.RED}✗ Falha{Style.RESET_ALL}"
                update_progress_display(
                    total_codes, i, codigo_mascarado,
                    final_status, success_count, fail_count
                )
                time.sleep(1)
        
        clear_console()
        print_banner()
        print(f"\n{Fore.CYAN}Processamento concluído!{Style.RESET_ALL}")
        print(f"\nResultados finais:")
        print(f"{Fore.GREEN}Sucessos: {success_count}{Style.RESET_ALL}")
        print(f"{Fore.RED}Falhas: {fail_count}{Style.RESET_ALL}")
        print("\nPressione ENTER para sair...")
        input()
        
    except Exception as e:
        logger.error(f"Erro: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
