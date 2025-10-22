# Deploy to Hugging Face Spaces

## Quick Deploy

1. **Create account**: https://huggingface.co/join

2. **Create new Space**:
   - Go to: https://huggingface.co/new-space
   - Name: `ugc-video-generator`
   - SDK: **Gradio**
   - Hardware: **CPU basic** (free) or **GPU** (paid)

3. **Push code**:

```bash
# Install git-lfs
brew install git-lfs
git lfs install

# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/ugc-video-generator
cd ugc-video-generator

# Copy files
cp /Users/janharmady/Desktop/projekty/ugc/gui.py app.py
cp -r /Users/janharmady/Desktop/projekty/ugc/src .
cp /Users/janharmady/Desktop/projekty/ugc/requirements.txt .

# Create README
cat > README.md << 'EOF'
---
title: UGC Video Generator
emoji: 🎥
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
---

# UGC Video Generator

AI-powered video generation using OpenAI Sora 2
EOF

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

4. **Add API Key**:
   - Go to Space Settings → Variables
   - Add: `OPENAI_API_KEY` = your key
   - Make it a **Secret**

5. **Done!** Your app will be live at:
   `https://huggingface.co/spaces/YOUR_USERNAME/ugc-video-generator`

## Cost
- **Free tier**: CPU basic (limited resources)
- **Paid**: $0.60/hour for GPU (recommended for video generation)

