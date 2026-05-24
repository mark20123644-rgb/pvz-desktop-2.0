// Меню выбора уровня при нажатии "Играть"

let levelSelectorModal = null;

function showLevelSelector() {
    // Создаём модальное окно
    if (levelSelectorModal) {
        levelSelectorModal.style.display = 'flex';
        return;
    }
    
    levelSelectorModal = document.createElement('div');
    levelSelectorModal.id = 'level-selector-modal';
    levelSelectorModal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.85);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        backdrop-filter: blur(5px);
    `;
    
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: linear-gradient(135deg, #1a2a1a, #0d1a0d);
        border: 3px solid #5cb85c;
        border-radius: 20px;
        padding: 30px 40px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,0.7);
        animation: modal-appear 0.3s ease-out;
    `;
    
    modalContent.innerHTML = `
        <style>
            @keyframes modal-appear {
                from { transform: scale(0.8); opacity: 0; }
                to { transform: scale(1); opacity: 1; }
            }
            .level-btn {
                font-family: 'Press Start 2P', monospace;
                background: linear-gradient(135deg, #2d6a2d, #3d8c3d);
                border: 2px solid #5cb85c;
                color: white;
                padding: 12px 30px;
                margin: 10px;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.2s;
                border-radius: 8px;
            }
            .level-btn:hover {
                transform: scale(1.05);
                background: linear-gradient(135deg, #3d8c3d, #5cb85c);
                box-shadow: 0 0 15px rgba(92,184,92,0.5);
            }
            .level-btn.random {
                background: linear-gradient(135deg, #9b59b6, #8e44ad);
                border-color: #ffd700;
            }
            .level-btn.random:hover {
                box-shadow: 0 0 15px rgba(155,89,182,0.5);
            }
            .level-btn.close {
                background: linear-gradient(135deg, #6a2d2d, #8c3d3d);
                border-color: #e74c3c;
            }
            .level-title {
                font-family: 'Press Start 2P', monospace;
                font-size: 18px;
                color: #ffd700;
                margin-bottom: 20px;
            }
            .level-list {
                max-height: 400px;
                overflow-y: auto;
                margin: 15px 0;
                padding: 5px;
            }
            .level-item {
                background: rgba(0,0,0,0.5);
                border: 1px solid #5cb85c;
                border-radius: 5px;
                padding: 8px 15px;
                margin: 5px;
                cursor: pointer;
                transition: all 0.2s;
                font-family: monospace;
                font-size: 12px;
            }
            .level-item:hover {
                background: rgba(92,184,92,0.3);
                transform: translateX(5px);
            }
        </style>
        <div class="level-title">🎮 ВЫБОР УРОВНЯ 🎮</div>
        <button class="level-btn random" id="random-level-btn">🎲 РАНДОМНЫЙ УРОВЕНЬ</button>
        <div class="level-list" id="custom-levels-list">
            <div style="color:#aaa; padding:10px;">Загрузка уровней...</div>
        </div>
    `;
    
    levelSelectorModal.appendChild(modalContent);
    document.body.appendChild(levelSelectorModal);
    
    // Загружаем список кастомных уровней
    fetch('/api/custom_waves')
        .then(r => r.json())
        .then(data => {
            const levels = data.waves || [];
            const levelList = document.getElementById('custom-levels-list');
            if (levels.length === 0) {
                levelList.innerHTML = '<div style="color:#aaa; padding:10px;">❌ Нет кастомных уровней</div>';
            } else {
                levelList.innerHTML = '';
                levels.forEach(level => {
                    const item = document.createElement('div');
                    item.className = 'level-item';
                    item.textContent = `📁 ${level.name || level._filename}`;
                    item.onclick = () => startCustomLevel(level);
                    levelList.appendChild(item);
                });
            }
        })
        .catch(() => {
            document.getElementById('custom-levels-list').innerHTML = '<div style="color:#e74c3c; padding:10px;">⚠️ Ошибка загрузки</div>';
        });
    
    document.getElementById('random-level-btn').onclick = startRandomLevel;
    document.getElementById('close-level-selector').onclick = () => {
        levelSelectorModal.style.display = 'none';
    };
    
    // Закрытие по клику вне окна
    levelSelectorModal.onclick = (e) => {
        if (e.target === levelSelectorModal) {
            levelSelectorModal.style.display = 'none';
        }
    };
}

// Запуск рандомного уровня (без босса)

// Функция для рандомного уровня - убираем ограничение растений
function startRandomLevel() {
    fetch('/api/custom_waves')
        .then(r => r.json())
        .then(data => {
            let levels = data.waves || [];
            // Фильтруем уровни, чтобы исключить босса "ваша смерть" в волнах
            levels = levels.filter(level => {
                // Проверяем, есть ли в волнах босс
                const waves = level.waves || [];
                for (const wave of waves) {
                    const zombies = wave.zombies || [];
                    for (const z of zombies) {
                        if (z.type === 'your_death') {
                            return false;
                        }
                    }
                }
                return true;
            });
            
            if (levels.length === 0) {
                alert('❌ Нет подходящих уровней для рандома');
                return;
            }
            
            const randomLevel = levels[Math.floor(Math.random() * levels.length)];
            
            // Убираем ограничение растений в уровне
            randomLevel.plants = null;  // null = все растения
            randomLevel.lawnmowers = true;
            
            startCustomLevel(randomLevel);
        })
        .catch(() => alert('Ошибка загрузки уровней'));
}


// Запуск выбранного уровня
function startCustomLevel(level) {
    if (levelSelectorModal) {
        levelSelectorModal.style.display = 'none';
    }
    
    // Запускаем уровень через Game
    if (window.Game && Game.startCustomWave) {
        Game.startCustomWave(level);
    } else {
        console.error('Game.startCustomWave not found');
        alert('Ошибка запуска уровня');
    }
}

// Перехватываем кнопку "Играть"
document.addEventListener('DOMContentLoaded', () => {
    const playBtn = document.getElementById('btn-play');
    if (playBtn) {
        const originalClick = playBtn.onclick;
        playBtn.onclick = (e) => {
            e.preventDefault();
            showLevelSelector();
        };
    }
});

console.log('✅ Меню выбора уровня загружено! Рандом без босса');
