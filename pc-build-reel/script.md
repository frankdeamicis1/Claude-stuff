# GPU / FPS reel: script, caption, DM reply

42.5 s, 1080×1920. The video works with the sound off: every line is on screen.
If you want to talk over it, the voiceover lines below follow the on-screen
timing. Read them straight; they're written the way you talk.

## Funnel shape

| Time | Beat | Job |
|---|---|---|
| 0:00 | "Your graphics card draws about 1,000,000,000 pixels every second" (counter spins up while you hold the GPU) | Hook |
| 0:03 | "Let's do the math real quick" (your hands-together pose from the photo) + name tag | Who's talking |
| 0:06 | 4K = 3840 × 2160 = 8,294,400 pixels, × 120 = 995,328,000 / sec | Fun fact |
| 0:15 | 1 frame every 8.3 ms, then you blink and it draws 12 frames | Fun fact payoff |
| 0:21 | CPU figures out the game, GPU draws it. 1080p → 4K = 4× the pixels, CPU work about the same | Why the GPU matters most |
| 0:29 | "In most games, your GPU decides your FPS" | The takeaway |
| 0:31 | GPU clicks in, glass on, power on | The build moment |
| 0:33 | 30 FPS vs 144 FPS side by side | Show the difference |
| 0:36 | "Want a PC that actually hits the frames you're paying for? DM me FPS" | CTA |

## Voiceover (optional, word for word)

- **0:00** Your graphics card draws about a billion pixels every second.
- **0:03** Let's do the math real quick.
- **0:06** A 4K screen is 3840 by 2160. That's 8,294,400 pixels.
- **0:09** Now do that 120 times a second, because that's what 120 FPS means.
- **0:11** That's 995,328,000 pixels a second. Basically a billion. Which is honestly kind of insane.
- **0:15** So it gets about 8 milliseconds to draw each frame.
- **0:18** You blink slower than that. It drew 12 frames while you blinked.
- **0:21** Here's the thing. Your CPU figures out what's happening in the game. Your graphics card is what actually draws it.
- **0:25** Go from 1080p to 4K and that's 4 times the pixels. The CPU's job stays about the same. The GPU's doesn't.
- **0:29** So in most games, the GPU decides your FPS.
- **0:31** *(click)* GPU in.
- **0:33** Same game, different GPU. More frames looks smoother, and it feels more responsive.
- **0:36** If you want a PC that actually hits the frames you're paying for, DM me "FPS." Send me your budget and the games you play, and I'll tell you what I'd build.

## Post caption

> Your graphics card draws about a billion pixels every second at 4K, 120 FPS. I did the math.
>
> 8,294,400 pixels a frame × 120 frames = 995,328,000 pixels a second. That's 8.3 ms per frame.
>
> Your CPU figures out what's happening in the game. The GPU actually draws it. So in most games, the GPU decides your FPS.
>
> Want a PC that actually hits the frames you're paying for? DM me "FPS" with your budget and the games you play. I'll tell you what I'd build.
>
> #gamingpc #pcbuild #gpu #fps #custompc

## DM reply (next step of the funnel)

When someone sends "FPS", whether you reply by hand or with an auto-reply:

> Hey, appreciate you reaching out. Two quick questions so I can point you the right way: what's your budget, and what games do you play? If you know your monitor (1080p, 1440p, 4K, refresh rate), send that too. I'll tell you what I'd build for it.

## Fact check (all on screen)

- 4K UHD = 3840 × 2160 = **8,294,400** pixels. × 120 = **995,328,000** pixels/sec.
- 1 second ÷ 120 = **8.33 ms** per frame. 144 FPS = 6.9 ms, 30 FPS = 33.3 ms.
- A blink is roughly 100–150 ms (often quoted as up to 400 ms), so "12 frames" is the low end. On screen it says "a blink takes about 100 ms."
- 1080p = 2,073,600 px, 1440p = 3,686,400 px, so 4K is exactly 4× 1080p.
- "In most games the GPU decides your FPS" holds at 1440p and 4K. At 1080p with a fast GPU, some esports titles are CPU-limited. That's why it says "most."
- The 30 vs 144 FPS lanes are a simulation: each dot is a frame the GPU drew in the last ~0.2 s.

## Things to change before posting (one line each in `reel.html`)

- CTA keyword: search for `“FPS”` (the green button) and `DM me` in the caption text.
- Name tag text: search for `builds &amp; sells gaming PCs`.
- Then run `./build.sh` to re-render.
