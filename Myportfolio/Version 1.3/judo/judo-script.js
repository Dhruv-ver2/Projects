document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('judo-background-canvas');
    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationFrameId;

    // Helper to get theme colors from CSS variables
    const getThemeColor = (variable) => getComputedStyle(document.body).getPropertyValue(variable).trim();

    class Particle {
        constructor(x, y, size, color) {
            this.x = x;
            this.y = y;
            this.size = size;
            this.color = color;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.fill();
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
            this.draw();
        }
    }

    function initCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        particles = [];
        
        // Use the accent color for particles
        const particleColor = getThemeColor('--judo-accent');
        const numberOfParticles = (canvas.width * canvas.height) / 15000;

        for (let i = 0; i < numberOfParticles; i++) {
            const size = Math.random() * 2 + 1;
            const x = Math.random() * canvas.width;
            const y = Math.random() * canvas.height;
            particles.push(new Particle(x, y, size, particleColor));
        }
    }

    function connectParticles() {
        // Use the glow variable for lines with low opacity
        const lineColor = getThemeColor('--judo-glow');
        for (let a = 0; a < particles.length; a++) {
            for (let b = a + 1; b < particles.length; b++) {
                const dx = particles[a].x - particles[b].x;
                const dy = particles[a].y - particles[b].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 150) {
                    ctx.strokeStyle = lineColor;
                    ctx.lineWidth = 1 - (distance / 150);
                    ctx.beginPath();
                    ctx.moveTo(particles[a].x, particles[a].y);
                    ctx.lineTo(particles[b].x, particles[b].y);
                    ctx.stroke();
                }
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        connectParticles();
        particles.forEach(p => p.update());
        animationFrameId = requestAnimationFrame(animate);
    }

    function startAnimation() {
        if (animationFrameId) cancelAnimationFrame(animationFrameId);
        initCanvas();
        animate();
    }

    // Initialize
    startAnimation();

    // Re-initialize on window resize or theme change
    window.addEventListener('resize', startAnimation);
    
    // Listen for theme option clicks to refresh colors
    document.querySelectorAll('.theme-option-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // Short delay to allow CSS variables to update
            setTimeout(startAnimation, 100);
        });
    });
});