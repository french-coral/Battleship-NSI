// Select the grid container
const gridContainer = document.querySelector('.grid-container');

// Number of tiles (8x8 grid = 64 buttons)
const gridSize = 8 * 8;

// Variables to track the state of specific tile groups
let group1Clicked = [false, false]; // (10, 11)
let group2Clicked = [false, false, false, false]; // (8, 16, 24, 32)
let group3Clicked = [false, false, false]; // (43, 44, 45)
const blueTiles = [9, 10, 7, 15, 23, 31, 42, 43, 44];
const buttons = [];

// Create buttons and add them to the grid
for (let i = 0; i < gridSize; i++) {
  const button = document.createElement('button');
  button.classList.add('grid-item');
  button.textContent = ""; // Remove label if not needed

  // Set initial color for specific tiles
  if (blueTiles.includes(i)) {
    button.style.backgroundColor = '#38b6ff'; // Set color to blue
  }

  // Add click event to change color on left click
  button.addEventListener('click', () => {
    // Check if the tile isn't already blue
    if (!button.classList.contains('clicked')) {
      button.classList.add('clicked');
      button.classList.add('blinking'); // Add blinking class
      setTimeout(() => {
        button.classList.remove('blinking'); // Remove blinking class
        if (blueTiles.includes(i)) {
          button.style.backgroundColor = 'orange';
        } else {
          button.style.backgroundColor = 'gray'; // Change to gray
        }

        // Update the state of the clicked tile in the respective group
        if (i === 9) group1Clicked[0] = true;
        if (i === 10) group1Clicked[1] = true;
        if (i === 7) group2Clicked[0] = true;
        if (i === 15) group2Clicked[1] = true;
        if (i === 23) group2Clicked[2] = true;
        if (i === 31) group2Clicked[3] = true;
        if (i === 42) group3Clicked[0] = true;
        if (i === 43) group3Clicked[1] = true;
        if (i === 44) group3Clicked[2] = true;

        // Check if all tiles in each group are clicked
        if (group1Clicked.every(Boolean)) {
          [9, 10].forEach(index => {
            document.querySelectorAll('.grid-item')[index].style.backgroundColor = 'red';
          });
        }
        if (group2Clicked.every(Boolean)) {
          [7, 15, 23, 31].forEach(index => {
            document.querySelectorAll('.grid-item')[index].style.backgroundColor = 'red';
          });
        }
        if (group3Clicked.every(Boolean)) {
          [42, 43, 44].forEach(index => {
            document.querySelectorAll('.grid-item')[index].style.backgroundColor = 'red';
          });
        }

        // Check if all previously blue tiles are red
        if (blueTiles.every(index => document.querySelectorAll('.grid-item')[index].style.backgroundColor === 'red')) {
          buttons.forEach(btn => {
            btn.classList.add('blinking-red'); // Add blinking-red class to all tiles
          });
          setTimeout(() => {
            buttons.forEach(btn => {
              btn.classList.remove('blinking-red'); // Remove blinking-red class
              btn.style.backgroundColor = ''; // Reset to original color
              btn.classList.remove('clicked'); // Remove clicked class
            });
            // Reset group clicked states
            group1Clicked = [false, false];
            group2Clicked = [false, false, false, false];
            group3Clicked = [false, false, false];
          }, 2000); // Blinking duration of 2 seconds
        }
      }, 500); // Delay of 500 milliseconds
    }
  });

  gridContainer.appendChild(button);
  buttons.push(button);
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
  .blinking-red {
    animation: blink-red-animation 1s steps(2, start) infinite;
  }
  @keyframes blink-red-animation {
    50% {
      background-color: red;
    }
  }
`;
document.head.appendChild(style);