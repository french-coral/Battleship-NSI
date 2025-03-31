// Select the grid container
const gridContainer = document.querySelector('.grid-container');

// Number of tiles (8x8 grid = 64 buttons)
const gridSize = 8 * 8;

// Variable to keep track of the number of colored tiles
let coloredTiles = 0;

// Variables to track the state of specific tiles
let tile43Clicked = false;
let tile44Clicked = false;
let tile45Clicked = false;

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
      button.classList.add('blinking'); // Add blinking class
      setTimeout(() => {
        button.classList.remove('blinking'); // Remove blinking class
        if (i === 42) {
          button.style.backgroundColor = 'red'; // Set color to red for tile 43
          tile43Clicked = true;
        } else if (i === 43) {
          button.style.backgroundColor = 'red'; // Set color to red for tile 44
          tile44Clicked = true;
        } else if (i === 44) {
          button.style.backgroundColor = 'red'; // Set color to red for tile 45
          tile45Clicked = true;
        } else {
          button.style.backgroundColor = '#ffa338'; // Set color to orange for other tiles
        }
        coloredTiles++; // Increment the counter

        // Check if all three specific tiles have been clicked
        if (tile43Clicked && tile44Clicked && tile45Clicked) {
          document.querySelectorAll('.grid-item').forEach((btn, index) => {
            if (index === 42 || index === 43 || index === 44) {
              btn.classList.add('slow-blinking'); // Add slow blinking class
              setTimeout(() => {
                btn.classList.remove('slow-blinking'); // Remove slow blinking class
                btn.style.backgroundColor = '#7ed957'; // Change color to green
              }, 2000); // Delay of 2 seconds
            }
          });
        }
      }, 500); // Delay of 500 milliseconds
    }
  });

  gridContainer.appendChild(button);
}

// Add CSS for blinking effect
const style = document.createElement('style');
style.textContent = `
  .blinking {
    animation: blink-animation 0.1s steps(5, start) infinite;
  }
  @keyframes blink-animation {
    to {
      visibility: hidden;
    }
  }
  .slow-blinking {
    animation: slow-blink-animation 1s steps(2, start) infinite;
  }
  @keyframes slow-blink-animation {
    50% {
      background-color: #e8e8e8;;
    }
  }
`;
document.head.appendChild(style);