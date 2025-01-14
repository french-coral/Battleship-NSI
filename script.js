// Select the grid container
const gridContainer = document.querySelector('.grid-container');

// Number of tiles (8x8 grid = 64 buttons)
const gridSize = 8 * 8;

// Create buttons and add them to the grid
for (let i = 0; i < gridSize; i++) {
  const button = document.createElement('button');
  button.classList.add('grid-item');
  button.textContent = ""; // Remove label if not needed

  // Add click event to change color on left click
  button.addEventListener('click', (event) => {
    if (event.button === 0) { // Left-click
      button.style.backgroundColor = '#38b6ff';
    }
  });

  gridContainer.appendChild(button);
}
