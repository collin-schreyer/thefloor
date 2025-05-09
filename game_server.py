import os
import http.server
import socketserver
import json
import random
import urllib.parse

# Directories containing the images (updated with your new folders)
DIRECTORIES = {
    "baby_essentials": "/Users/collinschreyer/GSA/the_floor/baby_essentials",
    "basketball": "/Users/collinschreyer/GSA/the_floor/basketball",
    "breakfast": "/Users/collinschreyer/GSA/the_floor/breakfast",
    "construction": "/Users/collinschreyer/GSA/the_floor/construction",
    "local_sights": "/Users/collinschreyer/GSA/the_floor/local_sights",
    "nursery_rhymes": "/Users/collinschreyer/GSA/the_floor/nursery_rhymes",
    "school": "/Users/collinschreyer/GSA/the_floor/school",
}

# Port to serve on
PORT = 8000

# HTML template for the game page (with new countdown overlay and reordered elements)
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Face-Off Game</title>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary-color: #4361ee;
      --secondary-color: #3a0ca3;
      --accent-color: #f72585;
      --light-color: #f8f9fa;
      --dark-color: #212529;
      --success-color: #38b000;
      --warning-color: #ffaa00;
      --danger-color: #d00000;
    }
    
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    
    body {
      font-family: 'Montserrat', sans-serif;
      background-color: #f5f5f5;
      color: var(--dark-color);
      line-height: 1.6;
      padding: 0;
      margin: 0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    
    .container {
      width: 100%;
      max-width: 1200px;
      margin: 1rem auto;
      padding: 0 1rem;
    }
    
    h1 {
      color: var(--primary-color);
      text-align: center;
      margin: 1rem 0;
      font-size: 2.5rem;
      font-weight: 700;
    }
    
    .card {
      background: white;
      border-radius: 12px;
      box-shadow: 0 8px 30px rgba(0,0,0,0.12);
      padding: 1.5rem;
      margin-bottom: 1rem;
      transition: all 0.3s ease;
    }
    
    .card h2 {
      color: var(--secondary-color);
      font-size: 1.8rem;
      margin-bottom: 1.5rem;
      font-weight: 600;
    }
    
    /* Category Selection */
    .category-buttons {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1rem;
      margin-bottom: 1.5rem;
    }
    
    .category-btn {
      background-color: var(--light-color);
      color: var(--dark-color);
      font-size: 1.1rem;
      padding: 1rem;
      border: 2px solid #ddd;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s ease;
      font-family: 'Montserrat', sans-serif;
      font-weight: 600;
      text-align: center;
    }
    
    .category-btn:hover {
      background-color: var(--primary-color);
      color: white;
      transform: translateY(-2px);
    }
    
    .category-btn.active {
      background-color: var(--primary-color);
      color: white;
      border-color: var(--primary-color);
    }
    
    .category-info {
      font-size: 1.1rem;
      margin: 1rem 0;
      color: #666;
    }
    
    #loading {
      display: none;
      margin: 1.5rem 0;
      font-size: 1.2rem;
      color: var(--primary-color);
      text-align: center;
    }
    
    /* Game Container */
    #game-container {
      display: none;
      width: 100%;
    }
    
    /* Score */
    #score {
      font-size: 1.3rem;
      text-align: center;
      margin-bottom: 1rem;
      font-weight: 600;
    }
    
    /* Image Container */
    #image-container {
      margin: 0.5rem auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 80vh;
      width: 100%;
    }
    
    #current-image {
      width: 90%;
      height: 75vh;
      border-radius: 8px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.1);
      object-fit: contain;
      transition: all 0.3s ease;
    }
    
    /* Answer (photo name) */
    #answer {
      font-size: 1.5rem;
      margin-top: 1rem;
      color: var(--secondary-color);
      font-weight: 700;
      text-align: center;
    }
    
    /* When guessed, the photo name is bigger */
    #answer.guessed {
      font-size: 2.5rem;
    }
    
    /* Timers and Turn Indicator (placed below the image) */
    #timers {
      display: flex;
      justify-content: space-around;
      margin-top: 1rem;
      gap: 1rem;
    }
    
    .timer {
      flex: 1;
      font-size: 1.5rem;
      font-weight: 600;
      padding: 0.8rem;
      border-radius: 8px;
      text-align: center;
      background-color: #f8f9fa;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      transition: all 0.3s ease;
    }
    
    #turn-indicator {
      font-size: 1.3rem;
      text-align: center;
      margin-top: 0.5rem;
      font-weight: 600;
      color: var(--secondary-color);
    }
    
    /* Buttons */
    #buttons {
      display: flex;
      justify-content: center;
      gap: 1rem;
      margin-top: 2rem;
    }
    
    button {
      font-family: 'Montserrat', sans-serif;
      font-size: 1.1rem;
      font-weight: 600;
      padding: 0.8rem 1.5rem;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    button:focus {
      outline: none;
    }
    
    button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      box-shadow: none;
    }
    
    #start-game-btn {
      background-color: var(--primary-color);
      color: white;
      font-size: 1.2rem;
      padding: 1rem 2rem;
      width: 100%;
      margin-top: 1rem;
    }
    
    #start-game-btn:hover:not(:disabled) {
      background-color: var(--secondary-color);
      transform: translateY(-2px);
    }
    
    #correct-btn {
      background-color: var(--success-color);
      color: white;
    }
    
    #correct-btn:hover:not(:disabled) {
      background-color: #2b9348;
      transform: translateY(-2px);
    }
    
    #pass-btn {
      background-color: var(--danger-color);
      color: white;
    }
    
    #pass-btn:hover:not(:disabled) {
      background-color: #9d0208;
      transform: translateY(-2px);
    }
    
    #restart-btn {
      background-color: var(--primary-color);
      color: white;
    }
    
    #restart-btn:hover:not(:disabled) {
      background-color: var(--secondary-color);
      transform: translateY(-2px);
    }
    
    /* Status */
    #status {
      font-size: 1.5rem;
      text-align: center;
      margin-top: 1.5rem;
      font-weight: 700;
      color: var(--success-color);
    }
    
    /* Active Player Styles */
    .player1-active {
      border-left: 5px solid var(--success-color);
      color: var(--success-color);
    }
    
    .player2-active {
      border-left: 5px solid var(--danger-color);
      color: var(--danger-color);
    }
    
    /* Admin Link */
    .admin-link {
      position: fixed;
      bottom: 10px;
      right: 10px;
      font-size: 0.8rem;
      color: #999;
      text-decoration: none;
    }
    
    /* Countdown Overlay */
    #countdown-overlay {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.7);
      z-index: 9999;
      align-items: center;
      justify-content: center;
    }
    
    #countdown-number {
      font-size: 8rem;
      color: white;
    }
    
    /* Responsive Adjustments */
    @media (max-width: 768px) {
      .container {
        padding: 0 0.5rem;
      }
      
      h1 {
        font-size: 2rem;
        margin: 1rem 0;
      }
      
      .card {
        padding: 1rem;
      }
      
      .category-buttons {
        grid-template-columns: 1fr;
      }
      
      #image-container {
        height: 60vh;
      }
      
      #current-image {
        max-height: 55vh;
      }
      
      .timer {
        font-size: 1.2rem;
      }
      
      #buttons {
        flex-direction: column;
        align-items: center;
      }
      
      button {
        width: 100%;
        max-width: 300px;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Face-Off Game</h1>
    
    <!-- Category Selection Screen -->
    <div id="category-selection" class="card">
      <h2>Select a Category</h2>
      <div class="category-buttons">
        <button class="category-btn" data-category="baby_essentials">Baby Essentials</button>
        <button class="category-btn" data-category="basketball">Basketball</button>
        <button class="category-btn" data-category="breakfast">Breakfast</button>
        <button class="category-btn" data-category="construction">Construction</button>
        <button class="category-btn" data-category="local_sights">Errands & Appointments</button>
        <button class="category-btn" data-category="nursery_rhymes">Nursery Rhymes</button>
        <button class="category-btn" data-category="school">School</button>
      </div>
      <div id="category-info" class="category-info"></div>
      <div id="loading">Loading images... <span id="loading-progress">0%</span></div>
      <button id="start-game-btn" disabled>Start Game</button>
    </div>
    
    <!-- Game Container (initially hidden) -->
    <div id="game-container" class="card">
      <div id="score">Player 1: 0 | Player 2: 0</div>
      <div id="image-container">
        <img id="current-image" src="" alt="Game Image">
        <div id="answer"></div>
      </div>
      <!-- Timers and Turn Indicator placed below the image -->
      <div id="timers">
        <div class="timer player1-active" id="player1-timer">Player 1: 30.00s</div>
        <div class="timer" id="player2-timer">Player 2: 30.00s</div>
      </div>
      <div id="turn-indicator">Current Turn: Player 1</div>
      <div id="buttons">
        <button id="correct-btn">Correct</button>
        <button id="pass-btn">Pass</button>
        <button id="restart-btn" style="display: none;">Restart Game</button>
      </div>
      <div id="status"></div>
    </div>
  </div>
  
  <!-- Countdown Overlay -->
  <div id="countdown-overlay">
    <div id="countdown-number"></div>
  </div>
  
  <!-- Small hidden link to admin page -->
  <a href="/admin" class="admin-link" target="_blank">Admin</a>
  
  <!-- Audio element for the "ding" sound -->
  <audio id="ding-sound" src="/ding-sound" preload="auto"></audio>
  
  <script>
    // DOM elements for category selection
    const categoryButtons = document.querySelectorAll('.category-btn');
    const categoryInfo = document.getElementById('category-info');
    const startGameBtn = document.getElementById('start-game-btn');
    const categorySelectionDiv = document.getElementById('category-selection');
    const loadingDiv = document.getElementById('loading');
    const loadingProgress = document.getElementById('loading-progress');
    
    // DOM elements for the game
    const gameContainer = document.getElementById('game-container');
    const scoreDisplay = document.getElementById('score');
    const currentImage = document.getElementById('current-image');
    const answerDisplay = document.getElementById('answer');
    const timersDiv = document.getElementById('timers');
    const turnIndicator = document.getElementById('turn-indicator');
    const player1TimerDisplay = document.getElementById('player1-timer');
    const player2TimerDisplay = document.getElementById('player2-timer');
    const correctBtn = document.getElementById('correct-btn');
    const passBtn = document.getElementById('pass-btn');
    const restartBtn = document.getElementById('restart-btn');
    const statusDisplay = document.getElementById('status');
    const dingSound = document.getElementById('ding-sound');
    const countdownOverlay = document.getElementById('countdown-overlay');
    const countdownNumber = document.getElementById('countdown-number');
    
    // Game variables
    let player1Time = 30.00;
    let player2Time = 30.00;
    let currentPlayer = 1;
    let timerInterval = null;
    let images = [];
    let currentImageIndex = 0;
    let player1Score = 0;
    let player2Score = 0;
    let selectedCategory = '';
    
    // Add event listeners to category buttons
    categoryButtons.forEach(button => {
      button.addEventListener('click', async function() {
        // Remove active class from all buttons
        categoryButtons.forEach(btn => btn.classList.remove('active'));
        
        // Add active class to clicked button
        this.classList.add('active');
        
        // Get category from data attribute
        selectedCategory = this.getAttribute('data-category');
        
        // Store category in localStorage
        localStorage.setItem('currentCategory', selectedCategory);
        
        // Show loading indicator
        loadingDiv.style.display = 'block';
        startGameBtn.disabled = true;
        
        try {
          // Fetch images for the selected category
          const response = await fetch(`/category-images?category=${selectedCategory}`);
          const data = await response.json();
          
          if (data.images.length === 0) {
            categoryInfo.textContent = 'No images found for this category.';
            loadingDiv.style.display = 'none';
            return;
          }
          
          // Store the images
          images = data.images;
          
          // Update info and enable start button
          categoryInfo.textContent = `${images.length} images found. Ready to play!`;
          startGameBtn.disabled = false;
          
        } catch (error) {
          console.error('Error loading category images:', error);
          categoryInfo.textContent = 'Error loading images. Please try again.';
        }
        
        loadingDiv.style.display = 'none';
      });
    });
    
    // Format time to display hundredths of a second
    function formatTime(time) {
      return time.toFixed(2) + 's';
    }
    
    // Start game when button is clicked with countdown overlay
    startGameBtn.addEventListener('click', function() {
      if (images.length === 0) {
        alert('Please select a category with available images first.');
        return;
      }
      
      // Hide category selection and show game container
      categorySelectionDiv.style.display = 'none';
      gameContainer.style.display = 'block';
      
      // Shuffle the images for gameplay
      shuffleArray(images);
      
      // Show countdown overlay and start countdown from 3
      countdownOverlay.style.display = 'flex';
      let countdownTime = 3;
      countdownNumber.textContent = countdownTime;
      dingSound.play();
      
      const countdownInterval = setInterval(function(){
        countdownTime--;
        if (countdownTime > 0) {
          countdownNumber.textContent = countdownTime;
          dingSound.play();
        } else {
          clearInterval(countdownInterval);
          countdownNumber.textContent = "GO!";
          dingSound.play();
          setTimeout(function(){
            countdownOverlay.style.display = 'none';
            // Initialize game state
            loadImage();
            updateTimers();
            updateTurnIndicator();
            updateScore();
            startTimer();
            localStorage.setItem('gameStarted', 'true');
            localStorage.setItem('imagesTotal', images.length);
          }, 1000);
        }
      }, 1000);
    });
    
    // Function to shuffle an array (Fisher-Yates algorithm)
    function shuffleArray(array) {
      for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
      }
    }
    
    // Update timer displays
    function updateTimers() {
      player1TimerDisplay.textContent = "Player 1: " + formatTime(player1Time);
      player2TimerDisplay.textContent = "Player 2: " + formatTime(player2Time);
      
      if (currentPlayer === 1) {
        player1TimerDisplay.classList.add('player1-active');
        player2TimerDisplay.classList.remove('player2-active');
      } else {
        player1TimerDisplay.classList.remove('player1-active');
        player2TimerDisplay.classList.add('player2-active');
      }
    }
    
    // Update turn indicator
    function updateTurnIndicator() {
      turnIndicator.textContent = "Current Turn: Player " + currentPlayer;
    }
    
    // Update score display
    function updateScore() {
      scoreDisplay.textContent = `Player 1: ${player1Score} | Player 2: ${player2Score}`;
    }
    
    // Load the current image and clear the answer
    function loadImage() {
      if (currentImageIndex >= images.length) {
        shuffleArray(images);
        currentImageIndex = 0;
      }
      
      currentImage.src = images[currentImageIndex].url;
      
      localStorage.setItem('currentImageURL', images[currentImageIndex].url);
      localStorage.setItem('currentImageName', images[currentImageIndex].name);
      localStorage.setItem('currentImageIndex', currentImageIndex);
      
      console.log(`Current image: ${images[currentImageIndex].name}`);
      
      answerDisplay.textContent = "";
      answerDisplay.classList.remove('guessed');
      
      if (currentImageIndex + 1 < images.length) {
        const nextImg = new Image();
        nextImg.src = images[currentImageIndex + 1].url;
      }
    }
    
    // Start the countdown timer for the active player
    function startTimer() {
      clearInterval(timerInterval);
      timerInterval = setInterval(function() {
        if (currentPlayer === 1) {
          player1Time -= 0.01;
          if (player1Time <= 0) {
            player1Time = 0;
            updateTimers();
            endGame(2);
            return;
          }
        } else {
          player2Time -= 0.01;
          if (player2Time <= 0) {
            player2Time = 0;
            updateTimers();
            endGame(1);
            return;
          }
        }
        updateTimers();
      }, 10);
    }
    
    // Pause the timer
    function pauseTimer() {
      clearInterval(timerInterval);
    }
    
    // Toggle active player
    function togglePlayer() {
      currentPlayer = (currentPlayer === 1) ? 2 : 1;
      updateTurnIndicator();
      updateTimers();
    }
    
    // Reveal the answer and make it bigger
    function revealAnswer() {
      answerDisplay.textContent = images[currentImageIndex].name;
      answerDisplay.classList.add('guessed');
    }
    
    // Move to the next image
    function nextImage() {
      currentImageIndex++;
      loadImage();
    }
    
    // End the game by declaring the winner
    function endGame(winner) {
      pauseTimer();
      statusDisplay.textContent = "Player " + winner + " wins!";
      correctBtn.disabled = true;
      passBtn.disabled = true;
      restartBtn.style.display = 'inline-block';
    }
    
    // Event: When "Correct" is pressed
    correctBtn.addEventListener('click', function() {
      pauseTimer();
      revealAnswer();
      dingSound.play();
      
      if (currentPlayer === 1) {
        player1Score++;
      } else {
        player2Score++;
      }
      updateScore();
      
      setTimeout(function() {
        nextImage();
        togglePlayer();
        startTimer();
      }, 1000);
    });
    
    // Event: When "Pass" is pressed
    passBtn.addEventListener('click', function() {
      revealAnswer();
      correctBtn.disabled = true;
      passBtn.disabled = true;
      
      setTimeout(function() {
        clearInterval(timerInterval);
        nextImage();
        correctBtn.disabled = false;
        passBtn.disabled = false;
        startTimer();
      }, 3000);
    });
    
    // Event: When "Restart" is pressed
    restartBtn.addEventListener('click', function() {
      player1Time = 30.00;
      player2Time = 30.00;
      currentPlayer = 1;
      currentImageIndex = 0;
      player1Score = 0;
      player2Score = 0;
      
      shuffleArray(images);
      loadImage();
      updateTimers();
      updateTurnIndicator();
      updateScore();
      
      correctBtn.disabled = false;
      passBtn.disabled = false;
      restartBtn.style.display = 'none';
      statusDisplay.textContent = '';
      
      startTimer();
    });
    
    // Handle image loading errors
    currentImage.addEventListener('error', function() {
      console.error(`Failed to load image: ${images[currentImageIndex].url}`);
      currentImage.src = '/fallback-image';
    });
  </script>
</body>
</html>'''

# HTML template for the admin page remains unchanged
ADMIN_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Face-Off Game Admin</title>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary-color: #4361ee;
      --secondary-color: #3a0ca3;
      --accent-color: #f72585;
      --light-color: #f8f9fa;
      --dark-color: #212529;
      --success-color: #38b000;
      --warning-color: #ffaa00;
      --danger-color: #d00000;
    }
    
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    
    body {
      font-family: 'Montserrat', sans-serif;
      background-color: #f5f5f5;
      color: var(--dark-color);
      line-height: 1.6;
      padding: 0;
      margin: 0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    
    .container {
      width: 100%;
      max-width: 800px;
      margin: 1rem auto;
      padding: 0 1rem;
    }
    
    .header {
      width: 100%;
      background-color: var(--primary-color);
      color: white;
      text-align: center;
      padding: 1rem;
      margin-bottom: 2rem;
      border-radius: 8px;
    }
    
    h1 {
      font-size: 2rem;
      font-weight: 700;
    }
    
    .card {
      background: white;
      border-radius: 12px;
      box-shadow: 0 8px 30px rgba(0,0,0,0.12);
      padding: 1.5rem;
      margin-bottom: 1rem;
      transition: all 0.3s ease;
    }
    
    .admin-panel {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }
    
    .info-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.8rem;
      background-color: var(--light-color);
      border-radius: 8px;
    }
    
    .info-label {
      font-weight: 600;
      color: var(--secondary-color);
    }
    
    .info-value {
      font-weight: 400;
    }
    
    .image-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-top: 1rem;
    }
    
    .preview-image {
      max-width: 100%;
      max-height: 300px;
      border-radius: 8px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.1);
      object-fit: contain;
    }
    
    .image-name {
      font-size: 1.5rem;
      margin-top: 1rem;
      font-weight: 700;
      color: var(--secondary-color);
    }
    
    .button-row {
      display: flex;
      justify-content: center;
      gap: 1rem;
      margin-top: 2rem;
    }
    
    .return-btn {
      font-family: 'Montserrat', sans-serif;
      font-size: 1.1rem;
      font-weight: 600;
      padding: 0.8rem 1.5rem;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
      background-color: var(--primary-color);
      color: white;
    }
    
    .return-btn:hover {
      background-color: var(--secondary-color);
      transform: translateY(-2px);
    }
    
    @media (max-width: 768px) {
      .container {
        padding: 0 0.5rem;
      }
      
      h1 {
        font-size: 1.5rem;
      }
      
      .card {
        padding: 1rem;
      }
      
      .info-row {
        padding: 0.5rem;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.3rem;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Face-Off Game Admin Panel</h1>
    </div>
    
    <div class="card">
      <div class="admin-panel">
        <div class="info-row">
          <span class="info-label">Category:</span>
          <span class="info-value" id="category-display">Not selected</span>
        </div>
        
        <div class="info-row">
          <span class="info-label">Image Number:</span>
          <span class="info-value" id="image-number">N/A</span>
        </div>
        
        <div class="image-container">
          <img id="preview-image" class="preview-image" src="" alt="No image selected">
          <div id="image-name" class="image-name">No image loaded</div>
        </div>
      </div>
      
      <div class="button-row">
        <button class="return-btn" onclick="window.location.href='/'">Return to Game</button>
      </div>
    </div>
  </div>

  <script>
    const categoryDisplay = document.getElementById('category-display');
    const imageNumberDisplay = document.getElementById('image-number');
    const previewImage = document.getElementById('preview-image');
    const imageNameDisplay = document.getElementById('image-name');
    
    function formatCategoryName(category) {
      if (!category) return 'Not selected';
      return category.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }
    
    function updateAdminPanel() {
      const category = localStorage.getItem('currentCategory');
      const imageURL = localStorage.getItem('currentImageURL');
      const imageName = localStorage.getItem('currentImageName');
      const imageIndex = localStorage.getItem('currentImageIndex');
      const imagesTotal = localStorage.getItem('imagesTotal');
      
      if (category) {
        categoryDisplay.textContent = formatCategoryName(category);
      }
      
      if (imageURL) {
        previewImage.src = imageURL;
      }
      
      if (imageName) {
        imageNameDisplay.textContent = imageName;
      }
      
      if (imageIndex && imagesTotal) {
        imageNumberDisplay.textContent = `${Number(imageIndex) + 1} of ${imagesTotal}`;
      }
    }
    
    updateAdminPanel();
    
    window.addEventListener('storage', function(event) {
      updateAdminPanel();
    });
    
    setInterval(function() {
      updateAdminPanel();
    }, 1000);
  </script>
</body>
</html>'''

class GameHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)
        
        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
            return
            
        elif path == "/admin":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(ADMIN_TEMPLATE.encode())
            return
            
        elif path == "/category-images":
            category = query.get('category', [''])[0]
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            images = []
            
            if category in DIRECTORIES:
                try:
                    directory = DIRECTORIES[category]
                    files_in_directory = os.listdir(directory)
                    
                    for filename in files_in_directory:
                        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                            name = os.path.splitext(filename)[0]
                            display_name = ' '.join(word.capitalize() for word in name.replace('_', ' ').split(' '))
                            images.append({
                                "name": display_name,
                                "url": f"/raw-image/{category}/{urllib.parse.quote(filename)}"
                            })
                    
                    print(f"Found {len(images)} images in {category} directory")
                    
                except Exception as e:
                    print(f"Error listing directory {category}: {e}")
            
            self.wfile.write(json.dumps({"images": images}).encode())
            return
        
        elif path.startswith("/raw-image/"):
            path_parts = path[len("/raw-image/"):].split('/', 1)
            if len(path_parts) != 2:
                self.send_response(404)
                self.end_headers()
                return
                
            category = path_parts[0]
            encoded_filename = path_parts[1]
            filename = urllib.parse.unquote(encoded_filename)
            
            if category not in DIRECTORIES:
                self.send_response(404)
                self.end_headers()
                return
                
            filepath = os.path.join(DIRECTORIES[category], filename)
            print(f"Trying to serve image: {filepath}")
            
            if os.path.isfile(filepath):
                content_type = "image/jpeg"
                if filename.lower().endswith('.png'):
                    content_type = "image/png"
                
                with open(filepath, 'rb') as f:
                    self.send_response(200)
                    self.send_header("Content-type", content_type)
                    self.end_headers()
                    self.wfile.write(f.read())
                    return
            
            print(f"File not found: {filepath}")
            self.send_response(302)
            self.send_header("Location", "/fallback-image")
            self.end_headers()
            return
        
        elif path == "/fallback-image":
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            
            from PIL import Image
            import io
            img = Image.new('RGB', (300, 200), color=(73, 109, 137))
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            self.wfile.write(buf.getvalue())
            return
            
        elif path == "/ding-sound":
            self.send_response(200)
            self.send_header("Content-type", "audio/mpeg")
            self.send_header("Content-Disposition", "inline")
            self.end_headers()
            
            try:
                from scipy.io import wavfile
                import numpy as np
                import io
                sample_rate = 44100
                duration = 0.5
                frequency = 880
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                note = np.sin(2 * np.pi * frequency * t)
                envelope = np.exp(-5 * t)
                note = note * envelope
                note = note * 32767 / np.max(np.abs(note))
                note = note.astype(np.int16)
                buffer = io.BytesIO()
                wavfile.write(buffer, sample_rate, note)
                buffer.seek(0)
                self.wfile.write(buffer.read())
                return
            except ImportError:
                self.wfile.write(bytes([
                    0x52, 0x49, 0x46, 0x46,
                    0x24, 0x00, 0x00, 0x00,
                    0x57, 0x41, 0x56, 0x45,
                    0x66, 0x6D, 0x74, 0x20,
                    0x10, 0x00, 0x00, 0x00,
                    0x01, 0x00,
                    0x01, 0x00,
                    0x44, 0xAC, 0x00, 0x00,
                    0x88, 0x58, 0x01, 0x00,
                    0x02, 0x00,
                    0x10, 0x00,
                    0x64, 0x61, 0x74, 0x61,
                    0x00, 0x00, 0x00, 0x00
                ]))
                return
        
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def main():
    handler = GameHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    
    print(f"Server running at http://localhost:{PORT}")
    print(f"Admin panel available at http://localhost:{PORT}/admin")
    print(f"Available categories:")
    for category, directory in DIRECTORIES.items():
        print(f"  - {category}: {directory}")
    print(f"Open http://localhost:{PORT} in your browser to play")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    main()