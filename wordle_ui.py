#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wordle Solver UI - Streamlit Interface

An interactive web-based interface for the Wordle Solver with a modern UI/UX
that mimics the official Wordle game experience.

Author: advaith
"""

import os

import streamlit as st

from naive.wordle_solver import MAX_TURNS, WORD_LENGTH, WordleSolver
from trained.trained_solver import TrainedWordleSolver


TRAINED_MODEL_PATH = "trained/trained_strategy.json"


def build_solver(mode: str):
    if mode == "trained":
        if os.path.exists(TRAINED_MODEL_PATH):
            return TrainedWordleSolver(model_path=TRAINED_MODEL_PATH)
        return TrainedWordleSolver()
    return WordleSolver()


def reset_game_state() -> None:
    st.session_state.solver = build_solver(st.session_state.solver_mode)
    st.session_state.solver.load_words()
    st.session_state.turn = 0
    st.session_state.game_over = False
    st.session_state.won = False
    st.session_state.feedback_submitted = False
    st.session_state.history = []
    st.session_state.current_guess = None
    st.session_state.guessed_words = []
    if "feedback" in st.session_state:
        del st.session_state.feedback

# Page configuration
st.set_page_config(
    page_title="Wordle Solver",
    page_icon="W",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    body {
        background-color: #121213;
        color: #ffffff;
        font-family: Arial, sans-serif;
    }
    
    .header-title {
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        letter-spacing: 0.1em;
        margin-bottom: 10px;
    }
    
    .guess-display {
        text-align: center;
        font-size: 2.5em;
        letter-spacing: 0.15em;
        font-weight: bold;
        margin: 20px 0;
        font-family: 'Courier New', monospace;
    }
    
    .tile {
        display: inline-block;
        width: 50px;
        height: 50px;
        margin: 5px;
        border-radius: 5px;
        text-align: center;
        line-height: 50px;
        font-weight: bold;
        font-size: 1.2em;
    }
    
    .stats {
        text-align: center;
        margin: 15px 0;
        font-size: 1.1em;
    }
    
    .info-text {
        text-align: center;
        color: #b3b6b7;
        margin: 10px 0;
    }
    
    .feedback-tiles {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin: 20px 0;
    }
    
    .feedback-tile {
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        font-weight: bold;
        font-size: 1.5em;
        border: 2px solid #3a3a3c;
        background-color: #121213;
        transition: all 0.2s ease;
    }
    
    .feedback-tile.grey {
        background-color: #3a3a3c;
        border-color: #3a3a3c;
    }
    
    .feedback-tile.yellow {
        background-color: #b59f3b;
        border-color: #b59f3b;
    }
    
    .feedback-tile.green {
        background-color: #538d4e;
        border-color: #538d4e;
    }
    
    .button-group {
        display: flex;
        gap: 4px;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

if "solver_mode" not in st.session_state:
    st.session_state.solver_mode = "naive"

selected_mode = st.selectbox(
    "Solver Mode",
    ["naive", "trained"],
    index=0 if st.session_state.solver_mode == "naive" else 1,
    help="Switch between the baseline naive heuristic and the trained strategy model.",
)

if selected_mode != st.session_state.solver_mode:
    st.session_state.solver_mode = selected_mode
    reset_game_state()
    st.rerun()

if st.session_state.solver_mode == "trained" and not os.path.exists(TRAINED_MODEL_PATH):
    st.warning("Trained model file not found. Using default trained weights.")

# Initialize session state
if "solver" not in st.session_state:
    reset_game_state()

solver = st.session_state.solver

# Generate current guess only once per turn
if not st.session_state.game_over and st.session_state.current_guess is None:
    st.session_state.current_guess = solver._get_strategic_guess(st.session_state.turn, st.session_state.guessed_words)
    solver.current_guess = st.session_state.current_guess

# Header
st.markdown("<div class='header-title'>WORDLE SOLVER</div>", unsafe_allow_html=True)
st.markdown(
    f"<p style='text-align: center; color: #b3b6b7;'>AI-Powered Solver ({st.session_state.solver_mode})</p>",
    unsafe_allow_html=True,
)

# Show intro message on first load
if "intro_shown" not in st.session_state:
    st.markdown("""
    <div style='text-align: center; background-color: #1f1f23; padding: 20px; border-radius: 8px; margin: 20px 0;'>
        <p style='font-size: 1.1em; margin: 10px 0;'>
            Are you struggling with Wordle today? <br>
            <span style='color: #b3b6b7; font-size: 0.95em;'>Let me help you solve it!</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.intro_shown = True

# Main game area
if not st.session_state.game_over:
    # Display current game stats - centered
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Turn", f"{st.session_state.turn + 1}/{MAX_TURNS}")
    with col2:
        st.metric("Confidence", f"{solver._calculate_confidence():.1f}%")
    with col3:
        st.metric("Possible Words", len(solver.possible_words))
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Get the current guess
    if st.session_state.turn < MAX_TURNS and not st.session_state.feedback_submitted:
        current_guess = st.session_state.current_guess
        
        # Initialize feedback state if needed
        if "feedback" not in st.session_state:
            st.session_state.feedback = [''] * WORD_LENGTH
        
        # Display colored tiles for the word
        tiles_html = '<div class="feedback-tiles">'
        color_map = {"0": "grey", "1": "yellow", "2": "green"}
        
        for i, letter in enumerate(current_guess):
            color_class = color_map.get(st.session_state.feedback[i], "")
            tiles_html += f'<div class="feedback-tile {color_class}">{letter.upper()}</div>'
        
        tiles_html += '</div>'
        st.markdown(tiles_html, unsafe_allow_html=True)
        
        st.markdown("<p class='info-text'>Provide feedback for each letter:</p>", unsafe_allow_html=True)
        
        # Create 5 columns for feedback buttons
        cols = st.columns(5)
        
        for i, col in enumerate(cols):
            with col:
                st.markdown(f"<p style='text-align: center; font-weight: bold; margin-bottom: 10px;'>{current_guess[i].upper()}</p>", unsafe_allow_html=True)
                
                # Create three buttons vertically stacked
                if st.button("⬜", key=f"grey_{i}", help="Grey - Not in word", use_container_width=True):
                    st.session_state.feedback[i] = "0"
                    st.rerun()
                
                if st.button("🟨", key=f"yellow_{i}", help="Yellow - Wrong position", use_container_width=True):
                    st.session_state.feedback[i] = "1"
                    st.rerun()
                
                if st.button("🟩", key=f"green_{i}", help="Green - Correct position", use_container_width=True):
                    st.session_state.feedback[i] = "2"
                    st.rerun()
        
        # Display current feedback and submit button
        if all(f != '' for f in st.session_state.feedback):
            feedback_str = "".join(st.session_state.feedback)
            
            st.divider()
            
            # Submit button
            if st.button("✓ Enter", key="submit", use_container_width=True):
                # Track this guess in session state
                st.session_state.guessed_words.append(current_guess)
                
                # Update solver
                solver.update_possibilities(current_guess, feedback_str)
                
                # Add to history
                st.session_state.history.append((current_guess, feedback_str))
                
                # Check for win
                if feedback_str == "2" * WORD_LENGTH:
                    st.session_state.won = True
                    st.session_state.game_over = True
                else:
                    st.session_state.turn += 1
                    st.session_state.current_guess = None  # Reset for next turn
                    
                    if st.session_state.turn >= MAX_TURNS:
                        st.session_state.game_over = True
                    
                    if len(solver.possible_words) == 0:
                        st.session_state.game_over = True
                
                # Reset feedback
                if "feedback" in st.session_state:
                    del st.session_state.feedback
                st.rerun()

else:
    # Game Over Screen
    st.divider()
    
    if st.session_state.won:
        st.success("**Computer Wins!**")
        st.markdown(f"<p style='text-align: center; font-size: 1.5em;'>The word was: **{solver.current_guess.upper()}**</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>Solved in **{st.session_state.turn + 1}** turn{'s' if st.session_state.turn + 1 != 1 else ''}</p>", unsafe_allow_html=True)
    elif len(solver.possible_words) == 0:
        st.error("**No Valid Words Remain**")
        st.markdown("<p style='text-align: center;'>Are you sure you haven't made a mistake? Please try again or verify your feedback.</p>", unsafe_allow_html=True)
        
        st.divider()
        st.markdown("<p style='text-align: center; font-weight: bold;'>Did you know what the word was?</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #b3b6b7; font-size: 0.9em;'>If you knew the answer, please enter it below to help us improve our database!</p>", unsafe_allow_html=True)
        
        user_word = st.text_input("Enter the word (5 letters):", max_chars=5, placeholder="e.g., GUAVA").lower().strip()
        
        if user_word:
            if len(user_word) == WORD_LENGTH and user_word.isalpha():
                st.success("**Thank you!**")
                st.markdown("<p style='text-align: center;'>We have recorded your word and will update our database accordingly!</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: #538d4e;'>Word: <strong>{user_word.upper()}</strong></p>", unsafe_allow_html=True)
            else:
                st.warning("Please enter a valid 5-letter word.")
    else:
        st.info("**Game Over**")
        st.markdown("<p style='text-align: center;'>Max turns reached without solving the puzzle.</p>", unsafe_allow_html=True)
    
    # Display game history
    if st.session_state.history:
        st.markdown("### Game History")
        for turn_num, (guess, feedback) in enumerate(st.session_state.history, 1):
            color_map = {"0": "⬜", "1": "🟨", "2": "🟩"}
            feedback_display = "".join(color_map[c] for c in feedback)
            st.markdown(f"**Turn {turn_num}:** {guess.upper()} {feedback_display}")
    
    # Reset button
    if st.button("Play Again", use_container_width=True):
        reset_game_state()
        st.rerun()

# Footer
st.divider()
st.markdown("<p style='text-align: center; color: #808080; font-size: 0.9em;'>Wordle Solver v1.0 | Built with Streamlit</p>", unsafe_allow_html=True)
