---
title: "Building a Cybersecurity Console with Vite and TypeScript: How I Created cybersec.raze.mx"
date: 2025-10-10T12:00:00-05:00
description: "Ever wondered what it feels like to be a hacker in a movie? I built cybersec.raze.mx - a cybersecurity educational platform with a retro terminal interface using modern web technologies. Here's how I combined the aesthetics of old-school hacking with cutting-edge development tools like Vite, TypeScript, and some serious vibe coding."
categories: ["Development", "Cybersecurity", "Frontend"]
tags: ["TypeScript", "Vite", "Cybersecurity", "Web Development", "Terminal UI", "Educational", "JavaScript"]
thumbnail: "images/ghibli.png"
---

## From Matrix Dreams to Modern Reality

Picture this: You're watching a classic hacker movie, mesmerized by those green-on-black terminal screens, rapid-fire typing, and that satisfying *click-click-click* of commands executing. Fast forward to 2025, and I thought: "Why can't cybersecurity education look this cool?"

That's exactly how **[cybersec.raze.mx](https://cybersec.raze.mx)** was born - a cybersecurity educational platform that brings the Hollywood hacker aesthetic to real-world security education. But instead of using outdated terminal emulators, I built it with modern web technologies that would make any frontend developer proud.

## The Vision: Education Meets Entertainment

The cybersecurity field has a serious image problem. Most educational platforms look like they were designed in the early 2000s (and probably were). I wanted to create something that would:

- **Look intimidating** but be beginner-friendly
- **Feel authentic** like a real security professional's environment
- **Teach practical skills** through interactive experiences
- **Inspire newcomers** to dive deeper into cybersecurity

The result? A web-based cybersecurity console that feels like you're Neo, but actually teaches you about cookies, web security, and digital privacy.

## The Tech Stack: Modern Tools for Retro Vibes

### Why Vite? Speed is Security

When you're building educational tools, development speed matters. Students' attention spans are short, and if your build process takes forever, you'll lose momentum. That's where **Vite** came to the rescue:

```bash
# Lightning-fast setup
npm create vite@latest cybersec-console -- --template vanilla-ts
cd cybersec-console
npm install
npm run dev
```

Vite's instant hot module replacement meant I could iterate on the terminal interface in real-time. Change a color? Instant feedback. Add a new command? Boom, there it is. This rapid iteration was crucial for getting the "feel" right.

### TypeScript: Type Safety in the Wild West

Cybersecurity tools need to be reliable. There's no room for `undefined is not a function` when you're teaching someone about XSS attacks. TypeScript brought sanity to what could have been a chaotic codebase:

```typescript
interface TerminalCommand {
  name: string;
  description: string;
  execute: (args: string[]) => Promise<TerminalOutput>;
  category: SecurityCategory;
}

interface TerminalOutput {
  content: string;
  type: 'success' | 'error' | 'warning' | 'info';
  metadata?: CommandMetadata;
}

enum SecurityCategory {
  COOKIES = 'cookies',
  NETWORK = 'network',
  ENCRYPTION = 'encryption',
  SOCIAL_ENGINEERING = 'social'
}
```

This type system made it impossible to accidentally break the command parser or pass wrong parameters to security functions. In cybersecurity education, precision matters.

### The Art of Vibe Coding

Here's where things got interesting. "Vibe coding" isn't a technical term - it's a philosophy. It means coding based on how the interface should *feel*, not just how it should function.

For the terminal interface, I wanted that satisfying typewriter effect:

```typescript
class TerminalTypewriter {
  private readonly typingSpeed = 50; // ms per character
  private readonly cursorBlinkRate = 500; // ms
  
  async typeText(element: HTMLElement, text: string): Promise<void> {
    return new Promise((resolve) => {
      let index = 0;
      const interval = setInterval(() => {
        if (index < text.length) {
          element.textContent += text[index];
          index++;
        } else {
          clearInterval(interval);
          resolve();
        }
      }, this.typingSpeed);
    });
  }
  
  startCursorBlink(element: HTMLElement): void {
    setInterval(() => {
      element.classList.toggle('cursor-visible');
    }, this.cursorBlinkRate);
  }
}
```

But here's the thing about vibe coding - you have to balance aesthetics with performance. That smooth typing effect? It needed to be skippable for power users and accessible for screen readers.

## Building the Cookie Analyzer: My First Command

The first feature I built was a cookie analyzer - perfect for teaching web privacy fundamentals. Users could scan their browser cookies and see what data websites were collecting:

```typescript
class CookieAnalyzer {
  async scanCookies(): Promise<CookieReport> {
    const cookies = await this.getAllCookies();
    const analysis = cookies.map(cookie => ({
      name: cookie.name,
      domain: cookie.domain,
      riskLevel: this.assessRisk(cookie),
      purpose: this.identifyPurpose(cookie),
      expiry: cookie.expirationDate
    }));
    
    return {
      totalCookies: cookies.length,
      riskDistribution: this.calculateRiskDistribution(analysis),
      recommendations: this.generateRecommendations(analysis),
      details: analysis
    };
  }
  
  private assessRisk(cookie: Cookie): RiskLevel {
    // Complex risk assessment logic
    if (cookie.httpOnly && cookie.secure && cookie.sameSite === 'strict') {
      return RiskLevel.LOW;
    }
    if (cookie.domain.includes('tracker') || cookie.name.includes('_ga')) {
      return RiskLevel.HIGH;
    }
    return RiskLevel.MEDIUM;
  }
}
```

The beauty of this approach was that users learned by doing. Instead of reading about cookies in a boring article, they could actively scan their own browser and see real-world privacy implications.

## The Terminal Interface: Making Complex Simple

Creating a convincing terminal interface in the browser is trickier than it looks. You need to handle:

- **Command parsing and execution**
- **History navigation** (up/down arrows)
- **Auto-completion** for commands
- **Proper focus management**
- **Accessibility** for screen readers

Here's how I handled the command system:

```typescript
class SecurityConsole {
  private commands = new Map<string, TerminalCommand>();
  private history: string[] = [];
  private historyIndex = -1;
  
  constructor() {
    this.registerCommands();
    this.setupEventListeners();
  }
  
  private registerCommands(): void {
    this.commands.set('cookie-analyzer', new CookieAnalyzerCommand());
    this.commands.set('network-scan', new NetworkScanCommand());
    this.commands.set('help', new HelpCommand());
    this.commands.set('clear', new ClearCommand());
  }
  
  async executeCommand(input: string): Promise<void> {
    const [command, ...args] = input.trim().split(' ');
    
    if (!this.commands.has(command)) {
      await this.displayError(`Command not found: ${command}`);
      return;
    }
    
    const cmd = this.commands.get(command)!;
    try {
      const output = await cmd.execute(args);
      await this.displayOutput(output);
    } catch (error) {
      await this.displayError(`Error executing ${command}: ${error.message}`);
    }
  }
}
```

## Challenges: When Aesthetics Meet Reality

### The Performance vs. Prettiness Dilemma

That beautiful typewriter effect I mentioned? It looked amazing but became a usability nightmare for power users. Solution: Progressive enhancement.

```typescript
class AdaptiveInterface {
  private userPreferences = {
    animationsEnabled: true,
    typingSpeed: 50,
    soundEnabled: false
  };
  
  async displayText(text: string): Promise<void> {
    if (this.userPreferences.animationsEnabled) {
      await this.typewriter.typeText(this.outputElement, text);
    } else {
      this.outputElement.textContent = text;
    }
  }
  
  detectPowerUser(): boolean {
    // If user types fast or uses shortcuts, disable animations
    return this.averageTypingSpeed > 200 || this.shortcutUsage > 5;
  }
}
```

### Mobile Responsiveness: Terminals on Touchscreens

Terminals weren't designed for mobile, but education should be accessible everywhere. I had to rethink the entire interface:

```css
/* Desktop: Full terminal experience */
@media (min-width: 768px) {
  .terminal {
    font-family: 'JetBrains Mono', monospace;
    background: #0a0a0a;
    color: #00ff41;
    padding: 2rem;
  }
}

/* Mobile: Simplified command interface */
@media (max-width: 767px) {
  .terminal {
    padding: 1rem;
    font-size: 14px;
  }
  
  .command-suggestions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.5rem;
    margin: 1rem 0;
  }
}
```

### Accessibility: Making Hacker Aesthetics Inclusive

Green text on black backgrounds look cool but are terrible for accessibility. The solution was a theme system that maintained the vibe while being inclusive:

```typescript
enum Theme {
  MATRIX = 'matrix',        // Green on black
  AMBER = 'amber',          // Amber on dark brown
  HIGH_CONTRAST = 'contrast', // White on black
  LIGHT = 'light'           // Dark on light
}

class ThemeManager {
  applyTheme(theme: Theme): void {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('preferred-theme', theme);
  }
  
  detectUserPreferences(): Theme {
    if (window.matchMedia('(prefers-contrast: high)').matches) {
      return Theme.HIGH_CONTRAST;
    }
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      // Disable animations for motion-sensitive users
      this.disableAnimations();
    }
    return Theme.MATRIX; // Default to the cool one
  }
}
```

## The Learning Architecture: Gamification Without the Cheese

Education platforms often fall into the trap of over-gamification - adding points and badges that feel meaningless. Instead, I focused on intrinsic motivation:

```typescript
interface LearningPath {
  id: string;
  title: string;
  description: string;
  commands: Command[];
  realWorldScenario: string;
  completionCriteria: string[];
}

const cookiePrivacyPath: LearningPath = {
  id: 'cookie-privacy',
  title: 'Web Privacy Fundamentals',
  description: 'Learn how websites track you and how to protect yourself',
  commands: ['cookie-analyzer', 'privacy-check', 'tracker-blocker'],
  realWorldScenario: 'You notice your browsing seems unusually targeted...',
  completionCriteria: [
    'Analyze cookies on 3 different websites',
    'Identify at least 2 tracking cookies',
    'Configure browser privacy settings'
  ]
};
```

Progress felt natural because users were solving real problems, not arbitrary challenges.

## Performance Optimization: Fast Like a Real Terminal

Web-based terminals can feel sluggish compared to native ones. Here's how I kept things snappy:

### Virtual Scrolling for Command History

```typescript
class VirtualScrollConsole {
  private visibleLines = 50;
  private totalLines = 0;
  private scrollTop = 0;
  
  renderVisibleLines(): void {
    const startIndex = Math.floor(this.scrollTop / this.lineHeight);
    const endIndex = Math.min(startIndex + this.visibleLines, this.totalLines);
    
    // Only render what's visible
    this.outputContainer.innerHTML = '';
    for (let i = startIndex; i < endIndex; i++) {
      this.outputContainer.appendChild(this.lines[i]);
    }
  }
}
```

### Debounced Command Suggestions

```typescript
class CommandSuggester {
  private suggestionCache = new Map<string, string[]>();
  
  getSuggestions = debounce(async (input: string): Promise<string[]> => {
    if (this.suggestionCache.has(input)) {
      return this.suggestionCache.get(input)!;
    }
    
    const suggestions = await this.computeSuggestions(input);
    this.suggestionCache.set(input, suggestions);
    return suggestions;
  }, 150);
}
```

## Deployment: Vite's Production Magic

Vite's build process made deployment a breeze:

```bash
# Build for production
npm run build

# Output analysis
npm run preview
```

The resulting bundle was tiny (thanks to tree-shaking) and blazing fast (thanks to Vite's optimizations). Deploying to a CDN meant users worldwide could access the console with minimal latency.

## Lessons Learned: Technical and Philosophical

### 1. Aesthetics Drive Engagement

The terminal interface wasn't just eye candy - it fundamentally changed how users approached cybersecurity learning. They felt like professionals from day one.

### 2. TypeScript Saves Sanity

In a project with complex state management and real-time interactions, TypeScript prevented countless bugs and made refactoring painless.

### 3. Vite Changes Everything

The development experience was so smooth that I could focus on user experience instead of fighting build tools.

### 4. Progressive Enhancement Works

Start with the cool stuff, then make it accessible. Users who need simpler interfaces get them automatically.

### 5. Education is UX

The best educational content in the world is useless if the interface gets in the way.

## What's Next: The Roadmap

The cybersec console is just the beginning. Here's what's coming:

- **Network Security Module**: Scan for open ports and vulnerabilities
- **Social Engineering Simulator**: Practice recognizing phishing attempts
- **Cryptography Playground**: Hands-on encryption/decryption exercises
- **Incident Response Training**: Simulated security breach scenarios
- **Mobile Security Toolkit**: Smartphone privacy and security

## The Code That Powers the Dream

Want to build something similar? Here's the starter template I'd use today:

```bash
# Start with Vite + TypeScript
npm create vite@latest security-console -- --template vanilla-ts

# Add essential dependencies
npm install
npm install -D @types/node

# Optional: Add testing
npm install -D vitest @vitest/ui
```

Key architectural decisions:

- **Modular command system** for easy extensibility
- **Event-driven architecture** for real-time updates
- **Progressive enhancement** for accessibility
- **Performance-first** rendering strategies

## Final Thoughts: When Code Meets Purpose

Building cybersec.raze.mx taught me that the best projects happen when technical skills meet genuine passion. I didn't just want to build another website - I wanted to make cybersecurity education as engaging as the field itself.

The terminal aesthetic wasn't a gimmick; it was a bridge between Hollywood's vision of cybersecurity and the real-world skills students need to learn. By making users feel like professionals from their first command, we removed the intimidation factor that keeps many people away from cybersecurity.

Modern web technologies like Vite and TypeScript made it possible to build something that looked retro but performed like cutting-edge software. And that's the real magic - using today's tools to solve yesterday's problems in tomorrow's interface.

**Try it yourself**: Visit [cybersec.raze.mx](https://cybersec.raze.mx) and run `help` to get started. Type `cookie-analyzer --scan` to see your browser's privacy footprint, and let me know what you discover!

The future of cybersecurity education isn't in boring PDFs or outdated interfaces - it's in experiences that make learning feel like an adventure. And with tools like Vite and TypeScript, that future is just a `npm create` away.

---

*What kind of educational interfaces are you building? Have you tried combining retro aesthetics with modern web technologies? Share your experiments in the comments below - I'd love to see what the community is creating!*
