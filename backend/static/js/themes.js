function applyHalloweenTheme() {
    removeThemes();
    document.body.classList.add('halloween-theme');
    startSpiderSpawning();
}

function applyWinterTheme() {
    removeThemes();
    document.body.classList.add('winter-theme');
    startSnowflakeSpawning();
    setTimeout(startSnowPile, 10000); // Start snow pile effect after 10 seconds
}

function removeThemes() {
    document.body.classList.remove('halloween-theme', 'winter-theme');
    document.querySelectorAll('.snowflake, .spider, .snow-pile').forEach(el => el.remove());
}

function startSpiderSpawning() {
    const spawnInterval = 2000; // Interval between each spider spawn

    function spawnSpider() {
        const spider = document.createElement('div');
        spider.classList.add('spider');

        // Set random size
        const size = Math.random() * 20 + 20; // Random size between 20px and 40px
        spider.style.width = `${size}px`;
        spider.style.height = `${size}px`;

        // Set a random position across the top of the screen
        spider.style.left = `${Math.random() * 80 + 10}%`; // Random horizontal position (10% to 90%)
        spider.style.top = '0px'; // Start at the top of the screen

        document.body.appendChild(spider);

        // Remove spider after it goes back up
        setTimeout(() => {
            spider.remove();
        }, 8000); // Adjust as needed for spider's total duration (hanging + going back up)

        // Schedule the next spider spawn with random delay
        setTimeout(spawnSpider, Math.random() * spawnInterval + spawnInterval);
    }

    // Initial spider spawn
    spawnSpider();
}

function startSnowflakeSpawning() {
    let spawnRate = 100; // Initial spawn rate in milliseconds (10 snowflakes per second)
    let timeElapsed = 0;

    function spawnSnowflake() {
        const snowflake = document.createElement('div');
        snowflake.classList.add('snowflake');

        // Set random size (small, medium, large)
        const sizeCategory = Math.random();
        if (sizeCategory < 0.3) {
            snowflake.style.width = '15px';
            snowflake.style.height = '15px';
        } else if (sizeCategory < 0.7) {
            snowflake.style.width = '25px';
            snowflake.style.height = '25px';
        } else {
            snowflake.style.width = '40px';
            snowflake.style.height = '40px';
        }

        // Set a random horizontal position for each snowflake
        snowflake.style.left = `${Math.random() * window.innerWidth}px`;

        // Append the snowflake to the document body
        document.body.appendChild(snowflake);

        // Remove snowflake once it has fallen off the screen
        setTimeout(() => {
            snowflake.remove();
        }, 5000);

        // Adjust spawn rate dynamically
        timeElapsed += spawnRate;
        if (timeElapsed >= 5000) {
            timeElapsed = 0;
            spawnRate = getRandomSpawnRate();
        }

        // Schedule the next snowflake spawn
        setTimeout(spawnSnowflake, spawnRate);
    }

    // Start the initial snowflake spawn
    spawnSnowflake();
}

function getRandomSpawnRate() {
    const rates = [100, 50, 200]; // Corresponding to 10, 20, and 5 snowflakes per second
    return rates[Math.floor(Math.random() * rates.length)];
}

function startSnowPile() {
    const snowPile = document.createElement('div');
    snowPile.classList.add('snow-pile');
    document.body.appendChild(snowPile);

    // Gradually increase the height of the snow pile over time
    let snowPileHeight = 0;
    const pileInterval = setInterval(() => {
        snowPileHeight += 2; // Increase by 2px
        snowPile.style.height = `${snowPileHeight}px`;

        // Stop growing once the pile reaches a certain height
        if (snowPileHeight >= 100) {
            clearInterval(pileInterval);
        }
    }, 200); // Adjust interval for a gradual effect
}
