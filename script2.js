// Select the grid container
const gridContainer = document.querySelector('.grid-container');

// Number of tiles (8x8 grid = 64 buttons)
const gridSize = 8 * 8;

// Variable to keep track of the number of colored tiles
let coloredTiles = 0;

// Create buttons and add them to the grid
for (let i = 0; i < gridSize; i++) {
  const button = document.createElement('button');
  button.classList.add('grid-item');
  button.textContent = ""; // Optional: Label each tile if needed

  // Add click event to change color on left click
  button.addEventListener('click', () => {
    // Check if the tile isn't already blue
    if (!button.classList.contains('clicked')) {
      button.classList.add('clicked');
      button.style.backgroundColor = '#ffa338';
      coloredTiles++; // Increment the counter

    }
  });

  gridContainer.appendChild(button);
} 