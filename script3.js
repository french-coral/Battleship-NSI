// Select the grid container
const gridContainer = document.querySelector('.grid-container');

// Number of tiles (8x8 grid = 64 buttons)
const gridSize = 8 * 8;

// Variables to track the state of specific tile groups
let group1Clicked = [false, false]; // (10, 11)
let group2Clicked = [false, false, false, false]; // (8, 16, 24, 32)
let group3Clicked = [false, false, false]; // (43, 44, 45)

// Create buttons and add them to the grid
for (let i = 0; i < gridSize; i++) {
  const button = document.createElement('button');
  button.classList.add('grid-item');
  button.textContent = ""; // Remove label if not needed

  // Set initial color for specific tiles
  if ([9, 10, 7, 15, 23, 31, 42, 43, 44].includes(i)) {
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
        if ([9, 10, 7, 15, 23, 31, 42, 43, 44].includes(i)){
          button.style.backgroundColor = '#ffa338'; // Set color to blue
        }else{
        button.style.backgroundColor = 'gray';
        }// Set color to gray for clicked tiles

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
`;
document.head.appendChild(style);