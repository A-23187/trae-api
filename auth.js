// ==UserScript==
// @name         获取并保存 Trae 登录凭证
// @namespace    a23187.cn
// @version      0.1.0
// @description  获取并保存 Trae 登录凭证
// @author       A23187
// @match        https://www.trae.ai/authorization?*
// @match        https://www.trae.com.cn/authorization?*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=trae.ai
// @grant        GM_setClipboard
// @license      MIT
// ==/UserScript==

(function () {
    'use strict';
    async function getRefreshToken(clientId) {
        const resp = await fetch('https://www.trae.ai/cloudide/api/v3/trae/oauth/GetRefreshToken', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ clientID: clientId }),
        }).then((resp) => resp.json());
        return resp.Result.RefreshToken;
    }
    async function exchangeToken(clientId, refreshToken) {
        const resp = await fetch('https://api-sg-central.trae.ai/cloudide/api/v3/trae/oauth/ExchangeToken', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ClientID: clientId, RefreshToken: refreshToken, ClientSecret: '-', UserID: '',
            }),
        }).then((resp) => resp.json());
        return resp.Result.Token;
    }
    const id = setInterval(() => {
        const mainTitleDiv = document.getElementsByClassName('main-title')[0];
        if (mainTitleDiv === undefined || mainTitleDiv?.innerText !== 'Login Successful') {
            return;
        }
        const saveTokenBtn = document.createElement('button');
        mainTitleDiv.parentElement.appendChild(saveTokenBtn);
        saveTokenBtn.innerText = 'Save token to clipboard';
        saveTokenBtn.onclick = async () => {
            const params = new URLSearchParams(document.location.search);
            const clientId = params.get('client_id');
            const refreshToken = await getRefreshToken(clientId);
            const token = await exchangeToken(clientId, refreshToken);
            GM_setClipboard(`
TRAE_APP_ID = "6eefa01c-1036-4c7e-9ca5-d891f63bfcd8"
TRAE_DEVICE_BRAND = "${params.get('x_device_brand')}"
TRAE_DEVICE_CPU = "Intel"
TRAE_DEVICE_ID = "${params.get('x_device_id')}"
TRAE_DEVICE_TYPE = "${params.get('x_device_type')}"
TRAE_IDE_TOKEN = "${token}"
TRAE_IDE_VERSION = ""
TRAE_IDE_VERSION_CODE = ""
TRAE_IDE_VERSION_TYPE = ""
TRAE_MACHINE_ID = "${params.get('x_machine_id')}"
TRAE_OS_VERSION = "${params.get('x_os_version')}"`, 'text', () => alert('已复制'));
        };
        clearInterval(id);
    }, 1000);
})();
