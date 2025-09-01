# 🚀 One-Click Deployment

## Deploy to Render (Free)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/indra7777/LLM-GD)

**After clicking deploy:**
1. Connect your GitHub account
2. Set your environment variables:
   - `GOOGLE_AI_STUDIO_KEY_1` - Your Google AI Studio key
   - `GOOGLE_AI_STUDIO_KEY_2` - (Optional) Additional key  
   - `GOOGLE_AI_STUDIO_KEY_3` - (Optional) Additional key
   - `GOOGLE_AI_STUDIO_KEY_4` - (Optional) Additional key
   - `PORT` - Set to `10000`
   - `DEBUG` - Set to `false`

3. Click "Create Web Service"
4. Wait 5-10 minutes for build to complete
5. Your app will be live at `https://your-app-name.onrender.com`

## Get API Keys (Free)

### Google AI Studio (Recommended - Free tier)
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click "Get API key"
3. Create new project or select existing
4. Generate API key
5. Copy the key to use as `GOOGLE_AI_STUDIO_KEY_1`

### Additional Providers (Optional)
- **Groq**: [console.groq.com](https://console.groq.com) - 6000 free requests/day
- **OpenAI**: [platform.openai.com](https://platform.openai.com) - $5 free credit
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com) - $5 free credit

## Manual Deployment Steps

If the one-click deploy doesn't work:

### Step 1: Fork Repository
1. Go to https://github.com/indra7777/LLM-GD
2. Click "Fork" to create your own copy

### Step 2: Deploy to Render
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your forked repository
5. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python web_api.py`
   - **Python Version**: 3.11

### Step 3: Add Environment Variables
In Render dashboard, add:
```
GOOGLE_AI_STUDIO_KEY_1=your_key_here
PORT=10000
DEBUG=false
```

### Step 4: Deploy Frontend (Static Site)
1. Create another service: "Static Site"
2. Same repository, different settings:
   - **Build Command**: `cd web && npm install && npm run build`
   - **Publish Directory**: `web/build`

## Other Deployment Options

### Railway (Alternative Free Option)
```bash
npm install -g @railway/cli
railway login
railway init
railway deploy
```

### Docker (Any Platform)
```bash
docker build -t llm-group-discussion .
docker run -p 8000:8000 llm-group-discussion
```

## Troubleshooting

### Build Fails
- Check that all environment variables are set
- Ensure Python version is 3.11 
- Verify requirements.txt exists

### App Won't Start
- Check logs in Render dashboard
- Ensure PORT is set to 10000
- Verify at least one AI provider key is valid

### Frontend Not Loading  
- Check that backend URL is correct
- Verify CORS settings include your domain
- Check browser console for errors

## Support

If you need help:
1. Check the logs in your Render dashboard
2. Review the DEPLOYMENT.md file
3. Ensure all environment variables are set correctly

Your app will be live at: `https://your-app-name.onrender.com`

🎉 **That's it! Your LLM Group Discussion app is now live!**