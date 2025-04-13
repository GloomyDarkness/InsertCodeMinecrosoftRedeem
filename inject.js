function createKeyboardEvent(type, key, code) {
    return new KeyboardEvent(type, {
        key: key,
        code: code,
        bubbles: true,
        cancelable: true,
        composed: true,
        keyCode: key.charCodeAt(0),
        which: key.charCodeAt(0)
    });
}

function simulateKeyboardInput(element, char) {
    const keyEvents = [
        ['keydown', char, `Key${char.toUpperCase()}`],
        ['keypress', char, `Key${char.toUpperCase()}`],
        ['keyup', char, `Key${char.toUpperCase()}`]
    ];

    keyEvents.forEach(([type, key, code]) => {
        element.dispatchEvent(createKeyboardEvent(type, key, code));
    });
}

function getCssSelectors() {
    return [
        '#store-cart-root > div > div > div > div.content--XhykSwL6 > input',
        '.input--mKKIbi6U',
        'input[name="tokenString"]',
        'input[aria-label="Digitar código de 25 caracteres"]',
        'input[maxlength="29"]',
        'input[type="text"][maxlength="29"]'
    ];
}

function getXPaths() {
    return [
        '//*[@id="store-cart-root"]/div/div/div/div[1]/input',
        '//input[@class="input--mKKIbi6U"]',
        '//input[@maxlength="29"]',
        '//input[@name="tokenString"]',
        '//input[@aria-label="Digitar código de 25 caracteres"]'
    ];
}

function findElementByXPath(xpath) {
    try {
        return document.evaluate(
            xpath,
            document,
            null,
            XPathResult.FIRST_ORDERED_NODE_TYPE,
            null
        ).singleNodeValue;
    } catch (e) {
        console.warn('Erro com XPath:', xpath, e);
        return null;
    }
}

function findElementByCss(selector) {
    try {
        return document.querySelector(selector);
    } catch (e) {
        console.warn('Erro com selector CSS:', selector, e);
        return null;
    }
}

function findInputByAttributesRecursive() {
    const matchingAttributes = {
        'class': 'input--mKKIbi6U',
        'maxlength': '29',
        'name': 'tokenString',
        'type': 'text'
    };

    function checkElement(element) {
        if (element.tagName === 'INPUT') {
            for (const [attr, value] of Object.entries(matchingAttributes)) {
                if (element.getAttribute(attr) === value) {
                    return element;
                }
            }
        }
        
        for (const child of element.children) {
            const result = checkElement(child);
            if (result) return result;
        }
        
        return null;
    }

    return checkElement(document.body);
}

function waitForElement(callback) {
    let attempts = 0;
    const maxAttempts = 20;
    let observer = null;

    function cleanup() {
        if (observer) {
            observer.disconnect();
        }
    }

    return new Promise((resolve) => {
        function findElement() {
            // Tenta CSS primeiro
            for (const selector of getCssSelectors()) {
                const element = findElementByCss(selector);
                if (element) {
                    console.log('Elemento encontrado via CSS:', selector);
                    cleanup();
                    resolve(element);
                    return true;
                }
            }

            // Tenta XPath
            for (const xpath of getXPaths()) {
                const element = findElementByXPath(xpath);
                if (element) {
                    console.log('Elemento encontrado via XPath:', xpath);
                    cleanup();
                    resolve(element);
                    return true;
                }
            }

            // Tenta busca recursiva
            const element = findInputByAttributesRecursive();
            if (element) {
                console.log('Elemento encontrado via busca recursiva');
                cleanup();
                resolve(element);
                return true;
            }

            attempts++;
            if (attempts >= maxAttempts) {
                console.error('Elemento não encontrado após', maxAttempts, 'tentativas');
                cleanup();
                resolve(null);
                return true;
            }

            return false;
        }

        // Configura MutationObserver para detectar mudanças na DOM
        observer = new MutationObserver(() => {
            if (findElement()) {
                observer.disconnect();
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // Primeira tentativa imediata
        if (!findElement()) {
            // Se não encontrar, continua tentando
            const interval = setInterval(() => {
                if (findElement() || attempts >= maxAttempts) {
                    clearInterval(interval);
                }
            }, 1000);
        }
    });
}

async function injectCode(code) {
    console.log('Iniciando busca do elemento...');
    const element = await waitForElement();

    if (!element) {
        console.error('Elemento não encontrado');
        return false;
    }

    try {
        console.log('Elemento encontrado, inserindo código...');
        
        // Força visibilidade e interatividade
        element.style.display = 'block';
        element.style.visibility = 'visible';
        element.disabled = false;
        element.readOnly = false;

        // Foca e limpa
        element.focus();
        element.value = '';
        
        // Insere o código
        element.value = code;

        // Dispara eventos
        ['input', 'change', 'blur', 'focus'].forEach(eventType => {
            element.dispatchEvent(new Event(eventType, { bubbles: true }));
        });

        console.log('Código inserido com sucesso');
        return true;
    } catch (e) {
        console.error('Erro ao manipular elemento:', e);
        return false;
    }
}

// Função para teste
async function test(code) {
    console.log('Iniciando teste...');
    const result = await injectCode(code);
    
    if (result) {
        // Tenta clicar no botão após sucesso
        setTimeout(() => {
            const button = document.querySelector('button[type="submit"]') ||
                          Array.from(document.getElementsByTagName('button'))
                               .find(b => b.textContent.includes('Seguinte'));
            if (button) {
                button.click();
                console.log('Botão clicado');
            }
        }, 1000);
    }
    
    return result;
}

// Exposição global para debug
window.debugFindElement = () => waitForElement();
