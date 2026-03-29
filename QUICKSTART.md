# Quick Start Guide - Yamaha PSR-i455 Professional MIDI Studio

## 🚀 Getting Started in 3 Steps

### Step 1: Check MIDI Connection
```powershell
python main.py
```
You should see:
```
INPUT PORTS:
['Digital Keyboard 0']

OUTPUT PORTS:
['Digital Keyboard 1']
```
✓ If you see both, your Yamaha is ready!

### Step 2: Start the Studio
```powershell
python studio.py
```

Or use the batch file (Windows):
```
Double-click: start.bat
```

### Step 3: Start Making Music!
```
Press [R] to record
Play on your Yamaha keyboard
Press [T] to stop
```

## 📋 Essential Commands

| Action | Key |
|--------|-----|
| **Record** | R |
| **Stop Recording** | T |
| **Save Session** | S |
| **Export to MIDI** | E |
| **Quit** | Q |

## 🎵 First Session

1. **Launch** the app: `python studio.py`
2. **Press R** to start recording
3. **Play some notes** on your Yamaha
4. **Press T** to stop
5. **Press S** to save your session
6. **Press E** to export as MIDI

## 💾 File Locations

After recording, check these folders:
- **Sessions** (JSON format): `sessions/`
- **Exports** (MIDI format): `exports/`

## 🎹 What You'll See

```
┌─────────────────────────────────────────────┐
│        88-Key Piano Keyboard Display        │
│  (Real-time visualization of your playing)  │
├─────────────────────────────────────────────┤
│ Chord: C Major          Status: ⏹ IDLE     │
│ Scale: Major            BPM: 120            │
│ Velocity: 95            Messages: 156       │
│ Active Notes: 3                             │
└─────────────────────────────────────────────┘
```

## 🔍 Real-Time Features

As you play, you'll see:
- **Piano Keyboard**: Which keys you're pressing (highlighted in blue)
- **Chord Detection**: What chord you're playing (e.g., "C Major")
- **Scale Analysis**: What scale emerges from your playing
- **Velocity**: How hard you're pressing (0-127)
- **Session Stats**: How many notes you've recorded

## 🎛️ Recording Mode

When you press **R**:
1. Display shows "🔴 RECORDING"
2. Every note is captured with timing
3. Continue playing until ready
4. Press **T** to stop

## 💫 Advanced Features

After getting comfortable, explore:

- **[1-5]**: Change scale visualizations
- **[+-]**: Adjust BPM
- **[L]**: Load previous sessions
- **[C]**: Clear current track
- **[P]**: Playback (coming soon)

## 🐛 Troubleshooting

**No MIDI Connection?**
- Check USB cable between Yamaha and computer
- Run: `python main.py` to verify detection
- Try different USB port
- Restart Yamaha keyboard

**Display glitches?**
- Close other graphics-heavy programs
- Update GPU drivers
- Reduce monitor refresh rate

**Latency issues?**
- Close other MIDI applications
- Use USB 3.0 port if available
- Disable background programs

## 📚 Next Steps

1. Read [README.md](README.md) for complete feature list
2. Check [ADVANCED.md](ADVANCED.md) for customization
3. Explore scale/chord analysis
4. Build multi-track compositions
5. Export to your DAW

## 🎓 Learning Resources

### Music Theory Basics
- The app auto-detects chords and scales
- Watch the "Chord" and "Scale" fields as you play
- Experiment with different keys and scales

### Recording Tips
- Use tracks for different sections (intro, verse, chorus)
- Save frequently with [S]
- Export to MIDI for further editing in DAWs

### Performance
- Monitor velocity to enhance expression
- Use scale visualization to stay in key
- Track multiple takes and compare

## 📞 Need Help?

1. Check README.md for detailed feature info
2. Review ADVANCED.md for customization
3. Run: `python main.py` to check MIDI setup  
4. Look at the logs for error messages

---

**You're all set!** 🎉 

Press [R] and start creating!

