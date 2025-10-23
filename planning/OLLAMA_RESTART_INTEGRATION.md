# ZeroRAG Start App - Ollama Restart Integration

## Overview

The `start_app.py` and `start_app.bat` scripts have been updated to automatically restart Ollama before starting the ZeroRAG application. This ensures that the LLM service always uses Ollama as the primary provider instead of falling back to HuggingFace.

## Changes Made

### 1. Updated `start_app.py`

**New Functions Added:**
- `restart_ollama()` - Restarts the Ollama service with cross-platform support
- `check_ollama_health()` - Checks if Ollama is running and accessible
- `restart_llm_service()` - Restarts the LLM service to detect Ollama

**Enhanced Startup Process:**
1. **Restart Ollama** - Stops and starts Ollama service
2. **Wait for Ollama** - Ensures Ollama is ready before proceeding
3. **Restart LLM Service** - Forces re-detection of available providers
4. **Start API Server** - Continues with normal startup
5. **Start Streamlit** - Launches the UI

**Cross-Platform Support:**
- **Windows**: Uses `taskkill` and multiple Ollama installation paths
- **Linux/macOS**: Uses `pkill` and standard Ollama commands

### 2. Updated `start_app.bat`

**Enhanced Features:**
- Added dependency checking
- Better error handling
- Updated messaging to reflect Ollama restart functionality

## Benefits

### ✅ Reliable Ollama Usage
- Ensures Ollama is always used as the primary LLM provider
- Eliminates the singleton initialization issue
- No more unexpected fallback to HuggingFace

### ✅ Fresh Service State
- Restarts Ollama for a clean state
- Resets LLM service to detect providers correctly
- Prevents cached configuration issues

### ✅ Better User Experience
- Automated setup process
- Clear progress indicators
- Helpful error messages and troubleshooting tips

## Usage

### Option 1: Python Script
```bash
python start_app.py
```

### Option 2: Batch File (Windows)
```bash
start_app.bat
```

## Startup Sequence

```
🤖 Starting ZeroRAG Application...
🔄 Restarting Ollama...
⏹️  Stopping Ollama service...
▶️  Starting Ollama service...
✅ Ollama started using: ollama
⏳ Waiting for Ollama to be ready...
✅ Ollama is ready!
🔄 Restarting LLM service to detect Ollama...
✅ LLM service restarted successfully!
🚀 Starting ZeroRAG API server...
⏳ Waiting for API server to start...
✅ API server is ready!
🎨 Starting ZeroRAG Streamlit app...
🎉 ZeroRAG is now running!
```

## Error Handling

The script includes comprehensive error handling:

- **Ollama Not Found**: Provides installation guidance
- **Ollama Startup Failure**: Continues with fallback options
- **LLM Service Issues**: Warns but doesn't block startup
- **API Server Problems**: Clear timeout and troubleshooting messages

## Troubleshooting

### If Ollama restart fails:
1. Check if Ollama is installed
2. Verify Ollama is in your system PATH
3. Try running `ollama serve` manually
4. Check firewall/antivirus settings

### If LLM service restart fails:
1. The application will still start with fallback models
2. You can manually run `python restart_llm_service.py`
3. Check the logs for specific error messages

### If API server doesn't start:
1. Check if port 8000 is available
2. Verify all Python dependencies are installed
3. Check the API server logs for errors

## Files Modified

1. `start_app.py` - Main startup script with Ollama restart
2. `start_app.bat` - Windows batch file with enhanced checks
3. `test_start_app.py` - Test script for validation
4. `restart_llm_service.py` - LLM service restart utility (existing)

## Configuration

The Ollama restart functionality uses these paths (Windows):
- `ollama` (if in PATH)
- `C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe`
- `C:\Program Files\Ollama\ollama.exe`
- `C:\Program Files (x86)\Ollama\ollama.exe`

On Linux/macOS, it uses the standard `ollama` command.

## Testing

Run the test script to verify functionality:
```bash
python test_start_app.py
```

This validates that all functions are properly loaded and Ollama is accessible.

---

**Result**: Your ZeroRAG application will now consistently use Ollama as the primary LLM provider, eliminating the fallback issues you were experiencing! 🎉