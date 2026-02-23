<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
    <title>Flappy Bird Pro Sound Edition</title>
    <style>
        * { margin: 0; padding: 0; overflow: hidden; }
        body { background: #4ec0ca; touch-action: manipulation; }
        canvas { display: block; }
        #score {
            position: absolute; top: 10%; width: 100%;
            text-align: center; color: white; font-family: 'Arial Black', sans-serif;
            font-size: 50px; text-shadow: 3px 3px 0 #000; pointer-events: none; z-index: 10;
        }
    </style>
</head>
<body>
    <div id="score">0</div>
    <canvas id="c"></canvas>

    <script>
        const canvas = document.getElementById("c");
        const ctx = canvas.getContext("2d");
        const scoreEl = document.getElementById("score");

        // --- SOUND ENGINE (Web Audio API) ---
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        
        function playSound(freq, type, duration, vol) {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(vol, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + duration);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + duration);
        }

        const sounds = {
            flap: () => playSound(400, 'triangle', 0.1, 0.1),
            score: () => playSound(880, 'square', 0.2, 0.05),
            dead: () => {
                playSound(150, 'sawtooth', 0.1, 0.2);
                setTimeout(() => playSound(100, 'sawtooth', 0.3, 0.2), 100);
            }
        };

        // --- GAME LOGIC ---
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resize);
        resize();

        let bird = { x: 50, y: 300, radius: 18, v: 0, g: 0.22, jump: -5.5, angle: 0 };
        let pipes = [];
        let score = 0;
        let frame = 0;
        let gameState = "START"; 

        function drawBird() {
            ctx.save();
            ctx.translate(bird.x, bird.y);
            bird.angle = Math.min(Math.PI / 4, Math.max(-Math.PI / 4, bird.v * 0.1));
            ctx.rotate(bird.angle);
            // Body
            ctx.fillStyle = "#f7e61c";
            ctx.beginPath(); ctx.arc(0, 0, bird.radius, 0, Math.PI * 2); ctx.fill();
            ctx.strokeStyle = "black"; ctx.lineWidth = 2; ctx.stroke();
            // Eye & Beak
            ctx.fillStyle = "white"; ctx.beginPath(); ctx.arc(8, -6, 7, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
            ctx.fillStyle = "black"; ctx.beginPath(); ctx.arc(10, -6, 3, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#f75b1c"; ctx.beginPath(); ctx.moveTo(12, 2); ctx.lineTo(25, 6); ctx.lineTo(12, 10); ctx.closePath(); ctx.fill(); ctx.stroke();
            ctx.restore();
        }

        function drawPipe(x, y, width, height, isTop) {
            let grad = ctx.createLinearGradient(x, 0, x + width, 0);
            grad.addColorStop(0, "#73bf2e"); grad.addColorStop(0.5, "#9de64e"); grad.addColorStop(1, "#558022");
            ctx.fillStyle = grad;
            ctx.fillRect(x, y, width, height);
            ctx.strokeRect(x, y, width, height);
            let lipY = isTop ? y + height - 25 : y;
            ctx.fillRect(x - 5, lipY, width + 10, 25);
            ctx.strokeRect(x - 5, lipY, width + 10, 25);
        }

        function resetGame() {
            bird.y = canvas.height / 2; bird.v = 0; pipes = []; score = 0; frame = 0;
            gameState = "PLAY"; scoreEl.innerText = "0";
            if (audioCtx.state === 'suspended') audioCtx.resume();
        }

        function handleInput() {
            if (gameState === "PLAY") {
                bird.v = bird.jump;
                sounds.flap();
            } else {
                resetGame();
            }
        }

        window.addEventListener("mousedown", handleInput);
        window.addEventListener("touchstart", (e) => { e.preventDefault(); handleInput(); }, {passive: false});

        function draw() {
            ctx.fillStyle = "#4ec0ca"; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "#95e14a"; ctx.fillRect(0, canvas.height - 50, canvas.width, 50);
            ctx.fillStyle = "#ded895"; ctx.fillRect(0, canvas.height - 60, canvas.width, 10);

            if (gameState === "PLAY") {
                bird.v += bird.g;
                bird.y += bird.v;
                if (frame % 100 === 0) {
                    let gap = 160;
                    let pHeight = Math.random() * (canvas.height - 300) + 50;
                    pipes.push({ x: canvas.width, y: pHeight, gap: gap, passed: false });
                }
                for (let i = pipes.length - 1; i >= 0; i--) {
                    pipes[i].x -= 3;
                    if (bird.x + 12 > pipes[i].x && bird.x - 12 < pipes[i].x + 60) {
                        if (bird.y - 12 < pipes[i].y || bird.y + 12 > pipes[i].y + pipes[i].gap) {
                            gameState = "GAMEOVER"; sounds.dead();
                        }
                    }
                    if (!pipes[i].passed && pipes[i].x < bird.x) {
                        score++; pipes[i].passed = true; scoreEl.innerText = score; sounds.score();
                    }
                    if (pipes[i].x < -100) pipes.splice(i, 1);
                }
                if (bird.y + bird.radius > canvas.height - 60 || bird.y < 0) {
                    gameState = "GAMEOVER"; sounds.dead();
                }
                frame++;
            }

            pipes.forEach(p => {
                drawPipe(p.x, 0, 60, p.y, true);
                drawPipe(p.x, p.y + p.gap, 60, canvas.height - (p.y + p.gap), false);
            });
            drawBird();

            if (gameState !== "PLAY") {
                ctx.fillStyle = "rgba(0,0,0,0.5)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "white"; ctx.font = "bold 30px Arial"; ctx.textAlign = "center";
                ctx.fillText(gameState === "START" ? "TAP TO START" : "GAME OVER", canvas.width/2, canvas.height/2);
            }
            requestAnimationFrame(draw);
        }
        draw();
    </script>
</body>
</html>
