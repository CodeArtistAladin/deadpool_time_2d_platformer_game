# Platformer Game - Complete Guide

A feature-rich 2D platformer game built with Python and Pygame. Navigate through 10+ challenging levels, collect coins, avoid enemies and lava, and reach the exit to progress. Features dynamic camera system, animated sprites, immersive sound effects, resizable window, and a built-in level editor.

## 🎮 Game Overview

**Platformer** is a classic-style platformer game where you control the Deadpool character through increasingly difficult levels. Jump over obstacles, dodge enemies and lava traps, collect coins for points, and reach the exit portal to complete each level. The game features smooth animations, responsive controls, and progressively challenging level design.

### Game Features
- **10+ Levels** - Auto-detecting level system that supports unlimited expansion
- **Dynamic Camera System** - Smooth viewport following the player with world boundary detection
- **Sprite Animation** - Animated player walking, enemies, and environmental elements
- **Sound Effects** - Background music, coin collection, jump, and game-over audio
- **Resizable Window** - Play at any window size with dynamic UI scaling (800×600 to 1000×950 max)
- **Full-Screen Ratio** - Optimized 1000×950 display (20 columns × 17 rows for game grid)
- **Cheat Codes** - Hidden secret codes for level skipping and final level access
- **Level Editor** - Enhanced level creation tool with preview mode, undo/redo, and file management

---

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Pygame library

### Installation

1. **Install Python dependencies:**
```bash
pip install pygame
```

2. **Navigate to the project directory:**
```bash
cd "s:\university\final game\prev\Platformer-master\final game surjo"
```

3. **Run the game:**
```bash
python "main file/main.py"
```

---

## 🎯 How to Play

### Controls
| Key | Action |
|-----|--------|
| **↑ UP Arrow** | Jump |
| **← LEFT Arrow** | Move Left |
| **→ RIGHT Arrow** | Move Right |

### Game Mechanics

**Objective:** 
- Navigate through each level
- Collect coins (★) to increase your score
- Reach the exit portal (⊞) to advance to the next level
- Complete all 10 levels to win the game

**Hazards:**
- **Enemies** (👾) - Moving aliens that patrol back and forth. Touching them ends your life
- **Lava** (🌊) - Deadly molten pits at the bottom or middle of levels. Avoid at all costs
- **Platforms** - Some move horizontally or vertically to add complexity
- **Boundaries** - Falling off the map or hitting obstacles resets your progress

**Scoring:**
- Collect coins throughout the level to increase your score
- Score carries between levels
- Resetting a level resets your score to 0

---

## 🏗️ Game Architecture

### Main Components

#### 1. **Player Class** (`main.py`)
Handles player character logic including:
- **Animation System** - 16-frame walking animation with idle state
- **Physics** - Gravity simulation, jumping mechanics, velocity
- **Collision Detection** - Detects collisions with tiles, platforms, enemies, lava, and coins
- **Health System** - Max health of 100 (framework for damage system)
- **Direction Handling** - Flips sprite based on movement direction

```python
# Player starts at world coordinates (100, ground_y)
player = Player(100, ground_y)
```

**Key Methods:**
- `update(game_over)` - Updates player position, animation, and collision detection each frame
- `reset(x, y)` - Resets player position and loads animation frames

#### 2. **World Class** (`main.py`)
Manages level layout and tile rendering:
- Loads level data from pickle files
- Converts tile codes into game objects
- Handles collision rectangles for static tiles
- Supports camera-based rendering optimization

**Tile Codes:**
| Code | Element | Collision |
|------|---------|-----------|
| 0 | Empty space | No |
| 1 | Dirt/Wall (border) | Yes |
| 2 | Grass platform | Yes |
| 3 | Enemy spawn | No |
| 4 | Horizontal moving platform | Yes |
| 5 | Vertical moving platform | Yes |
| 6 | Lava hazard | Yes |
| 7 | Coin pickup | No |
| 8 | Level exit | No |

#### 3. **Camera Class** (`main.py`)
Implements a viewport system for large worlds:
- **Following** - Centers camera on player position
- **Boundary Clamping** - Prevents camera from viewing outside world bounds
- **Coordinate Conversion** - Converts world space to screen space
- **Frustum Culling** - Only renders visible entities

```python
# Camera initialized with screen and world dimensions
camera = Camera(screen_width, screen_height, world_width, world_height)

# Each frame:
camera.update(player.rect.centerx, player.rect.centery)  # Follow player
screen_x, screen_y = camera.apply(world_x, world_y)      # Convert coords
```

#### 4. **Enemy Class** (`main.py`)
AI-controlled walking enemies:
- **Sprite Animation** - 36-frame animation cycle
- **Patrol Behavior** - Moves back and forth 50 pixels
- **Auto-reversal** - Bounces when reaching movement limits
- **Deadly on Touch** - Causes instant level failure

#### 5. **Platform Class** (`main.py`)
Moving platform mechanics:
- **Horizontal Movement** (Type 4) - Moves side-to-side
- **Vertical Movement** (Type 5) - Moves up-and-down
- **Player Adhesion** - Player moves with platform during horizontal motion
- **Bounce Distance** - Travels 50 pixels before reversing

#### 6. **Game Objects** (`main.py`)
- **Lava** - Stationary hazard, causes instant death
- **Coin** - Collectible that increases score by 1
- **Exit** - Level completion portal (size: 50×75 pixels)

#### 7. **Button Class** (`main.py`)
Interactive UI elements:
- **Hover Effects** - Changes image on mouseover
- **Click Detection** - Returns True on mouse click
- **State Management** - Prevents multiple triggers per click

#### 8. **Camera System** (`main.py`)
Viewport management for large level worlds:
- Follows player character
- Prevents viewing outside map boundaries
- Optimizes rendering by culling off-screen objects
- Smoothly updates as player moves

---

## 📁 File Structure

```
main file/
├── main.py                    # Main game engine and gameplay loop
├── __pycache__/               # Python bytecode cache

level_editor_enhanced.py       # Level creation and editing tool
create_levels.py               # Predefined level data (levels 8-11+)

level1_data                    # Pickled level data files
level2_data
level3_data
...
level10_data

img/                           # Asset directory
├── deadpool head.png          # Main menu background
├── sky.png                    # Fallback background
├── dirt.png                   # Ground tile
├── grass.png                  # Grass platform tile
├── platform.png               # Moving platform sprite
├── lava.png                   # Lava hazard sprite
├── golden gun.png             # Coin sprite
├── exit.png                   # Exit portal sprite
├── ghost.png                  # Player death sprite
├── game over.png              # Game over screen
├── winner.png                 # Victory screen
├── restart_btn.png            # Restart button
├── start_btn.png              # Start button
├── start_btn hover.png        # Start button hover state
├── exit_btn.png               # Exit button
├── music.wav                  # Background music
├── coin.wav                   # Coin collection sound
├── jump.wav                   # Jump sound effect
├── game_over.wav              # Game over sound
│
├── deadpool char/             # Player character sprites
│   └── frame_*.png            # 16 walking animation frames
│   └── frame idol_image.png   # Idle/neutral stance
│
├── enemy alien new/           # Enemy sprites
│   └── frame_*.png            # 36 animation frames for aliens
│
├── villain char/
│   └── other assets/
│
├── background/Untitled design/
│   └── *.png                  # Random backgrounds (cycling)
│
└── old elements/              # Deprecated assets

README.md                       # This file
```

---

## 🎮 Gameplay Systems

### Collision Detection
The game uses **Axis-Aligned Bounding Box (AABB)** collision detection:
- **X-axis** - Horizontal movement/wall collisions
- **Y-axis** - Vertical movement/platform landing
- **Threshold** - 20-pixel collision detection threshold for platforms
- **Tile-based** - All static blocks use tile collision rectangles

### Animation System
- **Player Walking** - 16 sprites, updates every 5 frames
- **Player Idle** - Static frame when not moving
- **Enemies** - 36-frame loop, updates every 3 frames
- **Direction Flipping** - Horizontal flip for left-facing animations

### Physics
- **Gravity** - 1 pixel/frame² acceleration
- **Terminal Velocity** - Capped at 10 pixels/frame
- **Jump Force** - Initial velocity of -15 pixels/frame
- **Movement Speed** - 5 pixels/frame for left/right movement

### Audio
- **Background Music** - Looping WAV file
- **Sound Effects** - Coin (50% volume), Jump (50%), Game Over (50%), Hit (30%)
- **Pre-initialization** - 44.1kHz, 16-bit, Stereo, 512-byte buffer

---

## 🔧 Level Editor (`level_editor_enhanced.py`)

### Features
- **Visual Grid** - 20×20 tile grid (50px per tile)
- **Tile Placement** - Click to place, drag to paint
- **Element Buttons** - Quick access to all game objects
- **Player Preview** - See where player spawns
- **Enemy Preview** - Visualize AI placements
- **Undo/Redo** - Up to 50 steps of history
- **Save/Load** - Pickle file format for level persistence
- **File Browser** - Load existing levels for editing
- **Clear Level** - Reset entire level to empty state

### How to Use the Editor
1. Run: `python level_editor_enhanced.py`
2. Select tile type from buttons at top
3. Click to place single tiles, drag to paint multiple
4. Use toolbar buttons for special functions
5. Save level when finished

### Tile Codes in Editor
Same as in-game codes (0-8) with visual representation for each type

---

## 🎮 Level Progression

### Level 1-7
Standard introductory levels with:
- Basic platform layouts
- Simple enemy patterns
- Coins scattered throughout
- Progressive difficulty increase

### Level 8 - Sky Platformer
- Vertical platform challenges
- Moving vertical platforms (tile type 5)
- Coins positioned on narrow platforms
- High spatial awareness required

### Level 9 - Lava Challenge
- Lava pits occupying entire level sections
- Limited platform real estate
- Requires precise jumping
- High difficulty spike

### Level 10 - Enemy Gauntlet
- Multiple enemies (3-4 per level)
- Combination of static and moving platforms
- Dense obstacle patterns
- Final level before victory

### Levels 11+ (Custom)
- Expandable system supporting unlimited levels
- Auto-detection of new level files
- Can be created with Level Editor

---

## 🎯 Cheat Codes

Access secret features by typing number sequences during gameplay:

| Code | Effect |
|------|--------|
| **4321** | Jump directly to Level 10 (final level) |
| **3211** | Skip to next level (or back to 1 if at level 10) |

**How to Use:**
1. During gameplay, type the number sequence on the keyboard
2. The game monitors the last 5 digits typed
3. If the last 5 digits match a cheat code, the effect activates
4. A code resets after being triggered

---

## 🔄 Game Flow

### Main Menu
```
┌─────────────────────┐
│   Platformer Game   │
│   [Start] [Exit]    │
└─────────────────────┘
```
- **Start** - Begin at Level 1
- **Exit** - Close the game

### Gameplay Loop
```
┌─ Update Player ──→ Check Collisions ──→ Update Enemies
│                                              │
└─ Render Scene ←────────────── Update Camera ←─
```

### Level Complete
- Exit portal touched → Auto-advance to next level
- Level 10 complete → Victory screen appears
- **Restart Button** - Returns to Level 1 with score reset

### Game Over
- Enemy contact / Lava touch → Game Over screen
- **Restart Button** - Reload current level from checkpoint

---

## 🎨 Display Settings

### Resizable Window
- **Minimum Size:** 800×600 pixels (recommended starting point)
- **Maximum Size:** 1000×950 pixels (20 columns × 17 rows for optimal gameplay)
- **Dynamic Scaling:** Game UI and backgrounds automatically scale to window size
- **Drag to Resize:** Simply drag the window edges to change dimensions
- **Camera Adjustment:** Viewport automatically updates when resizing

### Full Display Mode
When maximized to 1000×950:
- **Grid View:** 20 blocks wide × 17 blocks tall
- **UI Area:** 100 pixel margin at bottom for HUD elements
- **Aspect Ratio:** Perfectly matched to level editor dimensions for consistent level creation

### Background Cycling
- Random background loaded for each level
- Supports unlimited backgrounds in `img/background/Untitled design/`
- Auto-shuffled and looped for visual variety

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'pygame'"
```bash
pip install pygame
```

### Game won't start / Missing assets
- Ensure you're in the correct directory with all image/audio files
- Check that `img/` folder structure is intact
- Verify all PNG/WAV files are present

### Player falls through platforms
- This is a collision detection edge case
- Ensure platform collision threshold (20px) is sufficient
- Check that platform rectangles are properly defined

### Performance issues with large levels
- Camera system handles culling automatically
- Reduce number of animated sprites if needed
- Update FPS cap in `main.py` line 15: `fps = 60` (try lower value)

### Audio issues
- Ensure WAV files are in `img/` folder
- Check audio driver compatibility
- Pygame mixer initialized before music load

---

## 📊 Game Statistics

| Metric | Value |
|--------|-------|
| **Frame Rate** | 60 FPS |
| **Tile Size** | 50×50 pixels |
| **Game Grid** | 20×20 tiles (level editor) / 20×17 tiles (game max) |
| **Initial Window** | 800×600 pixels |
| **Maximum Window** | 1000×950 pixels |
| **Player Size** | 40×80 pixels |
| **Enemy Size** | 60×60 pixels |
| **Max Gravity** | 10 pixels/frame |
| **Jump Force** | 15 pixels/frame (upward) |
| **Movement Speed** | 5 pixels/frame |
| **Max Undo Steps** | 50 (in editor) |
| **Auto-detect Levels** | Up to 100 |

---

## 🎓 Code Examples

### Adding a New Game Object
```python
class MyObject(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/my_object.png')
        self.image = pygame.transform.scale(img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def update(self):
        # Custom logic here
        pass

# Add to world initialization (World.__init__)
if tile == 9:  # New tile code
    obj = MyObject(col_count * tile_size, row_count * tile_size)
    my_group.add(obj)
```

### Custom Cheat Code
In main game loop (around line 685):
```python
if secret_code.endswith("1234"):
    # Do something
    score += 100
    secret_code = ""
```

### Adjusting Difficulty
```python
# Player movement speed (faster = harder)
if key[pygame.K_LEFT]:
    dx -= 6  # Increased from 5

# Enemy patrol distance (shorter = easier)
if abs(self.move_counter) > 30:  # Changed from 50
    self.move_direction *= -1
```

---

## 🚀 Future Enhancements

Potential features for expansion:
- [ ] Power-ups (invincibility, speed boost, double jump)
- [ ] Difficulty settings (Easy, Normal, Hard)
- [ ] Leaderboard/high scores
- [ ] Pause menu during gameplay
- [ ] Controller support (gamepad)
- [ ] Procedural level generation
- [ ] Mobile touch controls
- [ ] Multiplayer mode
- [ ] Particle effects for coins/damage
- [ ] Water physics and swimming
- [ ] Checkpoint system

---

## 📝 Credits

**Creator:** Surjo  
**Game Title:** Platformer - Deadpool Edition  
**Engine:** Python 3.7+ with Pygame  

**Assets:**
- Character Sprites: Deadpool character animations (custom-created)
- Enemy Sprites: Alien character animations (custom-created)
- Background Images: Collected and curated collection
- Audio: Background music and sound effects
- UI Elements: Custom button graphics

**Development:** University Final Game Project  
**Copyright:** © 2025 Surjo. All rights reserved.

**License:** This game and all its assets are the original creation of Surjo.  
Assets are either newly created or sourced from copyright-free collections.  
The game is provided for educational and entertainment purposes.

---

## 🤝 Contributing

To improve the game:
1. Modify gameplay values in `main.py` (constants at top)
2. Create new levels with `level_editor_enhanced.py`
3. Add assets to `img/` folder
4. Update this README with changes

---

## ❓ FAQ

**Q: How many levels are there?**
A: The game includes 10 main levels plus 1 bonus level (11+). The system auto-detects new level files, so you can add more!

**Q: Can I create custom levels?**
A: Yes! Run `level_editor_enhanced.py` to create and edit levels visually.

**Q: How do I change the player character?**
A: Replace the image files in `img/deadpool char/` with your own animation frames, or modify the image loading in `Player.reset()`.

**Q: What's the highest score possible?**
A: There's no hard cap - it's the total coins collected across all 10 levels plus any bonus items in custom levels.

**Q: Can I play with a controller?**
A: Not currently, but keyboard controls use standard arrow keys. Gamepad support could be added in future versions.

**Q: Is the game open source?**
A: Yes! Feel free to modify and distribute for educational purposes.

---

## 📧 Support

For issues or questions:
- Check the Troubleshooting section above
- Verify all files are present in correct directories
- Ensure Python 3.7+ and Pygame are properly installed
- Review code comments in `main.py` for detailed explanations

---

**Enjoy the game and happy platforming!** 🎮✨
