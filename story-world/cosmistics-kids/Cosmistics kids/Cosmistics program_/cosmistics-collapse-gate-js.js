/**
 * COSMISTICS - Collapse Gate
 * Core functionality for the Collapse Gate experience
 * 
 * This file handles:
 * - Countdown timer and synchronization
 * - Form unlocking at zero
 * - Submission validation
 * - Fracture path activation
 */

// Firebase functions would be imported in the actual implementation
// import { updateUserFracturePath } from './firebase-functions.js';

// Configuration
const COUNTDOWN_DURATION = 10 * 60; // 10 minutes in seconds
const REQUIRED_KILLS = 7; // Number of kills needed before gate access

// State
let countdown = COUNTDOWN_DURATION;
let timerInterval = null;
let isFormUnlocked = false;
let userKills = 0;

// DOM Elements
let countdownDisplay;
let collapseForm;
let initiationField;
let submitButton;
let gongSound;
let fracturePath;

/**
 * Initialize the Collapse Gate
 */
function initCollapseGate() {
    // Get DOM elements
    countdownDisplay = document.getElementById('countdown-display');
    collapseForm = document.getElementById('collapse-form');
    initiationField = document.getElementById('initiation-phrase');
    submitButton = document.getElementById('submit-initiation');
    fracturePath = document.getElementById('fracture-path');
    
    // Set up audio
    gongSound = new Audio('media/gong.mp3');
    
    // Check user eligibility
    checkEligibility()
        .then(eligible => {
            if (eligible) {
                // Start the countdown
                startCountdown();
                
                // Set up form submission handler
                submitButton.addEventListener('click', handleSubmission);
            } else {
                // Show ineligibility message
                showIneligibilityMessage();
            }
        });
}

/**
 * Check if user is eligible to access the collapse gate
 * @returns {Promise<boolean>} Promise resolving to eligibility status
 */
function checkEligibility() {
    return new Promise((resolve) => {
        // In actual implementation, this would check Firebase for kill count
        // For demonstration, we'll use localStorage
        
        const kills = JSON.parse(localStorage.getItem('killLogs') || '[]');
        const today = new Date().toDateString();
        const todayKills = kills.filter(kill => {
            return new Date(kill.timestamp).toDateString() === today;
        });
        
        userKills = todayKills.length;
        
        // Resolve with eligibility status
        resolve(userKills >= REQUIRED_KILLS);
    });
}

/**
 * Start the countdown timer
 */
function startCountdown() {
    // Display initial time
    updateCountdownDisplay();
    
    // Start interval
    timerInterval = setInterval(() => {
        countdown--;
        
        if (countdown <= 0) {
            // Stop countdown
            clearInterval(timerInterval);
            countdown = 0;
            
            // Play gong sound
            gongSound.play();
            
            // Unlock form
            unlockForm();
        }
        
        // Update display
        updateCountdownDisplay();
    }, 1000);
}

/**
 * Update the countdown display with formatted time
 */
function updateCountdownDisplay() {
    const minutes = Math.floor(countdown / 60);
    const seconds = countdown % 60;
    
    countdownDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    // Add visual effects as countdown approaches zero
    if (countdown <= 60) {
        countdownDisplay.classList.add('pulse');
    }
    
    if (countdown <= 10) {
        document.body.classList.add('collapse-imminent');
    }
}

/**
 * Unlock the form when countdown reaches zero
 */
function unlockForm() {
    isFormUnlocked = true;
    
    // Enable form elements
    initiationField.disabled = false;
    submitButton.disabled = false;
    
    // Add visual cues
    collapseForm.classList.add('unlocked');
    
    // Focus the input field
    initiationField.focus();
}

/**
 * Handle form submission
 * @param {Event} event - Form submission event
 */
function handleSubmission(event) {
    event.preventDefault();
    
    // Check if form is unlocked
    if (!isFormUnlocked) {
        return;
    }
    
    const initiationPhrase = initiationField.value.trim();
    
    // Validate the phrase
    // In a real implementation, this would check against specific criteria
    if (initiationPhrase.length < 5) {
        showError('Initiation phrase too short. Min 5 characters required.');
        return;
    }
    
    // Process the initiation
    processInitiation(initiationPhrase)
        .then(success => {
            if (success) {
                // Show success state
                showSuccess();
                
                // Activate fracture path visualization
                activateFracturePath();
            } else {
                showError('Initiation failed. Please try again when next gate opens.');
            }
        });
}

/**
 * Process the initiation phrase
 * @param {string} phrase - Initiation phrase entered by user
 * @returns {Promise<boolean>} Promise resolving to success status
 */
function processInitiation(phrase) {
    return new Promise((resolve) => {
        // In a real implementation, this would send the phrase to Firebase
        // and validate against specific criteria
        
        // For demonstration, we'll accept any valid phrase
        
        // Encode the phrase for "processing"
        const encoded = btoa(phrase);
        
        // Simulate processing delay
        setTimeout(() => {
            // Store the successful initiation
            localStorage.setItem('lastInitiation', JSON.stringify({
                phrase,
                timestamp: new Date().toISOString(),
                encoded
            }));
            
            resolve(true);
        }, 2000);
    });
}

/**
 * Show an error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    const errorElement = document.getElementById('form-error');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    
    // Clear after 4 seconds
    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 4000);
}

/**
 * Show success state after successful initiation
 */
function showSuccess() {
    // Hide form
    collapseForm.style.display = 'none';
    
    // Show success message
    const successElement = document.getElementById('success-message');
    successElement.style.display = 'block';
    
    // Update user data in Firebase (in real implementation)
    // updateUserFracturePath(user.uid, phrase);
}

/**
 * Show ineligibility message when user hasn't completed enough kills
 */
function showIneligibilityMessage() {
    const ineligibleElement = document.getElementById('ineligible-message');
    ineligibleElement.textContent = `You need ${REQUIRED_KILLS} thought kills to access the Collapse Gate. Current: ${userKills}`;
    ineligibleElement.style.display = 'block';
    
    // Hide countdown and form
    countdownDisplay.parentElement.style.display = 'none';
    collapseForm.style.display = 'none';
}

/**
 * Activate the fracture path visualization
 */
function activateFracturePath() {
    fracturePath.style.display = 'block';
    
    // Initialize