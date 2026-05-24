// Версия игры 2.0
const GAME_VERSION = '2.0.0';

// Обновляем отображение версии везде
document.addEventListener('DOMContentLoaded', function() {
    const versionElements = document.querySelectorAll('.menu-version, .version-display');
    versionElements.forEach(el => {
        if (el) el.textContent = `v${GAME_VERSION}`;
    });
    
    // Обновляем заголовок окна
    document.title = `Plants VS Zombies Desktop v${GAME_VERSION}`;
    
    console.log(`🎮 PvZ Desktop v${GAME_VERSION} - Антивирус против босса!`);
});
