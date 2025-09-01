# Multi-Provider API Setup Guide

This guide will help you set up your cost-optimized multi-provider API strategy to achieve ~9,000+ daily requests for nearly $0.

## Your Optimal Strategy

- **Google AI Studio**: 1,500 free requests/day × multiple accounts = 3,000-4,500 requests
- **Groq**: 6,000 free requests/day (lightning fast)
- **OpenRouter**: 50 free requests/day (perfect for fact-checking)  
- **Cerebras**: 30 free requests/day (excellent for deep analysis)

**Total: 9,000+ requests/day for $0**

## Step 1: Google AI Studio Setup

### Account 1 (Primary)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your primary Google account
3. Create a new API key
4. Add to `.env` as `GOOGLE_AI_STUDIO_KEY_1`

### Account 2 (Secondary)  
1. Sign out and use a different Google account
2. Repeat the process
3. Add to `.env` as `GOOGLE_AI_STUDIO_KEY_2`

### Pro Account
1. Use your Google Pro account
2. Create API key
3. Add to `.env` as `GOOGLE_AI_STUDIO_PRO_KEY`

**Daily Limit**: 1,500 requests per account × 3 accounts = 4,500 requests

## Step 2: Groq Setup

1. Go to [Groq Console](https://console.groq.com/keys)
2. Sign up/sign in
3. Create a new API key
4. Add to `.env` as `GROQ_API_KEY`

**Daily Limit**: 6,000 requests (very fast inference)

## Step 3: OpenRouter Setup

1. Go to [OpenRouter](https://openrouter.ai/keys)
2. Sign up/sign in  
3. Get your free tier API key
4. Add to `.env` as `OPENROUTER_API_KEY`

**Daily Limit**: 50 requests (perfect for fact-checking)

## Step 4: Cerebras Setup

1. Go to [Cerebras Cloud](https://cloud.cerebras.ai/)
2. Sign up for free tier
3. Get API key from dashboard
4. Add to `.env` as `CEREBRAS_API_KEY`

**Daily Limit**: 30 requests (excellent quality)

## Step 5: Configure Environment

Create/edit your `.env` file:

```env
# Google AI Studio (1,500 free requests/day per account)
GOOGLE_AI_STUDIO_KEY_1=your_key_from_account_1
GOOGLE_AI_STUDIO_KEY_2=your_key_from_account_2  
GOOGLE_AI_STUDIO_PRO_KEY=your_pro_account_key

# Groq (6,000 free requests/day - super fast)
GROQ_API_KEY=your_groq_key

# OpenRouter (50 free requests/day - fact checking)
OPENROUTER_API_KEY=your_openrouter_key

# Cerebras (30 free requests/day - deep analysis)
CEREBRAS_API_KEY=your_cerebras_key
```

## How the System Routes Requests

The system automatically routes requests based on agent type for optimal performance:

### Agent-Provider Mapping
- **Skeptic Agent** → Groq (fast debate responses)
- **Synthesizer Agent** → Google AI Studio (high-quality synthesis)  
- **Analyst Agent** → Cerebras (deep analysis)
- **Explorer Agent** → Groq (creative responses)
- **Fact Checker** → OpenRouter (verification)

### Automatic Fallbacks
If a provider is unavailable or quota exceeded, the system automatically falls back to:
1. Secondary provider for the agent type
2. Google AI Studio (with account rotation)
3. Demo mode (if no providers available)

## Usage Monitoring

Track your usage with the `usage` command:

```
> usage

API Usage Report:
Total Requests: 47
Total Failures: 2
Daily Cost: $0.0000
Monthly Est: $0.00

Provider Status:
  ✓ google_ai_studio: 12/4500 (4488 left)
  ✓ groq: 28/6000 (5972 left)
  ✓ openrouter: 5/50 (45 left)
  ✓ cerebras: 2/30 (28 left)
```

## Cost Optimization Features

### 1. **Intelligent Routing**
- Agents automatically use the most cost-effective provider
- Quality vs speed optimization per agent type

### 2. **Quota Management**  
- Daily quota tracking with automatic reset
- Prevents over-limit charges
- Real-time availability checking

### 3. **Account Rotation**
- Google accounts rotate automatically
- Maximizes free tier utilization
- Seamless failover

### 4. **Graceful Degradation**
- Falls back to demo mode if all providers exhausted
- No system downtime

## Expected Performance

With this setup, you can expect:

- **Daily Capacity**: 9,000+ requests
- **Monthly Cost**: $0 (free tiers only)
- **Response Speed**: 
  - Groq: < 1 second
  - Google AI Studio: 1-3 seconds  
  - Cerebras: 2-4 seconds
  - OpenRouter: 3-5 seconds

## Scaling Options

When you need more capacity:

1. **More Google Accounts**: Add additional accounts for 1,500 more requests each
2. **Paid Tiers**: Upgrade specific providers based on usage patterns
3. **Additional Providers**: Add more free tier providers

## Troubleshooting

### Common Issues

**"Provider not available"**
- Check API key in `.env` file
- Verify account has remaining quota
- Try `usage` command to see status

**"All providers failed"**  
- All daily quotas exhausted
- System will auto-reset at midnight UTC
- Use demo mode for testing

**"Quota exceeded"**
- One provider hit daily limit
- System automatically uses fallback
- Check `usage` for remaining capacity

This setup gives you enterprise-level multi-agent discussions at consumer-friendly costs!