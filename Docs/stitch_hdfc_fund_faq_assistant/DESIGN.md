---
name: Luminous Equity
colors:
  surface: '#0e1418'
  surface-dim: '#0e1418'
  surface-bright: '#343a3f'
  surface-container-lowest: '#090f13'
  surface-container-low: '#161c21'
  surface-container: '#1a2025'
  surface-container-high: '#242b2f'
  surface-container-highest: '#2f363a'
  on-surface: '#dde3e9'
  on-surface-variant: '#c1c6d6'
  inverse-surface: '#dde3e9'
  inverse-on-surface: '#2b3136'
  outline: '#8b909f'
  outline-variant: '#414754'
  surface-tint: '#acc7ff'
  primary: '#acc7ff'
  on-primary: '#002f68'
  primary-container: '#498fff'
  on-primary-container: '#00285b'
  inverse-primary: '#005bbf'
  secondary: '#c2c7d0'
  on-secondary: '#2c3138'
  secondary-container: '#42474f'
  on-secondary-container: '#b1b5bf'
  tertiary: '#c1c7d0'
  on-tertiary: '#2b3138'
  tertiary-container: '#8b9199'
  on-tertiary-container: '#242a31'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d7e2ff'
  primary-fixed-dim: '#acc7ff'
  on-primary-fixed: '#001a40'
  on-primary-fixed-variant: '#004492'
  secondary-fixed: '#dee2ec'
  secondary-fixed-dim: '#c2c7d0'
  on-secondary-fixed: '#171c23'
  on-secondary-fixed-variant: '#42474f'
  tertiary-fixed: '#dde3ec'
  tertiary-fixed-dim: '#c1c7d0'
  on-tertiary-fixed: '#161c23'
  on-tertiary-fixed-variant: '#41474f'
  background: '#0e1418'
  on-background: '#dde3e9'
  surface-variant: '#2f363a'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-max-width: 1200px
  gutter: 24px
  margin-desktop: 64px
  margin-mobile: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style

The design system is engineered for high-stakes financial clarity. It targets a sophisticated investor demographic that values precision, speed, and institutional trust. The visual narrative combines the vast, focused depth of an "Ultra-dark" space aesthetic with the modern transparency of Glassmorphism.

The style is **Modern Glassmorphic**. It utilizes deep radial gradients to create a sense of infinite canvas, while floating translucent interface layers provide organizational structure. This mirrors the product's core value: distilling complex mutual fund data into clear, layered, and accessible "facts-only" insights. The interface feels premium and technical, yet remains approachable through soft light refraction and high-contrast typography.

## Colors

The palette is anchored by **Deep Space (#0a0d14)**, serving as the immersive foundation. **HDFC Royal Blue (#2f81f7)** is the exclusive primary accent, reserved for high-intent interactions, user-specific messaging, and critical pathways to ensure brand recognition and trust.

Surface colors utilize a layered translucency:
- **Surface (Primary):** `rgba(22, 27, 34, 0.7)` for main chat containers and navigation.
- **Stroke/Border:** `rgba(48, 54, 61, 0.5)` for subtle definition without breaking the glass effect.
- **Status Indicators:** Success is represented by a vibrant emerald, and alerts by a muted crimson, used sparingly as dot-indicators to maintain the "facts-only" professional tone.

## Typography

This design system uses **Inter** exclusively to ensure maximum legibility for dense financial data across all resolutions. The typographic scale is designed for hierarchical scanning—investors should be able to distinguish "Fact Headlines" from "Statistical Body Text" at a glance.

Headlines use pure white (`#ffffff`) with tighter letter spacing for a compact, authoritative feel. Body text defaults to a soft, readable gray (`#8b949e`), while labels and metadata are rendered in all-caps with increased tracking for clear categorization.

## Layout & Spacing

The layout employs a **Fluid-to-Fixed Grid**. For the chat interface, the core content is centered within a fixed-width container (max 1200px) on desktop to prevent long line lengths that hinder readability. 

- **Desktop:** 12-column grid with 24px gutters. Elements follow a 4px/8px baseline rhythm.
- **Mobile:** Single column with 16px horizontal safe-area margins.
- **Reflow:** Sidebars for "Recent Inquiries" or "Fund Categories" collapse into a bottom-sheet or hamburger menu on mobile devices.

Spacing is generous around "Fact Blocks" to ensure data points do not feel cluttered, maintaining the premium, airy aesthetic.

## Elevation & Depth

Hierarchy is achieved through **Glassmorphic stacking** rather than traditional shadows. Depth is defined by increasing opacity and blur intensity:

1.  **Background (Level 0):** Deep #0a0d14 with a soft radial gradient in the top-right corner.
2.  **Base Surface (Level 1):** Translucent layers with a 12px `backdrop-blur` and a `1px` solid border (`rgba(48, 54, 61, 0.5)`).
3.  **Active/Hover State (Level 2):** Increased background opacity (0.85) and a faint inner glow to simulate light hitting the edge of the glass.
4.  **Overlays/Modals (Level 3):** 24px `backdrop-blur` to completely isolate the user from the background noise, focusing purely on the data.

Inner "ghost" shadows (low opacity white) on the top-left edge of components can be used to further the tactile glass feel.

## Shapes

The design system adopts a **Rounded** shape language to soften the "tech" edges and make the assistant feel helpful and modern. 

- **Base Radius:** 0.5rem (8px) for small inputs and buttons.
- **Large Radius:** 1rem (16px) for message bubbles and data cards.
- **Extra Large Radius:** 1.5rem (24px) for the main chat container and floating action menus.

All borders are thin (1px) and use the semi-transparent stroke token to ensure they feel like part of the glass pane rather than a separate structural element.

## Components

### Buttons & Actions
Primary buttons use a solid HDFC Royal Blue fill with white text. Secondary actions use the "Ghost Glass" style—a transparent background with a 1px border and high-blur backdrop.

### Message Bubbles
- **Assistant:** Subtle gray-glass background with white text to represent objective data.
- **User:** HDFC Royal Blue glass with white text, right-aligned to clearly differentiate the user's voice.

### Input Fields
The chat input is a wide, pill-shaped glass bar with a 12px blur. The "Send" button is nested within the bar as a circular icon button for a compact, modern feel.

### Data Cards & Tables
Mutual fund facts (NAV, Exit Load, Risk) are presented in cards with internal dividers using `rgba(48, 54, 61, 0.3)`. Tables utilize "Zebra Striping" with variable glass opacity for readability.

### Custom Scrollbars
Scrollbars are ultra-thin (4px), using a rounded HDFC Royal Blue thumb with a 30% opacity, becoming 100% on hover to minimize visual distraction from the content.

### Status Indicators
Small 8px circular dots. Green (`#3fb950`) for "Live Data Connected" and Red (`#f85149`) for "Service Unavailable". These are always accompanied by label-md text for accessibility.