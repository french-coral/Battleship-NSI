// Select the grid container
const gridContainer = document.querySelector('.grid-container');

// Number of tiles (8x8 grid = 64 buttons)
const gridSize = 8 * 8;

// Create buttons and add them to the grid
const buttons = [];
let clickedTilesCount = 0;

for (let i = 0; i < gridSize; i++) {
  const button = document.createElement('button');
  button.classList.add('grid-item');
  button.textContent = ""; // Remove label if not needed

  // Add click event to change color on left click
  button.addEventListener('click', (event) => {
    if (event.button === 0) { // Left-click
      if (button.style.backgroundColor === 'rgb(56, 182, 255)') { // Check if the tile is already blue
        button.style.backgroundColor = ''; // Reset to original color

        // Reset adjacent tiles
        const row = Math.floor(i / 8);
        const col = i % 8;

        // Reset left tile
        if (col > 0) {
          buttons[i - 1].style.backgroundColor = '';
        }
        // Reset right tile
        if (col < 7) {
          buttons[i + 1].style.backgroundColor = '';
        }
        // Reset top tile
        if (row > 0) {
          buttons[i - 8].style.backgroundColor = '';
        }
        // Reset bottom tile
        if (row < 7) {
          buttons[i + 8].style.backgroundColor = '';
        }
      } else {
        button.style.backgroundColor = '#38b6ff'; // Set color to blue
        clickedTilesCount++; // Increment the counter

        // Check if 9 tiles are clicked
        if (clickedTilesCount === 12) {
          buttons.forEach(btn => {
            if (btn.style.backgroundColor !== 'rgb(56, 182, 255)') { // Check if the tile is not blue
              btn.style.backgroundColor = '#7ed957'; // Light_green color
            }
          });
        }
      }
    }
  });

  gridContainer.appendChild(button);
  buttons.push(button);
}
